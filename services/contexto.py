class ContextoConversacion:

    def __init__(self):
        self.historial = []
        self.categoria_actual = None
        self.ultima_pregunta = None

    def agregar_usuario(self, mensaje):

        self.historial.append({
            "rol": "usuario",
            "contenido": mensaje
        })

        self.ultima_pregunta = mensaje

    def agregar_asistente(self, mensaje):

        self.historial.append({
            "rol": "asistente",
            "contenido": mensaje
        })

    def establecer_categoria(self, categoria):

        self.categoria_actual = categoria

    def obtener_historial(self, limite=10):

        return self.historial[-limite:]

    def obtener_contexto(self):

        return {
            "categoria": self.categoria_actual,
            "ultima_pregunta": self.ultima_pregunta,
            "historial": self.obtener_historial()
        }

    def limpiar(self):

        self.historial = []
        self.categoria_actual = None
        self.ultima_pregunta = None