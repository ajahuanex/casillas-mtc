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
    fecha_firma: Optional[datetime] = None
    fecha_deposito: Optional[datetime] = None
    fecha_lectura: Optional[datetime] = None
    fecha_notificacion_efectiva: Optional[datetime] = None
    fecha_limite_gracia_5dias: Optional[datetime] = None
    fecha_inicio_computo: Optional[datetime] = None
    fecha_vencimiento_plazo: Optional[datetime] = None

    # Parámetros y cómputo procesal
    plazo_dias_habiles: int = 15
    tipo_procedimiento: Optional[str] = "Procedimiento Administrativo Sancionador"
    origen_notificacion_efectiva: Optional[str] = None
    estado_plazo: Optional[str] = "EN_ESPERA_LECTURA"
    dias_habiles_restantes: Optional[int] = None
    porcentaje_transcurrido: float = 0.0
    
    id_transaccion_mtc: Optional[str] = None
    
    casilla: Optional[CasillaResponse] = None
    documentos: List[DocumentoResponse] = []
    acuses: List[AcuseResponse] = []

    model_config = ConfigDict(from_attributes=True)


class DashboardKpis(BaseModel):
    total_notificaciones: int = 0
    en_plazo_ordinario: int = 0
    alerta_por_vencer_48h: int = 0
    plazo_vencido: int = 0
    notificadas_ficcion_legal: int = 0
    en_gracia_lectura: int = 0


class DashboardAlertasResponse(BaseModel):
    kpis: DashboardKpis
    notificaciones: List[NotificacionResponse]
    hora_oficial_peru: datetime

