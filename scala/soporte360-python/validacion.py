"""RF13: validaciones puras.

Cada validador devuelve (valor, None) si es correcto o (None, mensaje) si falla,
imitando el Either[String, A] de Scala.
"""

from typing import Optional

from modelo import buscar_opcion


def texto_obligatorio(campo: str):
    return lambda t: (None, f"El campo '{campo}' no puede estar vacío.") if not t.strip() else (t.strip(), None)


def id_unico(existentes: tuple):
    def validar(t: str):
        valor, error = texto_obligatorio("Identificador")(t)
        if error:
            return None, error
        repetido = any(map(lambda s: s.id.lower() == valor.lower(), existentes))
        return (None, f"El identificador '{valor}' ya está registrado.") if repetido else (valor, None)
    return validar


def a_numero(t: str) -> Optional[float]:
    try:
        n = float(t.strip().replace(",", "."))
        return n if n == n and n not in (float("inf"), float("-inf")) else None
    except ValueError:
        return None


def numero_no_negativo(campo: str):
    def validar(t: str):
        n = a_numero(t)
        if n is None:
            return None, f"'{t}' no es un número válido para '{campo}'."
        return (None, f"'{campo}' no puede ser negativo.") if n < 0 else (n, None)
    return validar


def entero_no_negativo(campo: str):
    return lambda t: (int(t.strip()), None) if t.strip().isdigit() \
        else (None, f"'{campo}' debe ser un número entero mayor o igual a 0.")


def opciones_texto(enum_cls) -> str:
    return " | ".join(map(lambda par: f"{par[0]}={par[1].value}", enumerate(enum_cls, start=1)))


def opcion(campo: str, enum_cls):
    def validar(t: str):
        v = buscar_opcion(enum_cls, t)
        return (v, None) if v is not None else \
            (None, f"'{t}' no es válido para '{campo}'. Opciones: {opciones_texto(enum_cls)}")
    return validar
