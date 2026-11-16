# Gemini: un Gem que usa el radar

> **Estado: sin probar.** Guía escrita a partir de cómo funcionan los Gems; nadie del equipo lo creó todavía. Quien lo haga, anota el resultado en `revisiones/REGISTRO.md`.

Un Gem es un chat de Gemini con instrucciones y archivos propios, que se comparte por link.

## Pasos

1. En Gemini: **Explorar Gems → Nuevo Gem**.
2. **Instrucciones:** pegar el contenido de [`INSTRUCCIONES_CHAT.md`](INSTRUCCIONES_CHAT.md). Agregar: *«Tu única base de hechos es el archivo paquete-chat.md.»*
3. **Conocimiento:** subir `docs/data/paquete-chat.md`. Un Gem no consulta direcciones por su cuenta, así que hay que volver a subir el archivo cuando se midan temas nuevos.
4. Guardar y compartir.

## Si se necesita una página propia, como el artefacto de Claude

El equivalente en el mundo de Google es publicar una página (por ejemplo con Firebase Hosting o desde Google AI Studio) que lea los mismos archivos JSON del radar y llame a Gemini. Eso requiere un proyecto de Google Cloud y una clave: es una decisión de la persona dueña del repositorio y no está hecho.

## Qué probar antes de darlo por bueno

Lo mismo que en `chatgpt-gpt.md`: un tema medido, uno no medido, y la pregunta «¿cuánta gente lo busca?».
