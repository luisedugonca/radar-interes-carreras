"""Chequeos estáticos de la web (docs/): que no se rompa por caché ni por archivos que faltan.

Corren en GitHub Actions antes de guardar datos, igual que las demás pruebas.
"""
import re
import unittest
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
PAGINAS = ["ia.html", "radar.html", "mapa.html"]


class Web(unittest.TestCase):
    def test_una_sola_version_en_todos_los_scripts_y_estilos(self):
        # Si la página pide un script nuevo y el navegador usa uno viejo de la caché, la parte
        # interactiva deja de funcionar sin avisar. Todas las referencias llevan la misma versión.
        versiones = set()
        for archivo in [*PAGINAS, *[p.name for p in (DOCS / "assets").glob("*.js")]]:
            ruta = DOCS / archivo if (DOCS / archivo).exists() else DOCS / "assets" / archivo
            texto = ruta.read_text(encoding="utf-8")
            for ref in re.findall(r'(?:from|src=|href=)\s*"(\.?/?(?:assets/)?[\w-]+\.(?:js|css))(\?v=[\w]+)?"', texto):
                self.assertTrue(ref[1], f"{archivo}: {ref[0]} sin número de versión")
                versiones.add(ref[1])
        self.assertEqual(len(versiones), 1, f"versiones mezcladas: {versiones}")

    def test_cada_pagina_tiene_icono_y_metadatos_para_buscadores(self):
        import json
        for pagina in [*PAGINAS, "index.html"]:
            texto = (DOCS / pagina).read_text(encoding="utf-8")
            for etiqueta in ('name="description"', 'rel="canonical"', 'property="og:image"', 'name="twitter:card"', 'rel="icon"', 'rel="manifest"'):
                self.assertIn(etiqueta, texto, f"{pagina}: falta {etiqueta}")
            for ref in re.findall(r'(?:href|content)="(?:https://luisedugonca\.github\.io/radar-interes-carreras/)?((?:assets/)[\w.-]+\.(?:svg|png|jpg)|site\.webmanifest)"', texto):
                self.assertTrue((DOCS / ref).exists(), f"{pagina} pide {ref}, que no existe")
            ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', texto, re.S)
            self.assertTrue(ld, f"{pagina}: sin schema.org")
            json.loads(ld.group(1))

    def test_lo_que_piden_las_paginas_existe(self):
        for pagina in PAGINAS:
            texto = (DOCS / pagina).read_text(encoding="utf-8")
            pedidos = re.findall(r'"((?:\./)?(?:assets|data)/[\w/.-]+?\.(?:js|css|json|md|csv))(?:\?v=\w+)?"', texto)
            pedidos += [p for p in re.findall(r'href="([\w-]+\.html)', texto)]
            for p in pedidos:
                self.assertTrue((DOCS / p.lstrip("./")).exists(), f"{pagina} pide {p}, que no existe")

    def test_ningun_esqueleto_sin_reemplazo(self):
        # Todo contenedor con esqueleto tiene que tener un id que el script vuelve a pintar
        for pagina in PAGINAS:
            texto = (DOCS / pagina).read_text(encoding="utf-8")
            html, script = texto.split("<script type=\"module\">", 1)
            # El contenedor de cada esqueleto es el elemento con id más cercano antes de él
            ids = set(re.findall(r'id="([\w-]+)"(?:(?!id=")[\s\S])*?\besq\b', html))
            for id_ in ids:
                if not re.search(rf'\$\("{id_}"\)|getElementById\("{id_}"\)', script):
                    self.fail(f"{pagina}: #{id_} tiene esqueleto y el script no lo pinta")


if __name__ == "__main__":
    unittest.main()
