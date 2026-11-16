# Registro: revisiones, correcciones y fuentes probadas

> Una fila por evento. Se escribe sin pedir OK (N0). Todo lo que figura acá se midió en una corrida real.

## Gate y correcciones

| Fecha | Pedido / entregable | Clase | Gate: veredicto | Resultado con el PO | Corrección posterior |
|---|---|---|---|---|---|
| 2026-11-16 | Plan + primera versión del radar (F0 a F3) | GRANDE | (se completa al cerrar el Gate) | Pendiente de OK | — |

## Fuentes probadas (2026-11-16)

| Fuente | Cómo se probó | Resultado | Decisión |
|---|---|---|---|
| Autocompletar de Google (`suggestqueries.google.com`, `client=chrome`) | 43 consultas por tema, 3 temas | 43 de 43 con respuesta en los 3 temas | **Se usa** |
| Autocompletar de YouTube (mismo servicio, `ds=yt`) | 3 consultas por tema, 3 temas | 3 de 3 con respuesta | **Se usa** |
| Autocompletar desde el navegador (JSONP) | Tema «gestión agropecuaria» en Chrome, web local | 17 de 17 consultas respondidas, 26 frases distintas | **Se usa** (modo en vivo) |
| Bing, página de resultados leída por script | «ciencia de datos», «ciencia de datos carrera uruguay» | HTTP 200 con 10 resultados **sin relación** con la consulta (perfumerías, Disney, Chrome). Caso guardado en `tests/fixtures/bing_sin_relacion_20261116.json` | **Descartada** |
| Bing en formato RSS | misma consulta | Resultados sin relación | **Descartada** |
| DuckDuckGo (`html.` y `lite.`) | misma consulta | HTTP 202, sin resultados | **Descartada** |
| Brave Search, página leída por script | misma consulta | Primer pedido: 200 con resultados correctos. Los siguientes: HTTP 429 | **Descartada** (no es estable) |
| Yahoo | misma consulta | HTTP 500 | **Descartada** |
| Otros buscadores | — | No se siguió probando: insistir contra los bloqueos de un buscador no corresponde | Top 10 solo por API oficial (F5) |

## Reglas agregadas a partir de los datos

- 2026-11-16 · La primera corrida de «ciencia de datos» dejó 215 de 508 frases en «Otros». Casi todas eran universidades y ciudades de otros países o temas vinculados (inteligencia artificial, negocios). Se amplió «Fuera de Uruguay» y se creó el grupo **«Temas con los que se combina»**. Con las reglas nuevas: 31 de 506 en «Otros». · origen: corrida de prueba, antes del primer commit.
- 2026-11-16 · «negocios digitales» trajo frases como «negocios digitales rentables» y «para ganar dinero». Se creó el grupo **«Emprender o ganar dinero»** (34 de 364 frases en ese tema; 0 en «ciencia de datos»). Lectura (Supuesto): «negocios digitales» se entiende en parte como negocio propio y no solo como carrera.
- 2026-11-16 · La regla de relevancia del top 10 (al menos 3 de 10 resultados nombran el tema) nace del caso de Bing.

## Candidatas a regla general

- Probar cada fuente con una consulta real y mirar el contenido, no solo el código de respuesta: un HTTP 200 puede traer basura.
