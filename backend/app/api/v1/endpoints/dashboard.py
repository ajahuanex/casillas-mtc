from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from typing import List

from app.db.session import get_db
from app.models.entities import Notificacion, CasillaMTC, Administrado
from app.schemas.notificacion import (
    DashboardAlertasResponse, DashboardKpis, NotificacionResponse,
    CasillaResponse, DocumentoResponse, AcuseResponse
)
from app.core.plazos_legal_engine import evaluar_computo_notificacion
from app.services.storage_service import storage_service

router = APIRouter()


@router.get("/alertas", response_model=DashboardAlertasResponse)
async def obtener_dashboard_alertas(
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna los KPIs ejecutivos y el listado de notificaciones con cómputo legal
    en tiempo real de plazos administrativos (TUO Ley 27444) y eficacia de notificación
    electrónica (D.S. N° 001-2020-MTC).
    """
    query = (
        select(Notificacion)
        .options(
            selectinload(Notificacion.casilla),
            selectinload(Notificacion.documentos),
            selectinload(Notificacion.acuses)
        )
        .order_by(Notificacion.created_at.desc())
    )
    result = await db.execute(query)
    notificaciones_db = result.scalars().all()

    ahora = datetime.now(timezone.utc)
    kpis = DashboardKpis()
    notificaciones_resp: List[NotificacionResponse] = []

    for notif in notificaciones_db:
        # Calcular cómputo procesal dinámico si ya fue depositada
        dias_restantes = None
        porcentaje = 0.0
        estado_plazo = notif.estado_plazo or "EN_ESPERA_LECTURA"
        fecha_limite_gracia = notif.fecha_limite_gracia_5dias
        fecha_inicio = notif.fecha_inicio_computo
        fecha_vencimiento = notif.fecha_vencimiento_plazo
        origen_efectiva = notif.origen_notificacion_efectiva

        if notif.fecha_deposito:
            computo = evaluar_computo_notificacion(
                fecha_deposito=notif.fecha_deposito,
                fecha_lectura=notif.fecha_lectura,
                plazo_dias_habiles=notif.plazo_dias_habiles or 15,
                fecha_referencia=ahora
            )
            dias_restantes = computo["dias_habiles_restantes"]
            porcentaje = computo["porcentaje_transcurrido"]
            estado_plazo = computo["estado_plazo"]
            fecha_limite_gracia = computo["fecha_limite_gracia_5dias"]
            if computo["fecha_inicio_computo"]:
                fecha_inicio = datetime.combine(
                    computo["fecha_inicio_computo"],
                    datetime.min.time(),
                    tzinfo=timezone.utc
                )
            if computo["fecha_vencimiento_plazo"]:
                fecha_vencimiento = datetime.combine(
                    computo["fecha_vencimiento_plazo"],
                    datetime.min.time(),
                    tzinfo=timezone.utc
                )
            if computo["es_ficcion_legal"]:
                origen_efectiva = "FICCION_LEGAL_5_DIAS"
            elif computo["es_lectura_voluntaria"]:
                origen_efectiva = "LECTURA_VOLUNTARIA"
            else:
                origen_efectiva = "PENDIENTE_LECTURA"

        # Acumular KPIs
        kpis.total_notificaciones += 1
        if estado_plazo == "EN_PLAZO":
            kpis.en_plazo_ordinario += 1
        elif estado_plazo in ("POR_VENCER_48H", "VENCE_HOY"):
            kpis.alerta_por_vencer_48h += 1
        elif estado_plazo == "PLAZO_FENECIDO":
            kpis.plazo_vencido += 1
        elif estado_plazo == "EN_GRACIA_LECTURA":
            kpis.en_gracia_lectura += 1

        if origen_efectiva in ("FICCION_LEGAL_5_DIAS", "FICCION_LEGAL_CONSUMADA"):
            kpis.notificadas_ficcion_legal += 1

        # Mapear documentos y acuses con URLs firmadas
        docs_resp = []
        for doc in notif.documentos:
            d_resp = DocumentoResponse.model_validate(doc)
            d_resp.download_url = storage_service.get_presigned_url(doc.storage_path)
            docs_resp.append(d_resp)

        acuses_resp = []
        for acuse in notif.acuses:
            a_resp = AcuseResponse.model_validate(acuse)
            a_resp.download_url = storage_service.get_presigned_url(acuse.storage_path)
            acuses_resp.append(a_resp)

        casilla_resp = CasillaResponse.model_validate(notif.casilla) if notif.casilla else None

        notificaciones_resp.append(NotificacionResponse(
            id=notif.id,
            codigo_expediente=notif.codigo_expediente,
            numero_acto_administrativo=notif.numero_acto_administrativo,
            asunto=notif.asunto,
            descripcion=notif.descripcion,
            estado=notif.estado,
            fecha_emision=notif.fecha_emision,
            fecha_firma=notif.fecha_firma,
            fecha_deposito=notif.fecha_deposito,
            fecha_lectura=notif.fecha_lectura,
            fecha_notificacion_efectiva=notif.fecha_notificacion_efectiva,
            fecha_limite_gracia_5dias=fecha_limite_gracia,
            fecha_inicio_computo=fecha_inicio,
            fecha_vencimiento_plazo=fecha_vencimiento,
            plazo_dias_habiles=notif.plazo_dias_habiles or 15,
            tipo_procedimiento=notif.tipo_procedimiento,
            origen_notificacion_efectiva=origen_efectiva,
            estado_plazo=estado_plazo,
            dias_habiles_restantes=dias_restantes,
            porcentaje_transcurrido=porcentaje,
            id_transaccion_mtc=notif.id_transaccion_mtc,
            casilla=casilla_resp,
            documentos=docs_resp,
            acuses=acuses_resp
        ))

    return DashboardAlertasResponse(
        kpis=kpis,
        notificaciones=notificaciones_resp,
        hora_oficial_peru=ahora
    )
