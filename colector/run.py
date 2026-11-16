"""Orquestador: extrae → registra → valida → transforma → carga → manifiesto.

Uso:
    python colector/run.py "ciencia de datos"
    TEMA="ciencia de datos" python colector/run.py        (así lo llama GitHub Actions)

Salidas:
    data/raw/<run_id>/            crudo, tal cual llegó
    docs/data/consultas/<slug>.json   lo que lee la web
    docs/data/indice.json         lista de consultas guardadas
    manifests/run_<run_id>.json   linaje y conteos de la corrida
    logs/colector.log
"""
from __future__ import annotations

import json
import logging
import os
import sys
import urllib.parse
from datetime import datetime, timezone

import extraer
import transformar
import validar
from comun import (DIR_CONSULTAS, DIR_LOGS, DIR_MANIFESTS, DIR_RAW, RUTA_INDICE, cargar_reglas,
                   limpiar_tema, slug)

log = logging.getLogger("run")


def configurar_log() -> None:
    DIR_LOGS.mkdir(exist_ok=True)
    formato = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    raiz = logging.getLogger()
    raiz.setLevel(logging.INFO)
    for manejador in (logging.StreamHandler(), logging.FileHandler(DIR_LOGS / "colector.log", encoding="utf-8")):
        manejador.setFormatter(formato)
        raiz.addHandler(manejador)


def actualizar_indice(entrada: dict) -> None:
    indice = json.loads(RUTA_INDICE.read_text(encoding="utf-8")) if RUTA_INDICE.exists() else {"consultas": []}
    indice["consultas"] = [c for c in indice["consultas"] if c["slug"] != entrada["slug"]] + [entrada]
    indice["consultas"].sort(key=lambda c: c["tema"])
    indice["actualizado_utc"] = entrada["generado_utc"]
    RUTA_INDICE.write_text(json.dumps(indice, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def correr(tema_crudo: str) -> dict:
    tema = limpiar_tema(tema_crudo)
    reglas = cargar_reglas()
    ahora = datetime.now(timezone.utc)
    run_id = f"{ahora:%Y%m%dT%H%M%SZ}_{slug(tema)}"
    dir_raw = DIR_RAW / run_id
    dir_raw.mkdir(parents=True, exist_ok=True)
    log.info("Corrida %s · tema %r · reglas versión %s", run_id, tema, reglas["version"])

    registros = extraer.extraer_sugerencias(tema, reglas, dir_raw)
    paginas = extraer.extraer_top10(tema)

    validas, rechazadas = validar.validar_sugerencias(registros, tema, reglas)
    top10 = validar.validar_top10(paginas, tema, reglas)
    log.info("Validación: %s sugerencias válidas, %s rechazadas · top 10: %s", len(validas), len(rechazadas),
             ", ".join(f"{p['buscador']}={p['estado']}" for p in top10))
    for p in top10:
        if p["estado"] != "ok":
            log.warning("Top 10 %s · %r: %s", p["estado"], p["consulta"], p["motivo"])

    resultado = transformar.transformar(validas, top10, tema, reglas)

    q = urllib.parse.quote(tema)
    consulta = {
        "tema": tema, "slug": slug(tema), "run_id": run_id,
        "generado_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pais": reglas["pais"]["nombre"], "reglas_version": reglas["version"],
        "fuentes": [
            {"id": "google", "nombre": "Autocompletar de Google", "pedidos": sum(1 for r in registros if r["fuente"] == "google"),
             "con_respuesta": sum(1 for r in registros if r["fuente"] == "google" and r["http"] == 200)},
            {"id": "youtube", "nombre": "Autocompletar de YouTube", "pedidos": sum(1 for r in registros if r["fuente"] == "youtube"),
             "con_respuesta": sum(1 for r in registros if r["fuente"] == "youtube" and r["http"] == 200)},
        ],
        **resultado,
        "top10": top10,
        "rechazadas": {
            "total": len(rechazadas),
            "por_motivo": _contar(r["motivo"] for r in rechazadas),
            "ejemplos": rechazadas[:25],
        },
        "enlaces": {
            "trends": f"https://trends.google.com/trends/explore?geo=UY&date=today%205-y&q={q}",
            "google": f"https://www.google.com/search?gl=uy&hl=es&q={q}",
            "bing": f"https://www.bing.com/search?cc=UY&setlang=es&q={q}",
            "duckduckgo": f"https://duckduckgo.com/?kl=uy-es&q={q}",
            "youtube": f"https://www.youtube.com/results?search_query={q}",
        },
    }
    DIR_CONSULTAS.mkdir(parents=True, exist_ok=True)
    ruta = DIR_CONSULTAS / f"{consulta['slug']}.json"
    ruta.write_text(json.dumps(consulta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    actualizar_indice({"tema": tema, "slug": consulta["slug"], "run_id": run_id,
                       "generado_utc": consulta["generado_utc"],
                       "sugerencias_unicas": resultado["resumen"]["sugerencias_unicas"]})

    manifiesto = {
        "run_id": run_id, "tema": tema, "inicio_utc": consulta["generado_utc"],
        "fin_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "reglas_usadas": reglas,
        "conteos": {"pedidos_autocompletar": len(registros), "sugerencias_validas": len(validas),
                    "sugerencias_rechazadas": len(rechazadas),
                    "sugerencias_unicas": resultado["resumen"]["sugerencias_unicas"],
                    "paginas_top10": len(top10), "top10_validas": resultado["resumen"]["top10_validos"]},
        "crudo": str(dir_raw.relative_to(dir_raw.parents[2])),
        "salida": str(ruta.relative_to(ruta.parents[3])),
    }
    DIR_MANIFESTS.mkdir(exist_ok=True)
    (DIR_MANIFESTS / f"run_{run_id}.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=1) + "\n",
                                                      encoding="utf-8")
    log.info("Listo: %s · %s sugerencias únicas · manifiesto manifests/run_%s.json",
             manifiesto["salida"], resultado["resumen"]["sugerencias_unicas"], run_id)
    return consulta


def _contar(valores) -> dict:
    conteo: dict[str, int] = {}
    for v in valores:
        conteo[v] = conteo.get(v, 0) + 1
    return dict(sorted(conteo.items(), key=lambda kv: -kv[1]))


if __name__ == "__main__":
    configurar_log()
    tema_arg = " ".join(sys.argv[1:]).strip() or os.environ.get("TEMA", "")
    if not tema_arg:
        sys.exit('Falta el tema. Ejemplo: python colector/run.py "ciencia de datos"')
    try:
        correr(tema_arg)
    except ValueError as e:
        log.error("%s", e)
        sys.exit(2)
