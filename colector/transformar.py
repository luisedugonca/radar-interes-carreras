"""Etapa 5 · Transformación: agrupa sugerencias repetidas y las clasifica por intención.

La clasificación usa los patrones de docs/data/reglas.json (los mismos que usa la web en vivo).
Lo que se mide: en cuántas consultas distintas apareció cada sugerencia ("apariciones").
Lo que NO se mide: cuánta gente la busca. El autocompletar no da volumen.
"""
from __future__ import annotations

import re

from comun import normalizar


def clasificar(texto_norm: str, reglas: dict) -> str:
    for intencion in reglas["intenciones"]:
        if intencion["patron"] and re.search(intencion["patron"], texto_norm):
            return intencion["id"]
    return "otros"


def instituciones(texto_norm: str, reglas: dict) -> list[str]:
    return [i["id"] for i in reglas["instituciones_uy"] if re.search(i["patron"], texto_norm)]


def transformar(validas: list[dict], top10: list[dict], tema: str, reglas: dict) -> dict:
    tema_norm = normalizar(tema)
    agrupadas: dict[str, dict] = {}
    for v in validas:
        clave = normalizar(v["texto"])
        if clave == tema_norm:
            continue  # el tema solo, sin nada más, no dice qué se busca sobre él
        g = agrupadas.setdefault(clave, {"texto": v["texto"], "semillas": [], "grupos": [], "fuentes": [],
                                         "relevancia_max": None})
        if v["semilla"] not in g["semillas"]:
            g["semillas"].append(v["semilla"])
        if v["grupo"] not in g["grupos"]:
            g["grupos"].append(v["grupo"])
        if v["fuente"] not in g["fuentes"]:
            g["fuentes"].append(v["fuente"])
        if v.get("relevancia") is not None:
            g["relevancia_max"] = max(g["relevancia_max"] or 0, v["relevancia"])

    por_intencion: dict[str, list[dict]] = {i["id"]: [] for i in reglas["intenciones"]}
    conteo_inst: dict[str, int] = {}
    for clave, g in agrupadas.items():
        g["apariciones"] = len(g["semillas"])
        # La institución se busca en lo que la sugerencia agrega al tema, no en el tema mismo.
        resto = clave.replace(tema_norm, " ")
        g["instituciones"] = instituciones(resto, reglas)
        for inst in g["instituciones"]:
            conteo_inst[inst] = conteo_inst.get(inst, 0) + 1
        g["intencion"] = clasificar(resto, reglas)
        por_intencion[g["intencion"]].append(g)

    total = len(agrupadas)
    intenciones = []
    for regla in reglas["intenciones"]:
        items = sorted(por_intencion[regla["id"]],
                       key=lambda s: (-s["apariciones"], -(s["relevancia_max"] or 0), s["texto"]))
        intenciones.append({"id": regla["id"], "nombre": regla["nombre"], "color": regla["color"],
                            "quien": regla["quien"], "que_es": regla["que_es"], "total": len(items),
                            "pct": round(100 * len(items) / total, 1) if total else 0.0,
                            "sugerencias": items})

    quien = {"familia": 0, "estudiante": 0, "ambos": 0, "ninguno": 0}
    for i in intenciones:
        quien[i["quien"]] += i["total"]

    dominios: dict[str, dict] = {}
    for pagina in top10:
        for r in pagina["resultados"]:
            d = dominios.setdefault(r["dominio"], {"dominio": r["dominio"], "apariciones": 0, "mejor_pos": r["pos"]})
            d["apariciones"] += 1
            d["mejor_pos"] = min(d["mejor_pos"], r["pos"])

    fuera = next(i["total"] for i in intenciones if i["id"] == "fuera_uy")
    return {
        "resumen": {
            "sugerencias_unicas": total,
            "intenciones_con_datos": sum(1 for i in intenciones if i["total"] and i["id"] not in ("otros", "fuera_uy", "emprender")),
            "fuera_de_uruguay": fuera,
            "fuera_de_uruguay_pct": round(100 * fuera / total, 1) if total else 0.0,
            "sin_clasificar": next(i["total"] for i in intenciones if i["id"] == "otros"),
            "instituciones_uy": sorted(({"id": k, "sugerencias": n} for k, n in conteo_inst.items()),
                                       key=lambda x: (-x["sugerencias"], x["id"])),
            "quien_supuesto": quien,
            "top10_validos": sum(1 for p in top10 if p["estado"] == "ok"),
            "top10_rechazados": sum(1 for p in top10 if p["estado"] == "rechazado"),
            "top10_pendientes": sum(1 for p in top10 if p["estado"] == "pendiente"),
        },
        "intenciones": intenciones,
        "dominios": sorted(dominios.values(), key=lambda d: (-d["apariciones"], d["mejor_pos"], d["dominio"])),
    }
