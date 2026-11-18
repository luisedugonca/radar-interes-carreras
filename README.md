# Radar de interés por carreras

Una herramienta para responder, sin pagar datos, una pregunta de oferta académica:

> **¿Qué busca la gente sobre este tema, y con qué palabras?**

Sirve para decidir cómo nombrar una carrera nueva, qué dudas tiene que responder su página y con qué temas conviene combinarla. Es un proyecto del Taller Integrador (UCU), de Luis Gonçalvez y Victoria Illa.

**Verla funcionando:** https://luisedugonca.github.io/radar-interes-carreras/ — el mapa de cómo trabajamos y el radar, sin instalar nada.

**Usarla desde un chat** (Claude, ChatGPT o Gemini): [`chat/README.md`](chat/README.md).

## Qué hace

1. **Mide.** Para un tema (por ejemplo «analista de datos»), pregunta al autocompletar de Google y de YouTube qué frases propone, con 46 consultas distintas: el tema solo, con cada letra del abecedario, como pregunta, y con dudas típicas de estudiantes y de familias.
2. **Ordena.** Agrupa las frases por tipo de duda: costo, becas, salida laboral, modalidad, plan y requisitos, dónde estudiar, tipo de formación, temas con los que se combina. Aparta las que hablan de otros países.
3. **Muestra.** Una web con un mapa interactivo, indicadores, una lista de términos candidatos y un pedido listo para pegar en un chat de IA.

## Qué NO hace

- **No dice cuánta gente busca.** Cuenta frases distintas, no búsquedas. Para cantidades hace falta otra fuente.
- **No trae el top 10 de buscadores todavía.** Leer la página de un buscador con un script no es confiable (lo probamos: ver `revisiones/REGISTRO.md`). La web abre cada buscador con el tema cargado, en un clic. El top 10 automático es la fase F5 del plan.
- **No sabe quién busca.** «Estudiante» o «familia» es una lectura nuestra, marcada como Supuesto.

## Usarla

**Ver la web en tu computadora**

```bash
python3 -m http.server 8000 --directory docs
# abrir http://localhost:8000
```

- **En las IA** (`ia.html`, la página de inicio): qué contestan ChatGPT y Gemini; hoy, una foto de oct-2026.
- **Mapa agéntico** (`mapa.html`): cómo trabajamos y en qué fase está el plan.
- **Radar de interés** (`radar.html`): elegí una consulta guardada o escribí un tema nuevo y tocá «Explorar en vivo».

**La base de datos** es un CSV: [`docs/data/base.csv`](docs/data/base.csv), una fila por frase de cada tema guardado. Se regenera sola cada vez que se guarda un tema y se abre en Excel. Desde la web, «⬇ Descargar CSV» baja el tema que estás mirando (también uno medido en vivo) y «⬆ Abrir CSV» lo vuelve a cargar.

**Guardar un tema nuevo** (queda con su crudo, su manifiesto, en la base y en la web)

- En GitHub: pestaña *Actions* → *Consulta de interés* → *Run workflow* → escribir el tema.
- O abrir un issue con el título `Consulta: <tema>`.
- O en tu computadora: `python3 colector/run.py "gestión agropecuaria"`.
- Sola, cada lunes a las 8:00 (hora de Uruguay): GitHub vuelve a medir todos los temas guardados y suma un punto a la evolución de cada uno. También se puede lanzar a mano: *Actions → Consulta de interés → Run workflow* con el tema vacío.

**Llevarlo a un chat de IA**

En el radar, sección 4, «Copiar pedido para el chat». Pegalo en Claude, ChatGPT o Gemini. Para dejar un chat armado y compartible (un artefacto de Claude, un GPT o un Gem), seguí [`chat/README.md`](chat/README.md).

**Trabajar en el repositorio con un agente de IA**

Las reglas están en `CLAUDE.md` y valen para cualquier agente. `AGENTS.md` y `GEMINI.md` apuntan ahí, para Codex, ChatGPT, Cursor y Gemini.

## Cómo está hecho

```
Fuente → Extracción → Registro del crudo → Validación → Transformación → Carga → Consulta → Web
```

| Etapa | Archivo | Qué deja |
|---|---|---|
| Extraer y registrar | `colector/extraer.py` | `data/raw/<corrida>/sugerencias.jsonl.gz` (cada respuesta, tal cual llegó, comprimida) |
| Historial | `colector/historial.py` | `docs/data/historial/<tema>/`: cada medición comprimida y `serie.json` para el gráfico de evolución |
| Validar | `colector/validar.py` | Válidas y rechazadas, cada rechazo con su motivo |
| Transformar | `colector/transformar.py` | Frases únicas, con apariciones y tipo de duda |
| Orquestar y cargar | `colector/run.py` | `docs/data/consultas/<tema>.json`, `manifests/run_<corrida>.json` |
| Base | `colector/base_csv.py` | `docs/data/base.csv`, una fila por frase de cada tema |
| Reprocesar | `colector/reprocesar.py` | Rehace los temas desde el crudo, sin pedir nada a Google |
| Reglas | `docs/data/reglas.json` | Semillas y patrones; las usan Python y la web |
| Mostrar | `docs/ia.html`, `docs/radar.html`, `docs/mapa.html` | Solo leen JSON; ningún número escrito a mano |

- **Idempotencia:** la misma frase encontrada por tres consultas es una sola fila con «3 apariciones» (prueba en `tests/test_colector.py`).
- **Linaje:** cada número de la web lleva fuente, fecha y corrida, con enlace al crudo y al manifiesto.
- **Pruebas:** `python3 -m unittest discover -s tests -v`. Corren en GitHub antes de guardar cualquier dato.

## Cómo trabajamos

El repositorio sigue el método «PO agéntico»: una persona decide, los agentes ejecutan, y todo lo que importa queda escrito.

- `PLAN.md` — objetivo, métrica de éxito, fases con su «hecho cuando» y lo que solo decide el PO.
- `docs/data/loop.json` — en qué fase estamos (la web lo muestra).
- `CLAUDE.md` — reglas y niveles de aprobación para los agentes.
- `revisiones/REGISTRO.md` — revisiones, correcciones y fuentes descartadas, con evidencia.
- `sesiones/hilo-radar.md` — qué quedó hecho y el próximo paso.
