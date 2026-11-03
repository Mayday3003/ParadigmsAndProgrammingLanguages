# Análisis comparativo Scala vs Python

Flujo automático que toma **el código fuente actual** de `soporte360-scala` y `soporte360-python` y genera
un dashboard visual con el veredicto de cuál lenguaje es mejor según el escenario.

## Ejecutar

```bash
cd scala/analisis
./analizar.sh
```

Abre `reporte/dashboard.html` en el navegador. **Si cambias el código, vuelve a ejecutar**: todo se recalcula
y la sección *Cambios* muestra qué indicadores se movieron respecto a la ejecución anterior.

Opciones útiles:

| Comando | Para qué |
|---|---|
| `./analizar.sh --tamanos 10,100` | Benchmark rápido (≈1 min) |
| `./analizar.sh --sin-sonar` | Sin internet / sin token |
| `./analizar.sh --sin-rendimiento` | Solo análisis estático |
| `./analizar.sh --corridas 10` | Mediciones más estables |
| `./analizar.sh --sin-garantias` | Sin experimentos de errores inyectados ni recursión |
| `./analizar.sh --recursion 5000,10000,20000,40000` | Prueba de estrés de recursión más agresiva |
| `./analizar.sh --scala RUTA --python RUTA` | Analizar otras carpetas |

Requisitos: entorno conda `paradigmas` (Java 21, sbt, pysonar, lizard, hyperfine) y la variable
`SONAR_TOKEN` (en fish: `set -Ux SONAR_TOKEN ...`). La organización y el proyecto de SonarQube Cloud
se leen de `sonar-project.properties` en la raíz del repositorio.

## Qué mide

| Capa | Herramienta | Métricas |
|---|---|---|
| 1. Calidad | **SonarQube Cloud + SonarAnalyzer** (Scala y Python) | bugs, vulnerabilidades, hotspots, code smells, deuda técnica, complejidad ciclomática y cognitiva, duplicación, calificaciones A–E |
| 2. Complejidad | **lizard** (mismo criterio para ambos) | complejidad por función, líneas por función, funciones más complejas |
| 3. Reglas de la práctica | verificador propio (`ast` en Python, lexer en Scala) | for, while, do-while, var, reasignación, mutación, global, return, null + recursos funcionales usados |
| 4. Rendimiento | **hyperfine** + `/usr/bin/time` | tiempo y memoria con las cinco solicitudes de `datos/benchmark.txt`, tiempo de compilación |
| 5. Equivalencia | comparación de salidas | ambos programas deben producir exactamente el mismo resultado |
| 6. **Garantías funcionales** | experimentos sobre copias del código | ¿el lenguaje **impide** romper el paradigma? 5 errores inyectados (reasignar, mutar un registro, tipo incorrecto, campo inexistente, `match` incompleto) y recursión bajo estrés (5.000 / 10.000 / 20.000 solicitudes) |

Los experimentos de garantías detectan solos el registro de datos (`case class` / `dataclass`), sus campos
numéricos, los `enum` y dónde se construye el registro; nunca modifican el código original (trabajan en
`salidas/garantias/`, que se borra al terminar).

Luego `escenarios.json` pondera los criterios en 6 escenarios (empresarial, prototipo, gran volumen,
equipo junior, funcional estricto, script). **Puedes editar los pesos o agregar escenarios** sin tocar el código.

## Archivos

```

El archivo usado por el benchmark se selecciona en la variable `BENCHMARK_INPUT` de
`rendimiento.py`. Las capturas manuales se guardan por separado en `datos/sesiones/`,
por lo que pueden reutilizarse sin alterar el conjunto benchmark.
analisis/
├── analizar.sh        ← punto de entrada (activa el entorno y el token)
├── pipeline.py        ← orquesta las capas, guarda resultados e historial
├── sonar.py           ← escaneo con pysonar + API de SonarQube
├── estatico.py        ← lizard + verificador de reglas funcionales
├── rendimiento.py     ← compilación, benchmarks y equivalencia
├── garantias.py       ← errores inyectados + recursión bajo estrés
├── puntaje.py         ← normalización 0–10 y motor de escenarios
├── dashboard.py       ← genera el HTML
├── escenarios.json    ← criterios y pesos (editable)
├── reporte/dashboard.html
└── salidas/           ← resultados.json, historial/, entradas y salidas generadas (no se versiona)
```
