"""Capa 2: análisis estático parejo para ambos lenguajes.

- lizard: complejidad ciclomática, líneas y parámetros por función (mismo criterio en Scala y Python).
- Verificador de reglas de la práctica: detecta for/while/var/mutación y cuenta los recursos funcionales.
  Python se analiza con su árbol de sintaxis (ast); Scala con un lexer que descarta comentarios y textos.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import lizard

from comun import archivos_fuente

# ============================== LIZARD ==============================


def complejidad(lang: dict) -> dict:
    funciones, total_nloc = [], 0
    for archivo in archivos_fuente(lang):
        info = lizard.analyze_file(str(archivo))
        total_nloc += info.nloc
        rel = str(archivo.relative_to(lang["fuentes"]))
        funciones += [{
            "funcion": f.name, "archivo": rel, "linea": f.start_line, "ccn": f.cyclomatic_complexity,
            "nloc": f.nloc, "parametros": len(f.parameters), "tokens": f.token_count,
        } for f in info.function_list]
    ccns = [f["ccn"] for f in funciones] or [0]
    return {
        "nloc": total_nloc,
        "funciones": len(funciones),
        "ccn_promedio": round(sum(ccns) / len(ccns), 2),
        "ccn_maximo": max(ccns),
        "nloc_promedio_funcion": round(sum(f["nloc"] for f in funciones) / (len(funciones) or 1), 2),
        "funciones_ccn_mayor_10": sum(1 for c in ccns if c > 10),
        "detalle": sorted(funciones, key=lambda f: (-f["ccn"], f["funcion"])),
    }


# ============================== REGLAS: PYTHON ==============================

FUNCIONES_ORDEN_SUPERIOR = {"map", "filter", "sorted", "reduce", "sum", "any", "all", "next", "zip",
                            "enumerate", "min", "max", "groupby", "partial"}
METODOS_MUTADORES = {"append", "extend", "insert", "pop", "remove", "clear", "update", "add",
                     "discard", "setdefault", "popitem", "sort", "reverse"}


class VisitantePython(ast.NodeVisitor):
    def __init__(self, archivo: str):
        self.archivo = archivo
        self.violaciones: list[dict] = []
        self.positivos = {"lambdas": 0, "orden_superior": 0, "recursivas": 0, "inmutables": 0, "funciones": 0}
        self.ambitos: list[set] = [set()]
        self.funcion_actual: list[str] = []

    def violar(self, nodo, regla: str, detalle: str):
        self.violaciones.append({"regla": regla, "archivo": self.archivo, "linea": nodo.lineno, "detalle": detalle})

    # --- ciclos ---
    def visit_For(self, n):
        self.violar(n, "for", "ciclo for"); self.generic_visit(n)
    visit_AsyncFor = visit_For

    def visit_While(self, n):
        self.violar(n, "while", "ciclo while"); self.generic_visit(n)

    def _comprension(self, n):
        self.violar(n, "for", f"comprensión ({type(n).__name__}) — contiene un for implícito"); self.generic_visit(n)
    visit_ListComp = visit_SetComp = visit_DictComp = visit_GeneratorExp = _comprension

    # --- mutabilidad ---
    def visit_Global(self, n):
        self.violar(n, "estado global", "uso de global"); self.generic_visit(n)
    visit_Nonlocal = visit_Global

    def visit_AugAssign(self, n):
        self.violar(n, "reasignación", f"asignación compuesta ({ast.unparse(n.target)} …=)"); self.generic_visit(n)

    def _nombres(self, objetivo) -> list:
        if isinstance(objetivo, ast.Name):
            return [objetivo]
        if isinstance(objetivo, (ast.Tuple, ast.List)):
            return [x for e in objetivo.elts for x in self._nombres(e)]
        return []

    def _registrar_asignacion(self, n, objetivos):
        for obj in objetivos:
            if isinstance(obj, (ast.Subscript, ast.Attribute)):
                self.violar(n, "mutación", f"modifica {ast.unparse(obj)}")
            for nombre in self._nombres(obj):
                if nombre.id in self.ambitos[-1]:
                    self.violar(n, "reasignación", f"'{nombre.id}' se asigna más de una vez")
                self.ambitos[-1].add(nombre.id)

    def visit_Assign(self, n):
        self._registrar_asignacion(n, n.targets); self.generic_visit(n)

    def visit_AnnAssign(self, n):
        if n.value is not None:
            self._registrar_asignacion(n, [n.target])
        self.generic_visit(n)

    def visit_Call(self, n):
        if isinstance(n.func, ast.Attribute) and n.func.attr in METODOS_MUTADORES:
            self.violar(n, "mutación", f"método mutador .{n.func.attr}()")
        nombre = n.func.id if isinstance(n.func, ast.Name) else n.func.attr if isinstance(n.func, ast.Attribute) else None
        if nombre in FUNCIONES_ORDEN_SUPERIOR:
            self.positivos["orden_superior"] += 1
        self.generic_visit(n)

    def visit_Lambda(self, n):
        self.positivos["lambdas"] += 1; self.generic_visit(n)

    def visit_FunctionDef(self, n):
        self.positivos["funciones"] += 1
        llamadas = {c.func.id for c in ast.walk(n) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}
        if n.name in llamadas:
            self.positivos["recursivas"] += 1
        self.ambitos.append({a.arg for a in n.args.args + n.args.kwonlyargs})
        self.generic_visit(n)
        self.ambitos.pop()
    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, n):
        congelada = any("frozen" in ast.unparse(d) for d in n.decorator_list)
        es_enum = any(ast.unparse(b) in ("Enum", "enum.Enum") for b in n.bases)
        if congelada or es_enum:
            self.positivos["inmutables"] += 1
        self.ambitos.append(set())
        self.generic_visit(n)
        self.ambitos.pop()


def reglas_python(lang: dict) -> dict:
    visitantes = []
    for archivo in archivos_fuente(lang):
        v = VisitantePython(str(archivo.relative_to(lang["fuentes"])))
        v.visit(ast.parse(archivo.read_text(encoding="utf-8")))
        visitantes.append(v)
    return consolidar(visitantes)


# ============================== REGLAS: SCALA ==============================


def limpiar_scala(codigo: str) -> str:
    """Reemplaza comentarios y literales de texto por espacios, conservando los saltos de línea."""
    patron = re.compile(r'"""[\s\S]*?"""|"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])\'|//[^\n]*|/\*[\s\S]*?\*/')
    return patron.sub(lambda m: re.sub(r"[^\n]", " ", m.group()), codigo)


REGLAS_SCALA = [
    ("var", r"\bvar\b", "variable mutable var"),
    ("while", r"\bwhile\b", "ciclo while"),
    ("for", r"\bfor\b", "ciclo/comprensión for"),
    ("do-while", r"\bdo\s*\{", "ciclo do-while"),
    ("mutación", r"\bcollection\.mutable\b|\bmutable\.\w+|\b(ArrayBuffer|ListBuffer|HashMap|StringBuilder)\b|\+=|-=", "colección o asignación mutable"),
    ("return", r"\breturn\b", "return explícito (estilo imperativo)"),
    ("null", r"\bnull\b", "uso de null en vez de Option"),
]
HOF_SCALA = r"\.(map|filter|flatMap|foldLeft|foldRight|fold|reduce|sortBy|sortWith|groupBy|count|exists|forall|find|collect|zip|zipWithIndex|sum|take|partition|mkString|headOption|getOrElse)\b"


class AnalizadorScala:
    def __init__(self, archivo: str, codigo: str):
        self.archivo = archivo
        self.violaciones: list[dict] = []
        limpio = limpiar_scala(codigo)
        lineas = limpio.splitlines()
        # Option(StdIn.readLine()) envuelve null de Java: se permite si aparece dentro de Option(...)
        for regla, patron, detalle in REGLAS_SCALA:
            for num, linea in enumerate(lineas, 1):
                if re.search(patron, linea):
                    self.violaciones.append({"regla": regla, "archivo": archivo, "linea": num, "detalle": detalle})
        defs = [(m.group(1), m.start(), len(m.group(0)) - len(m.group(0).lstrip()))
                for m in re.finditer(r"(?m)^[ \t]*(?:(?:private|protected|override|final|inline)\s+)*def\s+(\w+)", limpio)]
        recursivas = 0
        for i, (nombre, inicio, sangria) in enumerate(defs):
            fin = next((d[1] for d in defs[i + 1:] if d[2] <= sangria), len(limpio))
            cuerpo = limpio[inicio:fin]
            cuerpo_sin_firma = cuerpo.split("=", 1)[1] if "=" in cuerpo else ""
            if re.search(rf"(?<![.\w]){nombre}\s*[\(\[]", cuerpo_sin_firma):
                recursivas += 1
        self.positivos = {
            "lambdas": len(re.findall(r"=>", limpio)) - len(re.findall(r"\bcase\b[^\n]*=>", limpio)),
            "orden_superior": len(re.findall(HOF_SCALA, limpio)),
            "recursivas": recursivas,
            "inmutables": len(re.findall(r"\bcase\s+class\b|\benum\b", limpio)),
            "funciones": len(defs),
            "tailrec": len(re.findall(r"@tailrec", codigo)),
            "pattern_matching": len(re.findall(r"\bmatch\b", limpio)),
        }


def reglas_scala(lang: dict) -> dict:
    return consolidar([AnalizadorScala(str(a.relative_to(lang["fuentes"])), a.read_text(encoding="utf-8"))
                       for a in archivos_fuente(lang)])


# ============================== CONSOLIDACIÓN ==============================

REGLAS_PRACTICA = ["for", "while", "do-while", "var", "reasignación", "mutación", "estado global", "return", "null"]


def consolidar(analizadores: list) -> dict:
    violaciones = [v for a in analizadores for v in a.violaciones]
    claves = {k for a in analizadores for k in a.positivos}
    positivos = {k: sum(a.positivos.get(k, 0) for a in analizadores) for k in sorted(claves)}
    por_regla = {r: sum(1 for v in violaciones if v["regla"] == r) for r in REGLAS_PRACTICA}
    return {"violaciones": violaciones, "por_regla": por_regla, "total_violaciones": len(violaciones), "positivos": positivos}


def analizar(lang: dict) -> dict:
    reglas = reglas_scala(lang) if lang["id"] == "scala" else reglas_python(lang)
    comp = complejidad(lang)
    por_100 = reglas["total_violaciones"] / (comp["nloc"] or 1) * 100
    funcionales = reglas["positivos"].get("lambdas", 0) + reglas["positivos"].get("orden_superior", 0)
    return {
        "complejidad": comp,
        "reglas": reglas,
        "violaciones_por_100_lineas": round(por_100, 2),
        "densidad_funcional": round(funcionales / (comp["nloc"] or 1) * 100, 2),
    }
