"""GEO · indicadores de respuestas de ChatGPT y Gemini guardadas → docs/data/geo/

Lee las respuestas guardadas (una por archivo JSON) y cuenta, solo con reglas
(docs/data/geo/reglas_geo.json), qué instituciones y términos nombran, en qué orden y qué páginas citan.
No publica el texto de las respuestas: solo conteos, la pregunta y los dominios citados.

Uso: python3 colector/geo_indicadores.py <carpeta_de_respuestas> <preguntas.json>
     (hoy: ../ucu_salto/geo/snapshots y ../ucu_salto/geo/prompts_fase3.json)
Salida: docs/data/geo/respuestas.csv (una fila por respuesta) y docs/data/geo/indicadores.json
"""
from __future__ import annotations

import ast
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

from comun import RAIZ

DIR = RAIZ / "docs" / "data" / "geo"
UY = ZoneInfo("America/Montevideo")
IAS = ("ChatGPT", "Gemini")


def leer(path: Path, preguntas: dict) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    ia = "ChatGPT" if "chatgpt" in path.parent.name.lower() else "Gemini"
    crudo = d.get("respuesta") or d.get("texto") or ""
    pid = d.get("id") or path.stem
    pregunta = d.get("prompt") or preguntas.get(pid, {}).get("texto", "")
    if not pregunta:  # pruebas piloto: la pregunta quedó al principio del texto
        m = re.search(r"Dijiste:\s*(.+?)\s*ChatGPT dijo:", crudo, re.S)
        pregunta = m.group(1).strip() if m else ""
    # Contar solo lo que dice la IA: se quita el eco de la pregunta
    texto = crudo.split("dijo:", 1)[-1] if "dijo:" in crudo else crudo
    if pregunta:
        texto = texto.replace(pregunta, " ")
    links = d.get("links", [])
    if isinstance(links, str):
        try:
            links = ast.literal_eval(links)
        except (ValueError, SyntaxError):
            links = re.findall(r"https?://[^\s'\"\]]+", links)
    fecha = datetime.fromisoformat(d["fecha"].replace("Z", "+00:00")) if d.get("fecha") else None
    return {"archivo": path, "ia": ia, "fecha": fecha, "dia": path.parent.parent.name, "id": pid, "pregunta": pregunta,
            "piloto": pid.startswith("p0"), "texto": texto, "links": [u for u in links if str(u).startswith("http")],
            "login": str(d.get("login", "False")), "modelo": d.get("modelo_visible") or "no visible"}


def contar(r: dict, reglas: dict) -> dict:
    t = r["texto"]
    inst = {i["id"]: len(re.findall(i["patron"], t)) for i in reglas["instituciones"]}
    term = {x["id"]: len(re.findall(x["patron"], t, re.I)) for x in reglas["terminos"]}
    err = {x["id"]: bool(re.search(x["patron"], t, re.I)) for x in reglas["errores_conocidos"]}
    primeras = {i["id"]: m.start() for i in reglas["instituciones"] if (m := re.search(i["patron"], t))}
    orden = sorted(primeras, key=primeras.get)
    dominios = sorted({re.sub(r"^www\.", "", urlparse(u).netloc) for u in r["links"] if not re.search(reglas["dominios_ignorados"], u)})
    return {"inst": inst, "term": term, "err": err, "orden": orden, "dominios": dominios,
            "pregunta_nombra_ucu": bool(re.search(r"UCU|Cat[oó]lica", r["pregunta"]))}


def resumen_por(filas, clave, ids):
    salida = []
    for i in ids:
        x = {"id": i, "por_ia": {}}
        for ia in (*IAS, "total"):
            sub = [f for f in filas if ia == "total" or f["ia"] == ia]
            n = sum(1 for f in sub if f[clave][i] > 0)
            x["por_ia"][ia] = {"respuestas": n, "de": len(sub), "pct": round(100 * n / len(sub), 1) if sub else 0,
                               "veces": sum(f[clave][i] for f in sub)}
        salida.append(x)
    return sorted(salida, key=lambda x: -x["por_ia"]["total"]["respuestas"])


def main(carpeta: Path, ruta_preguntas: Path) -> None:
    reglas = json.loads((DIR / "reglas_geo.json").read_text(encoding="utf-8"))
    preguntas = {p["id"]: p for p in json.loads(ruta_preguntas.read_text(encoding="utf-8"))["prompts"]}
    filas = []
    for path in sorted(carpeta.glob("*/*/*.json")):
        r = leer(path, preguntas)
        filas.append({**r, **contar(r, reglas)})

    # Temporalidad: días, horas en Uruguay y condiciones de captura
    dias = []
    for dia in sorted({f["dia"] for f in filas}):
        sub = [f for f in filas if f["dia"] == dia and f["fecha"]]
        horas = sorted(f["fecha"].astimezone(UY) for f in sub)
        dias.append({"fecha": dia, "desde_uy": horas[0].strftime("%H:%M"), "hasta_uy": horas[-1].strftime("%H:%M"),
                     "respuestas": {ia: sum(1 for f in sub if f["ia"] == ia) for ia in IAS}})

    def puesto(ia):
        p = [f["orden"].index("UCU") + 1 for f in filas if (ia == "total" or f["ia"] == ia) and "UCU" in f["orden"]]
        return {"aparece": len(p), "primera": p.count(1), "promedio": round(sum(p) / len(p), 1) if p else None}

    sin_ucu = [f for f in filas if not f["pregunta_nombra_ucu"]]
    dom = {}
    for f in filas:
        for d in f["dominios"]:
            dom.setdefault(d, {"dominio": d, "ChatGPT": 0, "Gemini": 0, "total": 0})
            dom[d][f["ia"]] += 1
            dom[d]["total"] += 1
    ids_preg = list(dict.fromkeys(f["id"] for f in filas))
    indicadores = {
        "generado_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "reglas_version": reglas["version"],
        "fuente": "Respuestas de ChatGPT y Gemini guardadas a mano (texto completo y enlaces) en el proyecto UCU Salto. Conteo por reglas, sin IA.",
        "temporalidad": {
            "tipo": "foto",
            "desde": dias[0]["fecha"], "hasta": dias[-1]["fecha"], "dias": dias,
            "frecuencia": "Sin frecuencia: dos días de captura. No muestra tendencia.",
            "hacia_atras": "ChatGPT y Gemini no guardan un historial público: solo se puede medir desde el día en que se empieza.",
            "condiciones": [
                "Sin iniciar sesión en ninguna de las dos IA.",
                f"ChatGPT: modelo {'no visible' if all(f['modelo'] == 'no visible' for f in filas if f['ia'] == 'ChatGPT') else 'variable'}.",
                "Gemini: «Flash-Lite», el modelo que ofrece sin sesión.",
                "Cada pregunta se hizo una vez por día.",
            ],
        },
        "totales": {ia: sum(1 for f in filas if f["ia"] == ia) for ia in IAS} | {"total": len(filas)},
        "instituciones": resumen_por(filas, "inst", [i["id"] for i in reglas["instituciones"]]),
        "terminos": [{**x, "nombre": next(t["nombre"] for t in reglas["terminos"] if t["id"] == x["id"])}
                     for x in resumen_por(filas, "term", [t["id"] for t in reglas["terminos"]])],
        "ucu_puesto": {ia: puesto(ia) for ia in (*IAS, "total")},
        "ucu_sin_nombrarla_en_la_pregunta": {"respuestas": len(sin_ucu), "nombran_ucu": sum(1 for f in sin_ucu if f["inst"]["UCU"])},
        "errores": [{"id": e["id"], "nombre": e["nombre"], **{ia: sum(1 for f in filas if (ia == "total" or f["ia"] == ia) and f["err"][e["id"]]) for ia in (*IAS, "total")}}
                    for e in reglas["errores_conocidos"]],
        "dominios": sorted(dom.values(), key=lambda d: (-d["total"], d["dominio"]))[:12],
        "dominios_nota": [f"En las respuestas guardadas de {ia} no quedó ningún enlace: no se sabe si no citó páginas o si la captura no las tomó."
                          for ia in IAS if not any(f["links"] for f in filas if f["ia"] == ia)],
        # Conteos de cada respuesta, sin el texto: la web filtra por IA, día y pregunta con esto
        "respuestas": [{"ia": f["ia"], "dia": f["dia"], "pregunta": f["id"], "pregunta_nombra_ucu": f["pregunta_nombra_ucu"],
                        "inst": f["inst"], "term": f["term"], "orden": f["orden"], "dominios": f["dominios"],
                        "errores": [k for k, v in f["err"].items() if v]} for f in filas],
        "colores": {"instituciones": {"UCU": "#4f8dff", "Udelar": "#3ccf91", "UTEC": "#f2b03d", "ORT": "#f07f4f", "UM": "#a78bfa",
                                      "UTU": "#35c9d6", "UDE": "#ff6fa3", "CLAEH": "#c9d451"}},
        "terminos_def": [{"id": t["id"], "nombre": t["nombre"]} for t in reglas["terminos"]],
        "preguntas": [{"id": i, "texto": next(f["pregunta"] for f in filas if f["id"] == i), "piloto": i.startswith("p0"),
                       "nombra_ucu": next(f["pregunta_nombra_ucu"] for f in filas if f["id"] == i),
                       "perfil": preguntas.get(i, {}).get("perfil", "piloto")} for i in ids_preg],
    }
    DIR.mkdir(parents=True, exist_ok=True)
    (DIR / "indicadores.json").write_text(json.dumps(indicadores, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    cols = ["dia", "fecha_uy", "ia", "modelo", "pregunta_id", "pregunta", "pregunta_nombra_ucu", "orden_instituciones", "puesto_ucu", "dominios_citados"] \
        + [f"veces_{i['id']}" for i in reglas["instituciones"]] + [f"veces_{t['id']}" for t in reglas["terminos"]] + [e["id"] for e in reglas["errores_conocidos"]]
    with (DIR / "respuestas.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for f in filas:
            w.writerow([f["dia"], f["fecha"].astimezone(UY).strftime("%Y-%m-%d %H:%M") if f["fecha"] else "", f["ia"], f["modelo"], f["id"], f["pregunta"],
                        "si" if f["pregunta_nombra_ucu"] else "no", " > ".join(f["orden"]),
                        f["orden"].index("UCU") + 1 if "UCU" in f["orden"] else "", " | ".join(f["dominios"])]
                       + [f["inst"][i["id"]] for i in reglas["instituciones"]] + [f["term"][t["id"]] for t in reglas["terminos"]]
                       + ["si" if f["err"][e["id"]] else "no" for e in reglas["errores_conocidos"]])
    print(f"{len(filas)} respuestas · {indicadores['totales']} · días {[d['fecha'] for d in dias]}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(Path(sys.argv[1]), Path(sys.argv[2]))
