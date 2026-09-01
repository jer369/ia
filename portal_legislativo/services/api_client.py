import os
import requests
from dotenv import load_dotenv


# ============================================================
# CARGAR VARIABLES DE ENTORNO
# ============================================================

load_dotenv()


class APIClient:

    def __init__(self):

        # ====================================================
        # API OFICIAL GENERAL
        # ====================================================

        self.base_url = os.getenv(
            "API_OFICIAL_URL",
            ""
        ).strip()

        self.token = os.getenv(
            "API_OFICIAL_TOKEN",
            ""
        ).strip()

        # ====================================================
        # API DE SEGUIMIENTO DE TRÁMITES
        # ====================================================

        self.track_document_url = os.getenv(
            "TRACK_DOCUMENT_URL",
            "http://192.168.1.175:8000/api/v1/track-document"
        ).strip()

        print(
            "API seguimiento:",
            self.track_document_url
        )

    # ========================================================
    # VERIFICAR API GENERAL
    # ========================================================

    def disponible(self):

        return bool(
            self.base_url
        )

    # ========================================================
    # OBTENER INFORMACIÓN DE API GENERAL
    # ========================================================

    def obtener(
        self,
        endpoint,
        params=None
    ):

        if not self.base_url:
            return None

        url = (
            self.base_url.rstrip("/")
            + "/"
            + endpoint.lstrip("/")
        )

        headers = {
            "Accept": "application/json"
        }

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

        except requests.exceptions.ConnectionError as error:

            print(
                "Error API: no se pudo establecer conexión."
            )

            print(
                "Detalle:",
                error
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

        print("\n==============================")
        print("CONSULTA DE TRÁMITE")
        print("==============================")

        print(
            "URL:",
            self.track_document_url
        )

        print(
            "Código:",
            code
        )

        # No imprimir la contraseña por seguridad

        try:

            payload = {
                "code": code,
                "password": password
            }

            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            print(
                "Enviando solicitud..."
            )

            response = requests.post(
                self.track_document_url,
                json=payload,
                headers=headers,
                timeout=30
            )

            print(
                "HTTP:",
                response.status_code
            )

            print(
                "Respuesta:",
                response.text[:1000]
            )

            response.raise_for_status()

            resultado = response.json()

            print(
                "Status API:",
                resultado.get("status")
            )

            print(
                "Message API:",
                resultado.get("message")
            )

            # =================================================
            # VALIDAR RESPUESTA DE LA API
            # =================================================

            if resultado.get("status") != "Success":

                return {
                    "ok": False,
                    "error": resultado.get(
                        "message",
                        "No se pudo consultar el trámite."
                    )
                }

            # =================================================
            # OBTENER DATA
            # =================================================

            data = resultado.get(
                "data"
            )

            if not data:

                return {
                    "ok": False,
                    "error": (
                        "La API respondió correctamente, "
                        "pero no devolvió información del trámite."
                    )
                }

            # =================================================
            # RESPUESTA CORRECTA
            # =================================================

            return {
                "ok": True,
                "data": data
            }

        # =====================================================
        # TIMEOUT
        # =====================================================

        except requests.exceptions.Timeout as error:

            print(
                "TIMEOUT API TRÁMITE:",
                error
            )

            return {
                "ok": False,
                "error": (
                    "La consulta tardó demasiado tiempo."
                )
            }

        # =====================================================
        # ERROR DE CONEXIÓN
        # =====================================================

        except requests.exceptions.ConnectionError as error:

            print(
                "ERROR DE CONEXIÓN API TRÁMITE:"
            )

            print(
                error
            )

            return {
                "ok": False,
                "error": (
                    "No se pudo conectar con el "
                    "sistema de trámites."
                )
            }

        # =====================================================
        # ERROR HTTP
        # =====================================================

        except requests.exceptions.HTTPError as error:

            print(
                "ERROR HTTP API TRÁMITE:"
            )

            print(
                error
            )

            try:

                detalle = response.json()

            except Exception:

                detalle = {}

            return {
                "ok": False,
                "error": detalle.get(
                    "message",
                    f"El sistema respondió con HTTP {response.status_code}."
                )
            }

        # =====================================================
        # JSON INVÁLIDO
        # =====================================================

        except ValueError as error:

            print(
                "ERROR JSON API TRÁMITE:",
                error
            )

            return {
                "ok": False,
                "error": (
                    "El sistema de trámites "
                    "devolvió una respuesta inválida."
                )
            }

        # =====================================================
        # OTRO ERROR
        # =====================================================

        except Exception as error:

            print(
                "ERROR GENERAL API TRÁMITE:",
                error
            )

            return {
                "ok": False,
                "error": (
                    "No se pudo consultar el trámite."
                )
            }