"""Formato de cada reporte (dos decimales, tablas) y lista de reportes del menú."""

from typing import Callable

from analisis import (
    por_estado, sin_finalizar, conteo_por_categoria, categoria_mayor_demanda, valor_total,
    promedio, top_costosas, resumen_tecnicos, clientes_frecuentes, valor_por_cliente, criticas,
    promedio_horas, sobre_promedio_horas, conteo_por_prioridad, porcentaje_alta,
)
from modelo import Estado, Solicitud


def num(v: float) -> str:
    """Formato colombiano: 1.234,56 (dos decimales)."""
    return f"{v:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def dinero(v: float) -> str:
    return f"$ {num(v)}"


def pct(parte: int, total: int) -> str:
    return "0,00 %" if total == 0 else f"{num(parte * 100 / total)} %"


def titulo(t: str) -> str:
    linea = "=" * 78
    return f"\n{linea}\n  {t}\n{linea}\n"


def si_vacio(ls, mensaje: str, contenido: Callable[[], str]) -> str:
    return f"  (!) {mensaje}" if not ls else contenido()


def recortar(t: str, ancho: int) -> str:
    return t if len(t) <= ancho else t[: ancho - 1] + "…"


def lineas(textos) -> str:
    return "\n".join(textos)


def fila(s: Solicitud) -> str:
    return (f"  {recortar(s.id, 6):<6} {recortar(s.cliente, 16):<16} {recortar(s.tecnico, 14):<14} "
            f"{s.categoria.value:<9} {s.prioridad.value:<6} {s.estado.value:<11} {num(s.horas):>7} {dinero(s.valor):>16}")


def tabla(ls: tuple) -> str:
    encabezado = (f"  {'ID':<6} {'Cliente':<16} {'Técnico':<14} {'Categoría':<9} {'Prior.':<6} "
                  f"{'Estado':<11} {'Horas':>7} {'Valor':>16}")
    return lineas((encabezado, "  " + "-" * 76) + tuple(map(fila, ls)))


def reporte_general(ls: tuple) -> str:
    return titulo("RF02 · CONSULTA GENERAL DE SOLICITUDES") + si_vacio(
        ls, "No hay solicitudes registradas.",
        lambda: f"{tabla(ls)}\n\n  Total registradas: {len(ls)}")


def reporte_pendientes(ls: tuple) -> str:
    pend = por_estado(ls, Estado.PENDIENTE)
    proc = por_estado(ls, Estado.EN_PROCESO)
    return titulo("RF03 · SOLICITUDES SIN FINALIZAR") + si_vacio(
        pend + proc, "No hay solicitudes sin finalizar.",
        lambda: f"  >> Pendientes ({len(pend)})\n"
                + si_vacio(pend, "No hay solicitudes pendientes.", lambda: tabla(pend))
                + f"\n\n  >> En proceso ({len(proc)})\n"
                + si_vacio(proc, "No hay solicitudes en proceso.", lambda: tabla(proc))
                + f"\n\n  Total sin finalizar: {len(pend) + len(proc)}")


def reporte_categorias(ls: tuple) -> str:
    def contenido():
        mayor = categoria_mayor_demanda(ls)
        return lineas(map(lambda p: f"  {p[0].value:<10}: {p[1]:>3}  ({pct(p[1], len(ls))})",
                          conteo_por_categoria(ls))) \
            + (f"\n\n  Categoría con mayor demanda: {mayor[0].value} ({mayor[1]} solicitudes)" if mayor else "")
    return titulo("RF04 · DISTRIBUCIÓN POR CATEGORÍAS") + si_vacio(ls, "No hay solicitudes para analizar.", contenido)


def reporte_economico(ls: tuple) -> str:
    def contenido():
        prom = promedio(tuple(map(lambda s: s.valor, ls)))
        return lineas(map(lambda s: f"  {s.id:<6} {num(s.horas):>7} h x {dinero(s.costo_hora):>14} = {dinero(s.valor):>16}", ls)) \
            + f"\n\n  Valor total de los servicios : {dinero(valor_total(ls))}" \
            + f"\n  Valor promedio por solicitud : {dinero(prom) if prom is not None else 'N/A'}"
    return titulo("RF05 · ANÁLISIS ECONÓMICO") + si_vacio(ls, "No hay solicitudes para analizar.", contenido)


def reporte_top_costosas(ls: tuple) -> str:
    return titulo("RF06 · TOP 3 SOLICITUDES DE MAYOR COSTO") + si_vacio(
        ls, "No hay solicitudes para analizar.",
        lambda: lineas(map(lambda p: f"  {p[0]}. {p[1].id:<6} {p[1].cliente:<18} {p[1].categoria.value:<9} {dinero(p[1].valor):>16}",
                           enumerate(top_costosas(ls), start=1))))


def reporte_tecnicos(ls: tuple) -> str:
    res = resumen_tecnicos(ls)
    return titulo("RF07 · DESEMPEÑO DE LOS TÉCNICOS") + si_vacio(
        res, "No hay técnicos con solicitudes asignadas.",
        lambda: f"  {'Técnico':<20} {'Solicitudes':>11} {'Horas':>10} {'Finalizadas':>11}\n"
                + lineas(map(lambda r: f"  {recortar(r.nombre, 20):<20} {r.cantidad:>11} {num(r.horas):>10} {r.finalizadas:>11}", res))
                + f"\n\n  Técnico con mayor carga: {res[0].nombre} ({num(res[0].horas)} horas)")


def reporte_clientes_frecuentes(ls: tuple) -> str:
    frec = clientes_frecuentes(ls)
    return titulo("RF08 · CLIENTES FRECUENTES (más de una solicitud)") + si_vacio(
        frec, "Ningún cliente ha solicitado soporte más de una vez.",
        lambda: lineas(map(lambda p: f"  {p[0]:<25} {p[1]:>3} solicitudes", frec)))


def reporte_top_clientes(ls: tuple) -> str:
    top = valor_por_cliente(ls)[:3]
    return titulo("RF09 · TOP 3 CLIENTES POR VALOR ECONÓMICO") + si_vacio(
        top, "No hay solicitudes para analizar.",
        lambda: lineas(map(lambda p: f"  {p[0]}. {p[1][0]:<25} {dinero(p[1][1]):>18}", enumerate(top, start=1))))


def reporte_criticas(ls: tuple) -> str:
    crit = criticas(ls)
    return titulo("RF10 · SOLICITUDES CRÍTICAS (prioridad Alta sin finalizar)") + si_vacio(
        crit, "No hay solicitudes críticas.",
        lambda: f"  {'ID':<6} {'Cliente':<18} {'Técnico':<16} {'Categoría':<9} {'Estado':<11} {'Horas':>7}\n"
                + lineas(map(lambda s: f"  {s.id:<6} {recortar(s.cliente, 18):<18} {recortar(s.tecnico, 16):<16} "
                                       f"{s.categoria.value:<9} {s.estado.value:<11} {num(s.horas):>7}", crit))
                + f"\n\n  Total críticas: {len(crit)}")


def reporte_tiempos_elevados(ls: tuple) -> str:
    altos = sobre_promedio_horas(ls)
    return titulo("RF11 · SERVICIOS CON TIEMPOS ELEVADOS") + si_vacio(
        ls, "No hay solicitudes para analizar.",
        lambda: f"  Tiempo promedio de atención: {num(promedio_horas(ls))} horas\n\n"
                + si_vacio(altos, "Ninguna solicitud supera el promedio de horas.", lambda: tabla(altos)))


def reporte_prioridades(ls: tuple) -> str:
    return titulo("RF12 · CLASIFICACIÓN POR PRIORIDAD") + si_vacio(
        ls, "No hay solicitudes para analizar.",
        lambda: lineas(map(lambda p: f"  {p[0].value:<6}: {p[1]:>3}  ({pct(p[1], len(ls))})", conteo_por_prioridad(ls)))
                + f"\n\n  Porcentaje de prioridad Alta: {num(porcentaje_alta(ls))} %")


def reporte_resumen_ejecutivo(ls: tuple) -> str:
    mayor = categoria_mayor_demanda(ls)
    tecnicos = resumen_tecnicos(ls)
    clientes = valor_por_cliente(ls)
    prom = promedio_horas(ls)
    filas = (
        ("Total de solicitudes registradas", str(len(ls))),
        ("Solicitudes finalizadas", str(len(por_estado(ls, Estado.FINALIZADO)))),
        ("Solicitudes sin finalizar", str(len(sin_finalizar(ls)))),
        ("Categoría con mayor demanda", f"{mayor[0].value} ({mayor[1]})" if mayor else "N/A"),
        ("Técnico con más horas", f"{tecnicos[0].nombre} ({num(tecnicos[0].horas)} h)" if tecnicos else "N/A"),
        ("Valor económico total", dinero(valor_total(ls))),
        ("Tiempo promedio de atención", f"{num(prom)} h" if prom is not None else "N/A"),
        ("Solicitudes críticas", str(len(criticas(ls)))),
        ("Cliente de mayor valor", f"{clientes[0][0]} ({dinero(clientes[0][1])})" if clientes else "N/A"),
    )
    return titulo("RF14 · RESUMEN EJECUTIVO") + lineas(map(lambda f: f"  {f[0]:<34}: {f[1]}", filas))


REPORTES = (
    ("Consulta general (RF02)", reporte_general),
    ("Solicitudes sin finalizar (RF03)", reporte_pendientes),
    ("Distribución por categoría (RF04)", reporte_categorias),
    ("Análisis económico (RF05)", reporte_economico),
    ("Top 3 más costosas (RF06)", reporte_top_costosas),
    ("Desempeño de técnicos (RF07)", reporte_tecnicos),
    ("Clientes frecuentes (RF08)", reporte_clientes_frecuentes),
    ("Top 3 clientes por valor (RF09)", reporte_top_clientes),
    ("Solicitudes críticas (RF10)", reporte_criticas),
    ("Tiempos elevados (RF11)", reporte_tiempos_elevados),
    ("Clasificación por prioridad (RF12)", reporte_prioridades),
    ("Resumen ejecutivo (RF14)", reporte_resumen_ejecutivo),
)
