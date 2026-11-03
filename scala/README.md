# Práctica de Scala — Soporte360

Aplicación de consola para registrar y analizar solicitudes de soporte técnico de **Soporte360 SAS**,
desarrollada con **programación funcional** en **Scala 3** y, como segundo lenguaje, en **Python 3.10+**.

## Estructura

```
scala/
├── README.md                  ← este archivo (cómo ejecutar + mapa de requisitos)
├── datos/
│   └── datos_prueba.txt       ← entrada de ejemplo (incluye errores para probar RF13)
├── docs/
│   ├── enunciado/             ← PDF de la práctica y guía HTML
│   ├── comparacion.md         ← Scala vs Python: código lado a lado y conclusión
│   ├── sustentacion.md        ← orden para exponer, preguntas y cambios en vivo
│   └── salida_ejemplo_python.txt ← salida real con datos/datos_prueba.txt
├── soporte360-scala/          ← proyecto sbt (abrir en IntelliJ)
│   ├── build.sbt
│   ├── project/build.properties
│   └── src/main/scala/soporte360/
│       ├── Modelo.scala       ← enums Categoria/Prioridad/Estado, case class Solicitud
│       ├── Validacion.scala   ← RF13: validaciones puras con Either
│       ├── Entrada.scala      ← RF01: lectura por teclado con recursión de cola (@tailrec)
│       ├── Analisis.scala     ← RF03–RF12, RF14: lógica pura sobre List
│       ├── Reportes.scala     ← formato de cada reporte (dos decimales, tablas)
│       └── Main.scala         ← punto de entrada y menú de consultas
├── analisis/                  ← análisis comparativo automático (SonarQube + métricas + experimentos)
│   ├── analizar.sh            ← ./analizar.sh genera reporte/dashboard.html
│   └── reporte/dashboard.html ← dashboard visual con el veredicto por escenario
└── soporte360-python/         ← misma solución y mismos módulos que Scala
    ├── modelo.py
    ├── validacion.py
    ├── entrada.py
    ├── analisis.py
    ├── reportes.py
    └── main.py                ← punto de entrada
```

## Cómo ejecutar

### Scala (IntelliJ IDEA)
1. Instalar el plugin **Scala** en IntelliJ.
2. *File → Open* → seleccionar la carpeta `soporte360-scala` → **Open as sbt project**.
3. Esperar a que sbt descargue Scala 3.3.4 y abrir `Main.scala` → ▶ junto a `object Main`.

Por terminal: `cd soporte360-scala && sbt run` (o `sbt run < ../datos/datos_prueba.txt`).

### Python (IntelliJ IDEA / PyCharm)
En IntelliJ instalar el plugin **Python**, abrir `soporte360-python`, configurar un intérprete Python 3.10+
y ejecutar `main.py` (clic derecho → *Run*). No necesita librerías externas.

Por terminal:
```bash
cd soporte360-python
python3 main.py                          # interactivo
python3 main.py < ../datos/datos_prueba.txt   # con datos de prueba
```

### Flujo del programa
1. Pide **N** (cantidad de solicitudes) y luego cada solicitud campo por campo.
   Categoría, prioridad y estado se pueden escribir por nombre (`Hardware`, `en proceso`…) o por número (`1`, `2`, `3`).
2. Muestra la consulta general (RF02) y el resumen ejecutivo (RF14).
3. Abre un menú para consultar cualquier reporte (1–12), todos (13) o salir (0).

## Requisitos funcionales → código (Scala)

| RF | Dónde | Técnica funcional |
|----|-------|-------------------|
| RF01 Registro | `Entrada.registrar` | recursión de cola acumulando en `List` inmutable |
| RF02 Consulta general | `Reportes.general` | `map` + `mkString` |
| RF03 Pendientes / en proceso | `Analisis.porEstado` | `filter` |
| RF04 Categorías | `Analisis.conteoPorCategoria`, `categoriaMayorDemanda` | `map` + `count`, `sortBy`, `headOption` |
| RF05 Económico | `Solicitud.valor`, `Analisis.valorTotal`, `valorPromedio` | `map` + `sum`, `Option` para lista vacía |
| RF06 Top 3 costo | `Analisis.topCostosas` | `sortBy` + `take(3)` |
| RF07 Técnicos | `Analisis.resumenTecnicos` | `groupBy` + `map` |
| RF08 Clientes frecuentes | `Analisis.clientesFrecuentes` | `groupBy` + `filter(_ > 1)` |
| RF09 Top 3 clientes | `Analisis.topClientes` | `groupBy` + suma + `sortBy` |
| RF10 Críticas | `Analisis.criticas` | `filter` con dos condiciones |
| RF11 Tiempos elevados | `Analisis.sobrePromedioHoras` | `Option.map` + `filter` |
| RF12 Prioridades | `Analisis.conteoPorPrioridad`, `porcentajeAlta` | `map` + `count` |
| RF13 Validación | `Validacion.*`, `Entrada.pedir` | `Either[String, A]` + `@tailrec` que repite la pregunta |
| RF14 Resumen ejecutivo | `Analisis.resumenEjecutivo` | composición de las funciones anteriores |

### Condiciones técnicas cumplidas
- **Sin `for`, `while`, `do-while`** y **sin `var`**: todo se repite con recursión o funciones de orden superior.
- **Colecciones vacías**: los promedios devuelven `Option`; cada reporte muestra un mensaje `(!)` o `N/A` si no hay datos.
- **Dos decimales** en valores económicos: `Reportes.dinero` → `$ 1.930.000,00`.
- **Desempates consistentes**: a igual valor se ordena alfabéticamente por nombre/ID; a igual cantidad de
  categorías o prioridades, por el orden de definición (Hardware → Software → Redes).
- **Clientes y técnicos** se agrupan ignorando mayúsculas, espacios y tildes (`Bancolombia` = `bancolombia`).
- Sin bases de datos ni librerías externas (solo la biblioteca estándar).

### Cómo se cumplen las mismas reglas en Python
Python no prohíbe nada de esto, así que se aplicó por disciplina:
- **Sin `for`/`while`**, ni siquiera en comprensiones (`[x for x in ...]`): se usan `map`, `filter`, `sorted`,
  `sum`, `any`, `next`, `itertools.groupby` y recursión (`registrar`, `pedir`, `consultar`).
- **Inmutabilidad**: `@dataclass(frozen=True)` para las solicitudes, `tuple` en lugar de `list`, y cada nombre se
  asigna una sola vez.
- **Errores**: cada validador devuelve `(valor, None)` o `(None, mensaje)`, imitando el `Either` de Scala.

## Comparación: Scala vs Python

Ver [docs/comparacion.md](docs/comparacion.md): código lado a lado, tabla comparativa y conclusión.
**En resumen: Scala es mejor para esta práctica** porque garantiza las reglas funcionales (inmutabilidad,
tipos, `Either`/`Option`, `@tailrec`) en lugar de depender de la disciplina del programador.

### Análisis automático (SonarQube + experimentos)
```bash
cd analisis && ./analizar.sh      # luego abrir analisis/reporte/dashboard.html
```
Analiza el código actual de los dos lenguajes con **SonarQube Cloud (SonarAnalyzer)**, lizard, un verificador
de las reglas de la práctica, benchmarks y experimentos de garantías funcionales, y decide cuál lenguaje es
mejor en 6 escenarios. Si se cambia el código, basta con volver a ejecutarlo. Detalles en
[analisis/README.md](analisis/README.md).

Para preparar la exposición: [docs/sustentacion.md](docs/sustentacion.md).
