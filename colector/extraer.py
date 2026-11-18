"""Etapa 1-2 · Extracción y registro del crudo.

Fuentes gratuitas, sin clave:
  - Autocompletar de Google (suggestqueries.google.com, client=chrome)
  - Autocompletar de YouTube (mismo servicio, ds=yt)

Cada respuesta se guarda tal cual llega, antes de interpretarla.

El top 10 de buscadores NO se extrae acá todavía. El 2026-11-16 se probó leer la página de
resultados con un script: DuckDuckGo y Brave bloquean (HTTP 202 / 429) y Bing responde 200 con
resultados sin relación con la consulta. La vía correcta es una API oficial con clave gratuita
(fase F5 de PLAN.md, pendiente de decisión del PO). Ver extraer_top10().
"""
from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

log = logging.getLogger("extraer")

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
URL_SUGERENCIAS = "https://suggestqueries.google.com/complete/search"


def _get(url: str, intentos: int = 2, espera: float = 2.0) -> tuple[int, bytes]:
    ultimo = (0, b"")
    for intento in range(1, intentos + 1):
        pedido = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es-UY,es;q=0.9"})
        try:
            with urllib.request.urlopen(pedido, timeout=20) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            ultimo = (e.code, b"")
            log.warning("HTTP %s en %s (intento %s/%s)", e.code, url, intento, intentos)
        except (urllib.error.URLError, TimeoutError) as e:
            log.warning("Sin respuesta de %s: %s (intento %s/%s)", url, e, intento, intentos)
        if intento < intentos:
            time.sleep(espera)
    return ultimo


def armar_semillas(tema: str, reglas: dict) -> list[dict]:
    """Lista de consultas a pedir, cada una con su grupo (de dónde sale) y su fuente."""
    s = reglas["semillas"]
    semillas = []
    for grupo in ("base", "preguntas", "estudiante", "familia"):
        for plantilla in s[grupo]:
            semillas.append({"grupo": grupo, "fuente": "google", "consulta": plantilla.format(tema=tema)})
    for letra in s["alfabeto"]:
        semillas.append({"grupo": "alfabeto", "fuente": "google", "consulta": f"{tema} {letra}"})
    for plantilla in s["youtube"]:
        semillas.append({"grupo": "youtube", "fuente": "youtube", "consulta": plantilla.format(tema=tema)})
    return semillas


def extraer_sugerencias(tema: str, reglas: dict, dir_raw: Path, pausa: float = 0.25) -> list[dict]:
    """Pide el autocompletar de cada semilla y guarda una línea por pedido en sugerencias.jsonl (run.py lo comprime al final)."""
    pais = reglas["pais"]
    registros = []
    ruta = dir_raw / "sugerencias.jsonl"
    with ruta.open("w", encoding="utf-8") as f:
        for semilla in armar_semillas(tema, reglas):
            params = {"client": "chrome", "hl": pais["hl"], "gl": pais["gl"],
                      "ie": "utf-8", "oe": "utf-8", "q": semilla["consulta"]}
            if semilla["fuente"] == "youtube":
                params["ds"] = "yt"
            url = URL_SUGERENCIAS + "?" + urllib.parse.urlencode(params)
            estado, cuerpo = _get(url)
            registro = {**semilla, "url": url, "http": estado, "cuerpo": cuerpo.decode("utf-8", errors="replace")}
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")
            registros.append(registro)
            time.sleep(pausa)
    ok = sum(1 for r in registros if r["http"] == 200)
    log.info("Autocompletar: %s pedidos, %s con respuesta 200 -> %s", len(registros), ok, ruta)
    return registros


def extraer_top10(tema: str) -> list[dict]:
    """Todavía sin fuente automática: devuelve las dos consultas como 'pendiente', con el motivo.

    F5 reemplaza el cuerpo de esta función por la llamada a la API oficial que elija el PO.
    Lo que devuelva pasa igual por validar.validar_top10().
    """
    motivo = ("sin fuente automática: leer la página de un buscador con un script no es confiable "
              "(probado el 2026-11-16). Falta elegir una API oficial con clave gratuita (PLAN.md, fase F5).")
    return [{"buscador": "pendiente", "consulta": c, "estado": "pendiente", "motivo": motivo, "resultados": None}
            for c in (tema, f"{tema} carrera uruguay")]
