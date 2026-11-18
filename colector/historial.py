"""Historial de mediciones por tema → docs/data/historial/<slug>/

Cada corrida deja dos cosas, para que la web pueda mostrar la evolución y abrir una medición vieja:
  - <run_id>.json.gz : la consulta completa de esa corrida, comprimida (unos 8 KB)
  - serie.json        : un resumen por corrida (apariciones por tipo de duda, términos con más datos,
                        instituciones). Es lo que dibuja el gráfico de evolución.
Volver a registrar la misma corrida la reemplaza: no duplica (idempotente).
"""
from __future__ import annotations

import gzip
import json

from comun import RUTA_INDICE

DIR = RUTA_INDICE.parent / "historial"
APARTE = ("otros", "fuera_uy", "emprender")


def resumen(c: dict) -> dict:
    utiles = [i for i in c["intenciones"] if i["id"] not in APARTE]
    frases = sorted((s | {"rama": i["id"]} for i in utiles for s in i["sugerencias"]),
                    key=lambda s: (-s["apariciones"], -s.get("veces_top3", 0), s.get("pos_promedio") or 99, s["texto"]))
    inst: dict[str, int] = {}
    for s in frases:
        for x in s.get("instituciones", []):
            inst[x] = inst.get(x, 0) + 1
    return {
        "run_id": c["run_id"], "fecha_utc": c["generado_utc"],
        "consultas": sum(f["con_respuesta"] for f in c["fuentes"]),
        "frases": sum(i["total"] for i in c["intenciones"]),
        "apariciones_utiles": sum(i.get("apariciones_total", 0) for i in utiles),
        "ramas": {i["id"]: i.get("apariciones_total", 0) for i in c["intenciones"]},
        "top": [{"texto": s["texto"], "rama": s["rama"], "apariciones": s["apariciones"], "pos_promedio": s.get("pos_promedio")} for s in frases[:15]],
        "instituciones": dict(sorted(inst.items(), key=lambda kv: (-kv[1], kv[0]))),
    }


def registrar(c: dict) -> int:
    """Guarda la consulta en el historial de su tema. Devuelve cuántas mediciones tiene el tema."""
    d = DIR / c["slug"]
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{c['run_id']}.json.gz").write_bytes(
        gzip.compress(json.dumps(c, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), mtime=0))
    ruta = d / "serie.json"
    serie = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {"tema": c["tema"], "slug": c["slug"], "mediciones": []}
    serie["mediciones"] = sorted([m for m in serie["mediciones"] if m["run_id"] != c["run_id"]] + [resumen(c)],
                                 key=lambda m: m["fecha_utc"])
    ruta.write_text(json.dumps(serie, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return len(serie["mediciones"])
