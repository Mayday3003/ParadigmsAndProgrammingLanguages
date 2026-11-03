"""Soporte360 — versión Python con estilo funcional. Punto de entrada y menú de consultas.

Reglas: sin for/while (ni siquiera dentro de comprensiones), sin reasignar variables,
datos inmutables (dataclass frozen + tuplas) y funciones de orden superior.
Ejecutar: python3 main.py
"""

import sys

from entrada import pedir, registrar
from reportes import REPORTES, lineas, reporte_general, reporte_resumen_ejecutivo
from validacion import entero_no_negativo


# Número de la opción "Mostrar todos": siempre la siguiente al último reporte.
OPCION_TODOS = len(REPORTES) + 1


def menu() -> str:
    return lineas(
        ("\n=================== MENÚ DE CONSULTAS — SOPORTE360 ===================",)
        + tuple(map(lambda p: f"  {p[0]:>2}. {p[1][0]}", enumerate(REPORTES, start=1)))
        + (f"  {OPCION_TODOS:>2}. Mostrar todos los reportes", "   0. Salir"))


def consultar(ls: tuple) -> None:
    print(menu())
    op = pedir("Seleccione una opción: ", entero_no_negativo("Opción"))
    if op == 0:
        print("\nGracias por usar Soporte360. ¡Hasta pronto!")
        return
    print(lineas(map(lambda r: r[1](ls), REPORTES)) if op == OPCION_TODOS
          else REPORTES[op - 1][1](ls) if op <= len(REPORTES)
          else "   [ERROR] Opción no válida.")
    consultar(ls)


def main() -> None:
    print("==============================================================")
    print("   SOPORTE360 SAS — Análisis de solicitudes de soporte técnico")
    print("==============================================================")
    cantidad = pedir("¿Cuántas solicitudes desea registrar? ", entero_no_negativo("Cantidad"))
    solicitudes = registrar(1, cantidad)
    print(reporte_general(solicitudes))
    print(reporte_resumen_ejecutivo(solicitudes))
    consultar(solicitudes)


if __name__ == "__main__":
    sys.setrecursionlimit(10_000)
    main()
