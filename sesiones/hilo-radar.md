# Radar de interés por carreras — iniciado 2026-11-16 · última actualización 2026-11-16

## Objetivo
Que una persona de UCU pueda levantar, sin datos pagos, qué se busca sobre un tema y con qué palabras, para decidir sobre una carrera. Detalle en `PLAN.md`.

## Hecho (Confirmado)
- Colector de autocompletar (Google y YouTube) con validación, clasificación, crudo y manifiesto · `python3 -m unittest discover -s tests`.
- 10 temas guardados (el primero por la Action de GitHub fue «inteligencia artificial») · `docs/data/indice.json`.
- Repo privado creado y Action probada: corrida 43966453554, commit 2517df7.
- Gate del 2026-11-16: 9 de 10 criterios pasaron; el fallo y las observaciones se corrigieron · `revisiones/gate-2026-11-16.md`.
- Web: mapa agéntico (`docs/mapa.html`; la portada `index.html` lleva a «En las IA») y radar (`docs/radar.html`) con modo en vivo, términos candidatos y pedido para chat · probadas en Chrome sin errores de consola.
- Fuentes de top 10 por script: probadas y descartadas · `revisiones/REGISTRO.md`.
- F4 hecha: repo público y web en https://luisedugonca.github.io/radar-interes-carreras/ (200; modo en vivo probado ahí).
- Estructura para varias IA: `AGENTS.md`, `GEMINI.md`, `chat/` y `docs/data/paquete-chat.md`.

## Decisiones del PO
- 2026-11-16 · Solo consultas gratis, sin Semrush. Mapa agéntico interactivo como base y formato de tablero propio. La herramienta tiene que poder usarse desde un chat.

## Abiertos
1. F5 · Top 10: el PO elige una API oficial con clave gratuita.
2. Crear y probar el GPT y el Gem (`chat/chatgpt-gpt.md`, `chat/gemini-gem.md`): están escritos, sin probar.
3. F7 · Vista para comparar temas lado a lado. Ya hay 10 temas medidos.
4. F6 · Tendencia en el tiempo y países vecinos.
5. Sumar a Victoria como colaboradora (decisión del PO).

## Próximo paso
Cuando el PO elija la fuente del top 10, correr `prompts/fase-F5.md` en una sesión nueva.

## Cambios N1
- Ver el historial de git: cada consulta guardada es un commit.
