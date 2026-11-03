# Guía para la sustentación — Soporte360

Machete para responder preguntas y hacer cambios en vivo. Cada cambio indica qué tocar en Scala y en
Python (los módulos tienen el mismo nombre en los dos lenguajes).

## Orden sugerido para exponer

1. **Modelo** (`Modelo.scala` / `modelo.py`): enums con los valores permitidos y `Solicitud` inmutable;
   `valor = horas * costoHora` (RF05).
2. **Validación** (`Validacion` / `validacion`): cada validador devuelve `Either` (Scala) o una tupla
   `(valor, error)` (Python) — RF13.
3. **Entrada** (`Entrada` / `entrada`): `pedir` repite la pregunta con recursión; `registrar` acumula
   N solicitudes en una lista o tupla inmutable — RF01.
4. **Análisis** (`Analisis` / `analisis`): una función pura por requisito (`filter`, `groupBy`, `sortBy`,
   `count`, `sum`).
5. **Reportes** (`Reportes` / `reportes`): solo dan formato al resultado; `todos` / `REPORTES` alimenta el menú.
6. **Main** (`Main` / `main`): flujo del programa y menú recursivo.
7. Demo con `datos/datos_prueba.txt` (incluye errores a propósito) y la comparación de `docs/comparacion.md`.
8. **Dashboard del análisis** (`analisis/reporte/dashboard.html`): veredicto por escenario, SonarQube y la
   sección **Garantías del paradigma funcional** (errores inyectados: Scala 5/5 vs Python 0/5; recursión).
   Si piden un cambio en vivo, hacerlo y correr `cd analisis && ./analizar.sh --tamanos 10,100` (más rápido):
   la sección *Cambios* muestra qué se movió.

## Preguntas probables

| Pregunta | Respuesta corta |
|----------|-----------------|
| ¿Cómo repiten sin `for`/`while`? | Con recursión de cola (`@tailrec` en Scala) y funciones de orden superior (`map`, `filter`…). |
| ¿Dónde hay `var`? | En ninguna parte. Cada llamada recursiva recibe una lista nueva (`nueva :: acumuladas` y `reverse` al final en Scala; `acumuladas + (nueva,)` en Python). |
| ¿Qué pasa si N = 0? | Los reportes muestran `(!) No hay…` y el resumen muestra `N/A`. Los promedios devuelven `Option`/`None`. |
| ¿Cómo desempatan? | A igual valor, orden alfabético por nombre o ID. A igual conteo de categoría o prioridad, el orden en que se definieron (Hardware → Software → Redes; Alta → Media → Baja). |
| ¿"Bancolombia" y "bancolombia" son el mismo cliente? | Sí: se agrupan con `normalizar`, que ignora mayúsculas, espacios y tildes. |
| ¿Qué es SonarQube / SonarAnalyzer? | SonarQube es la plataforma de calidad de código; los SonarAnalyzer son sus analizadores por lenguaje (Scala y Python). Lo usamos en SonarQube Cloud con `pysonar`, y `analizar.sh` descarga las métricas por su API. |
| ¿Por qué Scala es mejor si Python gana 3 escenarios? | No hay un mejor absoluto: Python gana en arranque, compilación y facilidad. Pero la práctica es de **programación funcional**, y ahí Scala **garantiza** las reglas: el compilador atrapó 5 de 5 errores inyectados y `@tailrec` aguanta 20.000+ solicitudes. |
| ¿Por qué Python falla con 10.000 solicitudes? | `registrar` es recursiva y Python no optimiza la recursión de cola: cada solicitud agrega un marco a la pila hasta pasar el límite (`RecursionError`). En Scala `@tailrec` la convierte en un ciclo interno. Es una limitación del lenguaje, no un error de la lógica. |
| ¿El análisis está arreglado a favor de Scala? | No: todo sale de medir el código actual (SonarQube, lizard, tiempos y experimentos). Por eso Python gana los escenarios de prototipo, junior y script. Los únicos valores no medidos (tipos, aprendizaje, ecosistema) están marcados con `*`. |
| ¿Por qué dos decimales con coma? | Formato colombiano en `Reportes.dinero` / `reportes.dinero`: `$ 1.930.000,00`. |

## Cambios en vivo típicos

### Agregar una categoría (por ejemplo "Seguridad")
- **Scala:** en `Modelo.scala`, agregar `case Seguridad extends Categoria("Seguridad")`. Nada más: la
  validación, el menú de opciones y RF04 usan `Categoria.todas`.
- **Python:** en `modelo.py`, agregar `SEGURIDAD = "Seguridad"` a `Categoria`. Lo demás usa el enum completo.
- Lo mismo aplica para un nuevo **estado** o una nueva **prioridad**.

### Agregar un campo a la solicitud (por ejemplo "fecha" o "ciudad")
1. Agregarlo a `Solicitud` (en `Modelo` / `modelo`).
2. Pedirlo en `pedirSolicitud` / `pedir_solicitud` (en `Entrada` / `entrada`) con `textoObligatorio("Ciudad")`.
3. Mostrarlo en `fila` / `tabla` (en `Reportes` / `reportes`) si debe aparecer en la consulta general.
4. Agregar el valor en cada solicitud de `datos/datos_prueba.txt`.

### Agregar un reporte nuevo (por ejemplo "solicitudes por técnico X")
1. Escribir la función pura en `Analisis` / `analisis`:
   - Scala: `def porTecnico(ls: List[Solicitud], t: String) = ls.filter(s => normalizar(s.tecnico) == normalizar(t))`
   - Python: `def por_tecnico(ls, t): return tuple(filter(lambda s: normalizar(s.tecnico) == normalizar(t), ls))`
2. Escribir su formato en `Reportes` / `reportes`, reutilizando `titulo`, `siVacio`/`si_vacio` y `tabla`.
3. Agregar el par `"Nombre (RFxx)" -> funcion` a `Reportes.todos` (Scala) o a `REPORTES` (Python).
4. Listo: el menú se numera solo y la opción "Mostrar todos" se corre automáticamente al final
   (`opcionTodos = Reportes.todos.size + 1` / `OPCION_TODOS = len(REPORTES) + 1`).

### Cambiar el "top 3" por "top N"
- `topCostosas(ls, n)` y `topClientes(ls, n)` ya reciben `n` con valor por defecto 3. Basta con llamarlas
  con otro número en `Reportes`. En Python: `top_costosas(ls, n)` y `valor_por_cliente(ls)[:n]`.

### Cambiar el umbral de RF11 (por ejemplo "20 % sobre el promedio")
- En `sobrePromedioHoras` / `sobre_promedio_horas`, cambiar `_.horas > p` por `_.horas > p * 1.2`.

### Agregar una validación (por ejemplo "horas máximo 24")
- Crear un validador nuevo en `Validacion` / `validacion` siguiendo el patrón de `numeroNoNegativo`
  (devolver `Left`/`(None, mensaje)` si falla) y usarlo en `pedirSolicitud` / `pedir_solicitud`.
