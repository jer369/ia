import json
import os
import re
from functools import lru_cache


# Directorio raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


# Categorías y archivos JSON disponibles
ARCHIVOS = {
    "institucional": "institucional.json",
    "tramites": "tramites.json",
    "comunicacion": "comunicacion.json",
    "facultades_legislativas": "facultades_legislativas.json",
    "senadores": "senadores.json",
    "legislacion": "legislacion.json",
    "fiscalizacion": "fiscalizacion.json",
    "gestion": "gestion.json",
}


@lru_cache(maxsize=1)
def cargar_datos():
    """
    Carga todos los archivos JSON de la carpeta data.
    Se utiliza caché para evitar leer los archivos repetidamente.
    """
    datos = {}

    for categoria, archivo in ARCHIVOS.items():
        ruta = os.path.join(DATA_DIR, archivo)

        if not os.path.exists(ruta):
            datos[categoria] = {}
            continue

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos[categoria] = json.load(f)

        except (json.JSONDecodeError, OSError) as error:
            print(f"Error cargando {archivo}: {error}")
            datos[categoria] = {}

    return datos


def cargar_json(nombre):
    """
    Carga directamente un archivo JSON por su nombre.
    """
    ruta = os.path.join(DATA_DIR, nombre)

    if not os.path.exists(ruta):
        return {}

    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)

    except (json.JSONDecodeError, OSError) as error:
        print(f"Error cargando {nombre}: {error}")
        return {}


def cargar_todo():
    """
    Devuelve todos los datos cargados.
    """
    return cargar_datos()
def buscar_senador(nombre):
    """
    Busca un senador por nombre.
    """
    datos = obtener_categoria("senadores")

    senadores = datos.get("senadores", [])

    nombre = _normalizar(nombre)

    for senador in senadores:
        nombre_senador = _normalizar(
            senador.get("nombre", "")
        )

        if nombre in nombre_senador or nombre_senador in nombre:
            return senador

    return None
def buscar_senador_por_pregunta(pregunta):
    """
    Busca si la pregunta hace referencia
    a alguno de los senadores registrados.
    """

    datos = obtener_categoria("senadores")

    senadores = datos.get("senadores", [])

    pregunta_normalizada = _normalizar(pregunta)

    for senador in senadores:

        nombre = _normalizar(
            senador.get("nombre", "")
        )

        partes_nombre = nombre.split()

        coincidencias = 0

        for parte in partes_nombre:

            if len(parte) >= 4 and parte in pregunta_normalizada:
                coincidencias += 1

        # Si coinciden al menos 2 partes del nombre
        if coincidencias >= 2:
            return senador

    return None
def obtener_categoria(categoria):
    """
    Obtiene una categoría específica.
    """
    datos = cargar_datos()
    return datos.get(categoria, {})


def obtener_resumen():
    """
    Devuelve todos los datos.
    """
    return cargar_datos()


def estadisticas():
    """
    Obtiene las estadísticas de legislación,
    fiscalización y gestión.
    """
    d = cargar_datos()

    return {
        "legislacion": d.get("legislacion", {}).get("estadisticas", {}),
        "fiscalizacion": d.get("fiscalizacion", {}).get("estadisticas", {}),
        "gestion": d.get("gestion", {}).get("estadisticas", {}),
    }


def _normalizar(texto):
    """
    Normaliza un texto para facilitar las búsquedas.
    """
    if not texto:
        return ""

    return re.sub(r"\s+", " ", str(texto).lower()).strip()


def buscar_informacion(consulta):
    """
    Busca información en todas las categorías
    y las ordena por relevancia.
    """
    q = _normalizar(consulta)
    d = cargar_datos()

    palabras = [
        p
        for p in re.findall(r"[a-záéíóúñ0-9]+", q)
        if len(p) > 2
    ]

    resultados = []

    for categoria, contenido in d.items():

        texto = json.dumps(
            contenido,
            ensure_ascii=False
        ).lower()

        score = sum(
            1 for palabra in palabras
            if palabra in texto
        )

        if score:
            resultados.append({
                "categoria": categoria,
                "relevancia": score,
                "datos": contenido
            })

    resultados.sort(
        key=lambda x: x["relevancia"],
        reverse=True
    )

    return {
        "consulta": consulta,
        "resultados": resultados[:5]
    }


def contexto_institucional(pregunta):
    """
    Selecciona las categorías relevantes según la pregunta
    y construye un contexto institucional.
    """
    d = cargar_datos()
    q = _normalizar(pregunta)

    partes = []

    reglas = {
        "legislacion": [
            "ley",
            "leyes",
            "proyecto",
            "legislación",
            "legislacion",
            "tratamiento",
            "aprobado",
            "sancionado",
            "promulgado",
            "rechazado",
            "modific"
        ],

        "fiscalizacion": [
            "fiscalización",
            "fiscalizacion",
            "informe",
            "petición",
            "peticion",
            "oral",
            "escrito"
        ],

        "gestion": [
            "gestión",
            "gestion",
            "resolución",
            "resolucion",
            "declaración",
            "declaracion",
            "minuta"
        ],

        "senadores": [
            "senador",
            "senadores",
            "titular",
            "suplente"
        ],

        "institucional": [
            "senado",
            "mandato",
            "constitucional",
            "funciones",
            "historia",
            "antecedentes"
        ],

        "comunicacion": [
            "comunicación",
            "comunicacion",
            "noticia",
            "noticias",
            "comunicado",
            "agenda"
        ],

        "tramites": [
            "trámite",
            "tramite",
            "servicio",
            "servicios",
            "atención",
            "atencion"
        ],

        "facultades_legislativas": [
            "facultad",
            "facultades",
            "competencia",
            "competencias",
            "atribución",
            "atribuciones",
            "legislar"
        ],
    }

    categorias = [
        categoria
        for categoria, palabras in reglas.items()
        if any(palabra in q for palabra in palabras)
    ]

    # Si no se detecta una categoría concreta,
    # se utiliza toda la información disponible.
    if not categorias:
        categorias = list(d.keys())

    for categoria in categorias:

        if categoria not in d:
            continue

        partes.append(
            f"[{categoria.upper()}]\n"
            f"{json.dumps(d[categoria], ensure_ascii=False, indent=2)}"
        )

    return "\n\n".join(partes)