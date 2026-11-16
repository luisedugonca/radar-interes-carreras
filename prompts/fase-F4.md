# Prompt de fase F4 (publicar la web)

Pegar en una sesión nueva, **solo después del OK explícito del PO** para hacer público el repositorio.

```
Radar de interés por carreras — PLAN.md, fase F4 (publicar la web).
Lee CLAUDE.md, después PLAN.md (§0 objetivo, §1 decisiones, §2 contratos, §3 fila F4) y sesiones/hilo-radar.md. Nada más.

Estado de entrada: F0 a F3 hechas (Confirmado: ver docs/data/loop.json). El repo luisedugonca/radar-interes-carreras es privado. La web está en docs/ y funciona en local.

Haz SOLO la fase F4:
1. Antes de publicar, revisa que el repo no tenga nada que no deba ser público: `git ls-files` y `git grep -i -n -E "semrush|leads|inscriptos|api[_-]?key|token"`. Muestra el resultado al PO.
2. Con el OK del PO para cada acción (N3): `gh repo edit luisedugonca/radar-interes-carreras --visibility public --accept-visibility-change-consequences` y activar Pages desde la rama main, carpeta /docs.
3. Nada de F5 en adelante.

Esta fase mueve el punto 1 de la métrica de éxito (autonomía: alguien que no es Luis abre un link).
Hecho cuando: `curl -s -o /dev/null -w "%{http_code}" https://luisedugonca.github.io/radar-interes-carreras/` devuelve 200, y en esa dirección el modo en vivo del radar devuelve frases para un tema nuevo. Demuéstralo con el comando y su salida, y con una captura.
Si algo del plan no cierra con lo que encuentras, paras y lo reportas: no lo rediseñas.

Al cerrar: docs/data/loop.json (F4 hecha, con evidencia), sesiones/hilo-radar.md, commit, y el prompt de la fase siguiente en prompts/.
Modelo: liviano o medio · esfuerzo bajo.
```
