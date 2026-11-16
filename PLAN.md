# Plan — Radar de interés por carreras · 2026-11-16

**Clase:** GRANDE (define alcance, fuentes y qué se publica) → Gate antes del OK del PO.
**Método:** portafolio «PO agéntico», capítulo 11 (primero se planifica, después se ejecuta el plan).

## 0. Objetivo y éxito

- **Objetivo (una oración):** que una persona de UCU, sin instalar nada y sin datos pagos, pueda levantar qué se busca sobre un tema y con qué palabras, para decidir cómo nombrar, enfocar o actualizar una carrera.
- **Métrica de éxito (verificable):**
  1. **Autonomía:** alguien que no es Luis abre un link, escribe un tema y ve las búsquedas agrupadas por tipo de duda en menos de 1 minuto. *Línea base:* hoy ese levantamiento lo hace Luis con un agente y con Semrush pago (≈36.000 unidades gastadas en el proyecto UCU Salto; ver `CATALOGO_DATOS.md` de ese proyecto).
  2. **Costo de datos = 0** unidades pagas por consulta.
  3. **Trazabilidad:** cada número de la web muestra fuente, fecha y corrida; ningún número está escrito a mano en el HTML.
  4. **Sin tocar código:** un tema nuevo queda guardado abriendo un issue o corriendo la Action.
  5. **Del dato a la decisión:** la web entrega una lista de términos candidatos y un pedido listo para un chat de IA.
- **Qué no entra:**
  - Datos pagos (Semrush, Ahrefs) y datos internos de UCU (leads, inscriptos, Analytics).
  - Cantidad de búsquedas. El autocompletar dice **qué** se busca, no **cuánto**. Se avisa en la web.
  - Wikipedia como fuente (decisión del PO del 2026-10-14 en UCU Salto).
  - Leer la página de resultados de un buscador con un script (ver decisión 4).
  - El diagnóstico de la Lic. en Datos y Negocios: sigue en su tablero privado.

## 1. Decisiones que gobiernan el plan

1. 2026-11-16 · PO: *"crear dentro de mi propio GitHub algo que pueda disponibilizar para la UCU… todo lo que sea consultas gratis… sin Semrush"*.
2. 2026-11-16 · PO: *"tener como un mapa agéntico bastante claro… algo interactuable con eso como base y después utilizar… el formato de nuestro dashboard"*.
3. 2026-11-16 · PO: *"la idea es disponibilizarle una herramienta para que a partir de un chat puedan lograr tener un levantamiento consciente… para poder tomar una mejor decisión"*. Caso de uso que dio: el área comercial quiere sacar una carrera vinculada a análisis de datos.
4. 2026-11-16 · **Confirmado con prueba:** leer la página de un buscador con un script no sirve. DuckDuckGo respondió HTTP 202 sin resultados, Brave HTTP 429, y Bing HTTP 200 con resultados sin relación (el caso real está en `tests/fixtures/bing_sin_relacion_20261116.json`). El top 10 va por API oficial o no va.
5. 2026-11-16 · **Propuesta (espera OK del PO):** formato de entrega.
   - **La herramienta es una web dentro de GitHub** (GitHub Pages): link estable, gratis, se actualiza sola con cada consulta y muestra el método. El tablero es una sección de esa misma web, no un producto aparte.
   - **El chat es el modo de uso, no otro sistema:** la web arma el pedido con los datos medidos y la persona lo pega en el chat de IA que ya usa. Para un chat que guíe todo el levantamiento: `chat/INSTRUCCIONES_CHAT.md`.
   - **El artefacto de Claude queda para lo privado** (el tablero de UCU Salto, que tiene datos de Semrush y de la situación de la carrera). No reemplaza a la web: no corre el colector ni guarda historial.
6. 2026-11-16 · El repo nace **privado**. Publicarlo es N3 (fase F4).

## 2. Contratos que el ejecutor no puede inventar

- **Fuente de verdad de cada dato:**
  - Reglas (semillas, tipos de duda, instituciones): `docs/data/reglas.json`. La leen Python y JavaScript.
  - Una consulta guardada: `docs/data/consultas/<slug>.json`. Su crudo: `data/raw/<run_id>/`. Su manifiesto: `manifests/run_<run_id>.json`.
  - Estado del loop: `docs/data/loop.json`. Contenido del mapa agéntico: `docs/data/mapa.json`.
- **Formatos y nombres:** `run_id = AAAAMMDDTHHMMSSZ_<slug>` (UTC). `slug` = tema en minúsculas, sin tildes, con guiones.
- **Capas (no se mezclan):** `colector/` extrae, valida y transforma · `docs/data/` guarda · `docs/*.html` solo lee JSON con `fetch`.
- **Stack:** Python con biblioteca estándar; HTML y JavaScript sin frameworks. No se agregan dependencias sin pedido del PO.
- **Precedencia ante conflicto:** dato medido > regla > texto. Si un «hecho cuando» no se puede demostrar, la fase no está hecha.
- **Etiquetas:** Confirmado · Supuesto · Pendiente · Propuesta. «Quién pregunta» (estudiante o familia) es siempre Supuesto.
- **Nunca inventar una salida:** todo ejemplo sale de una corrida real.

## 3. Fases

| Fase | Objetivo | Construye / toca | Hecho cuando (demostrable) | Modelo · esfuerzo | Aprobación | Costo est. |
|---|---|---|---|---|---|---|
| F0 | Plan aprobable | `PLAN.md`, `CLAUDE.md`, `docs/data/loop.json` | El plan pasó por un revisor independiente y su fila está en `revisiones/REGISTRO.md` | Mayor · alto (decisión cara, una vez) | N2 | 1 sesión |
| F1 | Colector de autocompletar | `colector/`, `tests/`, `docs/data/reglas.json` | `python3 -m unittest discover -s tests` pasa y hay 3 temas guardados con crudo y manifiesto | Medio | N1 | bajo |
| F2 | Web: mapa agéntico + radar | `docs/*.html`, `docs/assets/` | Las dos páginas cargan sin errores de consola y el modo en vivo devuelve frases para un tema nuevo | Medio | N2 | bajo |
| F3 | Repo privado + Action | `.github/`, repo en GitHub | La Action corre con un tema nuevo y deja un commit con los datos | Medio | N3 (crear el repo lo pidió el PO) | bajo |
| F4 | Publicar la web | Visibilidad del repo, GitHub Pages | `curl -s -o /dev/null -w "%{http_code}" https://luisedugonca.github.io/radar-interes-carreras/` devuelve 200 y el modo en vivo funciona ahí | Liviano | **N3 · OK del PO** | 10 min |
| F5 | Top 10 por API oficial | `colector/extraer.py` (`extraer_top10`), secreto del repo | Una consulta guardada trae top 10 «ok» con 10 resultados y la prueba del caso Bing sigue pasando | Medio | **N3 · el PO elige fuente y crea la clave** | bajo |
| F6 | Tendencia y región | `colector/`, `docs/radar.html` | Cada consulta trae la serie mensual de Trends y la misma medición para 2 países vecinos, con su fuente | Medio | N1 | medio |
| F7 | Lote UCU + comparar temas | `docs/data/consultas/`, `docs/radar.html` | Están guardados los temas que dé el PO y la web compara 2 a 4 temas lado a lado | Medio | N1 · la lista la da el PO | medio |
| F8 | Cierre y presentación | `revisiones/REGISTRO.md`, presentación | Se midió cada punto de la métrica de éxito y la presentación usa capturas de la web | Medio | N2 | 1 sesión |

**Orden y dependencias:** F0 → F1 → F2 → F3 → F4. Después, en paralelo: F5, F6 y F7. F8 al final.
**Corte mínimo:** F1 a F4. Con eso UCU ya tiene el link, el modo en vivo, las consultas guardadas y el pedido para el chat.
**Red de seguridad:** las pruebas de `tests/` corren en la Action antes de escribir datos. Si fallan dos veces por la misma causa, se escala una vez a un modelo mayor; si repite, se para y va al PO.

**Qué parte de la métrica mueve cada fase:** F1 → 2 y 3 · F2 → 1, 3 y 5 · F3 → 4 · F4 → 1 · F5, F6 y F7 → 5 · F8 mide todas.

## 4. Riesgos

| Riesgo | Mitigación | Dueño |
|---|---|---|
| La sesión de ejecución improvisa fuera del plan | El prompt de fase trae el «hecho cuando» y prohíbe tocar la fase siguiente | ejecutor |
| Leer «apariciones» como cantidad de búsquedas | Aviso fijo en la web y en el pedido para el chat; la palabra «volumen» no se usa | orquestador |
| Google cambia o limita el autocompletar (no es un servicio con contrato) | El crudo queda guardado; la validación rechaza respuestas con otro formato; el fallo se ve en la web | ejecutor |
| El autocompletar mezcla frases de otros países (medido: 24 % a 40 % según el tema) | Grupo «Fuera de Uruguay» apartado y visible; la lista de reglas crece con el uso | orquestador |
| Reglas de clasificación incompletas (medido: «Otros» entre 6 % y 29 %) | El % sin clasificar es un indicador de la web; cada regla nueva se anota en el registro | orquestador |
| Publicar algo sensible de UCU | El repo solo tiene datos públicos de buscadores; nada de Semrush ni de la situación de la carrera. Publicar es N3 | PO |
| Abuso de la Action con issues de terceros | Solo corren issues de dueños y colaboradores; el tema entra por variable de entorno y se limpia | ejecutor |
| La IA del chat inventa cantidades | El pedido copiado trae los datos, su fuente y la regla «no inventes cantidades» | orquestador |

## 5. Lo que solo el PO decide

- ¿Se hace público el repo y se activa GitHub Pages? · bloquea: F4
- ¿Qué fuente oficial para el top 10? (requiere crear una clave gratuita a nombre del PO) · bloquea: F5
- ¿Qué temas o carreras entran en el lote de UCU? · bloquea: F7
- ¿Qué países vecinos se comparan? (Propuesta: Argentina y Paraguay, por cercanía con Salto) · bloquea: F6
- ¿Se comparte con Victoria como colaboradora del repo? · no bloquea

## 6. Traspaso

Prompt de la próxima fase: `prompts/fase-F4.md`. Cada sesión que cierra una fase escribe el de la siguiente con lo que realmente pasó.

## 7. Estado del loop

El estado vive en `docs/data/loop.json` (lo muestra la web en «El loop»). Se actualiza al cerrar cada fase y se lee al inicio de cada vuelta. Una prueba (`tests/test_plan.py`) comprueba que ese archivo y la tabla de arriba hablen de las mismas fases, y que ninguna fase figure como hecha sin evidencia.
