"""RF03–RF12 y RF14: lógica pura sobre tuplas inmutables.

Desempates: valores iguales -> orden alfabético por nombre/id; categorías -> orden de definición.
"""

from itertools import groupby
from typing import Optional

from modelo import Categoria, Estado, Prioridad, ResumenTecnico, normalizar




def por_estado(ls: tuple, estado: Estado) -> tuple:
    return tuple(filter(lambda s: s.estado == estado, ls))


def sin_finalizar(ls: tuple) -> tuple:
    return tuple(filter(lambda s: s.estado != Estado.FINALIZADO, ls))


def contar(ls: tuple, pred) -> int:
    return sum(map(lambda s: 1 if pred(s) else 0, ls))


def conteo_por_categoria(ls: tuple) -> tuple:
    return tuple(map(lambda c: (c, contar(ls, lambda s: s.categoria == c)), Categoria))


def categoria_mayor_demanda(ls: tuple):
    orden = list(Categoria)
    candidatos = sorted(filter(lambda p: p[1] > 0, conteo_por_categoria(ls)),
                        key=lambda p: (-p[1], orden.index(p[0])))
    return candidatos[0] if candidatos else None


def valor_total(ls) -> float:
    return sum(map(lambda s: s.valor, ls))


def promedio(valores: tuple) -> Optional[float]:
    return sum(valores) / len(valores) if valores else None


def top_costosas(ls: tuple, n: int = 3) -> tuple:
    return tuple(sorted(ls, key=lambda s: (-s.valor, s.id.lower()))[:n])


def agrupar(ls: tuple, clave) -> tuple:
    """Agrupa por clave normalizada; devuelve tupla de grupos (tuplas)."""
    ordenadas = sorted(ls, key=lambda s: normalizar(clave(s)))
    return tuple(map(lambda g: tuple(g[1]), groupby(ordenadas, key=lambda s: normalizar(clave(s)))))


def resumen_tecnicos(ls: tuple) -> tuple:
    resumenes = map(lambda g: ResumenTecnico(
        nombre=g[0].tecnico,
        cantidad=len(g),
        horas=sum(map(lambda s: s.horas, g)),
        finalizadas=contar(g, lambda s: s.estado == Estado.FINALIZADO),
    ), agrupar(ls, lambda s: s.tecnico))
    return tuple(sorted(resumenes, key=lambda r: (-r.horas, r.nombre.lower())))


def clientes_frecuentes(ls: tuple) -> tuple:
    pares = map(lambda g: (g[0].cliente, len(g)), agrupar(ls, lambda s: s.cliente))
    return tuple(sorted(filter(lambda p: p[1] > 1, pares), key=lambda p: (-p[1], p[0].lower())))


def valor_por_cliente(ls: tuple) -> tuple:
    pares = map(lambda g: (g[0].cliente, valor_total(g)), agrupar(ls, lambda s: s.cliente))
    return tuple(sorted(pares, key=lambda p: (-p[1], p[0].lower())))


def criticas(ls: tuple) -> tuple:
    return tuple(sorted(
        filter(lambda s: s.prioridad == Prioridad.ALTA and s.estado != Estado.FINALIZADO, ls),
        key=lambda s: (-s.horas, s.id.lower())))


def promedio_horas(ls: tuple) -> Optional[float]:
    return promedio(tuple(map(lambda s: s.horas, ls)))


def sobre_promedio_horas(ls: tuple) -> tuple:
    p = promedio_horas(ls)
    return () if p is None else tuple(sorted(filter(lambda s: s.horas > p, ls),
                                             key=lambda s: (-s.horas, s.id.lower())))


def conteo_por_prioridad(ls: tuple) -> tuple:
    return tuple(map(lambda p: (p, contar(ls, lambda s: s.prioridad == p)), Prioridad))


def porcentaje_alta(ls: tuple) -> Optional[float]:
    return contar(ls, lambda s: s.prioridad == Prioridad.ALTA) * 100 / len(ls) if ls else None
