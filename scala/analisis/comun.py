"""Utilidades compartidas: rutas, descubrimiento de archivos fuente y ejecución de comandos."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ANALISIS_DIR = Path(__file__).resolve().parent
SALIDAS_DIR = ANALISIS_DIR / "salidas"
REPORTE_DIR = ANALISIS_DIR / "reporte"

IGNORAR = {"target", "__pycache__", ".bsp", ".idea", ".scannerwork", "project", "out", ".venv", "venv"}


def log(msg: str) -> None:
    print(f"[análisis] {msg}", flush=True)


def aviso(msg: str) -> None:
    print(f"[análisis] ⚠  {msg}", flush=True)


def raiz_repo(desde: Path) -> Path:
    """Sube directorios hasta encontrar .git (raíz del repositorio)."""
    actual = desde.resolve()
    while actual != actual.parent:
        if (actual / ".git").exists():
            return actual
        actual = actual.parent
    return desde.resolve()


def lenguaje(id_: str, nombre: str, carpeta: Path, ext: str) -> dict:
    carpeta = carpeta.resolve()
    # En proyectos sbt el código vive en src/main/scala; si no existe se usa la carpeta completa.
    fuentes = carpeta / "src" / "main" / "scala" if id_ == "scala" and (carpeta / "src/main/scala").is_dir() else carpeta
    return {"id": id_, "nombre": nombre, "carpeta": carpeta, "fuentes": fuentes, "ext": ext}


def archivos_fuente(lang: dict) -> list[Path]:
    def valido(p: Path) -> bool:
        return p.is_file() and not any(parte in IGNORAR for parte in p.relative_to(lang["fuentes"]).parts)
    return sorted(filter(valido, lang["fuentes"].rglob(f"*{lang['ext']}")))


def huella(archivos: list[Path]) -> str:
    """Hash corto del contenido: cambia en cuanto se modifica cualquier archivo fuente."""
    h = hashlib.sha256()
    for a in archivos:
        h.update(a.name.encode())
        h.update(a.read_bytes())
    return h.hexdigest()[:12]


def ejecutar(cmd: list[str], cwd: Path | None = None, entrada: Path | None = None,
             timeout: float | None = None, env: dict | None = None) -> subprocess.CompletedProcess:
    stdin = open(entrada, "rb") if entrada else subprocess.DEVNULL
    try:
        return subprocess.run(cmd, cwd=cwd, stdin=stdin, capture_output=True, timeout=timeout, env=env)
    finally:
        if entrada:
            stdin.close()


def python_actual() -> str:
    return sys.executable
