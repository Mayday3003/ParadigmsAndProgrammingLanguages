"""Capa 5: garantías del paradigma funcional (experimentos sobre copias del código).

Experimento A — Errores inyectados: se introduce en una COPIA de cada proyecto un error típico que
rompe el paradigma funcional y se observa si el lenguaje lo detecta antes de ejecutar (compilación),
al ejecutar, o nunca. Los puntos de inyección se detectan automáticamente:
  · el registro de datos  → case class / dataclass con más campos
  · un campo numérico     → primer campo Double/Int (Scala) o float/int (Python)
  · dónde se construye    → llamada al registro con argumento nombrado para ese campo
  · un enum               → primer enum con al menos dos casos

Experimento B — Recursión bajo estrés: se procesan entradas cada vez más grandes para comprobar si
la recursión (que reemplaza a los ciclos) aguanta: @tailrec en Scala vs. límite de pila en Python.
"""

from __future__ import annotations

import ast
import re
import shutil
from pathlib import Path

import rendimiento
from comun import SALIDAS_DIR, archivos_fuente, ejecutar, log, aviso

ANSI = re.compile(r"\x1b\[[0-9;]*m")

# ============================== DETECCIÓN DEL MODELO ==============================


def modelo_scala(lang: dict) -> dict:
    registros, enums = [], []
    for a in archivos_fuente(lang):
        codigo = a.read_text(encoding="utf-8")
        for m in re.finditer(r"case\s+class\s+(\w+)\s*\(([^)]*)\)", codigo):
            campos = re.findall(r"(\w+)\s*:\s*([\w\[\]]+)", m.group(2))
            registros.append({"nombre": m.group(1), "campos": campos, "archivo": a})
        for m in re.finditer(r"\benum\s+(\w+)[^\n]*\n((?:[ \t]+[^\n]*\n|\s*\n)+)", codigo):
            casos = re.findall(r"\bcase\s+(\w+(?:\s*,\s*\w+)*)", m.group(2))
            nombres = [c.strip() for grupo in casos for c in grupo.split(",")]
            if len(nombres) >= 2:
                enums.append({"nombre": m.group(1), "casos": nombres, "archivo": a})
    registro = max(registros, key=lambda r: len(r["campos"]), default=None)
    numerico = next((c for c, t in (registro or {}).get("campos", []) if t in ("Double", "Int", "Long", "Float", "BigDecimal")), None)
    return {"registro": registro, "numerico": numerico, "enum": enums[0] if enums else None}


def modelo_python(lang: dict) -> dict:
    registros, enums = [], []
    for a in archivos_fuente(lang):
        arbol = ast.parse(a.read_text(encoding="utf-8"))
        for n in ast.walk(arbol):
            if not isinstance(n, ast.ClassDef):
                continue
            if any("dataclass" in ast.unparse(d) for d in n.decorator_list):
                campos = [(s.target.id, ast.unparse(s.annotation)) for s in n.body
                          if isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name)]
                registros.append({"nombre": n.name, "campos": campos, "archivo": a, "nodo": n})
            if any(ast.unparse(b) in ("Enum", "enum.Enum") for b in n.bases):
                casos = [s.targets[0].id for s in n.body if isinstance(s, ast.Assign) and isinstance(s.targets[0], ast.Name)]
                if len(casos) >= 2:
                    enums.append({"nombre": n.name, "casos": casos, "archivo": a})
    registro = max(registros, key=lambda r: len(r["campos"]), default=None)
    numerico = next((c for c, t in (registro or {}).get("campos", []) if t in ("float", "int")), None)
    return {"registro": registro, "numerico": numerico, "enum": enums[0] if enums else None}


# ============================== MUTACIONES ==============================
# Cada mutación recibe (copia del proyecto, modelo detectado, lenguaje) y modifica la copia.
# Devuelve el fragmento inyectado (para mostrarlo en el dashboard) o None si no es aplicable.


def _en_copia(lang: dict, copia: Path, archivo: Path) -> Path:
    return copia / archivo.relative_to(lang["carpeta"])


def _agregar_al_final(ruta: Path, texto: str) -> None:
    ruta.write_text(ruta.read_text(encoding="utf-8").rstrip() + "\n\n" + texto + "\n", encoding="utf-8")


def _py_insertar_post_init(lang, copia, mod, sentencia: str) -> str | None:
    """Agrega (o extiende) __post_init__ en el dataclass: se ejecuta cada vez que se crea un registro."""
    reg = mod["registro"]
    if not reg:
        return None
    ruta = _en_copia(lang, copia, reg["archivo"])
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    nodo = reg["nodo"]
    sangria = " " * nodo.body[0].col_offset
    existente = next((f for f in nodo.body if isinstance(f, ast.FunctionDef) and f.name == "__post_init__"), None)
    if existente:
        pos, bloque = existente.body[0].lineno - 1, [sangria * 2 + sentencia]
    else:
        pos, bloque = nodo.end_lineno, ["", sangria + "def __post_init__(self):", sangria * 2 + sentencia]
    ruta.write_text("\n".join(lineas[:pos] + bloque + lineas[pos:]) + "\n", encoding="utf-8")
    return sentencia


def m_reasignar(lang, copia, mod):
    if lang["id"] == "scala":
        reg = mod["registro"]
        archivo = reg["archivo"] if reg else archivos_fuente(lang)[0]
        codigo = "def __reasignar(): Int =\n  val total = 1\n  total = 2\n  total"
        _agregar_al_final(_en_copia(lang, copia, archivo), codigo)
        return codigo
    archivo = mod["registro"]["archivo"] if mod["registro"] else archivos_fuente(lang)[0]
    codigo = "def __reasignar():\n    total = 1\n    total = 2\n    return total"
    _agregar_al_final(_en_copia(lang, copia, archivo), codigo)
    return codigo


def m_mutar_registro(lang, copia, mod):
    reg, campo = mod["registro"], mod["numerico"]
    if not reg or not campo:
        return None
    if lang["id"] == "scala":
        codigo = f"def __mutar(r: {reg['nombre']}): Unit =\n  r.{campo} = r.{campo} * 2"
        _agregar_al_final(_en_copia(lang, copia, reg["archivo"]), codigo)
        return codigo
    return _py_insertar_post_init(lang, copia, mod, f"self.{campo} = self.{campo} * 2")


def m_campo_inexistente(lang, copia, mod):
    reg, campo = mod["registro"], mod["numerico"]
    if not reg or not campo:
        return None
    if lang["id"] == "scala":
        codigo = f"def __errata(r: {reg['nombre']}): Double =\n  r.{campo}s * 2"
        _agregar_al_final(_en_copia(lang, copia, reg["archivo"]), codigo)
        return codigo
    return _py_insertar_post_init(lang, copia, mod, f"_ = self.{campo}s * 2")


def m_tipo_incorrecto(lang, copia, mod):
    """Convierte a texto el valor de un campo numérico justo donde se construye el registro."""
    reg, campo = mod["registro"], mod["numerico"]
    if not reg or not campo:
        return None
    for a in archivos_fuente(lang):
        ruta = _en_copia(lang, copia, a)
        texto = ruta.read_text(encoding="utf-8")
        if lang["id"] == "scala":
            if f"{reg['nombre']}(" not in texto:
                continue
            patron = re.compile(rf"^(\s*{campo}\s*=\s*)(.+?)(,?)\s*$", re.M)
            m = patron.search(texto)
            if m:
                nuevo = f"{m.group(1)}({m.group(2)}).toString{m.group(3)}"
                ruta.write_text(texto[:m.start()] + nuevo + texto[m.end():], encoding="utf-8")
                return nuevo.strip()
        else:
            arbol = ast.parse(texto)
            llamada = next((k for n in ast.walk(arbol) if isinstance(n, ast.Call) and ast.unparse(n.func).split(".")[-1] == reg["nombre"]
                            for k in n.keywords if k.arg == campo), None)
            if llamada:
                lineas = texto.splitlines(keepends=True)
                ini = _byte_a_char(lineas, llamada.value.lineno, llamada.value.col_offset)
                fin = _byte_a_char(lineas, llamada.value.end_lineno, llamada.value.end_col_offset)
                original = texto[ini:fin]
                ruta.write_text(texto[:ini] + f"str({original})" + texto[fin:], encoding="utf-8")
                return f"{campo}=str({original})"
    return None


def _byte_a_char(lineas: list[str], lineno: int, col_bytes: int) -> int:
    """ast entrega columnas en bytes UTF-8; se convierten a posición de carácter en el texto."""
    previo = sum(map(len, lineas[:lineno - 1]))
    return previo + len(lineas[lineno - 1].encode()[:col_bytes].decode(errors="ignore"))


def m_match_incompleto(lang, copia, mod):
    enum = mod["enum"]
    if not enum:
        return None
    primero = enum["casos"][0]
    if lang["id"] == "scala":
        codigo = f'def __describir(e: {enum["nombre"]}): String = e match\n  case {enum["nombre"]}.{primero} => "{primero}"'
    else:
        codigo = (f"def __describir(e):\n    match e:\n        case {enum['nombre']}.{primero}:\n"
                  f"            return \"{primero}\"")
    _agregar_al_final(_en_copia(lang, copia, enum["archivo"]), codigo)
    return codigo


MUTACIONES = [
    ("reasignar", "Reasignar un valor inmutable", "Se declara un valor y luego se le asigna otro (en Scala `val`, en Python una variable).", m_reasignar),
    ("mutar", "Modificar un registro inmutable", "Se cambia un campo de una solicitud ya creada (case class / frozen dataclass).", m_mutar_registro),
    ("tipo", "Tipo incorrecto en un campo", "Las horas se guardan como texto en lugar de número al construir la solicitud.", m_tipo_incorrecto),
    ("errata", "Error de tipeo en un campo", "Se accede a un campo que no existe (por ejemplo `horass`).", m_campo_inexistente),
    ("match", "Caso faltante en un match", "Un `match` sobre un enum solo maneja uno de sus casos.", m_match_incompleto),
]

# ============================== EJECUCIÓN ==============================


def copiar(lang: dict, destino: Path) -> Path:
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(lang["carpeta"], destino, ignore=shutil.ignore_patterns(".bsp", ".idea", "__pycache__", ".scannerwork"))
    return destino


def compilar_scala(carpeta: Path) -> dict:
    r = ejecutar(["sbt", "-batch", "-no-colors", "compile"], cwd=carpeta, timeout=900)
    texto = ANSI.sub("", (r.stdout + r.stderr).decode(errors="replace"))
    errores = [l[8:].strip() for l in texto.splitlines() if l.startswith("[error]") and l[8:].strip()]
    avisos = [l[7:].strip() for l in texto.splitlines() if l.startswith("[warn]") and l[7:].strip()]
    return {"ok": r.returncode == 0, "errores": errores, "avisos": avisos}


def mensaje_relevante(lineas: list[str]) -> str:
    """Línea del compilador que describe el problema (sin la ruta, el código ni los adornos |)."""
    limpias = [re.sub(r"\s+", " ", l.strip(" |")) for l in lineas]
    claves = ("Reassignment", "Found:", "not a member", "not exhaustive", "match may not", "mismatch", "Not found")
    i = next((i for i, l in enumerate(limpias) if any(k in l for k in claves)), None)
    if i is None:
        return limpias[0] if limpias else ""
    requerido = next((l for l in limpias[i + 1:i + 3] if l.startswith("Required:")), None)
    return f"Tipo incorrecto · {limpias[i]} · {requerido}" if limpias[i].startswith("Found:") and requerido else limpias[i]


def ejecutar_y_comparar(comando: list[str], cwd: Path, entrada: Path, referencia: str) -> dict:
    try:
        r = ejecutar(comando, cwd=cwd, entrada=entrada, timeout=120)
    except Exception:
        return {"estado": "ejecucion", "mensaje": "El programa no terminó (se quedó bloqueado)"}
    if r.returncode != 0:
        err = r.stderr.decode(errors="replace").strip().splitlines()
        return {"estado": "ejecucion", "mensaje": err[-1] if err else f"código de salida {r.returncode}"}
    if r.stdout.decode(errors="replace").strip() != referencia.strip():
        return {"estado": "silencioso", "mensaje": "Se ejecutó sin errores pero produjo resultados distintos"}
    return {"estado": "no_detectado", "mensaje": "Se ejecutó normalmente; el lenguaje lo permitió sin aviso"}


def experimento_mutaciones(lang: dict, prep: dict, entrada: Path) -> list[dict]:
    mod = modelo_scala(lang) if lang["id"] == "scala" else modelo_python(lang)
    base = SALIDAS_DIR / "garantias" / lang["id"]
    referencia = ejecutar(prep["comando"], cwd=prep["cwd"], entrada=entrada, timeout=120).stdout.decode(errors="replace")
    avisos_base = len(compilar_scala(copiar(lang, base / "_base"))["avisos"]) if lang["id"] == "scala" else 0
    resultados = []
    for mid, nombre, desc, mutar in MUTACIONES:
        copia = copiar(lang, base / mid)
        try:
            inyectado = mutar(lang, copia, mod)
        except Exception as e:  # el código cambió de forma que la mutación no se puede aplicar
            inyectado, error_inyeccion = None, str(e)
        else:
            error_inyeccion = None
        fila = {"id": mid, "nombre": nombre, "descripcion": desc, "codigo": inyectado}
        if inyectado is None:
            resultados.append(fila | {"estado": "no_aplica", "mensaje": error_inyeccion or "No se encontró dónde aplicarla en este código"})
            continue
        log(f"{lang['nombre']}: probando «{nombre}» …")
        if lang["id"] == "scala":
            comp = compilar_scala(copia)
            if not comp["ok"]:
                resultados.append(fila | {"estado": "compilacion", "mensaje": mensaje_relevante(comp["errores"])})
                continue
            if len(comp["avisos"]) > avisos_base:
                resultados.append(fila | {"estado": "advertencia", "mensaje": mensaje_relevante(comp["avisos"])})
                continue
            comando = [p.replace(str(lang["carpeta"]), str(copia)) for p in prep["comando"]]
            resultados.append(fila | ejecutar_y_comparar(comando, copia, entrada, referencia))
        else:
            chequeo = ejecutar([prep["comando"][0], "-m", "py_compile", *map(str, archivos_fuente({**lang, "fuentes": copia}))])
            if chequeo.returncode != 0:
                resultados.append(fila | {"estado": "compilacion", "mensaje": chequeo.stderr.decode(errors="replace").strip().splitlines()[-1]})
                continue
            principal = copia / Path(prep["comando"][1]).relative_to(lang["carpeta"])
            resultados.append(fila | ejecutar_y_comparar([prep["comando"][0], str(principal)], principal.parent, entrada, referencia))
    shutil.rmtree(base, ignore_errors=True)
    return resultados


def experimento_recursion(langs: list[dict], preparados: dict, tamanos: list[int], timeout: int) -> list[dict]:
    filas = []
    caidos: set = set()
    for n in tamanos:
        entrada = rendimiento.generar_entrada(n)
        fila = {"n": n, "lenguajes": {}}
        for l in langs:
            if l["id"] in caidos:  # si ya falló con menos datos, con más también fallará
                fila["lenguajes"][l["id"]] = {"ok": False, "error": "omitido: ya falló con una entrada menor"}
                continue
            log(f"{l['nombre']}: recursión con {n} solicitudes …")
            r = rendimiento.corrida_unica(preparados[l["id"]], entrada, timeout)
            r.pop("salida", None)
            fila["lenguajes"][l["id"]] = r
            if not r["ok"]:
                caidos.add(l["id"])
        filas.append(fila)
    return filas


def analizar(langs: list[dict], preparados: dict, tamanos_recursion: list[int], timeout: int) -> dict:
    if not all(p["ok"] for p in preparados.values()):
        aviso("Garantías: algún lenguaje no se pudo preparar; se omiten los experimentos")
        return {"estado": "omitido"}
    entrada = rendimiento.generar_entrada(10)
    mutaciones = {l["id"]: experimento_mutaciones(l, preparados[l["id"]], entrada) for l in langs}
    recursion = experimento_recursion(langs, preparados, tamanos_recursion, timeout)
    resumen = {}
    for l in langs:
        aplicables = [m for m in mutaciones[l["id"]] if m["estado"] != "no_aplica"]
        antes = [m for m in aplicables if m["estado"] in ("compilacion", "advertencia")]
        exitos = [f["n"] for f in recursion if f["lenguajes"][l["id"]].get("ok")]
        resumen[l["id"]] = {
            "detectados_antes": len(antes), "aplicables": len(aplicables),
            "pct_antes": round(len(antes) / (len(aplicables) or 1) * 100, 1),
            "no_detectados": sum(1 for m in aplicables if m["estado"] in ("no_detectado", "silencioso")),
            "max_recursion": max(exitos, default=0),
        }
    return {"estado": "ok", "mutaciones": mutaciones, "recursion": recursion, "resumen": resumen}
