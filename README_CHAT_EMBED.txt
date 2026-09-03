# PORTAL LEGISLATIVO - VERSION CON CHAT EMBEBIBLE

Se agregó:
- static/chat-embed.js: widget reutilizable desde cualquier página.
- static/chat-embed-example.html: ejemplo de integración.
- INTEGRACION_CHAT_EMBED.py: guía para conectar el endpoint existente.
- Soporte de session_id para separar conversaciones.
- Estados visuales pensando, consultando y respondiendo.
- Voz.
- Botón de seguimiento hacia: https://systemdemo.es/track-document
- El widget usa por defecto recursos del mismo servidor donde está chat-embed.js.

INTEGRACIÓN EN OTRO SERVIDOR:

<script
  src="https://systemdemo.es/static/chat-embed.js"
  api-url="https://systemdemo.es/api/chat"
  avatar="https://systemdemo.es/static/cara2/9.png"
  avatar-thinking="https://systemdemo.es/static/cara2/8.png"
  avatar-viewing="https://systemdemo.es/static/cara2/10.png"
  avatar-responding="https://systemdemo.es/static/cara2/9.png"
  title="Asistente Institucional"
  subtitle="Senado"
  primary-color="#1a237e"
  tracking-url="https://systemdemo.es/track-document"
></script>

IMPORTANTE:
El widget ya está preparado para enviar:
{"mensaje":"...", "message":"...", "session_id":"..."}

Tu backend debe permitir CORS para los dominios donde se incruste.
No se reemplazó la lógica institucional existente porque debe conservarse.
