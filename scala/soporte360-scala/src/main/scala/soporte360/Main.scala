package soporte360

import scala.annotation.tailrec

object Main:

  private def menu: String =
    ("\n=================== MENÚ DE CONSULTAS — SOPORTE360 ===================" ::
      Reportes.todos.zipWithIndex.map { case ((nombre, _), i) => f"  ${i + 1}%2d. $nombre" } :::
      List("  13. Mostrar todos los reportes", "   0. Salir")).mkString("\n")

  private def todosLosReportes(ls: List[Solicitud]): String =
    Reportes.todos.map((_, reporte) => reporte(ls)).mkString("\n")

  @tailrec
  private def consultar(ls: List[Solicitud]): Unit =
    println(menu)
    Entrada.pedir("Seleccione una opción: ", Validacion.enteroNoNegativo("Opción")) match
      case 0 => println("\nGracias por usar Soporte360. ¡Hasta pronto!")
      case 13 =>
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
