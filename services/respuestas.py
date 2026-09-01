def respuesta_fuera_de_alcance():

    return (
        "Puedo ayudarte únicamente con información relacionada "
        "con el Senado, legislación, fiscalización, gestión, "
        "senadores, trámites, servicios, comunicación y "
        "demás información institucional."
    )


def respuesta_sin_informacion(categoria):

    nombres = {
        "institucional": "información institucional",
        "tramites": "trámites y servicios",
        "comunicacion": "comunicación institucional",
        "facultades_legislativas": "facultades legislativas",
        "senadores": "senadores",
        "legislacion": "legislación",
        "fiscalizacion": "fiscalización",
        "gestion": "gestión"
    }

    nombre = nombres.get(
        categoria,
        "información institucional"
    )

    return (
        f"No encontré información suficiente sobre {nombre} "
        "en las fuentes disponibles actualmente."
    )