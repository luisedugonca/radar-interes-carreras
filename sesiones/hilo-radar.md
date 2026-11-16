# Radar de interés por carreras — iniciado 2026-11-16 · última actualización 2026-11-16

## Objetivo
Que una persona de UCU pueda levantar, sin datos pagos, qué se busca sobre un tema y con qué palabras, para decidir sobre una carrera. Detalle en `PLAN.md`.

## Hecho (Confirmado)
- Colector de autocompletar (Google y YouTube) con validación, clasificación, crudo y manifiesto · `python3 -m unittest discover -s tests`.
- 4 temas guardados: «ciencia de datos», «negocios digitales», «analista de datos» e «inteligencia artificial» (este último, primero por la Action de GitHub) · `docs/data/indice.json`.
- Repo privado creado y Action probada: corrida 43966453554, commit 2517df7.
- Gate del 2026-11-16: 9 de 10 criterios pasaron; el fallo y las observaciones se corrigieron · `revisiones/gate-2026-11-16.md`.
- Web: mapa agéntico (`docs/index.html`) y radar (`docs/radar.html`) con modo en vivo, términos candidatos y pedido para chat · probadas en Chrome sin errores de consola.
- Fuentes de top 10 por script: probadas y descartadas · `revisiones/REGISTRO.md`.

## Decisiones del PO
- 2026-11-16 · Solo consultas gratis, sin Semrush. Mapa agéntico interactivo como base y formato de tablero propio. La herramienta tiene que poder usarse desde un chat.

## Abiertos
1. F4 · Publicar: hacer público el repo y activar Pages. Espera OK del PO.
2. F5 · Top 10: el PO elige una API oficial con clave gratuita.
3. F7 · El PO da la lista de temas o carreras del lote UCU.
4. Sumar a Victoria como colaboradora (decisión del PO).

## Próximo paso
Con el OK del PO, correr `prompts/fase-F4.md` en una sesión nueva.

## Cambios N1
- Ver el historial de git: cada consulta guardada es un commit.
