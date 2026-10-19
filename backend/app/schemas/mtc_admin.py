from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union


class LoginAdminRequest(BaseModel):
    """
    Modelo para el login administrativo contra wsapiadmcasilla.mtc.gob.pe
    """
    username: str = Field(..., description="Usuario o documento de identidad del operador MTC/DRTC")
    password: str = Field(..., description="Contraseña de acceso")
    captcha_text: Optional[str] = Field(None, description="Texto del captcha (opcional si is_automatic=True)")
    captcha_key: Optional[str] = Field(None, description="Llave del captcha retornada por el endpoint /captcha")
    is_automatic: bool = Field(False, description="Si es True, el sistema resuelve el captcha automáticamente vía OCR")


class ConsultaAutomaticaRequest(BaseModel):
    """
    Modelo para consulta automática completa en un solo paso
    """
    target_doc: str = Field(..., description="DNI (8 dígitos) o RUC (11 dígitos) del administrado a consultar")
    username: Optional[str] = Field("40396522", description="Usuario operador MTC")
    password: Optional[str] = Field("Ajahuana40396522%", description="Contraseña operador MTC")
    id_rol: Optional[Union[int, str]] = Field("1", description="ID de rol a seleccionar (ej. 1, 20)")
    captcha_text: Optional[str] = Field(None, description="Texto manual del captcha si el usuario decide ingresarlo")
    captcha_key: Optional[str] = Field(None, description="Key del captcha manual si se provee")
    force_refresh: bool = Field(False, description="Si es True, fuerza nuevo login ignorando la sesión en caché")


class SessionStatusResponse(BaseModel):
    """Estado de las credenciales de sesión temporal de MTC"""
    activa: bool
    username: Optional[str] = None
    idRol: Optional[str] = None
    segundos_restantes: int = 0
    minutos_restantes: float = 0.0
    creado_en: Optional[str] = None
    token_presente: bool = False



class CaptchaResponse(BaseModel):
    """Respuesta del endpoint de generación de captcha del MTC"""
    img: str = Field(..., description="Imagen del captcha en base64")
    key: str = Field(..., description="Identificador único/llave del captcha")
    resolved_text: Optional[str] = Field(None, description="Texto resuelto por OCR si se solicitó resolución")


class SelectRolRequest(BaseModel):
    """Modelo para selección de rol administrativo"""
    idRol: Union[int, str] = Field(..., description="ID del rol a seleccionar para la sesión")


class RolItem(BaseModel):
    idRol: Union[int, str]
    nombreRol: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[bool] = True
    raw: Optional[Dict[str, Any]] = None


class RolesResponse(BaseModel):
    success: bool = True
    message: str = "Roles obtenidos con éxito"
    roles: List[Dict[str, Any]] = []


class AdministradoItem(BaseModel):
    idPersona: Optional[int] = None
    nroDocumento: Optional[str] = None
    ruc: Optional[str] = None
    nombreCompleto: Optional[str] = None
    razonSocial: Optional[str] = None
    codTipoPersona: Optional[str] = None
    nombreTipoPersona: Optional[str] = None
    correoElectronico: Optional[str] = None
    estado: Optional[bool] = True
    username: Optional[str] = None


class BuscarAdministradoData(BaseModel):
    datos: List[AdministradoItem] = []
    total: int = 0


class BuscarAdministradoResponse(BaseModel):
    success: bool = True
    message: str = "Consulta realizada con éxito"
    data: BuscarAdministradoData
