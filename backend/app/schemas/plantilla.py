from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class PlantillaBase(BaseModel):
    codigo: str = Field(..., description="Código único de la plantilla con prefijo P- (ej. P-PAS-01)")
    nombre: str = Field(..., description="Nombre descriptivo oficial de la plantilla")
    categoria: str = Field(..., description="Categoría: FISCALIZADORA, ADMINISTRATIVA, IMPUGNATORIA, COACTIVA")
    tipo_procedimiento: str = Field(..., description="Tipo de procedimiento administrativo según LPAG o RNAT")
    base_legal: str = Field(..., description="Base legal aplicable y artículos sustantivos")
    asunto_predeterminado: str = Field(..., description="Asunto sugerido para la notificación")
    plazo_dias_defecto: int = Field(5, description="Plazo legal predeterminado en días")
    tipo_plazo: str = Field("DIAS_HABILES", description="DIAS_HABILES o DIAS_CALENDARIO")
    cuerpo_html_template: str = Field(..., description="Cuerpo redactado con etiquetas Jinja2")
    variables_requeridas: List[str] = Field(default_factory=list, description="Lista de tokens obligatorios (ej. ADMINISTRADO_NOMBRE)")
    organo_emisor_defecto: str = Field("Dirección Regional de Transportes y Comunicaciones - DRTC Puno")
    requiere_firma_digital: bool = True
    activo: bool = True
    version: int = 1


class PlantillaCreate(PlantillaBase):
    pass


class PlantillaUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    tipo_procedimiento: Optional[str] = None
    base_legal: Optional[str] = None
    asunto_predeterminado: Optional[str] = None
    plazo_dias_defecto: Optional[int] = None
    tipo_plazo: Optional[str] = None
    cuerpo_html_template: Optional[str] = None
    variables_requeridas: Optional[List[str]] = None
    organo_emisor_defecto: Optional[str] = None
    requiere_firma_digital: Optional[bool] = None
    activo: Optional[bool] = None
    version: Optional[int] = None


class PlantillaResponse(PlantillaBase):
    id: UUID
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class PlantillaRenderRequest(BaseModel):
    variables: Dict[str, Any] = Field(..., description="Diccionario clave-valor con los datos para reemplazar en el template")


class PlantillaRenderResponse(BaseModel):
    codigo: str
    nombre: str
    asunto_renderizado: str
    cuerpo_renderizado: str
    plazo_dias: int
    tipo_plazo: str
    variables_faltantes: List[str] = []
