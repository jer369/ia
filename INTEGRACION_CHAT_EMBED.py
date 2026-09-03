# INTEGRACION_CHAT_EMBED.py
# Copia estas partes a tu Flask actual. No reemplaza tu lógica institucional.
from flask import request, jsonify, session
from flask_cors import CORS

# Si tu app Flask ya existe:
# CORS(app, supports_credentials=True,
#      resources={r"/api/*": {"origins": [
#          "https://systemdemo.es",
#          "https://TU-OTRO-SERVIDOR.com"
#      ]}})

# Endpoint esperado por chat-embed.js:
#
# @app.post("/api/chat")
# def api_chat():
#     data = request.get_json(silent=True) or {}
#     mensaje = (data.get("mensaje") or data.get("message") or "").strip()
#     session_id = data.get("session_id")
#     if not mensaje:
#         return jsonify({"error":"Mensaje vacío"}), 400
#
#     # IMPORTANTE:
#     # Aquí llama a TU función actual que ya genera la respuesta institucional.
#     # Ejemplo:
#     # respuesta = procesar_consulta(mensaje, session_id)
#
#     return jsonify({"respuesta": respuesta, "session_id": session_id})
#
# Si ya tienes /api/chat, no crees otro endpoint: adapta el JSON recibido
# para aceptar mensaje/message y session_id.
