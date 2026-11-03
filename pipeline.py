"""Flujo completo de análisis comparativo Scala vs Python.

Uso (desde scala/analisis):  ./analizar.sh            (o: python pipeline.py --help)

Todo se calcula a partir del código fuente actual de las dos carpetas: si se modifica el código,
basta con ejecutar de nuevo para obtener métricas, veredictos y dashboard actualizados.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

import dashboard
import estatico
import garantias
import puntaje
import rendimiento
import sonar
from comun import ANALISIS_DIR, REPORTE_DIR, SALIDAS_DIR, archivos_fuente, huella, lenguaje, log, aviso, raiz_repo


def argumentos():
    p = argparse.ArgumentParser(description="Análisis comparativo Scala vs Python (SonarQube + métricas + rendimiento)")
    p.add_argument("--scala", default=str(ANALISIS_DIR.parent / "soporte360-scala"), help="carpeta del proyecto Scala")
    p.add_argument("--python", default=str(ANALISIS_DIR.parent / "soporte360-python"), help="carpeta del proyecto Python")
    p.add_argument("--tamanos", default="5", help="compatibilidad; el benchmark usa datos/benchmark.txt")
    p.add_argument("--corridas", type=int, default=5, help="corridas de hyperfine por medición")
    p.add_argument("--timeout", type=int, default=180, help="segundos máximos por ejecución")
    p.add_argument("--escenarios", default=str(ANALISIS_DIR / "escenarios.json"))
    p.add_argument("--sin-sonar", action="store_true", help="omitir SonarQube")
    p.add_argument("--sin-rendimiento", action="store_true", help="omitir benchmarks")
    p.add_argument("--sin-garantias", action="store_true", help="omitir los experimentos de garantías funcionales")
    p.add_argument("--recursion", default="5000,10000,20000", help="tamaños de la prueba de estrés de recursión")
    return p.parse_args()


def resumen_lenguaje(res: dict, lid: str) -> dict:
    """Indicadores clave para comparar contra la ejecución anterior."""
    s = res["sonar"].get("lenguajes", {}).get(lid, {})
    e = res["estatico"][lid]
    grande = next(reversed([f for f in (res.get("rendimiento") or {}).get("tamanos", [])]), None)
    g = grande["lenguajes"].get(lid, {}) if grande else {}
    return {
        "Líneas de código": s.get("ncloc", e["complejidad"]["nloc"]),
        "Complejidad ciclomática": s.get("complexity"),
        "Complejidad cognitiva": s.get("cognitive_complexity"),
        "Code smells": s.get("code_smells"),
        "Bugs": s.get("bugs"),
        "Violaciones reglas práctica": e["reglas"]["total_violaciones"],
        "Funciones": e["complejidad"]["funciones"],
        "Errores detectados antes de ejecutar (%)": (res.get("garantias") or {}).get("resumen", {}).get(lid, {}).get("pct_antes"),
        "Recursión máxima soportada": (res.get("garantias") or {}).get("resumen", {}).get(lid, {}).get("max_recursion"),
        f"Tiempo {grande['n'] if grande else ''} solicitudes (s)": (g.get("hyperfine") or {}).get("mean", g.get("tiempo_s")),
        **{f"Puntaje · {esc['nombre']}": esc["totales"][lid] for esc in res["puntaje"]["escenarios"]},
    }


def comparar_con_anterior(actual: dict, anterior: dict | None, ids: list[str]) -> dict | None:
    if not anterior:
        return None
    try:
        filas = []
        for lid in ids:
            antes, ahora = resumen_lenguaje(anterior, lid), resumen_lenguaje(actual, lid)
            for k, v in ahora.items():
                a = antes.get(k)
                if isinstance(v, (int, float)) and isinstance(a, (int, float)) and round(v, 3) != round(a, 3):
                    filas.append({"lenguaje": lid, "indicador": k, "antes": a, "ahora": v})
        return {"fecha_anterior": anterior["fecha"],
                "huellas_anteriores": {i: anterior["lenguajes"][i]["huella"] for i in ids},
                "cambios": filas}
    except Exception:
        return None


def main():
    args = argumentos()
    langs = [lenguaje("scala", "Scala", Path(args.scala), ".scala"),
             lenguaje("python", "Python", Path(args.python), ".py")]
    for l in langs:
        if not archivos_fuente(l):
            raise SystemExit(f"No se encontraron archivos {l['ext']} en {l['fuentes']}")
    ids = [l["id"] for l in langs]
    raiz = raiz_repo(ANALISIS_DIR)
    SALIDAS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTE_DIR.mkdir(parents=True, exist_ok=True)

    res = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "lenguajes": {l["id"]: {"nombre": l["nombre"], "carpeta": str(l["carpeta"].relative_to(raiz)),
                               "archivos": [str(a.relative_to(l["fuentes"])) for a in archivos_fuente(l)],
                               "huella": huella(archivos_fuente(l))} for l in langs},
    }

    log("1/5 SonarQube (SonarAnalyzer Scala + Python)")
    res["sonar"] = {"estado": "omitido", "motivo": "--sin-sonar"} if args.sin_sonar else \
        sonar.analizar(raiz, os.environ.get("SONAR_TOKEN"), langs)

    log("2/5 Análisis estático (lizard + reglas de la práctica)")
    res["estatico"] = {l["id"]: estatico.analizar(l) for l in langs}

    preparados = None if args.sin_rendimiento and args.sin_garantias else rendimiento.preparar_todos(langs)

    log("3/5 Rendimiento y equivalencia de resultados")
    res["rendimiento"] = None if args.sin_rendimiento else rendimiento.analizar(
        langs, preparados, [int(t) for t in args.tamanos.split(",")], args.corridas, args.timeout)

    log("4/5 Garantías del paradigma funcional (errores inyectados + recursión bajo estrés)")
    res["garantias"] = {"estado": "omitido"} if args.sin_garantias else garantias.analizar(
        langs, preparados, [int(t) for t in args.recursion.split(",")], max(args.timeout, 300))

    log("5/5 Escenarios y dashboard")
    config = json.loads(Path(args.escenarios).read_text(encoding="utf-8"))
    res["puntaje"] = puntaje.calcular(res, config, ids)

    historial = SALIDAS_DIR / "historial"
    historial.mkdir(exist_ok=True)
    previos = sorted(historial.glob("resultados_*.json"))
    anterior = json.loads(previos[-1].read_text(encoding="utf-8")) if previos else None
    res["comparacion_anterior"] = comparar_con_anterior(res, anterior, ids)

    texto = json.dumps(res, ensure_ascii=False, indent=2)
    (SALIDAS_DIR / "resultados.json").write_text(texto, encoding="utf-8")
    (historial / f"resultados_{datetime.now():%Y%m%d-%H%M%S}.json").write_text(texto, encoding="utf-8")
    destino = dashboard.generar(res, REPORTE_DIR / "dashboard.html")

    print()
    log("Resultado por escenario:")
    for e in res["puntaje"]["escenarios"]:
        g = res["lenguajes"][e["ganador"]]["nombre"] if e["ganador"] else "Empate"
        puntos = "  ".join(f"{res['lenguajes'][i]['nombre']} {e['totales'][i]:.2f}" for i in ids)
        print(f"   {e['icono']}  {e['nombre']:<38} → {g:<7} ({puntos})")
    if res["sonar"].get("estado") != "ok":
        aviso(f"SonarQube: {res['sonar'].get('motivo')}")
    log(f"Dashboard: {destino}")
    log(f"Datos:     {SALIDAS_DIR / 'resultados.json'}")


if __name__ == "__main__":
    main()
