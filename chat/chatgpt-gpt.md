# ChatGPT: un GPT propio que lee el radar

> **Estado: sin probar.** Esta guía está escrita a partir de cómo funcionan los GPT, pero nadie del equipo lo creó todavía. Quien lo haga, anota el resultado en `revisiones/REGISTRO.md`.

Un GPT es el equivalente en ChatGPT a un artefacto compartible: un chat con instrucciones propias que se abre por link.

## Pasos

1. En ChatGPT: **Explorar GPT → Crear**.
2. **Instrucciones:** pegar el contenido de [`INSTRUCCIONES_CHAT.md`](INSTRUCCIONES_CHAT.md). Agregar al final: *«Antes de responder, llamá a la acción `listarTemas` y, si hay un tema cercano a la carrera consultada, a `leerTema`. Si no hay ninguno, decilo.»*
3. **Acciones → Crear acción nueva → Importar esquema:** pegar el contenido de [`openapi-gpt.yaml`](openapi-gpt.yaml). No lleva autenticación: son archivos públicos.
4. **Alternativa sin acciones:** subir `docs/data/paquete-chat.md` en **Conocimiento**. Hay que volver a subirlo cuando se midan temas nuevos.
5. Guardar con «Cualquier persona con el enlace» y compartir el link.

## Qué probar antes de darlo por bueno

- Preguntar por un tema medido («analista de datos»): la respuesta tiene que citar frases que estén en el archivo del tema.
- Preguntar por uno no medido: tiene que decir que no está medido, sin inventar.
- Pedir «¿cuánta gente lo busca?»: tiene que responder que el radar no mide cantidades.
