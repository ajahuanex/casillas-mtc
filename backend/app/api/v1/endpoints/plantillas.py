from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jinja2 import Template, TemplateSyntaxError

from app.db.session import get_db
from app.models.entities import PlantillaNotificacion
from app.schemas.plantilla import (
    PlantillaResponse, PlantillaCreate, PlantillaUpdate,
    PlantillaRenderRequest, PlantillaRenderResponse
)
from app.db.seed_plantillas import sembrar_plantillas_si_no_existen

router = APIRouter()


@router.get("", response_model=List[PlantillaResponse], summary="Listar plantillas de notificación")
async def listar_plantillas(
    categoria: Optional[str] = Query(None, description="Filtrar por FISCALIZADORA, ADMINISTRATIVA, IMPUGNATORIA, COACTIVA"),
    db: AsyncSession = Depends(get_db)
):
    """Retorna todas las plantillas activas registradas en el sistema."""
    query = select(PlantillaNotificacion).where(PlantillaNotificacion.activo.is_(True)).order_by(PlantillaNotificacion.codigo.asc())
    if categoria:
        query = query.where(PlantillaNotificacion.categoria == categoria.upper())
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{codigo}", response_model=PlantillaResponse, summary="Obtener detalle de plantilla por código")
async def obtener_plantilla(
    codigo: str,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene la definición, variables y cuerpo de una plantilla específica por su código P-*."""
    stmt = select(PlantillaNotificacion).where(PlantillaNotificacion.codigo == codigo.upper())
    result = await db.execute(stmt)
    plantilla = result.scalar_one_or_none()
    
    if not plantilla:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La plantilla con código '{codigo}' no existe."
        )
    return plantilla


@router.post("", response_model=PlantillaResponse, status_code=status.HTTP_201_CREATED, summary="Crear nueva plantilla")
async def crear_plantilla(
    payload: PlantillaCreate,
    db: AsyncSession = Depends(get_db)
):
    """Registra una nueva plantilla oficial en el catálogo."""
    stmt = select(PlantillaNotificacion).where(PlantillaNotificacion.codigo == payload.codigo.upper())
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una plantilla con el código '{payload.codigo}'."
        )
    
    nueva = PlantillaNotificacion(**payload.model_dump())
    nueva.codigo = nueva.codigo.upper()
    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)
    return nueva


@router.post("/{codigo}/render", response_model=PlantillaRenderResponse, summary="Renderizar plantilla con variables dinámicas")
async def renderizar_plantilla(
    codigo: str,
    req: PlantillaRenderRequest,
    db: AsyncSession = Depends(get_db)
):
    """Procesa el template Jinja2 de la plantilla con las variables suministradas."""
    stmt = select(PlantillaNotificacion).where(PlantillaNotificacion.codigo == codigo.upper())
    result = await db.execute(stmt)
    plantilla = result.scalar_one_or_none()
    
    if not plantilla:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La plantilla con código '{codigo}' no existe."
        )
    
    # Identificar variables faltantes
    vars_provistas = set(req.variables.keys())
    vars_requeridas = set(plantilla.variables_requeridas)
    faltantes = list(vars_requeridas - vars_provistas)
    
    try:
        template_asunto = Template(plantilla.asunto_predeterminado)
        asunto_render = template_asunto.render(**req.variables)
        
        template_cuerpo = Template(plantilla.cuerpo_html_template)
        cuerpo_render = template_cuerpo.render(**req.variables)
    except TemplateSyntaxError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error de sintaxis en plantilla Jinja2: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al renderizar plantilla: {str(e)}"
        )
        
    return PlantillaRenderResponse(
        codigo=plantilla.codigo,
        nombre=plantilla.nombre,
        asunto_renderizado=asunto_render,
        cuerpo_renderizado=cuerpo_render,
        plazo_dias=plantilla.plazo_dias_defecto,
        tipo_plazo=plantilla.tipo_plazo,
        variables_faltantes=faltantes
    )


@router.post("/sembrar/inicializar", summary="Sincronizar y sembrar catálogo de plantillas oficiales P-*")
async def sembrar_catalogo(
    db: AsyncSession = Depends(get_db)
):
    """Siembra o actualiza las 14 plantillas estándar de transporte y tránsito."""
    await sembrar_plantillas_si_no_existen(db)
    return {"status": "ok", "mensaje": "Catálogo de 14 plantillas oficiales P-* sincronizado exitosamente."}
