"""El estado del loop (docs/data/loop.json) y el plan (PLAN.md) tienen que hablar de las mismas fases."""
import json
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


class PlanYLoop(unittest.TestCase):
    def test_mismas_fases_en_el_plan_y_en_el_estado(self):
        loop = json.loads((RAIZ / "docs/data/loop.json").read_text(encoding="utf-8"))
        plan = (RAIZ / "PLAN.md").read_text(encoding="utf-8")
        en_plan = re.findall(r"^\| (F\d+) \|", plan, flags=re.M)
        self.assertEqual([f["id"] for f in loop["fases"]], en_plan)

    def test_una_fase_hecha_siempre_tiene_evidencia(self):
        loop = json.loads((RAIZ / "docs/data/loop.json").read_text(encoding="utf-8"))
        for f in loop["fases"]:
            if f["estado"] == "hecho":
                self.assertTrue(f["evidencia"].strip(), f"{f['id']} está hecha sin evidencia")

    def test_el_mapa_apunta_a_archivos_que_existen(self):
        mapa = json.loads((RAIZ / "docs/data/mapa.json").read_text(encoding="utf-8"))
        for rama in mapa["ramas"]:
            for nodo in rama["nodos"]:
                if "donde" in nodo:
                    self.assertTrue((RAIZ / nodo["donde"]).exists(), f"{nodo['id']}: no existe {nodo['donde']}")


if __name__ == "__main__":
    unittest.main()
