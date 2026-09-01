def respuesta_fuera_de_alcance():

    return (
        "Puedo ayudarte con información del Senado, "
        "leyes, trámites, fiscalización y temas legislativos."
    )


def respuesta_sin_informacion(categoria):

    nombres = {
        "institucional": "información institucional",
        "tramites": "trámites",
        "comunicacion": "comunicación institucional",
        "facultades_legislativas": "facultades legislativas",
        "senadores": "senadores",
        "legislacion": "legislación",
        "fiscalizacion": "fiscalización",
        "gestion": "gestión"
    }

    nombre = nombres.get(
        categoria,
        "ese tema"
    )

    return f"No encontré información suficiente sobre {nombre}."