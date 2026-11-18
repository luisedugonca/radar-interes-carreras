"""Vuelve a validar y transformar las consultas guardadas a partir de su crudo, sin pedir nada a Google.

Sirve cuando cambian las reglas o el cálculo: la corrida (run_id, fecha, crudo) no cambia; el JSON de la
consulta se rehace y el manifiesto anota el reproceso. Es la prueba de que todo número sale del crudo.

Uso: python3 colector/reprocesar.py            (todas las consultas del índice)
     python3 colector/reprocesar.py <slug> ...  (solo esas)
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

import transformar
import validar
from comun import DIR_CONSULTAS, DIR_MANIFESTS, DIR_RAW, RUTA_INDICE, cargar_reglas
from run import armar_consulta


def reprocesar(entrada: dict, reglas: dict, motivo: str) -> dict:
    vieja = json.loads((DIR_CONSULTAS / f"{entrada['slug']}.json").read_text(encoding="utf-8"))
    crudo = DIR_RAW / vieja["run_id"] / "sugerencias.jsonl"
    registros = [json.loads(l) for l in crudo.read_text(encoding="utf-8").splitlines() if l.strip()]
    validas, rechazadas = validar.validar_sugerencias(registros, vieja["tema"], reglas)
    top10 = validar.validar_top10(vieja["top10"], vieja["tema"], reglas)
    resultado = transformar.transformar(validas, top10, vieja["tema"], reglas)
    nueva = armar_consulta(vieja["tema"], vieja["run_id"], vieja["generado_utc"], reglas, registros, rechazadas, top10, resultado)
    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    nueva["reprocesado_utc"] = ahora
    (DIR_CONSULTAS / f"{entrada['slug']}.json").write_text(json.dumps(nueva, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    ruta_m = DIR_MANIFESTS / f"run_{vieja['run_id']}.json"
    manifiesto = json.loads(ruta_m.read_text(encoding="utf-8"))
    manifiesto.setdefault("reprocesos", []).append({
        "utc": ahora, "reglas_version": reglas["version"], "motivo": motivo,
        "sugerencias_unicas_antes": vieja["resumen"]["sugerencias_unicas"],
        "sugerencias_unicas_despues": nueva["resumen"]["sugerencias_unicas"]})
    ruta_m.write_text(json.dumps(manifiesto, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return nueva


if __name__ == "__main__":
    reglas = cargar_reglas()
    indice = json.loads(RUTA_INDICE.read_text(encoding="utf-8"))
    pedidos = set(sys.argv[1:])
    for e in indice["consultas"]:
        if pedidos and e["slug"] not in pedidos:
            continue
        n = reprocesar(e, reglas, "se agrega el puesto de cada frase en la lista de sugerencias")
        print(f"{e['slug']}: {e['sugerencias_unicas']} -> {n['resumen']['sugerencias_unicas']} frases")
