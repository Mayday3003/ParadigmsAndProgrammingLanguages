"""Capa 3 y 4: rendimiento y equivalencia de resultados.

1. Genera entradas válidas de distintos tamaños (misma semilla → mismos datos en cada ejecución).
2. Compila Scala (midiendo el tiempo de construcción) y detecta automáticamente los puntos de entrada.
3. Ejecuta cada programa con cada entrada: verifica que termine, mide memoria máxima y compara
   la salida de ambos lenguajes. Luego mide el tiempo con hyperfine (varias corridas).
"""

from __future__ import annotations

import json
import random
import re
import shutil
import time
from pathlib import Path

from comun import SALIDAS_DIR, archivos_fuente, ejecutar, log, aviso, python_actual

CLIENTES = ["Bancolombia", "EAFIT", "Clínica Las Vegas", "Éxito", "UdeM", "Sura", "EPM", "Argos",
            "Nutresa", "Comfama", "Metro de Medellín", "ISA", "Haceb", "Postobón", "Colanta"]
TECNICOS = ["Laura Gómez", "Carlos Ruiz", "Andrés Mejía", "Sofía Herrera", "Juan Pérez", "Valentina Ríos"]


def generar_entrada(n: int, semilla: int = 360) -> Path:
    rnd = random.Random(semilla + n)
    lineas = [str(n)]
    for i in range(1, n + 1):
        lineas += [f"S{i:05d}", rnd.choice(CLIENTES), rnd.choice(TECNICOS), str(rnd.randint(1, 3)),
                   str(rnd.randint(1, 3)), str(rnd.randint(1, 3)), f"{rnd.uniform(0.5, 40):.1f}",
                   str(rnd.randrange(20000, 120000, 500))]
    lineas += ["13", "0"]  # mostrar todos los reportes y salir
    destino = SALIDAS_DIR / "entradas" / f"entrada_{n}.txt"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return destino


# ============================== PUNTOS DE ENTRADA ==============================


def clase_principal_scala(lang: dict) -> str | None:
    """Busca `def main(` dentro de un object, o una función anotada con @main (Scala 3)."""
    for archivo in archivos_fuente(lang):
        codigo = archivo.read_text(encoding="utf-8")
        paquete = re.search(r"^\s*package\s+([\w.]+)", codigo, re.M)
        prefijo = f"{paquete.group(1)}." if paquete else ""
        anotada = re.search(r"@main\s+def\s+(\w+)", codigo)
        if anotada:
            return prefijo + anotada.group(1)
        if re.search(r"\bdef\s+main\s*\(", codigo):
            objeto = re.search(r"\bobject\s+(\w+)", codigo)
            if objeto:
                return prefijo + objeto.group(1)
    return None


def entrada_python(lang: dict) -> Path | None:
    candidatos = [a for a in archivos_fuente(lang) if "__main__" in a.read_text(encoding="utf-8")]
    preferido = [a for a in candidatos if a.name == "main.py"]
    return (preferido or candidatos or [None])[0]


def preparar_scala(lang: dict) -> dict:
    if not shutil.which("sbt"):
        return {"ok": False, "error": "sbt no está instalado"}
    clase = clase_principal_scala(lang)
    if not clase:
        return {"ok": False, "error": "No se encontró un método main en el código Scala"}
    log("Scala: compilando desde cero con sbt (se mide el tiempo de construcción) …")
    inicio = time.perf_counter()
    r = ejecutar(["sbt", "-batch", "-error", "clean", "compile"], cwd=lang["carpeta"], timeout=900)
    construccion = time.perf_counter() - inicio
    if r.returncode != 0:
        return {"ok": False, "error": "Error de compilación:\n" + (r.stdout + r.stderr).decode(errors="replace")[-2000:]}
    cp = ejecutar(["sbt", "-batch", "-error", "export Runtime/fullClasspath"], cwd=lang["carpeta"], timeout=600)
    classpath = cp.stdout.decode().strip().splitlines()[-1] if cp.returncode == 0 else ""
    return {"ok": bool(classpath), "comando": ["java", "-Xss16m", "-cp", classpath, clase],
            "cwd": lang["carpeta"], "construccion_s": round(construccion, 2), "punto_entrada": clase,
            "error": None if classpath else "No se pudo obtener el classpath"}


def preparar_python(lang: dict) -> dict:
    principal = entrada_python(lang)
    if not principal:
        return {"ok": False, "error": "No se encontró un archivo con if __name__ == '__main__'"}
    inicio = time.perf_counter()
    r = ejecutar([python_actual(), "-m", "py_compile", *map(str, archivos_fuente(lang))])
    construccion = time.perf_counter() - inicio
    if r.returncode != 0:
        return {"ok": False, "error": "Error de sintaxis:\n" + r.stderr.decode(errors="replace")[-2000:]}
    return {"ok": True, "comando": [python_actual(), str(principal)], "cwd": principal.parent,
            "construccion_s": round(construccion, 2), "punto_entrada": str(principal.relative_to(lang["carpeta"]))}


# ============================== EJECUCIÓN ==============================


def corrida_unica(prep: dict, entrada: Path, timeout: int) -> dict:
    """Ejecuta una vez midiendo memoria máxima con /usr/bin/time."""
    medidor = ["/usr/bin/time", "-f", "__MEDIDA__ %M %e"] if Path("/usr/bin/time").exists() else []
    try:
        r = ejecutar(medidor + prep["comando"], cwd=prep["cwd"], entrada=entrada, timeout=timeout)
    except Exception as e:  # timeout
        return {"ok": False, "error": f"No terminó en {timeout} s ({type(e).__name__})", "salida": ""}
    err = r.stderr.decode(errors="replace")
    medida = re.search(r"__MEDIDA__ (\d+) ([\d.]+)", err)
    err_limpio = re.sub(r"__MEDIDA__.*|Command exited with non-zero status \d+|Command terminated by signal \d+", "", err).strip()
    salida = r.stdout.decode(errors="replace")
    ok = r.returncode == 0
    return {
        "ok": ok,
        "codigo_salida": r.returncode,
        "memoria_mb": round(int(medida.group(1)) / 1024, 1) if medida else None,
        "tiempo_s": float(medida.group(2)) if medida else None,
        "error": None if ok else (err_limpio.splitlines()[-1] if err_limpio else f"código de salida {r.returncode}"),
        "salida": salida,
    }


def medir_hyperfine(prep: dict, entrada: Path, corridas: int, nombre: str) -> dict | None:
    if not shutil.which("hyperfine"):
        return None
    destino = SALIDAS_DIR / "hyperfine" / f"{nombre}.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    comando = " ".join(f"'{p}'" for p in prep["comando"])
    r = ejecutar(["hyperfine", "--runs", str(corridas), "--warmup", "1", "--input", str(entrada),
                  "--output", "null", "--export-json", str(destino), "--command-name", nombre, comando],
                 cwd=prep["cwd"], timeout=1800)
    if r.returncode != 0 or not destino.exists():
        return None
    res = json.loads(destino.read_text())["results"][0]
    # hyperfine < 1.19 guarda mean/stddev en la raíz; las versiones nuevas en summary.time_wall_clock
    tiempos = res if "mean" in res else res["summary"]["time_wall_clock"]
    return {k: round(tiempos[k] or 0, 4) for k in ("mean", "stddev", "min", "max", "median")}


def normalizar_salida(texto: str) -> list[str]:
    return [l.rstrip() for l in texto.strip().splitlines()]


def comparar(a: str, b: str) -> dict:
    la, lb = normalizar_salida(a), normalizar_salida(b)
    diferentes = [i for i in range(max(len(la), len(lb))) if (la[i:i + 1] or [""])[0] != (lb[i:i + 1] or [""])[0]]
    return {
        "identicas": not diferentes,
        "lineas_diferentes": len(diferentes),
        "total_lineas": max(len(la), len(lb)),
        "primera_diferencia": None if not diferentes else {
            "linea": diferentes[0] + 1,
            "a": (la[diferentes[0]:diferentes[0] + 1] or ["<sin línea>"])[0],
            "b": (lb[diferentes[0]:diferentes[0] + 1] or ["<sin línea>"])[0],
        },
    }


def preparar_todos(lenguajes: list[dict]) -> dict:
    preparados = {l["id"]: (preparar_scala(l) if l["id"] == "scala" else preparar_python(l)) for l in lenguajes}
    for lid, p in preparados.items():
        if not p["ok"]:
            aviso(f"{lid}: {p['error']}")
    return preparados


def analizar(lenguajes: list[dict], preparados: dict, tamanos: list[int], corridas: int, timeout: int) -> dict:

    resultados = []
    for n in tamanos:
        entrada = generar_entrada(n)
        fila = {"n": n, "lenguajes": {}}
        for l in lenguajes:
            prep = preparados[l["id"]]
            if not prep["ok"]:
                fila["lenguajes"][l["id"]] = {"ok": False, "error": prep["error"]}
                continue
            log(f"{l['nombre']}: ejecutando con {n} solicitudes …")
            unica = corrida_unica(prep, entrada, timeout)
            if unica["ok"]:
                unica["hyperfine"] = medir_hyperfine(prep, entrada, corridas, f"{l['id']}_{n}")
            else:
                aviso(f"{l['nombre']} falló con {n} solicitudes: {unica['error']}")
            fila["lenguajes"][l["id"]] = unica
        ids = [l["id"] for l in lenguajes]
        a, b = (fila["lenguajes"].get(i, {}) for i in ids)
        if a.get("ok") and b.get("ok"):
            fila["equivalencia"] = comparar(a["salida"], b["salida"])
        (SALIDAS_DIR / "entradas" / f"salida_{n}.txt").write_text(
            "\n\n".join(f"===== {i} =====\n{fila['lenguajes'][i].get('salida', '')}" for i in ids), encoding="utf-8")
        for i in ids:
            fila["lenguajes"][i].pop("salida", None)
        resultados.append(fila)

    return {
        "preparacion": {k: {c: v for c, v in p.items() if c not in ("comando", "cwd")} for k, p in preparados.items()},
        "corridas": corridas,
        "tamanos": resultados,
    }
