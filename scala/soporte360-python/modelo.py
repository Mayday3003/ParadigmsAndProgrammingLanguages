"""Modelo: enums Categoria/Prioridad/Estado, Solicitud inmutable y utilidades de texto."""

import unicodedata
from dataclasses import dataclass
from enum import Enum


def normalizar(texto: str) -> str:
    """Compara textos sin importar mayúsculas, espacios ni tildes."""
    sin_tildes = unicodedata.normalize("NFD", texto.strip().lower())
    return "".join(filter(lambda c: unicodedata.category(c) != "Mn" and not c.isspace(), sin_tildes))


class Categoria(Enum):
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    REDES = "Redes"


class Prioridad(Enum):
    ALTA = "Alta"
    MEDIA = "Media"
    BAJA = "Baja"


class Estado(Enum):
    PENDIENTE = "Pendiente"
    EN_PROCESO = "En proceso"
    FINALIZADO = "Finalizado"


@dataclass(frozen=True)
class Solicitud:
    id: str
    cliente: str
    tecnico: str
    categoria: Categoria
    prioridad: Prioridad
    estado: Estado
    horas: float
    costo_hora: float

    @property
    def valor(self) -> float:
        """RF05: valor = horas * costo por hora."""
        return self.horas * self.costo_hora


@dataclass(frozen=True)
class ResumenTecnico:
    nombre: str
    cantidad: int
    horas: float
    finalizadas: int


def buscar_opcion(enum_cls, texto: str):
    """Busca una opción de un Enum por número (1, 2, 3) o por nombre."""
    valores = list(enum_cls)
    t = texto.strip()
    if t.isdigit():
        return valores[int(t) - 1] if 1 <= int(t) <= len(valores) else None
    return next(filter(lambda v: normalizar(v.value) == normalizar(t), valores), None)
