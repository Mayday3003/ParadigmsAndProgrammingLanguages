package soporte360

/** Normaliza un texto para comparar sin importar mayúsculas, espacios ni tildes. */
def normalizar(texto: String): String =
  java.text.Normalizer
    .normalize(texto.trim.toLowerCase, java.text.Normalizer.Form.NFD)
    .replaceAll("\\p{M}", "")
    .replaceAll("\\s+", "")

/** Busca una opción de un enum por número (1, 2, 3) o por nombre. */
def buscarOpcion[A](valores: List[A], nombre: A => String)(texto: String): Option[A] =
  texto.trim.toIntOption match
    case Some(n) => valores.lift(n - 1)
    case None    => valores.find(v => normalizar(nombre(v)) == normalizar(texto))

enum Categoria(val nombre: String):
  case Hardware extends Categoria("Hardware")
  case Software extends Categoria("Software")
  case Redes    extends Categoria("Redes")

object Categoria:
  val todas: List[Categoria] = values.toList
  def desde(texto: String): Option[Categoria] = buscarOpcion(todas, _.nombre)(texto)

enum Prioridad(val nombre: String):
  case Alta  extends Prioridad("Alta")
  case Media extends Prioridad("Media")
  case Baja  extends Prioridad("Baja")

object Prioridad:
  val todas: List[Prioridad] = values.toList
  def desde(texto: String): Option[Prioridad] = buscarOpcion(todas, _.nombre)(texto)

enum Estado(val nombre: String):
  case Pendiente  extends Estado("Pendiente")
  case EnProceso  extends Estado("En proceso")
  case Finalizado extends Estado("Finalizado")

object Estado:
  val todos: List[Estado] = values.toList
  def desde(texto: String): Option[Estado] = buscarOpcion(todos, _.nombre)(texto)

/** Solicitud de soporte técnico (inmutable). */
case class Solicitud(
    id: String,
    cliente: String,
    tecnico: String,
    categoria: Categoria,
    prioridad: Prioridad,
    estado: Estado,
    horas: Double,
    costoHora: Double
):
  /** RF05: valor económico = horas * costo por hora. */
  val valor: Double = horas * costoHora

case class ResumenTecnico(nombre: String, cantidad: Int, horas: Double, finalizadas: Int)

case class ResumenEjecutivo(
    total: Int,
    finalizadas: Int,
    sinFinalizar: Int,
    categoriaMayorDemanda: Option[(Categoria, Int)],
    tecnicoMayorCarga: Option[ResumenTecnico],
    valorTotal: Double,
    promedioHoras: Option[Double],
    criticas: Int,
    clienteMayorValor: Option[(String, Double)]
)
