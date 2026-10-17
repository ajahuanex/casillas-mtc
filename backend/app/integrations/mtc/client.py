import httpx
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings

logger = logging.getLogger(__name__)


class MTCIntegrationError(Exception):
    """Excepción para fallas de comunicación con el API de Casillas MTC."""
    pass


class MTCClient:
    """
    Cliente Oficial para la Integración con el Sistema de Casillas Electrónicas del MTC.
    Especificación Oficial: Oficina de Desarrollo Tecnológico y Digital (MTC / GORE PUNO)
    
    Servicios implementados:
    1. Token Externo: GET /notificaciones/token
    2. Verificar Estado Casilla: GET /verificar-estado-casilla
    3. Notificaciones Externas: POST /notificaciones-externas
    4. Constancias (Depósito y Lectura): GET /notificaciones/constancias/{idNotificacion}
    """

    def __init__(self):
        self.base_url = settings.MTC_BASE_URL.rstrip("/")
        self.client_id = settings.MTC_CLIENT_ID
        self.client_secret = settings.MTC_CLIENT_SECRET
        self.grant_type = settings.MTC_GRANT_TYPE

        # Gestión interna de token con expiración
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0

    async def obtener_token(self, forzar_renovacion: bool = False) -> str:
        """
        1. Servicio Público de Token Externo.
        GET /notificaciones/token?grantType=authorization_code&clientId={}&clientSecret={}
        """
        ahora = time.time()
        if not forzar_renovacion and self._access_token and ahora < (self._token_expires_at - 60):
            return self._access_token

        url = f"{self.base_url}/notificaciones/token"
        params = {
            "grantType": self.grant_type,
            "clientId": self.client_id,
            "clientSecret": self.client_secret
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                token = data.get("accessToken")
                expires_in = data.get("expiresIn", 3600)
                
                if not token:
                    raise MTCIntegrationError(f"MTC no devolvió accessToken: {data}")

                self._access_token = token
                self._token_expires_at = ahora + float(expires_in)
                logger.info(f"Nuevo Token MTC obtenido exitosamente (Expira en {expires_in}s)")
                return self._access_token
            except httpx.HTTPStatusError as e:
                logger.error(f"Error HTTP obteniendo token MTC: {e.response.status_code} - {e.response.text}")
                raise MTCIntegrationError(f"Error al autenticar con MTC: {e.response.status_code}")
            except Exception as e:
                logger.error(f"Falla de red obteniendo token MTC: {e}")
                raise MTCIntegrationError(f"No se pudo conectar con el servidor de autenticación MTC: {str(e)}")

    async def _get_auth_headers(self) -> Dict[str, str]:
        token = await self.obtener_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=True
    )
    async def verificar_estado_casilla(
        self,
        nro_documento: str,
        cod_tipo_persona: str = "00001",
        cod_tipo_documento: str = "00002"
    ) -> Dict[str, Any]:
        """
        2. Verificar estado casilla.
        GET /verificar-estado-casilla
        
        codTipoPersona:
          00001 = PERSONA NATURAL
          00002 = PERSONA JURIDICA
          00004 = PERSONA EXTRANJERA
          00005 = PERSONA NATURAL CON RUC
          
        codTipoDocumento:
          00001 = RUC
          00002 = DNI
          00003 = CARNET DE EXTRANJERIA
          00005 = PASAPORTE
          00101 = CARNET SOLICITANTE DE REFUGIO
          00102 = PERMISO TEMPORAL DE PERMANENCIA
        """
        url = f"{self.base_url}/verificar-estado-casilla"
        params = {
            "codTipoPersona": cod_tipo_persona,
            "codTipoDocumento": cod_tipo_documento,
            "nroDocumento": nro_documento
        }

        headers = await self._get_auth_headers()

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url, params=params, headers=headers)
                
                # Manejo de token expirado o inválido
                if response.status_code == 401:
                    logger.warning("Token MTC expirado. Renovando y reintentando...")
                    headers = {"Authorization": f"Bearer {await self.obtener_token(forzar_renovacion=True)}"}
                    response = await client.get(url, params=params, headers=headers)

                response.raise_for_status()
                data = response.json()
                logger.info(f"Verificación casilla MTC ({nro_documento}): {data.get('message')}")
                return data
            except httpx.HTTPStatusError as e:
                logger.error(f"Error HTTP verificando casilla {nro_documento}: {e.response.status_code} - {e.response.text}")
                raise MTCIntegrationError(f"Error verificando casilla MTC: {e.response.status_code}")
            except Exception as e:
                logger.error(f"Error de red verificando casilla {nro_documento}: {e}")
                raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=True
    )
    async def registrar_notificacion_externa(
        self,
        nro_documento: str,
        asunto: str,
        mensaje_html: str,
        adjuntos: List[Dict[str, str]],
        cod_tipo_persona: str = "00001",
        cod_tipo_documento: str = "00002",
        id_categoria: int = 5,
        con_sello_tiempo: bool = True
    ) -> Dict[str, Any]:
        """
        4. Notificaciones externas.
        POST /notificaciones-externas
        
        idCategoria:
          1 = Autorización
          2 = Sanción
          3 = Cancelación
          4 = Nueva Ley
          5 = Notificación
          6 = Resoluciones
          7 = Carta
          8 = Documentos de Fiscalización
          
        adjuntos:
          [{"url": "...", "nombreArchivo": "documento.pdf"}]
        """
        url = f"{self.base_url}/notificaciones-externas"
        headers = await self._get_auth_headers()

        payload = {
            "codTipoPersona": cod_tipo_persona,
            "codTipoDocumento": cod_tipo_documento,
            "nroDocumento": nro_documento,
            "asunto": asunto,
            "mensaje": mensaje_html,
            "idCategoria": id_categoria,
            "conSelloTiempo": con_sello_tiempo,
            "adjuntos": adjuntos
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 401:
                    logger.warning("Token MTC expirado en notificación. Renovando...")
                    headers = {"Authorization": f"Bearer {await self.obtener_token(forzar_renovacion=True)}"}
                    response = await client.post(url, json=payload, headers=headers)

                response.raise_for_status()
                data = response.json()

                if not data.get("success"):
                    msj = data.get("message") or "El API del MTC no procesó la notificación."
                    raise MTCIntegrationError(f"Rechazo MTC: {msj}")

                logger.info(f"Notificación externa registrada en MTC: ID={data.get('data', {}).get('idNotificacion')}")
                return data
            except httpx.HTTPStatusError as e:
                logger.error(f"Error HTTP depositando notificación: {e.response.status_code} - {e.response.text}")
                raise MTCIntegrationError(f"Falla HTTP en depósito MTC: {e.response.status_code}")
            except Exception as e:
                logger.error(f"Error general en depósito de notificación MTC: {e}")
                raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=True
    )
    async def obtener_constancias(
        self,
        id_notificacion: int,
        tipo: str = "base64"
    ) -> Dict[str, Any]:
        """
        5. Constancias (Acuse de Depósito y Acuse de Lectura).
        GET /notificaciones/constancias/{idNotificacion}?tipo={tipo}
        
        tipo: 'url' o 'base64' (opcional)
        Retorna:
          data: {
            "constanciaDeposito": "URL o Archivo base 64 de la constancia de depósito",
            "constanciaLectura": "URL o Archivo base 64 de la constancia de lectura (null si no leída)"
          }
        """
        url = f"{self.base_url}/notificaciones/constancias/{id_notificacion}"
        params = {"tipo": tipo}
        headers = await self._get_auth_headers()

        async with httpx.AsyncClient(timeout=25.0) as client:
            try:
                response = await client.get(url, params=params, headers=headers)
                
                if response.status_code == 401:
                    headers = {"Authorization": f"Bearer {await self.obtener_token(forzar_renovacion=True)}"}
                    response = await client.get(url, params=params, headers=headers)

                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error consultando constancias de notificación {id_notificacion}: {e}")
    async def verificar_estado_casilla_drtc(
        self,
        nro_documento: str,
        cod_tipo_persona: str = "00001",
        cod_tipo_documento: str = "00002"
    ) -> Dict[str, Any]:
        """
        Consulta al API oficial de Casillas Electrónicas (Node-RED) de la DRTC Puno:
        GET https://mtc.transportespuno.gob.pe/api/v2/info
        Header: x-api-key: topSecret123
        """
        url = f"{settings.MTC_DRTC_BASE_URL.rstrip('/')}/info"
        headers = {
            "x-api-key": settings.MTC_DRTC_API_KEY,
            "Accept": "application/json"
        }
        params = {
            "codTipoPersona": cod_tipo_persona,
            "codTipoDocumento": cod_tipo_documento,
            "nroDocumento": nro_documento
        }

        async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.warning(f"Error consultando DRTC Puno casilla Node-RED ({nro_documento}): {e}")
                raise MTCIntegrationError(f"Error consultando casilla DRTC Puno: {str(e)}")


mtc_client = MTCClient()

