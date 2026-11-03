"""Motor de escenarios: convierte las métricas en puntajes 0–10 por criterio y pondera por escenario.

Normalización entre los dos lenguajes (relativa, fácil de explicar):
  - "menor es mejor":  puntaje = 10 · (mejor + ε) / (valor + ε)
  - "mayor es mejor":  puntaje = 10 · (valor + ε) / (mejor + ε)
  ε = 5 % del mayor valor: evita divisiones por cero y que diferencias mínimas parezcan enormes.
Si un criterio tiene varias sub-métricas, se promedian sus puntajes.
"""

from __future__ import annotations

EMPATE = 0.3  # diferencia mínima (sobre 10) para declarar un ganador


def normalizar(valores: dict, menor_es_mejor: bool) -> dict:
    validos = {k: v for k, v in valores.items() if v is not None}
    if not validos:
        return {}
    eps = max(map(abs, validos.values())) * 0.05 + 1e-9
    mejor = min(validos.values()) if menor_es_mejor else max(validos.values())
    return {k: (round(10 * (mejor + eps) / (v + eps), 2) if menor_es_mejor else round(10 * (v + eps) / (mejor + eps), 2)) if v is not None else 0.0
            for k, v in valores.items()}


def tamano_comun(rend: dict, ids: list[str]) -> tuple[dict | None, dict | None]:
    """Devuelve (fila más pequeña, fila más grande) entre los tamaños donde alguno terminó bien."""
    filas = [f for f in rend.get("tamanos", []) if any(f["lenguajes"].get(i, {}).get("ok") for i in ids)]
    if not filas:
        return None, None
    ambos = [f for f in filas if all(f["lenguajes"].get(i, {}).get("ok") for i in ids)]
    return (ambos or filas)[0], filas[-1]


def tiempo(fila: dict, lid: str):
    d = fila["lenguajes"].get(lid, {})
    if not d.get("ok"):
        return None
    return (d.get("hyperfine") or {}).get("mean", d.get("tiempo_s"))


def valores_medidos(res: dict, ids: list[str]) -> dict:
    """Para cada criterio: lista de (descripción, {lenguaje: valor}, menor_es_mejor)."""
    sonar = res["sonar"].get("lenguajes", {}) if res["sonar"].get("estado") == "ok" else {}
    est, rend = res["estatico"], res.get("rendimiento") or {}
    por = lambda f: {i: f(i) for i in ids}
    fallos = por(lambda i: sum(1 for f in rend.get("tamanos", []) if not f["lenguajes"].get(i, {}).get("ok", True)))
    c = {}
    if sonar:
        kloc = por(lambda i: (sonar[i]["ncloc"] or 1) / 1000)
        c["mantenibilidad"] = [
            ("Minutos de deuda técnica por kLOC", por(lambda i: sonar[i]["sqale_index"] / kloc[i]), True),
            ("Code smells por kLOC", por(lambda i: sonar[i]["code_smells"] / kloc[i]), True)]
        c["confiabilidad"] = [("Bugs (Sonar) + ejecuciones fallidas", por(lambda i: sonar[i]["bugs"] + fallos[i]), True)]
        c["seguridad"] = [("Vulnerabilidades ×3 + hotspots", por(lambda i: sonar[i]["vulnerabilities"] * 3 + sonar[i]["hotspots"]), True)]
        c["legibilidad"] = [("Complejidad cognitiva por función (Sonar)", por(lambda i: sonar[i]["complejidad_cognitiva_por_funcion"]), True)]
        c["concision"] = [("Líneas de código (Sonar ncloc)", por(lambda i: sonar[i]["ncloc"]), True)]
    else:
        c["confiabilidad"] = [("Ejecuciones fallidas", fallos, True)]
        c["concision"] = [("Líneas de código (lizard)", por(lambda i: est[i]["complejidad"]["nloc"]), True)]
    c.setdefault("legibilidad", []).append(("Complejidad ciclomática promedio (lizard)", por(lambda i: est[i]["complejidad"]["ccn_promedio"]), True))
    c["pureza_funcional"] = [
        ("Violaciones a las reglas por 100 líneas", por(lambda i: est[i]["violaciones_por_100_lineas"]), True),
        ("Densidad funcional (lambdas + orden superior por 100 líneas)", por(lambda i: est[i]["densidad_funcional"]), False)]

    pequena, grande = tamano_comun(rend, ids)
    if pequena:
        c["arranque_rapido"] = [(f"Tiempo con {pequena['n']} solicitudes (s)", por(lambda i: tiempo(pequena, i)), True)]
    if grande:
        c["rendimiento_volumen"] = [(f"Tiempo con {grande['n']} solicitudes (s)", por(lambda i: tiempo(grande, i)), True)]
        c["memoria"] = [(f"Memoria máxima con {grande['n']} solicitudes (MB)",
                         por(lambda i: grande["lenguajes"][i].get("memoria_mb") if grande["lenguajes"].get(i, {}).get("ok") else None), True)]
    gar = res.get("garantias") or {}
    if gar.get("estado") == "ok":
        r = gar["resumen"]
        c["garantias_funcionales"] = [
            ("Errores inyectados detectados antes de ejecutar (%)", por(lambda i: r[i]["pct_antes"]), False),
            ("Máximo de solicitudes procesadas con recursión", por(lambda i: r[i]["max_recursion"]), False)]
    prep = rend.get("preparacion", {})
    if prep:
        c["ciclo_desarrollo"] = [("Tiempo de compilación/preparación (s)",
                                  por(lambda i: prep.get(i, {}).get("construccion_s") if prep.get(i, {}).get("ok") else None), True)]
    return c


def calcular(res: dict, config: dict, ids: list[str]) -> dict:
    medidos = valores_medidos(res, ids)
    criterios = {}
    for cid, meta in config["criterios"].items():
        if meta["tipo"] == "cualitativo":
            criterios[cid] = {**meta, "puntajes": {i: float(meta["valores"].get(i, 0)) for i in ids}, "submetricas": []}
        elif cid in medidos:
            subs = [{"descripcion": d, "valores": v, "menor_es_mejor": m, "puntajes": normalizar(v, m)} for d, v, m in medidos[cid]]
            puntajes = {i: round(sum(s["puntajes"].get(i, 0) for s in subs) / len(subs), 2) for i in ids}
            criterios[cid] = {**meta, "puntajes": puntajes, "submetricas": subs}

    escenarios = []
    for esc in config["escenarios"]:
        pesos = {c: w for c, w in esc["pesos"].items() if c in criterios and w > 0}
        total_w = sum(pesos.values()) or 1
        totales = {i: round(sum(criterios[c]["puntajes"][i] * w for c, w in pesos.items()) / total_w, 2) for i in ids}
        orden = sorted(ids, key=lambda i: -totales[i])
        ganador, perdedor = orden[0], orden[-1]
        empate = totales[ganador] - totales[perdedor] < EMPATE
        aportes = sorted(({"criterio": c, "nombre": criterios[c]["nombre"], "peso": w,
                           "diferencia": round(criterios[c]["puntajes"][ganador] - criterios[c]["puntajes"][perdedor], 2),
                           "impacto": round(w * (criterios[c]["puntajes"][ganador] - criterios[c]["puntajes"][perdedor]) / total_w, 2)}
                          for c, w in pesos.items()), key=lambda a: -a["impacto"])
        escenarios.append({
            **{k: esc[k] for k in ("id", "nombre", "icono", "descripcion")},
            "pesos": pesos,
            "omitidos": [c for c in esc["pesos"] if c not in criterios],
            "totales": totales,
            "ganador": None if empate else ganador,
            "margen": round(totales[ganador] - totales[perdedor], 2),
            "a_favor": [a for a in aportes if a["impacto"] > 0][:3],
            "en_contra": [a for a in reversed(aportes) if a["impacto"] < 0][:2],
        })

    victorias = {i: sum(1 for e in escenarios if e["ganador"] == i) for i in ids}
    return {"criterios": criterios, "escenarios": escenarios, "victorias": victorias,
            "empates": sum(1 for e in escenarios if e["ganador"] is None)}
