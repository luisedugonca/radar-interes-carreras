# Prompt de fase F5 (top 10 por API oficial)

Pegar en una sesión nueva, **después de que el PO elija la fuente y cargue la clave como secreto del repositorio**.

```
Radar de interés por carreras — PLAN.md, fase F5 (top 10 por API oficial).
Lee CLAUDE.md, después PLAN.md (§0, §1 decisiones 4 y 7, §2 contratos, §3 fila F5) y sesiones/hilo-radar.md. Nada más.

Estado de entrada: F0 a F4 hechas (Confirmado: docs/data/loop.json). El repo es público. colector/extraer.py:extraer_top10 devuelve «pendiente». La regla de relevancia ya existe y está probada (colector/validar.py:validar_top10, tests/fixtures/bing_sin_relacion_20261116.json).
Dato del PO que necesitas: qué API eligió y el nombre del secreto. Si no lo tienes, paras y lo pides.

Haz SOLO la fase F5:
1. Lee la documentación oficial vigente de esa API antes de escribir (no de memoria).
2. Reemplaza el cuerpo de extraer_top10: una llamada por consulta, clave por variable de entorno, crudo guardado en data/raw/<run_id>/ antes de interpretarlo. Sin clave, sigue devolviendo «pendiente».
3. Pasa la clave a la Action como secreto. No leas páginas de buscadores con scripts.
4. Nada de F6 en adelante.

Esta fase mueve el punto 5 de la métrica de éxito (del dato a la decisión).
Hecho cuando: una consulta guardada trae top10 con estado «ok» y 10 resultados, y `python3 -m unittest discover -s tests` sigue pasando (incluida la prueba del caso Bing). Demuéstralo con comandos y su salida.
Si algo del plan no cierra con lo que encuentras, paras y lo reportas: no lo rediseñas.

Al cerrar: docs/data/loop.json, sesiones/hilo-radar.md, docs/data/mapa.json (nodo top10), commit y el prompt de la fase siguiente.
Modelo: medio · esfuerzo medio. Cambia el colector (N2): preview al PO antes del commit.
```
