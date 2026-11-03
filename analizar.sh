#!/usr/bin/env bash
# Flujo completo de análisis Scala vs Python.
# Uso:  ./analizar.sh                      (analiza ../soporte360-scala y ../soporte360-python)
#       ./analizar.sh --sin-sonar          (sin SonarQube)
#       ./analizar.sh --tamanos 10,100     (benchmark más corto)
#       ./analizar.sh --help
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENTORNO="${CONDA_ENV:-paradigmas}"

# Activa el entorno conda con las herramientas (pysonar, lizard, sbt, java, hyperfine)
for base in "${CONDA_PREFIX_1:-}" "$HOME/miniconda3" "$HOME/anaconda3" "$HOME/miniforge3"; do
  if [ -n "$base" ] && [ -f "$base/etc/profile.d/conda.sh" ]; then
    # shellcheck disable=SC1091
    source "$base/etc/profile.d/conda.sh" && conda activate "$ENTORNO" && break
  fi
done

# El token puede estar definido en fish (set -Ux SONAR_TOKEN ...) aunque se ejecute desde bash
if [ -z "${SONAR_TOKEN:-}" ] && command -v fish >/dev/null 2>&1; then
  SONAR_TOKEN="$(fish -c 'printf %s "$SONAR_TOKEN"' 2>/dev/null || true)"
  export SONAR_TOKEN
fi

cd "$DIR"
python pipeline.py "$@"
