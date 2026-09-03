import os
import uuid

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv

from services.legislativo import buscar_informacion, estadisticas
from services.chat_service import responder
from services.memory import limpiar_memoria
from services.api_client import APIClient

# ============================================================
# CONFIGURACIÓN
# ============================================================

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY", "cambia-esta-clave")

# ============================================================
# CORS - COMUNICACIÓN CON PÁGINA EXPRESS
# ============================================================
# LOCAL:
#   http://localhost:3000
#   http://127.0.0.1:3000
# PRODUCCIÓN:
#   cambia ALLOWED_ORIGINS en .env por el dominio real.

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]

CORS(
    app,
    resources={r"/api/*": {"origins": allowed_origins}},
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept", "X-Requested-With"],
    supports_credentials=False,
    max_age=86400,
)

api_client = APIClient()

# ============================================================
# SESIÓN LOCAL DEL PORTAL
# ============================================================

@app.before_request
def asegurar_sesion():
    """Mantiene una sesión para las páginas propias del Portal.

    El widget embebido NO depende de esta cookie. Para permitir
    comunicación estable entre dominios, el chat utiliza el
    session_id enviado explícitamente en el JSON.
    """
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())


def obtener_session_id_chat(datos):
    """Obtiene el identificador enviado por el widget embebido.

    No usamos la cookie de Flask para el widget porque Express y
    Portal Legislativo pueden estar en dominios distintos.
    """
    session_id = str(datos.get("session_id") or "").strip()

    if not session_id:
        session_id = str(uuid.uuid4())

    # Límite defensivo para evitar valores enormes.
    return session_id[:128]


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

@app.get("/")
def inicio():
    return render_template("index.html")


# ============================================================
# ESTADÍSTICAS
# ============================================================

@app.get("/api/estadisticas")
def api_estadisticas():
    try:
        return jsonify(estadisticas())
    except Exception as error:
        print("Error estadísticas:", error)
        return jsonify({
            "ok": False,
            "error": "No se pudieron obtener las estadísticas."
        }), 500


# ============================================================
# BUSCADOR LEGISLATIVO
# ============================================================

@app.get("/api/legislativo/buscar")
def api_buscar():
    q = request.args.get("q", "").strip()

    if not q:
        return jsonify({"consulta": "", "resultados": []})

    try:
        return jsonify(buscar_informacion(q))
    except Exception as error:
        print("Error búsqueda:", error)
        return jsonify({
            "ok": False,
            "error": "No se pudo realizar la búsqueda."
        }), 500


# ============================================================
# CHAT INSTITUCIONAL - ENDPOINT DEL SCRIPT EMBEBIDO
# ============================================================

@app.route("/api/chat", methods=["POST", "OPTIONS"])
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    """Endpoint usado por chat-embed.js.

    JSON aceptado:
    {
        "mensaje": "...",
        "message": "...",
        "session_id": "..."
    }

    La sesión se transporta en el JSON, no mediante cookies.
    Esto permite que el widget funcione desde otro servidor/dominio.
    """
    if request.method == "OPTIONS":
        return ("", 204)

    datos = request.get_json(silent=True) or {}

    pregunta = str(
        datos.get("pregunta")
        or datos.get("mensaje")
        or datos.get("message")
        or ""
    ).strip()

    if not pregunta:
        return jsonify({
            "ok": False,
            "error": "Escribe una consulta."
        }), 400

    session_id = obtener_session_id_chat(datos)

    try:
        resultado = responder(pregunta, session_id)

        # Garantiza que el navegador conserve el mismo identificador
        # incluso si el backend generó uno nuevo.
        if isinstance(resultado, dict):
            resultado.setdefault("ok", True)
            resultado["session_id"] = session_id

        return jsonify(resultado)

    except Exception as error:
        print("Error chat:", error)
        return jsonify({
            "ok": False,
            "error": "Ocurrió un error al procesar la consulta.",
            "session_id": session_id
        }), 500


# ============================================================
# CONSULTA DE TRÁMITES
# ============================================================

@app.post("/api/tramite")
def consultar_tramite():
    datos = request.get_json(silent=True) or {}

    code = str(datos.get("code", "")).strip()
    if not code:
        return jsonify({
            "ok": False,
            "error": "Debe ingresar el código del trámite."
        }), 400

    password = str(datos.get("password", "")).strip()
    if not password:
        return jsonify({
            "ok": False,
            "error": "Debe ingresar la contraseña del trámite."
        }), 400

    try:
        resultado = api_client.consultar_tramite(code, password)
    except Exception as error:
        print("Error consulta trámite:", error)
        return jsonify({
            "ok": False,
            "error": "No se pudo consultar el sistema institucional."
        }), 502

    if not resultado.get("ok", False):
        return jsonify(resultado), 502

    return jsonify(resultado)


# ============================================================
# LIMPIAR MEMORIA
# ============================================================

@app.post("/api/memoria/limpiar")
def api_limpiar_memoria():
    datos = request.get_json(silent=True) or {}
    session_id = str(datos.get("session_id") or session.get("session_id") or "").strip()

    if not session_id:
        return jsonify({
            "ok": False,
            "error": "No se recibió la sesión."
        }), 400

    try:
        limpiar_memoria(session_id[:128])
        return jsonify({
            "ok": True,
            "mensaje": "Conversación limpiada.",
            "session_id": session_id[:128]
        })
    except Exception as error:
        print("Error limpiando memoria:", error)
        return jsonify({
            "ok": False,
            "error": "No se pudo limpiar la conversación."
        }), 500


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return jsonify({
        "ok": True,
        "servicio": "Portal Legislativo V2",
        "chat": "/api/chat",
        "allowed_origins": allowed_origins
    })


# ============================================================
# EJECUTAR SERVIDOR
# ============================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug
    )
