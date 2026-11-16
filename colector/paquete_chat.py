"""Arma docs/data/paquete-chat.md: todas las consultas guardadas en un solo archivo de texto.

Sirve para subirlo como conocimiento a un GPT, a un Gem o a un proyecto de Claude, o para pegarlo
en cualquier chat. No agrega nada: es un resumen de docs/data/consultas/*.json.

Uso: python3 colector/paquete_chat.py
"""
from __future__ import annotations

import json

from comun import DIR_CONSULTAS, RUTA_INDICE

SALIDA = RUTA_INDICE.parent / "paquete-chat.md"
APARTE = ("otros", "fuera_uy")


def armar() -> str:
    indice = json.loads(RUTA_INDICE.read_text(encoding="utf-8"))
    lineas = [
        "# Radar de interés por carreras — paquete para chats",
        "",
        "Datos medidos del autocompletar de Google y de YouTube para Uruguay.",
        "**Son frases distintas que el buscador propone. El número entre paréntesis es en cuántas consultas apareció "
        "cada frase. NO es cantidad de búsquedas ni de personas.**",
        "«Quién» (estudiante o familia) es una lectura del equipo: tratarlo como supuesto.",
        "",
        f"Actualizado: {indice['actualizado_utc']} · {len(indice['consultas'])} temas.",
        "",
    ]
    for entrada in indice["consultas"]:
        c = json.loads((DIR_CONSULTAS / f"{entrada['slug']}.json").read_text(encoding="utf-8"))
        r = c["resumen"]
        inst = ", ".join(f"{i['id']} ({i['sugerencias']})" for i in r["instituciones_uy"]) or "ninguna"
        lineas += [
            f"## {c['tema']}",
            "",
            f"- Medido: {c['generado_utc']} · corrida `{c['run_id']}`",
            f"- Frases distintas: {r['sugerencias_unicas']} · de otros países: {r['fuera_de_uruguay_pct']} % · "
            f"sin clasificar: {r['sin_clasificar']}",
            f"- Instituciones uruguayas nombradas: {inst}",
            "",
        ]
        for i in c["intenciones"]:
            if not i["total"] or i["id"] in APARTE:
                continue
            frases = "; ".join(f"{s['texto']} ({s['apariciones']})" for s in i["sugerencias"][:10])
            lineas.append(f"- **{i['nombre']}** — {i['total']} frases ({i['pct']} %): {frases}")
        lineas.append("")
    return "\n".join(lineas)


if __name__ == "__main__":
    SALIDA.write_text(armar(), encoding="utf-8")
    print(f"{SALIDA.name}: {SALIDA.stat().st_size // 1024} KB")
