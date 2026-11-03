"""Capa 1: SonarQube Cloud (SonarAnalyzer para Scala y Python).

Ejecuta el escaneo con pysonar, espera a que el servidor procese el análisis y descarga
las métricas e issues por archivo, agregándolos por carpeta de cada lenguaje.
"""

from __future__ import annotations

import base64
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

from comun import ejecutar, log, aviso

METRICAS = [
    "ncloc", "lines", "functions", "statements", "classes", "complexity", "cognitive_complexity",
    "code_smells", "bugs", "vulnerabilities", "sqale_index", "duplicated_lines", "comment_lines",
]

SEVERIDAD_A_NOTA = {None: "A", "INFO": "A", "MINOR": "B", "MAJOR": "C", "CRITICAL": "D", "BLOCKER": "E"}
ORDEN_SEVERIDAD = ["INFO", "MINOR", "MAJOR", "CRITICAL", "BLOCKER"]


def leer_propiedades(raiz: Path) -> dict:
    archivo = raiz / "sonar-project.properties"
    if not archivo.exists():
        return {}
    lineas = archivo.read_text(encoding="utf-8").splitlines()
    pares = [l.split("=", 1) for l in lineas if "=" in l and not l.strip().startswith("#")]
    return {k.strip(): v.strip() for k, v in pares}


class ClienteSonar:
    def __init__(self, host: str, token: str):
        self.host = host.rstrip("/")
        self.auth = "Basic " + base64.b64encode(f"{token}:".encode()).decode()

    def get(self, ruta: str, **params) -> dict:
        url = f"{self.host}{ruta}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"Authorization": self.auth})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())

    def paginado(self, ruta: str, clave: str, **params) -> list:
        resultados, pagina = [], 1
        while True:
            datos = self.get(ruta, p=pagina, ps=500, **params)
            resultados += datos.get(clave, [])
            total = datos.get("paging", {}).get("total", datos.get("total", 0))
            if pagina * 500 >= total:
                return resultados
            pagina += 1


def escanear(raiz: Path, token: str, fuentes: list[Path]) -> dict | None:
    relativas = ",".join(str(f.relative_to(raiz)) for f in fuentes)
    log(f"SonarQube: escaneando {relativas} …")
    r = ejecutar(["pysonar", "--token", token, "--sonar-sources", relativas], cwd=raiz, timeout=900)
    salida = r.stdout.decode(errors="replace") + r.stderr.decode(errors="replace")
    if r.returncode != 0:
        aviso("pysonar terminó con error:\n" + "\n".join(salida.splitlines()[-15:]))
        return None
    reporte = raiz / ".scannerwork" / "report-task.txt"
    if not reporte.exists():
        aviso("No se encontró .scannerwork/report-task.txt")
        return None
    pares = [l.split("=", 1) for l in reporte.read_text().splitlines() if "=" in l]
    return {k: v for k, v in pares}


def esperar_procesamiento(cliente: ClienteSonar, task_id: str, limite_s: int = 300) -> bool:
    inicio = time.time()
    while time.time() - inicio < limite_s:
        estado = cliente.get("/api/ce/task", id=task_id)["task"]["status"]
        if estado == "SUCCESS":
            return True
        if estado in ("FAILED", "CANCELED"):
            aviso(f"El análisis en SonarQube terminó en estado {estado}")
            return False
        time.sleep(3)
    aviso("Tiempo de espera agotado procesando el análisis en SonarQube")
    return False


def nota_mantenibilidad(ratio: float) -> str:
    # Escala de Sonar: A ≤ 5 %, B ≤ 10 %, C ≤ 20 %, D ≤ 50 %, E > 50 %
    return next((n for n, lim in (("A", 5), ("B", 10), ("C", 20), ("D", 50)) if ratio <= lim), "E")


def peor_severidad(issues: list[dict]) -> str | None:
    return max((i.get("severity") for i in issues), key=lambda s: ORDEN_SEVERIDAD.index(s) if s in ORDEN_SEVERIDAD else -1, default=None)


def agregar(archivos: list[dict], issues: list[dict], hotspots: list[dict], prefijo: str) -> dict:
    propios = [a for a in archivos if a["path"].startswith(prefijo)]
    suma = {m: sum(float(a["medidas"].get(m, 0)) for a in propios) for m in METRICAS}
    iss = [i for i in issues if i["path"].startswith(prefijo)]
    hot = [h for h in hotspots if h["path"].startswith(prefijo)]
    ncloc = suma["ncloc"] or 1
    ratio = suma["sqale_index"] / (ncloc * 30) * 100  # costo de desarrollo por línea: 30 min (valor por defecto de Sonar)
    return {
        **{m: suma[m] for m in METRICAS},
        "archivos": len(propios),
        "deuda_ratio": round(ratio, 3),
        "nota_mantenibilidad": nota_mantenibilidad(ratio),
        "nota_confiabilidad": SEVERIDAD_A_NOTA[peor_severidad([i for i in iss if i["type"] == "BUG"])],
        "nota_seguridad": SEVERIDAD_A_NOTA[peor_severidad([i for i in iss if i["type"] == "VULNERABILITY"])],
        "hotspots": len(hot),
        "duplicacion_pct": round(suma["duplicated_lines"] / (suma["lines"] or 1) * 100, 2),
        "comentarios_pct": round(suma["comment_lines"] / ((suma["comment_lines"] + suma["ncloc"]) or 1) * 100, 2),
        "complejidad_cognitiva_por_funcion": round(suma["cognitive_complexity"] / (suma["functions"] or 1), 2),
        "por_archivo": [{"archivo": a["path"][len(prefijo):].lstrip("/"), **a["medidas"]} for a in propios],
        "issues": [{k: i.get(k) for k in ("type", "severity", "rule", "message", "line")} | {"archivo": i["path"][len(prefijo):].lstrip("/")} for i in iss],
    }


def analizar(raiz: Path, token: str | None, lenguajes: list[dict]) -> dict:
    props = leer_propiedades(raiz)
    proyecto, host = props.get("sonar.projectKey"), props.get("sonar.host.url", "https://sonarcloud.io")
    if not token:
        aviso("SONAR_TOKEN no definido: se omite SonarQube")
        return {"estado": "omitido", "motivo": "No hay SONAR_TOKEN"}
    if not proyecto:
        aviso("Falta sonar.projectKey en sonar-project.properties: se omite SonarQube")
        return {"estado": "omitido", "motivo": "Falta sonar-project.properties"}

    tarea = escanear(raiz, token, [l["fuentes"] for l in lenguajes])
    cliente = ClienteSonar(host, token)
    if not tarea or not esperar_procesamiento(cliente, tarea["ceTaskId"]):
        return {"estado": "error", "motivo": "El escaneo de SonarQube falló (ver consola)"}

    log("SonarQube: descargando métricas e issues …")
    componentes = cliente.paginado("/api/measures/component_tree", "components",
                                   component=proyecto, qualifiers="FIL", metricKeys=",".join(METRICAS))
    archivos = [{"path": c["path"], "medidas": {m["metric"]: float(m.get("value", 0)) for m in c.get("measures", [])}}
                for c in componentes]
    issues = [i | {"path": i["component"].split(":", 1)[-1]}
              for i in cliente.paginado("/api/issues/search", "issues", componentKeys=proyecto, resolved="false")]
    try:
        hotspots = [h | {"path": h["component"].split(":", 1)[-1]}
                    for h in cliente.paginado("/api/hotspots/search", "hotspots", projectKey=proyecto)]
    except Exception:
        hotspots = []

    return {
        "estado": "ok",
        "url": tarea.get("dashboardUrl", f"{host}/dashboard?id={proyecto}"),
        "lenguajes": {l["id"]: agregar(archivos, issues, hotspots, str(l["fuentes"].relative_to(raiz)))
                      for l in lenguajes},
    }
