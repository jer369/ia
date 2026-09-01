import os
import requests


class APIClient:

    def __init__(self):

        # ====================================================
        # API OFICIAL GENERAL
        # ====================================================

        self.base_url = os.getenv(
            "API_OFICIAL_URL",
            ""
        )

        self.token = os.getenv(
            "API_OFICIAL_TOKEN",
            ""
        )

        # ====================================================
        # API DE SEGUIMIENTO DE TRÁMITES
        # ====================================================

        self.track_document_url = os.getenv(
            "TRACK_DOCUMENT_URL",
            "http://172.16.30.237:8000/api/v1/track-document"
        )


    # ========================================================
    # VERIFICAR SI LA API OFICIAL ESTÁ CONFIGURADA
    # ========================================================

    def disponible(self):
        """
        Indica si existe una URL configurada para
        la API oficial general.
        """

        return bool(self.base_url)


    # ========================================================
    # OBTENER INFORMACIÓN DE LA API OFICIAL
    # ========================================================

    def obtener(self, endpoint, params=None):
        """
        Realiza una petición GET a la API oficial general.

        Ejemplo:

            api.obtener(
                "/senadores",
                {"estado": "activo"}
            )
        """

        if not self.base_url:
            return None


        # Construir URL final
        url = (
            self.base_url.rstrip("/")
            + "/"
            + endpoint.lstrip("/")
        )


        # Headers
        headers = {}

        if self.token:

            headers["Authorization"] = (
                f"Bearer {self.token}"
            )


        try:

            respuesta = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=10
            )

            respuesta.raise_for_status()

            return respuesta.json()


        except requests.exceptions.Timeout:

            print(
                "Error API: tiempo de espera agotado."
            )

            return None


        except requests.exceptions.ConnectionError:

            print(
                "Error API: no se pudo establecer conexión."
            )

            return None


        except requests.exceptions.HTTPError as error:

            print(
                "Error HTTP API:",
                error
            )

            return None


        except ValueError:

            print(
                "Error API: respuesta JSON inválida."
            )

            return None


        except Exception as error:

            print(
                "Error API:",
                error
            )

            return None


    # ========================================================
    # CONSULTAR TRÁMITE
    # ========================================================

    def consultar_tramite(
        self,
        code,
        password
    ):
        """
        Consulta un trámite en la API institucional.

        Parámetros:

            code:
                Código del trámite.

            password:
                Contraseña del trámite.
        """


        # ----------------------------------------------------
        # VALIDAR DATOS
        # ----------------------------------------------------

        if not code or not password:

            return {
                "ok": False,
                "error": (
                    "Debe proporcionar el código "
                    "y la contraseña."
                )
            }


        # ----------------------------------------------------
        # DATOS PARA LA API
        # ----------------------------------------------------

        payload = {
            "code": code,
            "password": password
        }


        # ----------------------------------------------------
        # CONSULTAR API
        # ----------------------------------------------------

        try:

            response = requests.post(
                self.track_document_url,
                json=payload,
                timeout=15
            )


            # ------------------------------------------------
            # ERROR HTTP
            # ------------------------------------------------

            if not response.ok:

                return {
                    "ok": False,
                    "status_code": response.status_code,
                    "error": (
                        "La API no pudo procesar "
                        "la consulta."
                    )
                }


            # ------------------------------------------------
            # CONVERTIR RESPUESTA A JSON
            # ------------------------------------------------

            try:

                data = response.json()

            except ValueError:

                return {
                    "ok": False,
                    "error": (
                        "La API devolvió una "
                        "respuesta no válida."
                    )
                }


            # ------------------------------------------------
            # RESPUESTA EXITOSA
            # ------------------------------------------------

            return {
                "ok": True,
                "data": data
            }


        # ----------------------------------------------------
        # TIMEOUT
        # ----------------------------------------------------

        except requests.exceptions.Timeout:

            return {
                "ok": False,
                "error": (
                    "La consulta tardó demasiado tiempo."
                )
            }


        # ----------------------------------------------------
        # ERROR DE CONEXIÓN
        # ----------------------------------------------------

        except requests.exceptions.ConnectionError:

            return {
                "ok": False,
                "error": (
                    "No se pudo conectar con "
                    "el sistema institucional."
                )
            }


        # ----------------------------------------------------
        # OTROS ERRORES
        # ----------------------------------------------------

        except Exception as error:

            print(
                "Error API:",
                error
            )

            return {
                "ok": False,
                "error": (
                    "Ocurrió un error al consultar "
                    "el trámite."
                )
            }