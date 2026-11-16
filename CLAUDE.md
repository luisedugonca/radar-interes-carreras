# Radar de interés por carreras — constitución

Archivo de instrucciones para cualquier agente que trabaje en este repositorio. Corto a propósito: lo que cambia vive en otros archivos (ver el router).

## Objetivo del producto

Que una persona de UCU, sin instalar nada y sin datos pagos, pueda levantar qué se busca sobre un tema y con qué palabras, para decidir cómo nombrar, enfocar o actualizar una carrera. Proyecto educativo (Taller Integrador, UCU). Equipo: Luis Gonçalvez (PO) y Victoria Illa.

## Reglas duras

1. **Nunca inventar una salida.** Todo ejemplo (log, frase, número) sale de una corrida real.
2. **La web no tiene datos escritos a mano.** `docs/*.html` solo lee `docs/data/*.json` con `fetch`.
3. **Solo fuentes públicas y gratuitas.** Nada de Semrush, Ahrefs ni datos internos de UCU. Wikipedia no se usa.
4. **«Apariciones» no es cantidad de búsquedas.** No usar «volumen» para datos de autocompletar.
5. **No leer la página de resultados de un buscador con un script.** Probado el 2026-11-16: no es confiable. Top 10 solo por API oficial.
6. **Tres capas separadas:** `colector/` (extrae, valida, transforma) · `docs/data/` (guarda) · `docs/` (muestra). No se mezclan.
7. **Sin dependencias nuevas** (Python estándar, HTML y JS sin frameworks) salvo pedido del PO.
8. **Cada afirmación lleva etiqueta:** Confirmado · Supuesto · Pendiente · Propuesta.

## Niveles de aprobación

| Nivel | Qué cubre acá | Cómo se aprueba |
|---|---|---|
| **N0 · Libre** | Leer, analizar, correr pruebas, escribir en `sesiones/` y `revisiones/` | Sin aviso |
| **N1 · Hago y registro** | Datos: `docs/data/consultas/`, `data/raw/`, `manifests/`, `docs/data/loop.json` | Commit + una línea en el hilo |
| **N2 · Un OK por lote** | Reglas y artefactos: `CLAUDE.md`, `PLAN.md`, `docs/data/reglas.json`, `docs/data/mapa.json`, la web, el colector | Preview del lote + un OK explícito |
| **N3 · OK por acción** | Hacer público el repo, activar Pages, crear claves o secretos, invitar colaboradores, borrar | Cada acción, con OK del PO |

El silencio nunca es aprobación. Ante la duda entre dos niveles, el más alto.

## Ciclo de trabajo

1. **Clasificar** el pedido: consulta, entregable chico o entregable grande.
2. **Verificar en la fuente viva** antes de afirmar (correr el colector o las pruebas).
3. **Grande** (cambia alcance, fuentes, reglas o lo que se publica) → revisor independiente antes del preview al PO. **Chico** → autochequeo de una línea.
4. Trabajo de más de una sesión → `PLAN.md`: cada fase es una sesión que hace solo esa fase y demuestra su «hecho cuando».
5. Al cerrar: actualizar `sesiones/hilo-radar.md` y `docs/data/loop.json`; una línea en `revisiones/REGISTRO.md` si hubo Gate o corrección del PO; commit.

## Router

| Necesito… | Está en |
|---|---|
| El plan, las fases y lo que solo decide el PO | `PLAN.md` |
| En qué fase estamos | `docs/data/loop.json` |
| Qué quedó hecho y el próximo paso | `sesiones/hilo-radar.md` |
| Revisiones, correcciones y fuentes descartadas | `revisiones/REGISTRO.md` |
| Reglas de clasificación y semillas | `docs/data/reglas.json` |
| Cómo se corre todo | `README.md` |
| El pedido de la próxima fase | `prompts/` |
| Usar el radar desde un chat (Claude, ChatGPT, Gemini) | `chat/README.md` |
| Instrucciones para agentes que no son Claude | `AGENTS.md`, `GEMINI.md` |

## Comandos

```bash
python3 -m unittest discover -s tests -v      # pruebas
python3 colector/run.py "ciencia de datos"    # una consulta (crudo, datos y manifiesto)
python3 colector/paquete_chat.py              # regenerar el paquete para chats
python3 -m http.server 8000 --directory docs  # ver la web en http://localhost:8000
```
