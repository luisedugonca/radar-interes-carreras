"""Etapa 4 · Validación: separa lo válido de lo rechazado, siempre con motivo.

Dos contratos:
  - Sugerencia de autocompletar: texto no vacío, tipo QUERY, largo razonable y que nombre el tema.
  - Top 10 de un buscador: que traiga resultados y que los resultados hablen del tema.
    Esta última regla existe porque Bing, cuando detecta un script, responde 200 con
    resultados que no tienen relación con la consulta (medido el 2026-11-16; el caso real
    está guardado en tests/fixtures/bing_sin_relacion_20261116.json).
"""
from __future__ import annotations

import json
import re
from urllib.parse import urlparse

from comun import normalizar, tokens_tema


def validar_sugerencias(registros: list[dict], tema: str, reglas: dict) -> tuple[list[dict], list[dict]]:
    v = reglas["validacion"]
    tokens = tokens_tema(tema)
    validas, rechazadas = [], []
    for reg in registros:
        base = {"semilla": reg["consulta"], "grupo": reg["grupo"], "fuente": reg["fuente"]}
        if reg["http"] != 200:
            rechazadas.append({**base, "texto": "", "motivo": f"el pedido falló (HTTP {reg['http']})"})
            continue
        try:
            datos = json.loads(reg["cuerpo"])
            textos = datos[1]
            extra = datos[4] if len(datos) > 4 and isinstance(datos[4], dict) else {}
        except (json.JSONDecodeError, IndexError, TypeError):
            rechazadas.append({**base, "texto": "", "motivo": "la respuesta no tiene el formato esperado"})
            continue
        tipos = extra.get("google:suggesttype", [])
        relevancias = extra.get("google:suggestrelevance", [])
        for i, texto in enumerate(textos):
            item = {**base, "texto": str(texto).strip(), "pos": i + 1, "de": len(textos),
                    "relevancia": relevancias[i] if i < len(relevancias) else None}
            tipo = tipos[i] if i < len(tipos) else "QUERY"
            norm = normalizar(item["texto"])
            if not norm:
                motivo = "texto vacío"
            elif tipo not in v["tipos_aceptados"]:
                motivo = f"no es una búsqueda (tipo {tipo})"
            elif len(item["texto"]) > v["largo_maximo"]:
                motivo = "texto demasiado largo"
            elif not any(t in norm for t in tokens):
                motivo = "no nombra el tema"
            else:
                validas.append(item)
                continue
            rechazadas.append({**item, "motivo": motivo})
    return validas, rechazadas


def validar_top10(paginas: list[dict], tema: str, reglas: dict) -> list[dict]:
    """Cada página trae 'resultados': lista de {titulo, url} en el orden del buscador, o None si está pendiente."""
    minimo = reglas["validacion"]["top10_min_relacionados"]
    tokens = tokens_tema(tema)
    salida = []
    for p in paginas:
        item = {"buscador": p["buscador"], "consulta": p["consulta"], "estado": p.get("estado", "rechazado"),
                "motivo": p.get("motivo", ""), "resultados": []}
        if p.get("resultados") is None:
            salida.append(item)
            continue
        crudos = p["resultados"][:10]
        relacionados = sum(1 for r in crudos if any(t in normalizar(r["titulo"] + " " + r["url"]) for t in tokens))
        if not crudos:
            item["estado"], item["motivo"] = "rechazado", "el buscador no devolvió resultados"
        elif relacionados < minimo:
            item["estado"] = "rechazado"
            item["motivo"] = (f"solo {relacionados} de {len(crudos)} resultados nombran el tema: "
                              "el buscador devolvió resultados sin relación con la consulta")
        else:
            item["estado"], item["motivo"] = "ok", ""
            for pos, r in enumerate(crudos, start=1):
                dominio = urlparse(r["url"] if "://" in r["url"] else "https://" + r["url"]).netloc
                item["resultados"].append({"pos": pos, "titulo": r["titulo"], "url": r["url"],
                                           "dominio": re.sub(r"^www\.", "", dominio)})
        salida.append(item)
    return salida
