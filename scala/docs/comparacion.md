# Comparación: Scala vs Python — Soporte360

Las dos versiones resuelven los mismos RF01–RF14 con las mismas reglas: sin `for`/`while`, sin variables
mutables, solo funciones y colecciones. Además están divididas en los mismos módulos, así que se pueden
comparar archivo por archivo:

| Responsabilidad | Scala (`soporte360-scala/src/main/scala/soporte360/`) | Python (`soporte360-python/`) |
|-----------------|------------------------------------------------------|-------------------------------|
| Modelo de datos | `Modelo.scala` | `modelo.py` |
| Validación (RF13) | `Validacion.scala` | `validacion.py` |
| Entrada por teclado (RF01) | `Entrada.scala` | `entrada.py` |
| Análisis (RF03–RF12, RF14) | `Analisis.scala` | `analisis.py` |
| Formato de reportes | `Reportes.scala` | `reportes.py` |
| Menú y punto de entrada | `Main.scala` | `main.py` |

## 1. El mismo requisito en los dos lenguajes

### RF09 — valor económico por cliente

```scala
def valorPorCliente(ls: List[Solicitud]): List[(String, Double)] =
  ls.groupBy(s => clave(s.cliente))
    .values
    .map(grupo => grupo.head.cliente -> valorTotal(grupo))
    .toList
    .sortBy((nombre, v) => (-v, nombre.toLowerCase))
```

```python
def valor_por_cliente(ls: tuple) -> tuple:
    pares = map(lambda g: (g[0].cliente, valor_total(g)), agrupar(ls, lambda s: s.cliente))
    return tuple(sorted(pares, key=lambda p: (-p[1], p[0].lower())))
```

- En Scala, `groupBy` ya es un método de `List` y las operaciones se encadenan de arriba hacia abajo.
- Python no tiene un `groupBy` equivalente: hubo que escribir `agrupar` con `itertools.groupby`, que
  además exige ordenar antes. Las funciones van anidadas y hay que leerlas de adentro hacia afuera.

### RF13 — pedir un dato hasta que sea válido

```scala
@tailrec
def pedir[A](mensaje: String, validar: String => Either[String, A]): A =
  validar(leerLinea(mensaje)) match
    case Right(valor) => valor
    case Left(error)  => println(...); pedir(mensaje, validar)
```

```python
def pedir(mensaje: str, validar: Callable[[str], tuple]):
    valor, error = validar(leer_linea(mensaje))
    if error is None:
        return valor
    print(f"   [ERROR] {error} Intente nuevamente.")
    return pedir(mensaje, validar)
```

- Scala tiene `Either` incorporado y `@tailrec` **garantiza** que la recursión no desborda la pila.
- Python imita el `Either` con una tupla `(valor, error)`. No optimiza la recursión de cola, así que
  se subió el límite con `sys.setrecursionlimit`.

### RF05 — colecciones vacías

```scala
def promedio(valores: List[Double]): Option[Double] =
  if valores.isEmpty then None else Some(valores.sum / valores.size)
```

```python
def promedio(valores: tuple) -> Optional[float]:
    return sum(valores) / len(valores) if valores else None
```

- Las dos funciones devuelven "sin resultado" cuando no hay datos. En Scala, si alguien usa el
  `Option` sin revisarlo, el compilador lo marca como error. En Python, olvidar revisar el `None`
  solo se descubre cuando el programa falla al ejecutarse.

## 2. Tabla comparativa

| Aspecto | Scala 3 | Python 3 |
|---------|---------|----------|
| Inmutabilidad | Por defecto y verificada por el compilador (`val`, `List`, `case class`) | Solo por convención: `frozen=True` y `tuple`; cualquier nombre se puede reasignar |
| Tipos | Estáticos: los errores de tipo aparecen al compilar | Dinámicos: los errores aparecen al ejecutar (las anotaciones no se verifican) |
| Errores de validación | `Either[String, A]` / `Option` nativos | No existen: se usaron tuplas `(valor, error)` y `None` |
| Recursión | `@tailrec`: el compilador garantiza que no desborda la pila | Sin optimización de cola; límite de ~1000 llamadas (se subió con `sys.setrecursionlimit`) |
| Lambdas | Multilínea, con pattern matching (`case ((c, v), i) =>`) | Solo una expresión; tuplas con índices `p[0]`, `p[1]` |
| Colecciones | `groupBy`, `sortBy`, `count`, `sum`, `take` como métodos encadenables | Funciones sueltas anidadas (`tuple(sorted(filter(...)))`); `groupby` exige ordenar antes |
| Ordenar con desempate | `sortBy(s => (-s.valor, s.id))` | `sorted(ls, key=lambda s: (-s.valor, s.id))` — igual de claro |
| Estilo idiomático | Lo funcional es lo natural del lenguaje | Lo idiomático son ciclos y comprensiones; prohibirlos hace el código menos "pythónico" |
| Ejecución | Requiere compilar (sbt), arranque más lento, ejecución más rápida (JVM) | Sin compilar, arranque inmediato, ejecución más lenta |
| Tamaño del código | ~495 líneas en 6 archivos | ~490 líneas en 6 archivos |
| Curva de aprendizaje | Más difícil | Muy fácil de leer y escribir |

## 3. Evidencia medida (análisis automático)

Resultados de `analisis/analizar.sh` (ver `analisis/reporte/dashboard.html`; los números se recalculan en
cada ejecución):

| Evidencia | Scala | Python |
|---|---|---|
| Calidad en SonarQube (bugs / vulnerabilidades / code smells) | 0 / 0 / 0 · nota A | 0 / 0 / 0 · nota A |
| Complejidad cognitiva total (SonarQube) | **24** | 39 |
| Violaciones a las reglas de la práctica | 0 | 0 |
| Errores inyectados detectados **antes de ejecutar** | **5 de 5** | 0 de 5 |
| Recursión bajo estrés (máximo de solicitudes procesadas) | **20.000** (y más, gracias a `@tailrec`) | 5.000 (con 10.000: `RecursionError`) |
| Tiempo con 10 solicitudes (incluye arranque) | 0,5 s (arranque de la JVM) | **0,07 s** |
| Compilación antes de ejecutar | 14 s | **0,1 s** |

Veredicto por escenario: Scala gana **funcional estricto**, **sistema empresarial** y **gran volumen**;
Python gana **prototipo rápido**, **equipo junior** y **script ocasional**.

Los dos programas cumplen las reglas, pero el experimento de errores inyectados muestra la diferencia de fondo:
en Scala el **compilador impide** romper el paradigma (reasignar un `val`, mutar una `case class`, usar un
tipo equivocado, un campo inexistente o un `match` incompleto); en Python esos errores solo aparecen al
ejecutar o nunca.

## 4. Conclusión: para esta práctica Scala es mejor

El problema consiste en transformar y resumir una colección (filtrar, agrupar, contar, ordenar, sumar)
respetando reglas funcionales estrictas, y **Scala garantiza esas reglas en lugar de solo permitirlas**:

1. **Inmutabilidad por defecto:** `List` y `case class` no se pueden modificar. En Python nada impide
   reasignar una variable o usar un `for`; todo depende de la disciplina del programador.
2. **Errores detectados al compilar:** un tipo equivocado o un `Option` sin revisar no llega a ejecutarse.
3. **`Either` y `Option` incorporados**, pensados justo para validar datos y manejar colecciones vacías.
4. **`@tailrec`** permite reemplazar los ciclos con recursión sin riesgo de desbordar la pila.

Python gana en simplicidad, en lo fácil que es de leer y en rapidez para prototipar. Pero en esta
práctica hubo que ir en contra de su estilo natural (sin ciclos ni comprensiones) e imitar
herramientas que Scala ya trae. La práctica evalúa programación funcional segura y expresiva, y en eso
Scala es superior.
