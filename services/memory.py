import json
import os
from datetime import datetime
from threading import Lock


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

ARCHIVO = os.path.join(
    BASE_DIR,
    "historial.json"
)

# Máximo de mensajes que se conservarán por sesión
MAX_MENSAJES = 30

# Evita que dos procesos escriban el archivo al mismo tiempo
_LOCK = Lock()


# ============================================================
# LEER HISTORIAL
# ============================================================

def _leer():
    """
    Lee todo el archivo historial.json.

    Si el archivo no existe, está vacío o tiene un JSON inválido,
    devuelve un diccionario vacío.
    """

    if not os.path.exists(ARCHIVO):
        return {}

    try:
        with open(
            ARCHIVO,
            "r",
            encoding="utf-8"
        ) as archivo:

            data = json.load(archivo)

            # El historial principal debe ser un diccionario
            if isinstance(data, dict):
                return data

            return {}

    except (json.JSONDecodeError, OSError):
        return {}


# ============================================================
# GUARDAR HISTORIAL
# ============================================================

def _guardar(data):
    """
    Guarda el historial completo en historial.json.
    """

    with open(
        ARCHIVO,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            data,
            archivo,
            ensure_ascii=False,
            indent=2
        )


# ============================================================
# OBTENER HISTORIAL DE UNA SESIÓN
# ============================================================

def obtener_historial(session_id):
    """
    Obtiene los últimos mensajes de una sesión.

    session_id identifica una conversación concreta.

    Ejemplo:

        obtener_historial("usuario_123")
    """

    data = _leer()

    historial = data.get(
        session_id,
        []
    )

    # Devuelve solamente los últimos MAX_MENSAJES
    return historial[-MAX_MENSAJES:]


# ============================================================
# AGREGAR MENSAJE
# ============================================================

def agregar_mensaje(
    session_id,
    rol,
    mensaje
):
    """
    Agrega un mensaje a una conversación.

    Parámetros:

        session_id:
            Identificador de la conversación.

        rol:
            Quién envía el mensaje.
            Por ejemplo:
                "usuario"
                "assistant"
                "sistema"

        mensaje:
            Contenido del mensaje.
    """

    with _LOCK:

        data = _leer()

        # Si la sesión todavía no existe, se crea
        data.setdefault(
            session_id,
            []
        )

        # Agregar mensaje con fecha
        data[session_id].append({
            "fecha": datetime.now().isoformat(),
            "rol": rol,
            "mensaje": mensaje
        })

        # Mantener solamente los últimos mensajes
        data[session_id] = (
            data[session_id][-MAX_MENSAJES:]
        )

        # Guardar cambios
        _guardar(data)


# ============================================================
# GUARDAR USUARIO Y RESPUESTA
# ============================================================

def guardar_mensaje(
    session_id,
    usuario,
    respuesta
):
    """
    Guarda una interacción completa:

        usuario -> mensaje enviado
        assistant -> respuesta generada

    Esto permite conservar la función del segundo código,
    pero utilizando el sistema de sesiones del primero.
    """

    with _LOCK:

        data = _leer()

        data.setdefault(
            session_id,
            []
        )

        # Mensaje del usuario
        data[session_id].append({
            "fecha": datetime.now().isoformat(),
            "rol": "usuario",
            "mensaje": usuario
        })

        # Respuesta del asistente
        data[session_id].append({
            "fecha": datetime.now().isoformat(),
            "rol": "assistant",
            "mensaje": respuesta
        })

        # Limitar historial
        data[session_id] = (
            data[session_id][-MAX_MENSAJES:]
        )

        _guardar(data)


# ============================================================
# LIMPIAR MEMORIA
# ============================================================

def limpiar_memoria(session_id):
    """
    Elimina completamente el historial de una sesión.
    """

    with _LOCK:

        data = _leer()

        # Eliminar la sesión
        data.pop(
            session_id,
            None
        )

        _guardar(data)


# ============================================================
# LIMPIAR TODO EL HISTORIAL
# ============================================================

def limpiar_todo():
    """
    Elimina todas las conversaciones almacenadas.
    """

    with _LOCK:
        _guardar({})