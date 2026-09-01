import os
import re

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from services.memory import obtener_historial, agregar_mensaje
from services.legislativo import (
    contexto_institucional,
    obtener_categoria,
    cargar_todo,
    buscar_senador_por_pregunta
)
from services.buscador import detectar_categoria
from services.respuestas import respuesta_sin_informacion


# ============================================================
# CONFIGURACIÓN DE OLLAMA
# ============================================================

MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)


try:
    llm = ChatOllama(
        model=MODEL,
        temperature=0.3,
        base_url=OLLAMA_BASE_URL,
        num_predict=180,
    )

except Exception as error:
    print("Error inicializando Ollama:", error)
    llm = None


# ============================================================
# PROMPT PRINCIPAL
# ============================================================

SYSTEM_PROMPT = """
Eres el Asistente Institucional del Senado de Bolivia.

Responde de manera natural, clara y breve.

Puedes ayudar con:

- información institucional;
- legislación y proyectos de ley;
- fiscalización;
- gestión camaral;
- senadores y comisiones;
- trámites y servicios;
- comunicación institucional;
- facultades y proceso legislativo.

REGLAS DE RESPUESTA

- Responde siempre en español.
- Sé directo, claro, natural, humano y útil.
- Normalmente responde en 1 a 4 frases. Si el ciudadano pide una explicación detallada, puedes ampliar la respuesta.
- No repitas la pregunta ni hagas introducciones innecesarias.
- Usa listas solo cuando realmente ayuden a comprender la información.
- No termines siempre con una pregunta ni preguntes automáticamente si quiere saber más.
- Mantén el contexto de toda la conversación. Si el ciudadano dice "eso", "y eso", "¿cómo?", "¿para qué?", "¿cuántos?" o expresiones similares, interpreta la consulta según lo conversado anteriormente.
- Usa primero la información institucional disponible y únicamente la información proporcionada por las fuentes institucionales.
- No inventes nombres, fechas, leyes, cifras, cargos, autoridades, proyectos, estados de trámites, estadísticas ni ningún otro dato.
- Si una fuente local presenta un dato únicamente como referencia, no lo presentes como un dato oficial o en tiempo real.
- Si la información disponible no permite responder exactamente, explica brevemente qué información sí se conoce y qué dato falta.
- Puedes responder consultas relacionadas con diferentes temas o categorías sin obligar al ciudadano a elegir previamente un menú.
- Si la consulta no está relacionada con el Senado, indícalo de manera amable y, cuando corresponda, ofrece orientar nuevamente hacia la información institucional disponible.
- Si el ciudadano expresa enojo, frustración o crítica, responde con naturalidad, respeto y sin sermones.
- Evita el lenguaje excesivamente formal, burocrático o parecido a un manual institucional.
- Si la pregunta es sencilla, responde de forma sencilla.
- Si el ciudadano solicita mayor detalle, proporciona una explicación más completa sin perder claridad.
- Nunca presentes como hecho confirmado aquello que no esté respaldado por la información institucional disponible.
- Cuando sea realmente útil para continuar la atención, termina con una pregunta breve y relacionada con la consulta.

EJEMPLOS DE ESTILO:

Usuario: ¿Para qué sirve el Senado?

Respuesta:
"El Senado participa en la elaboración de leyes y también ejerce funciones de fiscalización y control."

Usuario: ¿Y eso para qué me sirve?

Respuesta:
"Principalmente, para participar y conocer cómo se toman decisiones que afectan al país."

Usuario: es una mierda

Respuesta:
"Entiendo la molestia. Si quieres, podemos revisar qué parte del Senado te está generando ese problema."

Usuario: me parece que es todo

Respuesta:
"Entiendo. Podemos revisar el tema que más te interese: leyes, senadores, trámites o fiscalización."

No hagas respuestas largas salvo que el ciudadano pida una explicación detallada.
"""


# ============================================================
# CONVERTIR HISTORIAL A MENSAJES LANGCHAIN
# ============================================================

def _historial_langchain(historial):

    mensajes = []

    for item in historial or []:

        rol = item.get("rol")

        contenido = item.get(
            "mensaje",
            item.get("contenido", "")
        )

        if not contenido:
            continue

        if rol == "usuario":

            mensajes.append(
                HumanMessage(
                    content=contenido
                )
            )

        elif rol in ("ia", "assistant"):

            mensajes.append(
                AIMessage(
                    content=contenido
                )
            )

    return mensajes


# ============================================================
# OBTENER DATOS SEGÚN CATEGORÍA
# ============================================================

def _obtener_datos(pregunta):

    try:

        categoria = detectar_categoria(
            pregunta
        )

    except Exception:

        categoria = None


    if categoria:

        try:

            datos = obtener_categoria(
                categoria
            )

            if datos:

                return categoria, datos

        except Exception as error:

            print(
                "Error obteniendo categoría:",
                error
            )


    try:

        contexto = contexto_institucional(
            pregunta
        )

        if contexto:

            return (
                categoria or "institucional",
                contexto
            )

    except Exception as error:

        print(
            "Error obteniendo contexto:",
            error
        )


    return categoria, {}


# ============================================================
# CONSULTAR OLLAMA
# ============================================================

def _consultar_ollama(
    pregunta,
    datos,
    historial
):

    if llm is None:

        return None


    mensajes = [
        SystemMessage(
            content=SYSTEM_PROMPT
        )
    ]


    # Agregar últimos mensajes de memoria

    mensajes.extend(
        _historial_langchain(
            (historial or [])[-4:]
        )
    )


    # Preparar contexto

    contexto = (
        datos
        if isinstance(datos, str)
        else str(datos)
    )


    # Evitar enviar demasiado contexto

    contexto = contexto[:18000]


    mensajes.append(
        SystemMessage(
            content=
            "INFORMACIÓN INSTITUCIONAL DISPONIBLE:\n\n"
            + contexto
        )
    )


    mensajes.append(
        HumanMessage(
            content=pregunta
        )
    )


    try:

        resultado = llm.invoke(
            mensajes
        )


        contenido = getattr(
            resultado,
            "content",
            None
        )


        if isinstance(
            contenido,
            list
        ):

            contenido = "".join(

                str(
                    x.get("text", "")
                )
                if isinstance(x, dict)
                else str(x)

                for x in contenido
            )


        if (
            contenido
            and str(contenido).strip()
        ):

            return str(
                contenido
            ).strip()


    except Exception as error:

        print(
            "Error consultando Ollama:",
            error
        )


    return None


# ============================================================
# RESPUESTA FALLBACK
# ============================================================

def _respuesta_fallback(
    pregunta,
    categoria,
    datos
):

    """
    Respuesta útil sin Ollama.
    Solo usa datos existentes; no inventa.
    """

    q = pregunta.lower()


    # ========================================================
    # LEGISLACIÓN
    # ========================================================

    if (
        categoria == "legislacion"
        and isinstance(datos, dict)
    ):

        e = datos.get(
            "estadisticas",
            {}
        )


        if e:

            nombres = {

                "proyectos_tratamiento":
                    "proyectos en tratamiento",

                "proyectos_aprobados":
                    "proyectos aprobados",

                "leyes_sancionadas":
                    "leyes sancionadas",

                "leyes_promulgadas":
                    "leyes promulgadas",

                "proyectos_modificaciones":
                    "proyectos con modificaciones",

                "proyectos_rechazados":
                    "proyectos rechazados",
            }


            for clave, nombre in nombres.items():

                if (
                    any(
                        p in q
                        for p in clave.split("_")
                    )
                    or nombre in q
                ):

                    if clave in e:

                        return (
                            f"Según la información disponible "
                            f"en el sistema, hay {e[clave]} "
                            f"{nombre}."
                        )


            resumen = ", ".join(

                f"{nombres.get(k, k)}: {v}"

                for k, v in e.items()
            )


            return (
                "Los datos legislativos disponibles son: "
                + resumen
                + "."
            )


    # ========================================================
    # FISCALIZACIÓN
    # ========================================================

    if (
        categoria == "fiscalizacion"
        and isinstance(datos, dict)
    ):

        e = datos.get(
            "estadisticas",
            {}
        )


        if e:

            return (

                "En la información disponible figuran "

                f"{e.get('peticiones_informe_escrito', 0)} "
                "peticiones de informe escrito y "

                f"{e.get('peticiones_informe_oral', 0)} "
                "peticiones de informe oral."
            )


    # ========================================================
    # GESTIÓN
    # ========================================================

    if (
        categoria == "gestion"
        and isinstance(datos, dict)
    ):

        e = datos.get(
            "estadisticas",
            {}
        )


        if e:

            return (

                "En la información disponible figuran "

                f"{e.get('resoluciones_camarales', 0)} "
                "resoluciones camarales, "

                f"{e.get('declaraciones_camarales', 0)} "
                "declaraciones camarales y "

                f"{e.get('minutas_comunicacion', 0)} "
                "minutas de comunicación."
            )


    # ========================================================
    # CONTENIDOS GENERALES
    # ========================================================

    if isinstance(
        datos,
        dict
    ):

        seccion = datos.get(
            "seccion"
        )

        contenidos = (
            datos.get("contenidos")
            or datos.get("temas")
        )


        if seccion and contenidos:

            if isinstance(
                contenidos,
                list
            ):

                items = []


                for item in contenidos:

                    if isinstance(
                        item,
                        dict
                    ):

                        items.append(
                            item.get(
                                "titulo"
                            )
                            or str(item)
                        )

                    else:

                        items.append(
                            str(item)
                        )


                return (
                    f"En {seccion} puedo orientarte sobre: "
                    + ", ".join(items)
                    + "."
                )


    # ========================================================
    # FALLBACK GENERAL
    # ========================================================

    disponibles = []


    try:

        for nombre, contenido in (
            cargar_todo().items()
        ):

            if contenido:

                disponibles.append(
                    nombre.replace(
                        "_",
                        " "
                    )
                )

    except Exception:

        pass


    if disponibles:

        return (

            "Puedo ayudarte con esa consulta, "
            "pero el motor de IA no está disponible "
            "en este momento. La base local contiene "
            "información sobre: "

            + ", ".join(disponibles)

            + ". Prueba una pregunta concreta "
              "sobre alguno de esos temas."
        )


    return (
        "No encontré datos suficientes en las "
        "fuentes institucionales disponibles "
        "para responder esa consulta con seguridad."
    )


# ============================================================
# ENLACE OFICIAL DEL SENADOR
# ============================================================

def _slug_senador(nombre):
    """Convierte el nombre del senador al formato de URL institucional."""
    import unicodedata

    texto = unicodedata.normalize("NFKD", str(nombre or ""))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9]+", "-", texto)
    return texto.strip("-")


def _enlace_senador(senador):
    """Construye el enlace sin depender de una URL guardada en cada registro."""
    nombre = senador.get("nombre", "")
    slug = _slug_senador(nombre)

    if not slug:
        return None

    base = os.getenv(
        "SENADO_WEB_BASE",
        "http://demoap.senado.gob.bo"
    ).rstrip("/")

    cargo = str(senador.get("cargo", "")).lower()
    prefijo = "/senador/suplente/" if "suplente" in cargo else "/senador/"

    return f"{base}{prefijo}{slug}"


# ============================================================
# RESPUESTA DIRECTA SOBRE SENADORES
# ============================================================

def _respuesta_senador(pregunta):

    try:

        senador = buscar_senador_por_pregunta(
            pregunta
        )

    except Exception as error:

        print(
            "Error buscando senador:",
            error
        )

        return None


    if not senador:

        return None


    q = pregunta.lower()


    nombre = senador.get(
        "nombre",
        "No disponible"
    )


    # ========================================================
    # QUIÉN ES
    # ========================================================

    if (
        "quien es" in q
        or "quién es" in q
    ):

        return (

            f"{nombre} es "
            f"{senador.get('cargo', 'senador')} "
            f"por "
            f"{senador.get('departamento', 'departamento no disponible')}. "

            f"Forma parte del "
            f"{senador.get('comite_comision', 'comité no disponible')}."
        )


    # ========================================================
    # FECHA DE NACIMIENTO
    # ========================================================

    if (
        "cuando nacio" in q
        or "cuándo nació" in q
        or "nacimiento" in q
    ):

        return (

            f"{nombre} nació el "
            f"{senador.get('fecha_nacimiento', 'dato no disponible')}."
        )


    # ========================================================
    # LUGAR DE NACIMIENTO
    # ========================================================

    if (
        "donde nacio" in q
        or "dónde nació" in q
        or "nacido en" in q
        or "lugar de nacimiento" in q
    ):

        return (

            f"{nombre} nació en "
            f"{senador.get('lugar_nacimiento', 'dato no disponible')}."
        )


    # ========================================================
    # COMITÉ / COMISIÓN
    # ========================================================

    if (
        "comite" in q
        or "comité" in q
        or "comision" in q
        or "comisión" in q
    ):

        return (

            f"{nombre} forma parte del "
            f"{senador.get('comite_comision', 'dato no disponible')}."
        )


    # ========================================================
    # SUPLENTE
    # ========================================================

    if "suplente" in q:

        return (

            f"El senador suplente de {nombre} es "
            f"{senador.get('suplente', 'dato no disponible')}."
        )


    # ========================================================
    # PARTIDO
    # ========================================================

    if "partido" in q:

        return (

            f"{nombre} pertenece al "
            f"{senador.get('partido', 'dato no disponible')}."
        )


    # ========================================================
    # DEPARTAMENTO
    # ========================================================

    if (
        "departamento" in q
        or "por donde" in q
        or "por dónde" in q
    ):

        return (

            f"{nombre} es senador por "
            f"{senador.get('departamento', 'dato no disponible')}."
        )


    # ========================================================
    # OCUPACIÓN
    # ========================================================

    if (
        "ocupacion" in q
        or "ocupación" in q
        or "trabajo" in q
        or "profesion" in q
        or "profesión" in q
    ):

        return (

            f"La ocupación registrada de {nombre} es "
            f"{senador.get('ocupacion', 'dato no disponible')}."
        )


    # ========================================================
    # RESPUESTA RESUMIDA
    # ========================================================

    return (

        f"{nombre} es "
        f"{senador.get('cargo', 'senador')} "
        f"por "
        f"{senador.get('departamento', 'dato no disponible')}. "

        f"Nació el "
        f"{senador.get('fecha_nacimiento', 'dato no disponible')} "
        f"en "
        f"{senador.get('lugar_nacimiento', 'dato no disponible')}. "

        f"Actualmente figura en "
        f"{senador.get('comite_comision', 'comité no disponible')}. "

        f"Su suplente es "
        f"{senador.get('suplente', 'dato no disponible')}."
    )


# ============================================================
# RESPONDER
# ============================================================

def responder(
    pregunta,
    session_id=None,
    historial=None
):

    # ========================================================
    # VALIDAR PREGUNTA
    # ========================================================

    if not pregunta:

        return {
            "respuesta":
                "Por favor, introduce una pregunta.",

            "categoria":
                None,

            "fuente":
                "Sistema",
        }


    pregunta = str(
        pregunta
    ).strip()


    # ========================================================
    # OBTENER HISTORIAL
    # ========================================================

    if (
        historial is None
        and session_id
    ):

        try:

            historial = obtener_historial(
                session_id
            )

        except Exception as error:

            print(
                "Error obteniendo historial:",
                error
            )

            historial = []


    historial = historial or []


    # ========================================================
    # 1. CONSULTA DIRECTA DE SENADORES
    # ========================================================

    respuesta = _respuesta_senador(
        pregunta
    )


    if respuesta:

        categoria = "senadores"
        senador_detectado = buscar_senador_por_pregunta(pregunta)


    else:

        senador_detectado = None

        # ====================================================
        # 2. CONSULTA NORMAL
        # ====================================================

        categoria, datos = _obtener_datos(
            pregunta
        )


        respuesta = (

            _consultar_ollama(
                pregunta,
                datos,
                historial
            )

            if datos

            else None
        )


        # ====================================================
        # 3. FALLBACK SI OLLAMA NO RESPONDE
        # ====================================================

        if not respuesta:

            respuesta = _respuesta_fallback(
                pregunta,
                categoria,
                datos
            )


    # ========================================================
    # 4. GUARDAR CONVERSACIÓN
    # ========================================================

    if session_id:

        try:

            agregar_mensaje(
                session_id,
                "usuario",
                pregunta
            )


            agregar_mensaje(
                session_id,
                "ia",
                respuesta
            )


        except Exception as error:

            print(
                "Error guardando historial:",
                error
            )


    # ========================================================
    # 5. RESPUESTA FINAL
    # ========================================================

    resultado = {

        "respuesta":
            respuesta,

        "categoria":
            categoria,

        "fuente":
            "Base institucional + IA local",

        "session_id":
            session_id,
    }

    # El enlace se entrega como dato separado para que el frontend
    # muestre solamente un botón y nunca exponga la URL completa.
    if senador_detectado:
        enlace = _enlace_senador(senador_detectado)
        if enlace:
            resultado["enlace_senador"] = enlace

    return resultado
