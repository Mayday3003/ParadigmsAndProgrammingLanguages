package soporte360

import scala.annotation.tailrec

object Main:

  /** Número de la opción "Mostrar todos": siempre la siguiente al último reporte. */
  private val opcionTodos: Int = Reportes.todos.size + 1

  private def menu: String =
    ("\n=================== MENÚ DE CONSULTAS — SOPORTE360 ===================" ::
      Reportes.todos.zipWithIndex.map { case ((nombre, _), i) => f"  ${i + 1}%2d. $nombre" } :::
      List(f"  $opcionTodos%2d. Mostrar todos los reportes", "   0. Salir")).mkString("\n")

  private def todosLosReportes(ls: List[Solicitud]): String =
    Reportes.todos.map((_, reporte) => reporte(ls)).mkString("\n")

  @tailrec
  private def consultar(ls: List[Solicitud]): Unit =
    println(menu)
    Entrada.pedir("Seleccione una opción: ", Validacion.enteroNoNegativo("Opción")) match
      case 0 => println("\nGracias por usar Soporte360. ¡Hasta pronto!")
      case n if n == opcionTodos =>
        println(todosLosReportes(ls))
        consultar(ls)
      case n if n <= Reportes.todos.size =>
        println(Reportes.todos(n - 1)._2(ls))
        consultar(ls)
      case _ =>
        println("   [ERROR] Opción no válida.")
        consultar(ls)

  def main(args: Array[String]): Unit =
    println("==============================================================")
    println("   SOPORTE360 SAS — Análisis de solicitudes de soporte técnico")
    println("==============================================================")
    val cantidad    = Entrada.pedir("¿Cuántas solicitudes desea registrar? ", Validacion.enteroNoNegativo("Cantidad"))
    val solicitudes = Entrada.registrar(cantidad)
    println(Reportes.general(solicitudes))
    println(Reportes.resumenEjecutivo(solicitudes))
    consultar(solicitudes)
