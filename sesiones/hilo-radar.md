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

- Medición semanal programada (lunes 8:00 UY, `run.py --todos` en GitHub Actions). Probada a mano el 18-nov-2026: 11 temas, 0 errores (corrida 44342703719). El radar muestra la evolución (semana a semana / mes a mes) y deja elegir cada medición.

- 2026-11-18 · Filtro Desde–Hasta (Últimos 3 meses / año / 5 años / desde 2004 / a medida) que recorta «Evolución» y muestra el gráfico oficial de Google Trends (Uruguay, tema + comparados). Probado en Chrome, escritorio y celular.

- 2026-11-19 · Ícono (SVG + PNG 32/180/192/512), tarjeta para compartir 1200×630, metadatos (descripción, canonical, Open Graph, Twitter), schema.org (WebSite, WebApplication, Dataset), manifest, robots.txt y sitemap.xml. Prueba nueva en tests/test_web.py.

- 2026-11-19 · Radar: primero lo histórico y comparativo (Trends → Comparación → Evolución; en celular, antes que el mapa). Período y Desde–Hasta al inicio de los filtros. Comparación siempre visible con atajos de un clic a temas guardados.

## Decisiones del PO
- 2026-11-18 · OK a la medición semanal automática de los temas guardados y a publicar el crudo comprimido.
- 2026-11-16 · Solo consultas gratis, sin Semrush. Mapa agéntico interactivo como base y formato de tablero propio. La herramienta tiene que poder usarse desde un chat.

- 2026-11-18 · OK del PO a usar el gráfico oficial de Google Trends dentro del radar como fuente de historia larga.

- 2026-11-19 · El PO prioriza el dato histórico y comparativo sobre la foto del día para la toma de decisiones.

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
