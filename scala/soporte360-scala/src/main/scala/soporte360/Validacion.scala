package soporte360

/** RF13: funciones puras de validación. Devuelven Right(valor) o Left(mensaje de error). */
object Validacion:

  def textoObligatorio(campo: String)(texto: String): Either[String, String] =
    if texto.trim.isEmpty then Left(s"El campo '$campo' no puede estar vacío.")
    else Right(texto.trim)

  def idUnico(existentes: List[Solicitud])(texto: String): Either[String, String] =
    textoObligatorio("Identificador")(texto).flatMap { id =>
      if existentes.exists(_.id.equalsIgnoreCase(id)) then
        Left(s"El identificador '$id' ya está registrado.")
      else Right(id)
    }

  def numeroNoNegativo(campo: String)(texto: String): Either[String, Double] =
    texto.trim.replace(',', '.').toDoubleOption match
      case None                    => Left(s"'$texto' no es un número válido para '$campo'.")
      case Some(n) if n.isNaN || n.isInfinite => Left(s"'$texto' no es un número válido para '$campo'.")
      case Some(n) if n < 0        => Left(s"'$campo' no puede ser negativo.")
      case Some(n)                 => Right(n)

  def enteroNoNegativo(campo: String)(texto: String): Either[String, Int] =
    texto.trim.toIntOption match
      case Some(n) if n >= 0 => Right(n)
      case _                 => Left(s"'$campo' debe ser un número entero mayor o igual a 0.")

  def opcion[A](campo: String, valores: List[A], nombre: A => String, desde: String => Option[A])(
      texto: String
  ): Either[String, A] =
    desde(texto).toRight(
      s"'$texto' no es válido para '$campo'. Opciones: " +
        valores.zipWithIndex.map((v, i) => s"${i + 1}=${nombre(v)}").mkString(" | ")
    )

  val categoria: String => Either[String, Categoria] =
    opcion("Categoría", Categoria.todas, _.nombre, Categoria.desde)

  val prioridad: String => Either[String, Prioridad] =
    opcion("Prioridad", Prioridad.todas, _.nombre, Prioridad.desde)

  val estado: String => Either[String, Estado] =
    opcion("Estado", Estado.todos, _.nombre, Estado.desde)
