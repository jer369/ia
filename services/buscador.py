import re


CATEGORIAS = {
    "institucional": [
        "institucional",
        "senado",
        "cámara",
        "camara",
        "mandato constitucional",
        "constitución",
        "constitucion",
        "funciones",
        "historia",
        "histórico",
        "historico",
        "antecedentes",
        "organización",
        "organizacion"
    ],

    "tramites": [
        "trámite",
        "tramite",
        "trámites",
        "tramites",
        "servicio",
        "servicios",
        "atención",
        "atencion",
        "ciudadano",
        "documentación",
        "documentacion"
    ],

    "comunicacion": [
        "comunicación",
        "comunicacion",
        "noticia",
        "noticias",
        "comunicado",
        "agenda",
        "actividad",
        "actividades",
        "publicación",
        "publicaciones"
    ],

    "facultades_legislativas": [
        "facultad",
        "facultades",
        "facultades legislativas",
        "legislativa",
        "legislativas",
        "iniciativa legislativa",
        "proceso legislativo",
        "legislar",
        "aprobación",
        "aprobacion",
        "sanción",
        "sancion",
        "promulgación",
        "promulgacion"
    ],

    "senadores": [
        "senador",
        "senadores",
        "titular",
        "titulares",
        "suplente",
        "suplentes",
        "comisión",
        "comision",
        "comisiones",
        "departamento",
        "circunscripción",
        "circunscripcion"
    ],

    "legislacion": [
        "legislación",
        "legislacion",
        "ley",
        "leyes",
        "proyecto",
        "proyectos",
        "proyecto de ley",
        "proyectos de ley",
        "tratamiento",
        "aprobado",
        "aprobados",
        "sancionado",
        "sancionados",
        "promulgado",
        "promulgados",
        "modificación",
        "modificaciones",
        "rechazado",
        "rechazados"
    ],

    "fiscalizacion": [
        "fiscalización",
        "fiscalizacion",
        "fiscalizar",
        "petición",
        "peticion",
        "peticiones",
        "informe",
        "informes",
        "informe escrito",
        "informe oral"
    ],

    "gestion": [
        "gestión",
        "gestion",
        "resolución",
        "resolucion",
        "resoluciones",
        "declaración",
        "declaracion",
        "declaraciones",
        "minuta",
        "minutas",
        "comunicación camaral"
    ]
}


def normalizar(texto):
    texto = texto.lower()

    reemplazos = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ü": "u"
    }

    for original, nuevo in reemplazos.items():
        texto = texto.replace(original, nuevo)

    return texto


def detectar_categoria(pregunta):
    pregunta = normalizar(pregunta)

    resultados = {}

    for categoria, palabras in CATEGORIAS.items():

        puntuacion = 0

        for palabra in palabras:

            palabra_normalizada = normalizar(palabra)

            if palabra_normalizada in pregunta:
                puntuacion += 2

        resultados[categoria] = puntuacion

    categoria = max(resultados, key=resultados.get)

    if resultados[categoria] == 0:
        return "institucional"

    return categoria


def detectar_temas(pregunta):

    pregunta = normalizar(pregunta)

    encontrados = []

    for categoria, palabras in CATEGORIAS.items():

        for palabra in palabras:

            if normalizar(palabra) in pregunta:
                encontrados.append(categoria)
                break

    return list(dict.fromkeys(encontrados))