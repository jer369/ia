import os
import uuid

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session
)

from dotenv import load_dotenv

from services.legislativo import (
    buscar_informacion,
    estadisticas
)

from services.chat_service import responder

from services.memory import (
    limpiar_memoria
)

from services.api_client import (
    APIClient
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

load_dotenv()


app = Flask(__name__)


# Clave para las sesiones de Flask
app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "cambia-esta-clave"
)


# Cliente de APIs institucionales
api_client = APIClient()


# ============================================================
# SESIÓN DEL USUARIO
# ============================================================

@app.before_request
def asegurar_sesion():

    """
    Crea un identificador único para cada conversación.

    Esto permite que el sistema pueda mantener
    el historial del chat de cada usuario.
    """

    if "session_id" not in session:

        session["session_id"] = str(
            uuid.uuid4()
        )


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

@app.get("/")
def inicio():

    """
    Página principal del portal.
    """

    return render_template(
        "index.html"
    )


# ============================================================
# ESTADÍSTICAS
# ============================================================

@app.get("/api/estadisticas")
def api_estadisticas():

    """
    Devuelve las estadísticas legislativas,
    de fiscalización y de gestión.
    """

    try:

        return jsonify(
            estadisticas()
        )

    except Exception as error:

        print(
            "Error estadísticas:",
            error
        )

        return jsonify({
            "ok": False,
            "error": (
                "No se pudieron obtener "
                "las estadísticas."
            )
        }), 500


# ============================================================
# BUSCADOR LEGISLATIVO
# ============================================================

@app.get("/api/legislativo/buscar")
def api_buscar():

    """
    Busca información dentro de la base institucional.

    Ejemplo:

        /api/legislativo/buscar?q=proyectos de ley
    """

    q = request.args.get(
        "q",
        ""
    ).strip()


    if not q:

        return jsonify({
            "consulta": "",
            "resultados": []
        })


    try:

        resultado = buscar_informacion(
            q
        )

        return jsonify(
            resultado
        )

    except Exception as error:

        print(
            "Error búsqueda:",
            error
        )

        return jsonify({
            "ok": False,
            "error": (
                "No se pudo realizar "
                "la búsqueda."
            )
        }), 500


# ============================================================
# CHAT INSTITUCIONAL
# ============================================================

@app.post("/api/chat")
@app.post("/chat")
def chat():

    """
    Recibe una pregunta del usuario y
    genera una respuesta institucional.

    Acepta:

        {
            "pregunta": "..."
        }

    o:

        {
            "message": "..."
        }
    """

    datos = request.get_json(
        silent=True
    ) or {}


    pregunta = (
        datos.get("pregunta")
        or datos.get("message")
        or ""
    ).strip()


    if not pregunta:

        return jsonify({
            "error": "Escribe una consulta."
        }), 400


    try:

        resultado = responder(
            pregunta,
            session["session_id"]
        )

        return jsonify(
            resultado
        )


    except Exception as error:

        print(
            "Error chat:",
            error
        )

        return jsonify({
            "error": (
                "Ocurrió un error al "
                "procesar la consulta."
            )
        }), 500


# ============================================================
# CONSULTA DE TRÁMITES
# ============================================================

@app.post("/api/tramite")
def consultar_tramite():

    """
    Consulta el estado de un trámite
    utilizando la API institucional.

    Recibe:

        {
            "code": "ABC123",
            "password": "123456"
        }
    """

    datos = request.get_json(
        silent=True
    ) or {}


    # --------------------------------------------------------
    # CÓDIGO DEL TRÁMITE
    # --------------------------------------------------------

    code = str(
        datos.get(
            "code",
            ""
        )
    ).strip()


    if not code:

        return jsonify({
            "ok": False,
            "error": (
                "Debe ingresar el código "
                "del trámite."
            )
        }), 400


    # --------------------------------------------------------
    # CONTRASEÑA
    # --------------------------------------------------------

    password = str(
        datos.get(
            "password",
            ""
        )
    ).strip()


    if not password:

        return jsonify({
            "ok": False,
            "error": (
                "Debe ingresar la contraseña "
                "del trámite."
            )
        }), 400


    # --------------------------------------------------------
    # CONSULTAR API
    # --------------------------------------------------------

    try:

        resultado = api_client.consultar_tramite(
            code,
            password
        )


    except Exception as error:

        print(
            "Error consulta trámite:",
            error
        )

        return jsonify({
            "ok": False,
            "error": (
                "No se pudo consultar "
                "el sistema institucional."
            )
        }), 502


    # --------------------------------------------------------
    # ERROR DE API
    # --------------------------------------------------------

    if not resultado.get(
        "ok",
        False
    ):

        return jsonify(
            resultado
        ), 502


    # --------------------------------------------------------
    # RESPUESTA EXITOSA
    # --------------------------------------------------------

    return jsonify(
        resultado
    )


# ============================================================
# LIMPIAR MEMORIA DEL CHAT
# ============================================================

@app.post("/api/memoria/limpiar")
def api_limpiar_memoria():

    """
    Elimina el historial de conversación
    de la sesión actual.
    """

    try:

        limpiar_memoria(
            session["session_id"]
        )

        return jsonify({
            "ok": True,
            "mensaje": (
                "Conversación limpiada."
            )
        })


    except Exception as error:

        print(
            "Error limpiando memoria:",
            error
        )

        return jsonify({
            "ok": False,
            "error": (
                "No se pudo limpiar "
                "la conversación."
            )
        }), 500


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    """
    Endpoint utilizado para comprobar
    que el servidor está funcionando.
    """

    return jsonify({
        "ok": True,
        "servicio": "Portal Legislativo V2"
    })


# ============================================================
# EJECUTAR SERVIDOR
# ============================================================

if __name__ == "__main__":

    port = int(
        os.getenv(
            "PORT",
            "5000"
        )
    )


    debug = (
        os.getenv(
            "FLASK_DEBUG",
            "true"
        ).lower()
        == "true"
    )


    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug
    )