package soporte360

import java.util.Locale

/** Construye los textos de cada reporte. Son funciones puras: reciben datos y devuelven String. */
object Reportes:

  private val locale = Locale.forLanguageTag("es-CO")

  /** Condición 7: valores económicos con dos decimales. */
  def dinero(v: Double): String = "$ " + String.format(locale, "%,.2f", Double.box(v))
  def num(v: Double): String    = String.format(locale, "%,.2f", Double.box(v))

  private def titulo(texto: String): String =
    val linea = "=" * 78
    s"\n$linea\n  $texto\n$linea"

  private def siVacio(ls: List[?], mensaje: String)(contenido: => String): String =
    if ls.isEmpty then s"  (!) $mensaje" else contenido

  private def recortar(texto: String, ancho: Int): String =
    if texto.length <= ancho then texto else texto.take(ancho - 1) + "…"

  private val encabezado =
    f"  ${"ID"}%-6s ${"Cliente"}%-16s ${"Técnico"}%-14s ${"Categoría"}%-9s ${"Prior."}%-6s ${"Estado"}%-11s ${"Horas"}%7s ${"Valor"}%16s"

  def fila(s: Solicitud): String =
    f"  ${recortar(s.id, 6)}%-6s ${recortar(s.cliente, 16)}%-16s ${recortar(s.tecnico, 14)}%-14s " +
      f"${s.categoria.nombre}%-9s ${s.prioridad.nombre}%-6s ${s.estado.nombre}%-11s ${num(s.horas)}%7s ${dinero(s.valor)}%16s"

  def tabla(ls: List[Solicitud]): String =
    (encabezado :: ("  " + "-" * 76) :: ls.map(fila)).mkString("\n")

  private def porcentaje(parte: Int, total: Int): String =
    if total == 0 then "0,00 %" else num(parte * 100.0 / total) + " %"

  // RF02
  def general(ls: List[Solicitud]): String =
    titulo("RF02 · CONSULTA GENERAL DE SOLICITUDES") + "\n" +
      siVacio(ls, "No hay solicitudes registradas.") {
        tabla(ls) + s"\n\n  Total registradas: ${ls.size}"
      }

  // RF03
  def pendientes(ls: List[Solicitud]): String =
    val pend = Analisis.porEstado(ls, Estado.Pendiente)
    val proc = Analisis.porEstado(ls, Estado.EnProceso)
    titulo("RF03 · SOLICITUDES SIN FINALIZAR") + "\n" +
      siVacio(pend ++ proc, "No hay solicitudes sin finalizar.") {
        s"  >> Pendientes (${pend.size})\n" +
          siVacio(pend, "No hay solicitudes pendientes.")(tabla(pend)) +
          s"\n\n  >> En proceso (${proc.size})\n" +
          siVacio(proc, "No hay solicitudes en proceso.")(tabla(proc)) +
          s"\n\n  Total sin finalizar: ${pend.size + proc.size}"
      }

  // RF04
  def categorias(ls: List[Solicitud]): String =
    titulo("RF04 · DISTRIBUCIÓN POR CATEGORÍAS") + "\n" +
      siVacio(ls, "No hay solicitudes para analizar.") {
        Analisis.conteoPorCategoria(ls)
          .map((c, n) => f"  ${c.nombre}%-10s: $n%3d  (${porcentaje(n, ls.size)})")
          .mkString("\n") +
          Analisis.categoriaMayorDemanda(ls)
            .map((c, n) => s"\n\n  Categoría con mayor demanda: ${c.nombre} ($n solicitudes)")
            .getOrElse("")
      }

  // RF05
  def economico(ls: List[Solicitud]): String =
    titulo("RF05 · ANÁLISIS ECONÓMICO") + "\n" +
      siVacio(ls, "No hay solicitudes para analizar.") {
        ls.map(s => f"  ${s.id}%-6s ${num(s.horas)}%7s h x ${dinero(s.costoHora)}%14s = ${dinero(s.valor)}%16s")
          .mkString("\n") +
          s"\n\n  Valor total de los servicios : ${dinero(Analisis.valorTotal(ls))}" +
          s"\n  Valor promedio por solicitud : ${Analisis.valorPromedio(ls).map(dinero).getOrElse("N/A")}"
      }

  // RF06
  def topCostosas(ls: List[Solicitud]): String =
    titulo("RF06 · TOP 3 SOLICITUDES DE MAYOR COSTO") + "\n" +
      siVacio(ls, "No hay solicitudes para analizar.") {
        Analisis.topCostosas(ls).zipWithIndex
          .map((s, i) => f"  ${i + 1}. ${s.id}%-6s ${s.cliente}%-18s ${s.categoria.nombre}%-9s ${dinero(s.valor)}%16s")
          .mkString("\n")
      }

  // RF07
  def tecnicos(ls: List[Solicitud]): String =
    val resumen = Analisis.resumenTecnicos(ls)
    titulo("RF07 · DESEMPEÑO DE LOS TÉCNICOS") + "\n" +
      siVacio(resumen, "No hay técnicos con solicitudes asignadas.") {
        f"  ${"Técnico"}%-20s ${"Solicitudes"}%11s ${"Horas"}%10s ${"Finalizadas"}%11s\n" +
          resumen
            .map(r => f"  ${recortar(r.nombre, 20)}%-20s ${r.cantidad}%11d ${num(r.horas)}%10s ${r.finalizadas}%11d")
            .mkString("\n") +
          Analisis.tecnicoMayorCarga(ls)
            .map(r => s"\n\n  Técnico con mayor carga: ${r.nombre} (${num(r.horas)} horas)")
            .getOrElse("")
      }

  // RF08
  def clientesFrecuentes(ls: List[Solicitud]): String =
    val frecuentes = Analisis.clientesFrecuentes(ls)
    titulo("RF08 · CLIENTES FRECUENTES (más de una solicitud)") + "\n" +
      siVacio(frecuentes, "Ningún cliente ha solicitado soporte más de una vez.") {
        frecuentes.map((c, n) => f"  $c%-25s $n%3d solicitudes").mkString("\n")
      }

  // RF09
  def topClientes(ls: List[Solicitud]): String =
    titulo("RF09 · TOP 3 CLIENTES POR VALOR ECONÓMICO") + "\n" +
      siVacio(ls, "No hay solicitudes para analizar.") {
        Analisis.topClientes(ls).zipWithIndex
          .map { case ((c, v), i) => f"  ${i + 1}. $c%-25s ${dinero(v)}%18s" }
          .mkString("\n")
      }

  // RF10
  def criticas(ls: List[Solicitud]): String =
    val crit = Analisis.criticas(ls)
    titulo("RF10 · SOLICITUDES CRÍTICAS (prioridad Alta sin finalizar)") + "\n" +
      siVacio(crit, "No hay solicitudes críticas.") {
        f"  ${"ID"}%-6s ${"Cliente"}%-18s ${"Técnico"}%-16s ${"Categoría"}%-9s ${"Estado"}%-11s ${"Horas"}%7s\n" +
          crit
            .map(s => f"  ${s.id}%-6s ${recortar(s.cliente, 18)}%-18s ${recortar(s.tecnico, 16)}%-16s ${s.categoria.nombre}%-9s ${s.estado.nombre}%-11s ${num(s.horas)}%7s")
            .mkString("\n") +
          s"\n\n  Total críticas: ${crit.size}"
      }

  // RF11
  def tiemposElevados(ls: List[Solicitud]): String =
    val altos = Analisis.sobrePromedioHoras(ls)
    titulo("RF11 · SERVICIOS CON TIEMPOS ELEVADOS") + "\n" +
      siVacio(ls, "No hay solicitudes para analizar.") {
        s"  Tiempo promedio de atención: ${Analisis.promedioHoras(ls).map(num).getOrElse("N/A")} horas\n\n" +
          siVacio(altos, "Ninguna solicitud supera el promedio de horas.")(tabla(altos))
      }

  // RF12
  def prioridades(ls: List[Solicitud]): String =
    titulo("RF12 · CLASIFICACIÓN POR PRIORIDAD") + "\n" +
      siVacio(ls, "No hay solicitudes para analizar.") {
        Analisis.conteoPorPrioridad(ls)
          .map((p, n) => f"  ${p.nombre}%-6s: $n%3d  (${porcentaje(n, ls.size)})")
          .mkString("\n") +
          s"\n\n  Porcentaje de prioridad Alta: ${Analisis.porcentajeAlta(ls).map(p => num(p) + " %").getOrElse("N/A")}"
      }

  // RF14
  def resumenEjecutivo(ls: List[Solicitud]): String =
    val r = Analisis.resumenEjecutivo(ls)
    titulo("RF14 · RESUMEN EJECUTIVO") + "\n" +
      List(
        "Total de solicitudes registradas" -> r.total.toString,
        "Solicitudes finalizadas"          -> r.finalizadas.toString,
        "Solicitudes sin finalizar"        -> r.sinFinalizar.toString,
        "Categoría con mayor demanda"      -> r.categoriaMayorDemanda.map((c, n) => s"${c.nombre} ($n)").getOrElse("N/A"),
        "Técnico con más horas"            -> r.tecnicoMayorCarga.map(t => s"${t.nombre} (${num(t.horas)} h)").getOrElse("N/A"),
        "Valor económico total"            -> dinero(r.valorTotal),
        "Tiempo promedio de atención"      -> r.promedioHoras.map(h => s"${num(h)} h").getOrElse("N/A"),
        "Solicitudes críticas"             -> r.criticas.toString,
        "Cliente de mayor valor"           -> r.clienteMayorValor.map((c, v) => s"$c (${dinero(v)})").getOrElse("N/A")
      ).map((k, v) => f"  $k%-34s: $v").mkString("\n")

  /** Todos los reportes en orden, asociados al número de opción del menú. */
  val todos: List[(String, List[Solicitud] => String)] = List(
    "Consulta general (RF02)"           -> general,
    "Solicitudes sin finalizar (RF03)"  -> pendientes,
    "Distribución por categoría (RF04)" -> categorias,
    "Análisis económico (RF05)"         -> economico,
    "Top 3 más costosas (RF06)"         -> topCostosas,
    "Desempeño de técnicos (RF07)"      -> tecnicos,
    "Clientes frecuentes (RF08)"        -> clientesFrecuentes,
    "Top 3 clientes por valor (RF09)"   -> topClientes,
    "Solicitudes críticas (RF10)"       -> criticas,
    "Tiempos elevados (RF11)"           -> tiemposElevados,
    "Clasificación por prioridad (RF12)"-> prioridades,
    "Resumen ejecutivo (RF14)"          -> resumenEjecutivo
  )
