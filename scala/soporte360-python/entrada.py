"""RF01: lectura por teclado. La repetición se hace con recursión, sin for/while."""

import sys
from typing import Callable

from modelo import Categoria, Estado, Prioridad, Solicitud
from validacion import id_unico, numero_no_negativo, opcion, opciones_texto, texto_obligatorio


def leer_linea(mensaje: str) -> str:
    try:
        return input(mensaje)
    except EOFError:
        print("\n\nEntrada finalizada. Cerrando el programa.")
        sys.exit(0)


def pedir(mensaje: str, validar: Callable[[str], tuple]):
    """Pide un dato hasta que sea válido (recursión en lugar de while)."""
    valor, error = validar(leer_linea(mensaje))
    if error is None:
        return valor
    print(f"   [ERROR] {error} Intente nuevamente.")
    return pedir(mensaje, validar)


def pedir_solicitud(numero: int, total: int, existentes: tuple) -> Solicitud:
    print(f"\n--- Solicitud {numero} de {total} ---")
    return Solicitud(
        id=pedir("  Identificador único: ", id_unico(existentes)),
        cliente=pedir("  Nombre del cliente: ", texto_obligatorio("Cliente")),
        tecnico=pedir("  Técnico responsable: ", texto_obligatorio("Técnico")),
        categoria=pedir(f"  Categoría [{opciones_texto(Categoria)}]: ", opcion("Categoría", Categoria)),
        prioridad=pedir(f"  Prioridad [{opciones_texto(Prioridad)}]: ", opcion("Prioridad", Prioridad)),
        estado=pedir(f"  Estado [{opciones_texto(Estado)}]: ", opcion("Estado", Estado)),
        horas=pedir("  Horas dedicadas: ", numero_no_negativo("Horas")),
        costo_hora=pedir("  Costo por hora: ", numero_no_negativo("Costo por hora")),
    )


def registrar(actual: int, total: int, acumuladas: tuple = ()) -> tuple:
    """Registra N solicitudes de forma recursiva, devolviendo una tupla inmutable."""
    if actual > total:
        return acumuladas
    nueva = pedir_solicitud(actual, total, acumuladas)
    print(f"  ✔ Solicitud '{nueva.id}' registrada.")
    return registrar(actual + 1, total, acumuladas + (nueva,))
