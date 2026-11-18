"""Base única en CSV: una fila por frase de cada tema guardado → docs/data/base.csv

Es la «base de datos» descargable del radar. Se regenera sola al final de cada corrida
(run.py y reprocesar.py la llaman). Las mismas columnas usa la web para descargar
un tema medido en vivo y para volver a abrir un CSV guardado (docs/assets/nucleo.js).

Uso: python3 colector/base_csv.py
"""
from __future__ import annotations

import csv
import json

from comun import DIR_CONSULTAS, RUTA_INDICE

SALIDA = RUTA_INDICE.parent / "base.csv"
COLUMNAS = ["tema", "slug", "run_id", "medido_utc", "pais", "consultas_respondidas", "tipo_duda_id", "tipo_duda",
            "frase", "apariciones", "pos_promedio", "pos_mejor", "veces_top3", "veces_top10", "instituciones", "fuentes"]


def filas(c: dict) -> list[dict]:
    n = sum(f["con_respuesta"] for f in c["fuentes"])
    salida = []
    for i in c["intenciones"]:
        for s in i["sugerencias"]:
            salida.append({
                "tema": c["tema"], "slug": c["slug"], "run_id": c["run_id"], "medido_utc": c["generado_utc"],
                "pais": c["pais"], "consultas_respondidas": n, "tipo_duda_id": i["id"], "tipo_duda": i["nombre"],
                "frase": s["texto"], "apariciones": s["apariciones"],
                "pos_promedio": "" if s.get("pos_promedio") is None else s["pos_promedio"],
                "pos_mejor": "" if s.get("pos_mejor") is None else s["pos_mejor"],
                "veces_top3": s.get("veces_top3", 0), "veces_top10": s.get("veces_top10", 0),
                "instituciones": "|".join(s.get("instituciones", [])), "fuentes": "|".join(s.get("fuentes", [])),
            })
    return salida


def regenerar() -> int:
    indice = json.loads(RUTA_INDICE.read_text(encoding="utf-8"))
    todas = []
    for e in indice["consultas"]:
        todas += filas(json.loads((DIR_CONSULTAS / f"{e['slug']}.json").read_text(encoding="utf-8")))
    # utf-8 con BOM: Excel lo abre con tildes correctas
    with SALIDA.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS)
        w.writeheader()
        w.writerows(todas)
    return len(todas)


if __name__ == "__main__":
    print(f"{SALIDA.name}: {regenerar()} filas")
