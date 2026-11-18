# Instrucciones para agentes de IA (cualquier herramienta)

Este archivo lo leen los agentes que siguen la convención `AGENTS.md` (Codex y ChatGPT con acceso al repo, Cursor, Gemini CLI y otros). Claude Code lee `CLAUDE.md`; Gemini CLI también lee `GEMINI.md`. **Las reglas son las mismas para todos y viven en un solo lugar: [`CLAUDE.md`](CLAUDE.md).** Leelo completo antes de tocar nada.

## Lo mínimo, por si no podés abrir otro archivo

1. **Nunca inventes una salida.** Todo ejemplo sale de una corrida real del colector.
2. **Solo fuentes públicas y gratuitas.** Nada de datos pagos ni de datos internos de la universidad.
3. **«Apariciones» no es cantidad de búsquedas.** No uses «volumen» para datos de autocompletar.
4. **La web no tiene números escritos a mano:** `docs/*.html` solo lee `docs/data/*.json`.
5. **No leas la página de resultados de un buscador con un script.** Top 10 solo por API oficial.
6. **Publicar, crear claves o borrar necesita el OK explícito de la persona dueña del repo.**
7. Trabajo de más de una sesión: seguí `PLAN.md`, hacé solo la fase que te toca y demostrá su «hecho cuando» con un comando y su salida.

## Mapa del repositorio

| Carpeta o archivo | Qué es |
|---|---|
| `colector/` | Programa en Python (biblioteca estándar): extrae, valida, clasifica y guarda |
| `docs/` | La web (GitHub Pages): mapa agéntico y radar de interés |
| `docs/data/` | Datos que lee la web: consultas, reglas, estado del loop, paquete para chats |
| `data/raw/`, `manifests/` | Crudo de cada corrida y su manifiesto (linaje) |
| `chat/` | Cómo usar el radar desde un chat: Claude, ChatGPT y Gemini |
| `tests/` | Pruebas; corren antes de guardar cualquier dato |
| `PLAN.md`, `docs/data/loop.json` | Plan por fases y en qué fase estamos |
| `sesiones/`, `revisiones/`, `prompts/` | Memoria entre sesiones, registro de revisiones, pedido de la próxima fase |

## Comandos

```bash
python3 -m unittest discover -s tests -v      # pruebas
python3 colector/run.py "ciencia de datos"    # medir un tema
python3 colector/base_csv.py                  # regenerar la base CSV (run.py ya lo hace)
python3 colector/reprocesar.py                # rehacer los temas desde el crudo
python3 colector/paquete_chat.py              # regenerar el paquete para chats
python3 -m http.server 8000 --directory docs  # ver la web en local
```
