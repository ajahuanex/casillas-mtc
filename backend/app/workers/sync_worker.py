import asyncio
import logging
import base64
from datetime import datetime, timezone
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionLocal
from app.models.entities import Notificacion, AcuseMTC, NotificacionBitacora
from app.models.enums import EstadoNotificacion, TipoAcuse
from app.services.storage_service import storage_service
from app.integrations.mtc.client import mtc_client
from app.core.config import settings
from app.core.plazos_legal_engine import evaluar_computo_notificacion

logger = logging.getLogger(__name__)


async def sincronizar_constancias_pendientes():
    """
    Tarea periódica en segundo plano:
    1. Busca todas las notificaciones en estado DEPOSITADO.
    2. Consulta al endpoint MTC GET /notificaciones/constancias/{idNotificacion}?tipo=base64.
    3. Si el administrado abrió y leyó la notificación, descarga la constancia de lectura en PDF,
       la custodia en MinIO con hash SHA-256 y marca la notificación como LEIDO_NOTIFICADO.
    """
    async with AsyncSessionLocal() as db:
        try:
            query = (
                select(Notificacion)
                .options(selectinload(Notificacion.acuses))
                .where(Notificacion.estado == EstadoNotificacion.DEPOSITADO)
            )
            result = await db.execute(query)
            notificaciones = result.scalars().all()

            for notif in notificaciones:
                if not notif.id_transaccion_mtc or not notif.id_transaccion_mtc.isdigit():
                    continue

                id_mtc = int(notif.id_transaccion_mtc)
                try:
                    resp = await mtc_client.obtener_constancias(id_mtc, tipo="base64")
                    data = resp.get("data", {})
                    constancia_lectura_b64 = data.get("constanciaLectura")

                    if constancia_lectura_b64:
                        pdf_bytes = base64.b64decode(constancia_lectura_b64)
                        storage_path = f"notificaciones/{notif.id}/acuses/acuse_lectura.pdf"
                        saved_path, sha256_hash, _ = await storage_service.upload_document(
                            file_bytes=pdf_bytes,
                            destination_path=storage_path,
                            content_type="application/pdf"
                        )

                        # Registrar acuse si no existe
                        existe = any(a.tipo_acuse == TipoAcuse.LECTURA_NOTIFICACION for a in notif.acuses)
                        if not existe:
                            acuse_lectura = AcuseMTC(
                                notificacion_id=notif.id,
                                tipo_acuse=TipoAcuse.LECTURA_NOTIFICACION,
                                codigo_verificacion_mtc=f"LEC-{id_mtc}",
                                storage_path=saved_path,
                                sha256_hash=sha256_hash,
                                fecha_hora_mtc=datetime.utcnow(),
                                datos_tecnicos_mtc=data
                            )
                            db.add(acuse_lectura)

                        notif.estado = EstadoNotificacion.LEIDO_NOTIFICADO
                        notif.fecha_lectura = datetime.utcnow()
                        notif.fecha_notificacion_efectiva = notif.fecha_lectura
                        notif.origen_notificacion_efectiva = "LECTURA_VOLUNTARIA"
                        notif.mtc_payload_lectura = resp

                        # Cómputo de plazo
                        computo = evaluar_computo_notificacion(
                            fecha_deposito=notif.fecha_deposito,
                            fecha_lectura=notif.fecha_lectura,
                            plazo_dias_habiles=notif.plazo_dias_habiles or 15
                        )
                        if computo["fecha_inicio_computo"]:
                            notif.fecha_inicio_computo = datetime.combine(
                                computo["fecha_inicio_computo"], datetime.min.time(), tzinfo=timezone.utc
                            )
                        if computo["fecha_vencimiento_plazo"]:
                            notif.fecha_vencimiento_plazo = datetime.combine(
                                computo["fecha_vencimiento_plazo"], datetime.min.time(), tzinfo=timezone.utc
                            )
                        notif.estado_plazo = computo["estado_plazo"]

                        db.add(NotificacionBitacora(
                            notificacion_id=notif.id,
                            accion="LECTURA_EFECTIVA_MTC_WORKER",
                            estado_anterior=EstadoNotificacion.DEPOSITADO.value,
                            estado_nuevo=EstadoNotificacion.LEIDO_NOTIFICADO.value,
                            detalles={"sha256": sha256_hash, "id_mtc": id_mtc}
                        ))

                        await db.commit()
                        logger.info(f"Notificación {notif.codigo_expediente} (ID MTC {id_mtc}) sincronizada como LEÍDA.")
                    else:
                        # Evaluar si operó la Ficción Legal de 5 días hábiles sin apertura (DS 001-2020-MTC Art. 11)
                        computo = evaluar_computo_notificacion(
                            fecha_deposito=notif.fecha_deposito,
                            fecha_lectura=None,
                            plazo_dias_habiles=notif.plazo_dias_habiles or 15
                        )
                        if computo["es_ficcion_legal"]:
                            notif.estado = EstadoNotificacion.LEIDO_NOTIFICADO
                            notif.fecha_notificacion_efectiva = computo["fecha_notificacion_efectiva"]
                            notif.origen_notificacion_efectiva = "FICCION_LEGAL_5_DIAS"
                            if computo["fecha_inicio_computo"]:
                                notif.fecha_inicio_computo = datetime.combine(
                                    computo["fecha_inicio_computo"], datetime.min.time(), tzinfo=timezone.utc
                                )
                            if computo["fecha_vencimiento_plazo"]:
                                notif.fecha_vencimiento_plazo = datetime.combine(
                                    computo["fecha_vencimiento_plazo"], datetime.min.time(), tzinfo=timezone.utc
                                )
                            notif.estado_plazo = computo["estado_plazo"]

                            db.add(NotificacionBitacora(
                                notificacion_id=notif.id,
                                accion="NOTIFICACION_FICCION_LEGAL_5_DIAS",
                                estado_anterior=EstadoNotificacion.DEPOSITADO.value,
                                estado_nuevo=EstadoNotificacion.LEIDO_NOTIFICADO.value,
                                detalles={
                                    "motivo": "Transcurso de 5 días hábiles sin apertura (D.S. 001-2020-MTC Art. 11)",
                                    "fecha_vencimiento_plazo": str(notif.fecha_vencimiento_plazo)
                                }
                            ))
                            await db.commit()
                            logger.info(f"Notificación {notif.codigo_expediente} operó FICCIÓN LEGAL tras 5 días hábiles.")
                except Exception as e:
                    logger.warning(f"Worker: No se pudo verificar lectura de notificación ID MTC {id_mtc}: {e}")

        except Exception as e:
            logger.error(f"Error general en sync_worker: {e}")


async def iniciar_worker_loop():
    """Inicia el bucle continuo del worker de sincronización."""
    logger.info("Iniciando Worker de Sincronización de Constancias MTC...")
    while True:
        try:
            await sincronizar_constancias_pendientes()
        except Exception as e:
            logger.error(f"Excepción en bucle de worker: {e}")
        await asyncio.sleep(settings.MTC_POLLING_INTERVAL_SECONDS)
