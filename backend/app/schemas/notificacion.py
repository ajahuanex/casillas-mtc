from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from app.models.enums import (
    TipoDocumentoIdentidad, EstadoCasilla,
    EstadoNotificacion, TipoDocumentoAdjunto, TipoAcuse
)


class AdministradoBase(BaseModel):
    tipo_documento: TipoDocumentoIdentidad
    numero_documento: str = Field(..., max_length=20)
    razon_social_o_nombre: str = Field(..., max_length=255)
    correo_electronico: Optional[str] = None
    telefono: Optional[str] = None
    direccion_fiscal: Optional[str] = None


class AdministradoResponse(AdministradoBase):
    id: uuid.UUID
    estado_activo: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CasillaResponse(BaseModel):
    id: uuid.UUID
    codigo_casilla: str
    estado_casilla: EstadoCasilla
    ultima_verificacion: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


class DocumentoResponse(BaseModel):
    id: uuid.UUID
    tipo_documento: TipoDocumentoAdjunto
    nombre_archivo: str
    storage_path: str
    sha256_hash: str
    tamanio_bytes: int
    mime_type: str
    created_at: datetime
    download_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class AcuseResponse(BaseModel):
    id: uuid.UUID
    tipo_acuse: TipoAcuse
    codigo_verificacion_mtc: str
    storage_path: str
    sha256_hash: str
    fecha_hora_mtc: datetime
    download_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class NotificacionCreate(BaseModel):
    codigo_expediente: str = Field(..., max_length=50, description="Ej: EXP-2026-00452")
    numero_acto_administrativo: str = Field(..., max_length=100, description="Ej: RESOLUCION DIRECTORAL N° 120-2026-MTC")
    asunto: str = Field(..., max_length=255)
    descripcion: Optional[str] = None
    
    # Destinatario
    tipo_documento: TipoDocumentoIdentidad
    numero_documento: str
    razon_social_o_nombre: str


class NotificacionResponse(BaseModel):
    id: uuid.UUID
    codigo_expediente: str
    numero_acto_administrativo: str
    asunto: str
    descripcion: Optional[str]
    estado: EstadoNotificacion
    
    fecha_emision: datetime
    fecha_firma: Optional[datetime]
    fecha_deposito: Optional[datetime]
    fecha_notificacion_efectiva: Optional[datetime]
    
    id_transaccion_mtc: Optional[str]
    
    casilla: Optional[CasillaResponse] = None
    documentos: List[DocumentoResponse] = []
    acuses: List[AcuseResponse] = []

    model_config = ConfigDict(from_attributes=True)
