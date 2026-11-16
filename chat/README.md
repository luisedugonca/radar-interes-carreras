# Usar el radar desde un chat

La idea: una persona del área comercial o académica escribe **el nombre de la carrera y un contexto breve**, y el chat le devuelve una recomendación apoyada en datos medidos. No tiene que instalar ni programar nada.

Las tres opciones usan lo mismo: las **instrucciones** (`INSTRUCCIONES_CHAT.md`) y los **datos** del radar.

| Herramienta | Qué se arma | Cómo recibe los datos | Guía | Estado |
|---|---|---|---|---|
| **Claude** | Un artefacto con asistente incorporado, o un Proyecto | El artefacto trae los datos adentro; el Proyecto usa `paquete-chat.md` | [`claude.md`](claude.md) | Artefacto: publicado y revisado en pantalla. El asistente necesita una prueba con sesión de Claude |
| **ChatGPT** | Un GPT propio, compartible por link | Una Acción que lee los datos publicados en la web del radar | [`chatgpt-gpt.md`](chatgpt-gpt.md) | Guía escrita. **Sin probar**: hay que crearlo desde una cuenta de ChatGPT |
| **Gemini** | Un Gem, compartible por link | El archivo `paquete-chat.md` subido como conocimiento | [`gemini-gem.md`](gemini-gem.md) | Guía escrita. **Sin probar**: hay que crearlo desde una cuenta de Gemini |

Sin armar nada: en la web del radar, sección 4, el botón **«Copiar pedido para el chat»** deja un pedido listo para pegar en cualquier chat.

## Los datos, en una dirección fija

Cuando la web está publicada, cualquier herramienta puede leer:

- Lista de temas medidos: `https://luisedugonca.github.io/radar-interes-carreras/data/indice.json`
- Un tema: `https://luisedugonca.github.io/radar-interes-carreras/data/consultas/<slug>.json`
- Todo junto, en texto: `https://luisedugonca.github.io/radar-interes-carreras/data/paquete-chat.md`

## Para medir un tema que todavía no está

El chat no mide: lee lo medido. Un tema nuevo se mide en la web («Explorar en vivo») o se guarda abriendo un issue `Consulta: <tema>` en el repositorio.
