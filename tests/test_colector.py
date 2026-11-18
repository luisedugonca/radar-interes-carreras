"""Pruebas del colector. Correr: python3 -m unittest discover -s tests -v"""
import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "colector"))

import comun  # noqa: E402
import transformar  # noqa: E402
import validar  # noqa: E402

REGLAS = comun.cargar_reglas()


def registro(consulta, textos, tipos=None, http=200):
    extra = {"google:suggesttype": tipos or ["QUERY"] * len(textos)}
    return {"consulta": consulta, "grupo": "base", "fuente": "google", "http": http,
            "cuerpo": json.dumps([consulta, textos, [], [], extra])}


class Tema(unittest.TestCase):
    def test_limpia_el_prefijo_del_issue_y_los_simbolos(self):
        self.assertEqual(comun.limpiar_tema("Consulta:  Ciencia de Datos; rm -rf $(x)"), "ciencia de datos rm -rf x")

    def test_rechaza_un_tema_vacio_o_enorme(self):
        for malo in ("", "a", "x" * 80):
            with self.assertRaises(ValueError):
                comun.limpiar_tema(malo)

    def test_slug_sin_tildes(self):
        self.assertEqual(comun.slug("Gestión Agropecuaria"), "gestion-agropecuaria")


class Sugerencias(unittest.TestCase):
    def test_separa_validas_de_rechazadas_con_motivo(self):
        regs = [registro("ciencia de datos", ["ciencia de datos udelar", "costo de vida", "", "ciencia.com"],
                         ["QUERY", "QUERY", "QUERY", "NAVIGATION"]),
                registro("ciencia de datos z", [], http=429)]
        validas, rechazadas = validar.validar_sugerencias(regs, "ciencia de datos", REGLAS)
        self.assertEqual([v["texto"] for v in validas], ["ciencia de datos udelar"])
        self.assertEqual(sorted(r["motivo"] for r in rechazadas),
                         sorted(["no nombra el tema", "texto vacío", "no es una búsqueda (tipo NAVIGATION)",
                                 "el pedido falló (HTTP 429)"]))

    def test_idempotencia_la_misma_sugerencia_en_tres_consultas_es_una_fila(self):
        validas = [{"texto": t, "semilla": s, "grupo": "base", "fuente": "google", "relevancia": 600}
                   for t, s in (("Ciencia de datos UCU", "a"), ("ciencia de datos ucu", "b"),
                                ("ciencia de datos ucu", "b"), ("ciencia de datos ucu", "c"))]
        r = transformar.transformar(validas, [], "ciencia de datos", REGLAS)
        self.assertEqual(r["resumen"]["sugerencias_unicas"], 1)
        donde = next(i for i in r["intenciones"] if i["id"] == "donde")
        self.assertEqual(donde["sugerencias"][0]["apariciones"], 3)
        self.assertEqual(donde["sugerencias"][0]["instituciones"], ["UCU"])

    def test_puesto_en_la_lista_de_sugerencias(self):
        regs = [registro("ciencia de datos", ["ciencia de datos ucu", "ciencia de datos udelar"]),
                registro("ciencia de datos u", ["ciencia de datos udelar", "x", "ciencia de datos ucu"] + [f"ciencia de datos u{i}" for i in range(9)] + ["ciencia de datos ucu"])]
        validas, _ = validar.validar_sugerencias(regs, "ciencia de datos", REGLAS)
        r = transformar.transformar(validas, [], "ciencia de datos", REGLAS)
        frases = {s["texto"]: s for i in r["intenciones"] for s in i["sugerencias"]}
        ucu, udelar = frases["ciencia de datos ucu"], frases["ciencia de datos udelar"]
        # ucu: puesto 1 en la primera consulta y 3 en la segunda (la repetición en el puesto 13 no cuenta)
        self.assertEqual((ucu["apariciones"], ucu["pos_promedio"], ucu["pos_mejor"], ucu["veces_top3"], ucu["veces_top10"]), (2, 2.0, 1, 2, 2))
        self.assertEqual((udelar["pos_promedio"], udelar["veces_top3"]), (1.5, 2))
        donde = next(i for i in r["intenciones"] if i["id"] == "donde")
        self.assertEqual([s["texto"] for s in donde["sugerencias"][:2]], ["ciencia de datos udelar", "ciencia de datos ucu"])
        self.assertEqual(donde["apariciones_total"], sum(s["apariciones"] for s in donde["sugerencias"]))

    def test_clasifica_por_lo_que_agrega_al_tema(self):
        casos = {"ciencia de datos becas": "becas", "ciencia de datos cuanto cuesta": "costo",
                 "ciencia de datos salida laboral": "salida", "ciencia de datos a distancia": "modalidad",
                 "ciencia de datos uba": "fuera_uy", "ciencia de datos para negocios": "temas",
                 "ciencia de datos rentables": "emprender", "ciencia de datos zzz": "otros"}
        for texto, esperada in casos.items():
            resto = texto.replace("ciencia de datos", " ")
            self.assertEqual(transformar.clasificar(resto, REGLAS), esperada, texto)


class BaseCSV(unittest.TestCase):
    def test_una_fila_por_frase_con_todas_las_columnas(self):
        import base_csv
        c = {"tema": "x y", "slug": "x-y", "run_id": "r", "generado_utc": "t", "pais": "Uruguay",
             "fuentes": [{"con_respuesta": 40}, {"con_respuesta": 3}],
             "intenciones": [{"id": "costo", "nombre": "Costo", "sugerencias": [
                 {"texto": "x y gratis", "apariciones": 2, "pos_promedio": 3.5, "pos_mejor": 2, "veces_top3": 1,
                  "veces_top10": 2, "instituciones": [], "fuentes": ["google", "youtube"]}]},
                             {"id": "otros", "nombre": "Otros", "sugerencias": []}]}
        f = base_csv.filas(c)
        self.assertEqual(len(f), 1)
        self.assertEqual(list(f[0]), base_csv.COLUMNAS)
        self.assertEqual((f[0]["consultas_respondidas"], f[0]["fuentes"]), (43, "google|youtube"))


class Historial(unittest.TestCase):
    def test_registrar_dos_veces_la_misma_corrida_no_duplica(self):
        import gzip
        import tempfile
        from pathlib import Path
        import historial
        c = {"tema": "x y", "slug": "x-y", "run_id": "r1", "generado_utc": "2026-11-16T00:00:00Z",
             "fuentes": [{"con_respuesta": 46}],
             "intenciones": [{"id": "costo", "nombre": "Costo", "total": 1, "apariciones_total": 2, "sugerencias": [
                 {"texto": "x y gratis", "apariciones": 2, "pos_promedio": 1.5, "veces_top3": 2, "instituciones": ["UCU"]}]}]}
        with tempfile.TemporaryDirectory() as tmp:
            antes, historial.DIR = historial.DIR, Path(tmp)
            try:
                self.assertEqual(historial.registrar(c), 1)
                self.assertEqual(historial.registrar(c), 1)
                self.assertEqual(historial.registrar({**c, "run_id": "r2", "generado_utc": "2026-11-23T00:00:00Z"}), 2)
                serie = json.loads((Path(tmp) / "x-y" / "serie.json").read_text(encoding="utf-8"))
                self.assertEqual([m["run_id"] for m in serie["mediciones"]], ["r1", "r2"])
                self.assertEqual(serie["mediciones"][0]["instituciones"], {"UCU": 1})
                vuelta = json.loads(gzip.decompress((Path(tmp) / "x-y" / "r1.json.gz").read_bytes()))
                self.assertEqual(vuelta["run_id"], "r1")
            finally:
                historial.DIR = antes


class Top10(unittest.TestCase):
    def test_rechaza_el_caso_real_de_bing_sin_relacion(self):
        caso = json.loads((RAIZ / "tests/fixtures/bing_sin_relacion_20261116.json").read_text(encoding="utf-8"))
        pagina = {"buscador": "bing", "consulta": caso["consulta"], "estado": "ok", "resultados": caso["resultados"]}
        salida = validar.validar_top10([pagina], caso["consulta"], REGLAS)[0]
        self.assertEqual(salida["estado"], "rechazado")
        self.assertIn("sin relación", salida["motivo"])
        self.assertEqual(salida["resultados"], [])

    def test_acepta_resultados_que_hablan_del_tema(self):
        res = [{"titulo": f"Carrera de Ciencia de Datos {i}", "url": f"https://ejemplo{i}.edu.uy/datos"} for i in range(10)]
        salida = validar.validar_top10([{"buscador": "x", "consulta": "ciencia de datos", "resultados": res}],
                                       "ciencia de datos", REGLAS)[0]
        self.assertEqual(salida["estado"], "ok")
        self.assertEqual([r["pos"] for r in salida["resultados"]], list(range(1, 11)))

    def test_pendiente_pasa_sin_inventar_resultados(self):
        salida = validar.validar_top10([{"buscador": "pendiente", "consulta": "x", "estado": "pendiente",
                                         "motivo": "falta fuente", "resultados": None}], "x y z", REGLAS)[0]
        self.assertEqual((salida["estado"], salida["resultados"]), ("pendiente", []))


if __name__ == "__main__":
    unittest.main()
