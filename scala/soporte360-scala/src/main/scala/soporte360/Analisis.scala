package soporte360

/**
 * Lógica de negocio: solo funciones puras sobre colecciones inmutables.
 * Criterios de desempate (condición 8):
 *  - Valores numéricos iguales -> orden alfabético por nombre / identificador.
 *  - Categorías o prioridades iguales -> orden en que se definen (Hardware, Software, Redes).
 */
object Analisis:

  private def clave(texto: String): String = normalizar(texto)

  // RF03
  def sinFinalizar(ls: List[Solicitud]): List[Solicitud] =
    ls.filter(_.estado != Estado.Finalizado)

  def porEstado(ls: List[Solicitud], estado: Estado): List[Solicitud] =
    ls.filter(_.estado == estado)

  // RF04
  def conteoPorCategoria(ls: List[Solicitud]): List[(Categoria, Int)] =
    Categoria.todas.map(c => c -> ls.count(_.categoria == c))

  def categoriaMayorDemanda(ls: List[Solicitud]): Option[(Categoria, Int)] =
    conteoPorCategoria(ls)
      .filter(_._2 > 0)
      .sortBy((c, n) => (-n, c.ordinal))
      .headOption

  // RF05
  def valorTotal(ls: List[Solicitud]): Double = ls.map(_.valor).sum

  def promedio(valores: List[Double]): Option[Double] =
    if valores.isEmpty then None else Some(valores.sum / valores.size)

  def valorPromedio(ls: List[Solicitud]): Option[Double] = promedio(ls.map(_.valor))

  // RF06
  def topCostosas(ls: List[Solicitud], n: Int = 3): List[Solicitud] =
    ls.sortBy(s => (-s.valor, s.id.toLowerCase)).take(n)

  // RF07
  def resumenTecnicos(ls: List[Solicitud]): List[ResumenTecnico] =
    ls.groupBy(s => clave(s.tecnico))
      .values
      .map { grupo =>
        ResumenTecnico(
          nombre = grupo.head.tecnico,
          cantidad = grupo.size,
          horas = grupo.map(_.horas).sum,
          finalizadas = grupo.count(_.estado == Estado.Finalizado)
        )
      }
      .toList
      .sortBy(r => (-r.horas, r.nombre.toLowerCase))

  def tecnicoMayorCarga(ls: List[Solicitud]): Option[ResumenTecnico] =
    resumenTecnicos(ls).headOption

  // RF08
  def clientesFrecuentes(ls: List[Solicitud]): List[(String, Int)] =
    ls.groupBy(s => clave(s.cliente))
      .values
      .map(grupo => grupo.head.cliente -> grupo.size)
      .filter(_._2 > 1)
      .toList
      .sortBy((nombre, n) => (-n, nombre.toLowerCase))

  // RF09
  def valorPorCliente(ls: List[Solicitud]): List[(String, Double)] =
    ls.groupBy(s => clave(s.cliente))
      .values
      .map(grupo => grupo.head.cliente -> valorTotal(grupo))
      .toList
      .sortBy((nombre, v) => (-v, nombre.toLowerCase))

  def topClientes(ls: List[Solicitud], n: Int = 3): List[(String, Double)] =
    valorPorCliente(ls).take(n)

  // RF10
  def criticas(ls: List[Solicitud]): List[Solicitud] =
    ls.filter(s => s.prioridad == Prioridad.Alta && s.estado != Estado.Finalizado)
      .sortBy(s => (-s.horas, s.id.toLowerCase))

  // RF11
  def promedioHoras(ls: List[Solicitud]): Option[Double] = promedio(ls.map(_.horas))

  def sobrePromedioHoras(ls: List[Solicitud]): List[Solicitud] =
    promedioHoras(ls)
      .map(p => ls.filter(_.horas > p).sortBy(s => (-s.horas, s.id.toLowerCase)))
      .getOrElse(Nil)

  // RF12
  def conteoPorPrioridad(ls: List[Solicitud]): List[(Prioridad, Int)] =
    Prioridad.todas.map(p => p -> ls.count(_.prioridad == p))

  def porcentajeAlta(ls: List[Solicitud]): Option[Double] =
    if ls.isEmpty then None
    else Some(ls.count(_.prioridad == Prioridad.Alta) * 100.0 / ls.size)

  // RF14
  def resumenEjecutivo(ls: List[Solicitud]): ResumenEjecutivo =
    ResumenEjecutivo(
      total = ls.size,
      finalizadas = porEstado(ls, Estado.Finalizado).size,
      sinFinalizar = sinFinalizar(ls).size,
      categoriaMayorDemanda = categoriaMayorDemanda(ls),
      tecnicoMayorCarga = tecnicoMayorCarga(ls),
      valorTotal = valorTotal(ls),
      promedioHoras = promedioHoras(ls),
      criticas = criticas(ls).size,
      clienteMayorValor = valorPorCliente(ls).headOption
    )
