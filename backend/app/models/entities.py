import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    String, Text, Boolean, Integer, BigInteger, DateTime,
    ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import (
    TipoDocumentoIdentidad, EstadoCasilla,
    EstadoNotificacion, TipoDocumentoAdjunto, TipoAcuse
)


class Administrado(Base, TimestampMixin):
    """Destinatario o administrado sujeto de notificación."""
    __tablename__ = "administrados"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tipo_documento: Mapped[TipoDocumentoIdentidad] = mapped_column(SQLEnum(TipoDocumentoIdentidad), nullable=False)
    numero_documento: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    razon_social_o_nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    correo_electronico: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    direccion_fiscal: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    estado_activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relaciones
    casilla: Mapped[Optional["CasillaMTC"]] = relationship(back_populates="administrado", uselist=False)


class CasillaMTC(Base, TimestampMixin):
    """Casilla Electrónica asignada por el MTC."""
    __tablename__ = "casillas_mtc"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    administrado_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("administrados.id"), unique=True, nullable=False)
    codigo_casilla: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    estado_casilla: Mapped[EstadoCasilla] = mapped_column(SQLEnum(EstadoCasilla), default=EstadoCasilla.ACTIVA, nullable=False)
    ultima_verificacion: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    detalles_mtc: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relaciones
    administrado: Mapped["Administrado"] = relationship(back_populates="casilla")
    notificaciones: Mapped[List["Notificacion"]] = relationship(back_populates="casilla")


class Notificacion(Base, TimestampMixin):
    """Entidad principal: Notificación legal enviada a la Casilla MTC."""
    __tablename__ = "notificaciones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo_expediente: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    numero_acto_administrativo: Mapped[str] = mapped_column(String(100), nullable=False)
    asunto: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    casilla_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("casillas_mtc.id"), nullable=False)
    usuario_creador_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    estado: Mapped[EstadoNotificacion] = mapped_column(
        SQLEnum(EstadoNotificacion),
        default=EstadoNotificacion.BORRADOR,
        index=True,
        nullable=False
    )

    # Fechas críticas de control de plazos y cómputo legal (Ley 27444 y DS 001-2020-MTC)
    fecha_emision: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    fecha_firma: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    fecha_deposito: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    fecha_lectura: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    fecha_notificacion_efectiva: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    fecha_limite_gracia_5dias: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    fecha_inicio_computo: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    fecha_vencimiento_plazo: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Parámetros procesales
    plazo_dias_habiles: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    tipo_procedimiento: Mapped[Optional[str]] = mapped_column(String(100), default="Procedimiento Administrativo Sancionador", nullable=True)
    origen_notificacion_efectiva: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    estado_plazo: Mapped[Optional[str]] = mapped_column(String(50), default="PENDIENTE_DEPOSITO", nullable=True)

    # Identificadores y payloads devueltos por el MTC
    id_transaccion_mtc: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    mtc_payload_firma: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    mtc_payload_deposito: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    mtc_payload_lectura: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relaciones
    casilla: Mapped["CasillaMTC"] = relationship(back_populates="notificaciones")
    documentos: Mapped[List["NotificacionDocumento"]] = relationship(back_populates="notificacion", cascade="all, delete-orphan")
    acuses: Mapped[List["AcuseMTC"]] = relationship(back_populates="notificacion", cascade="all, delete-orphan")
    bitacoras: Mapped[List["NotificacionBitacora"]] = relationship(back_populates="notificacion", cascade="all, delete-orphan")


class NotificacionDocumento(Base, TimestampMixin):
    """Documentos asociados (original, firmado digitalmente, anexos)."""
    __tablename__ = "notificacion_documentos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notificacion_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("notificaciones.id"), nullable=False)
    tipo_documento: Mapped[TipoDocumentoAdjunto] = mapped_column(SQLEnum(TipoDocumentoAdjunto), nullable=False)
    nombre_archivo: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False) # Ruta en MinIO
    sha256_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False) # Garantía legal de no alteración
    tamanio_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), default="application/pdf", nullable=False)

    notificacion: Mapped["Notificacion"] = relationship(back_populates="documentos")


class AcuseMTC(Base, TimestampMixin):
    """Constancias emitidas por el MTC: Acuse de Depósito y Acuse de Notificación/Lectura."""
    __tablename__ = "acuses_mtc"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notificacion_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("notificaciones.id"), nullable=False)
    tipo_acuse: Mapped[TipoAcuse] = mapped_column(SQLEnum(TipoAcuse), nullable=False)
    codigo_verificacion_mtc: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False) # PDF emitido por MTC en MinIO
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    fecha_hora_mtc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    datos_tecnicos_mtc: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    notificacion: Mapped["Notificacion"] = relationship(back_populates="acuses")


class NotificacionBitacora(Base, TimestampMixin):
    """Log inmutable de auditoría para peritajes judiciales y OCI."""
    __tablename__ = "notificacion_bitacora"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notificacion_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("notificaciones.id"), nullable=False)
    usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    accion: Mapped[str] = mapped_column(String(100), nullable=False)
    estado_anterior: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    estado_nuevo: Mapped[str] = mapped_column(String(50), nullable=False)
    direccion_ip: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    detalles: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    notificacion: Mapped["Notificacion"] = relationship(back_populates="bitacoras")
