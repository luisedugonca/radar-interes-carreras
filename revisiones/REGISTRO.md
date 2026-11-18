# Registro: revisiones, correcciones y fuentes probadas

> Una fila por evento. Se escribe sin pedir OK (N0). Todo lo que figura acá se midió en una corrida real.

## Gate y correcciones

| Fecha | Pedido / entregable | Clase | Gate: veredicto | Resultado con el PO | Corrección posterior |
|---|---|---|---|---|---|
| 2026-11-16 | Plan + primera versión del radar (F0 a F3) | GRANDE | Vuelta 1 · ≈101.000 tokens · 16 llamadas · **NO LISTO**: 9 de 10 criterios pasan; falla C5 (dos rangos de `PLAN.md` desactualizados al sumar el cuarto tema). Informe: `revisiones/gate-2026-11-16.md` | Pendiente de OK del PO | Corregido el mismo día: rangos de `PLAN.md`; el modo en vivo clasifica igual que Python (`replaceAll`); «fase F4» → «F5» en el aviso del top 10; «búsquedas distintas» → «frases distintas»; la Action no falla si no hay cambios. No hubo segunda vuelta del Gate: las correcciones se comprobaron con las pruebas y a mano. |

| 2026-11-16 | Publicar el repo y la web (F4) + estructura para Claude, ChatGPT y Gemini | GRANDE | Sin Gate: **excepción** (pedido textual del PO; el control previo a publicar fue el criterio C8 del Gate y un `git grep` repetido antes del cambio) | Hecho con OK del PO | — |

| 2026-11-18 | Panel derecho del mapa: indicadores por rama, carrusel de términos ordenados por datos, puesto en la lista de sugerencias | CHICO (pedido textual del PO; no cambia fuentes ni reglas de clasificación) | Autochequeo: 13 pruebas OK; reproceso desde el crudo deja las mismas frases en los 10 temas; probado en Chrome (guardado, en vivo y a 500 px) | Pendiente de que el PO lo mire | — |

| 2026-11-18 | Radar rehecho: buscador estilo Glimpse (tema, comparar, filtros), mapa fijo a la izquierda, claro/oscuro, glosario, menos texto | CHICO (pedido textual del PO; no cambia fuentes ni datos) | Autochequeo: pruebas OK; probado en Chrome en claro y oscuro, con 3 temas comparados, filtros por tipo de duda y fuente, en vivo y a 500 px; sin errores de consola | Pendiente de que el PO lo mire | — |
| 2026-11-18 | Corrección del PO sobre los KPIs | — | — | — | «Frases distintas» y «útiles para Uruguay» no son KPIs. Se quedan: apariciones por término, posición en la lista, instituciones nombradas. Se suman, cuando haya fuente: interés (Trends), keywords, posición en Google (top 3 / 4–10 / más allá del 10), popularidad del sitio |

| 2026-11-18 | Base CSV (`docs/data/base.csv`), descargar y abrir CSV en la web, comparar con un tema escrito | CHICO (pedido textual del PO) | Autochequeo: 14 pruebas OK; ida y vuelta CSV en la web = mismas 363 frases y 484 apariciones que el JSON guardado; probado en Chrome (comparar guardado, comparar en vivo, abrir CSV) | Pendiente de que el PO lo mire | — |

| 2026-11-18 | Rol Analista de Datos Senior: análisis por reglas en la web (sin IA), calidad de datos, rol en el pedido para chats; carga visible; plan GEO (F9–F11) | CHICO para la web (pedido textual del PO); el plan GEO cambia alcance: queda como Propuesta hasta el OK del PO | Autochequeo: 14 pruebas OK; probado en Chrome con 3 temas comparados y una medición en vivo (carga visible con avance y tiempo restante) | Pendiente de que el PO lo mire | — |

| 2026-11-18 | Página «En las IA» (GEO, foto de oct-2026) + temporalidad de cada fuente en el glosario y en cada gráfico | CHICO (pedido textual del PO) | Autochequeo: el script da las mismas cifras que la tabla corregida a mano (34 respuestas: ChatGPT 18, Gemini 16); probado en Chrome sin errores | Pendiente de que el PO lo mire | — |
| 2026-11-18 | Corrección propia: la primera tabla de menciones leyó como vacías las 2 respuestas piloto de ChatGPT (otro formato de archivo) | — | — | Se avisó al PO y se rehízo con `colector/geo_indicadores.py` | Regla: contar siempre con el script versionado, no con conteos sueltos |

| 2026-11-18 | Esqueletos de carga en las tres páginas para bajar el CLS | CHICO (pedido textual del PO) | Medido en Chrome, red 4G rápida, antes → después. Escritorio: En las IA 0,968 → 0,014 · Radar 0,706 → 0,012 · Mapa agéntico 0,420 → 0. Celular (400 px): 0 · 0,002 · 0. Ningún esqueleto queda en pantalla al terminar | Pendiente de que el PO lo mire | — |

| 2026-11-18 | QA completo de las 3 páginas tras el aviso del PO «dejó de funcionar el comparar» | — | Comparar funcionaba con Enter; fallaba sin aviso al escribir un tema nuevo y salir del campo (no había botón). Riesgo real: scripts sin versión → página nueva con script viejo de la caché deja todo sin funcionar. Corregido: botón «Comparar» con avisos, versión en todos los módulos, barras vacías deshabilitadas. 27 chequeos en Chrome OK; 17 pruebas OK (3 nuevas en tests/test_web.py) | Pendiente de que el PO lo confirme | — |

| 2026-11-18 | Temporalidad editable en el radar: historial de mediciones, selector «Medido el…», agrupación semana a semana / mes a mes, gráfico de evolución | CHICO (pedido textual del PO) | Probado en Chrome con 2 mediciones reales de «negocios digitales» (16-nov: 363 frases; 18-nov: 361). 18 pruebas OK. Medición semanal programada en GitHub Actions (lunes 8:00 UY) con **OK del PO** el 2026-11-18 («programa la revisión semanal de las búsquedas que vayan quedando guardadas») | Aprobado | — |

| 2026-11-18 | Sellos «Foto · fecha» / «En vivo · ahora» / «Historial · N mediciones» en cada bloque del radar y de En las IA, con leyenda | CHICO (pedido textual del PO) | Probado en Chrome: tema guardado, en vivo y filtro por día en En las IA; sin errores. 18 pruebas OK | Pendiente de que el PO lo mire | — |

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

- 2026-11-16 · La primera corrida de «ciencia de datos» dejó 215 de 508 frases en «Otros». Casi todas eran universidades y ciudades de otros países o temas vinculados (inteligencia artificial, negocios). Se amplió «Fuera de Uruguay» y se creó el grupo **«Temas con los que se combina»**. Con las reglas nuevas, en la corrida vigente: 28 de 506 en «Otros». · origen: corrida de prueba, antes del primer commit.
- 2026-11-16 · «negocios digitales» trajo frases como «negocios digitales rentables» y «para ganar dinero». Se creó el grupo **«Emprender o ganar dinero»** (33 de 363 frases en ese tema en la corrida vigente; 0 en «ciencia de datos»). Lectura (Supuesto): «negocios digitales» se entiende en parte como negocio propio y no solo como carrera.
- 2026-11-16 · La regla de relevancia del top 10 (al menos 3 de 10 resultados nombran el tema) nace del caso de Bing.

## Candidatas a regla general

- Al agregar un dato nuevo, releer las cifras ya escritas en la documentación: quedaron viejas en el plan (lo encontró el Gate).
- El autocompletar no es estable entre corridas: toda cifra citada en un documento lleva fecha y corrida.

- Probar cada fuente con una consulta real y mirar el contenido, no solo el código de respuesta: un HTTP 200 puede traer basura.
