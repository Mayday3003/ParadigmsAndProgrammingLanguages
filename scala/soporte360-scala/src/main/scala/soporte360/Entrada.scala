package soporte360

import scala.annotation.tailrec
import scala.io.StdIn

/** Entrada por teclado. La repetición se hace con recursión de cola, sin for/while ni var. */
object Entrada:

  /** Lee una línea; si la entrada se cierra (EOF) termina el programa de forma controlada. */
  private def leerLinea(mensaje: String): String =
    print(mensaje)
    Option(StdIn.readLine()).getOrElse {
      println("\n\nEntrada finalizada. Cerrando el programa.")
      sys.exit(0)
    }

  /** RF13: pide un dato hasta que sea válido, informando cada error. */
  @tailrec
  def pedir[A](mensaje: String, validar: String => Either[String, A]): A =
    validar(leerLinea(mensaje)) match
      case Right(valor) => valor
      case Left(error) =>
        println(s"   [ERROR] $error Intente nuevamente.")
        pedir(mensaje, validar)

  private def menuOpciones[A](valores: List[A], nombre: A => String): String =
    valores.zipWithIndex.map((v, i) => s"${i + 1}=${nombre(v)}").mkString(" | ")

  def pedirSolicitud(numero: Int, total: Int, existentes: List[Solicitud]): Solicitud =
    println(s"\n--- Solicitud $numero de $total ---")
    Solicitud(
      id        = pedir("  Identificador único: ", Validacion.idUnico(existentes)),
      cliente   = pedir("  Nombre del cliente: ", Validacion.textoObligatorio("Cliente")),
      tecnico   = pedir("  Técnico responsable: ", Validacion.textoObligatorio("Técnico")),
      categoria = pedir(s"  Categoría [${menuOpciones(Categoria.todas, _.nombre)}]: ", Validacion.categoria),
      prioridad = pedir(s"  Prioridad [${menuOpciones(Prioridad.todas, _.nombre)}]: ", Validacion.prioridad),
      estado    = pedir(s"  Estado [${menuOpciones(Estado.todos, _.nombre)}]: ", Validacion.estado),
      horas     = pedir("  Horas dedicadas: ", Validacion.numeroNoNegativo("Horas")),
      costoHora = pedir("  Costo por hora: ", Validacion.numeroNoNegativo("Costo por hora"))
    )

  /** RF01: registra N solicitudes acumulándolas en una lista inmutable. */
  def registrar(total: Int): List[Solicitud] =
    @tailrec
    def loop(actual: Int, acumuladas: List[Solicitud]): List[Solicitud] =
      if actual > total then acumuladas.reverse
      else
        val nueva = pedirSolicitud(actual, total, acumuladas)
        println(s"  ✔ Solicitud '${nueva.id}' registrada.")
        loop(actual + 1, nueva :: acumuladas)
    loop(1, Nil)
