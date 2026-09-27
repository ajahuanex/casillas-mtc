from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
import uuid
import base64
from datetime import datetime

from app.db.session import get_db
from app.models.entities import (
    Notificacion, NotificacionDocumento, CasillaMTC, Administrado,
    AcuseMTC, NotificacionBitacora
)
from app.models.enums import (
    EstadoNotificacion, TipoDocumentoAdjunto, TipoAcuse,
    TipoDocumentoIdentidad, EstadoCasilla
)
from app.schemas.notificacion import NotificacionResponse
from app.services.storage_service import storage_service
from app.integrations.mtc.client import mtc_client, MTCIntegrationError

router = APIRouter()


@router.get("/", response_model=List[NotificacionResponse])
async def listar_notificaciones(
    estado: Optional[EstadoNotificacion] = None,
    codigo_expediente: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Lista las notificaciones con sus relaciones y estados legales."""
    query = (
        select(Notificacion)
        .options(
            selectinload(Notificacion.casilla),
            selectinload(Notificacion.documentos),
            selectinload(Notificacion.acuses)
        )
        .order_by(Notificacion.created_at.desc())
    )
    if estado:
        query = query.where(Notificacion.estado == estado)
    if codigo_expediente:
        query = query.where(Notificacion.codigo_expediente.ilike(f"%{codigo_expediente}%"))

    result = await db.execute(query)
    notificaciones = result.scalars().all()

    for notif in notificaciones:
        for doc in notif.documentos:
            doc.download_url = storage_service.get_presigned_url(doc.storage_path)
        for acuse in notif.acuses:
            acuse.download_url = storage_service.get_presigned_url(acuse.storage_path)

    return notificaciones


@router.get("/verificar-casilla")
async def verificar_casilla(
    numero_documento: str,
    tipo_persona: str = "00001",
    tipo_documento: str = "00002"
):
    """
    2. Verificar estado casilla.
    Consulta el endpoint oficial GET /verificar-estado-casilla del MTC.
    """
    try:
        resultado = await mtc_client.verificar_estado_casilla(
            nro_documento=numero_documento,
            cod_tipo_persona=tipo_persona,
            cod_tipo_documento=tipo_documento
        )
        return resultado
    except MTCIntegrationError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/", response_model=NotificacionResponse, status_code=status.HTTP_201_CREATED)
async def crear_notificacion(
    codigo_expediente: str = Form(...),
    numero_acto_administrativo: str = Form(...),
    asunto: str = Form(...),
    descripcion: Optional[str] = Form(None),
    tipo_documento_destinatario: TipoDocumentoIdentidad = Form(...),
    numero_documento_destinatario: str = Form(...),
    nombre_destinatario: str = Form(...),
    archivo: UploadFile = File(..., description="Documento PDF del acto administrativo"),
    db: AsyncSession = Depends(get_db)
):
    """
    Registra el acto administrativo en estado BORRADOR, custodiando el PDF original en MinIO
    y calculando el hash criptográfico SHA-256 para validez legal.
    """
    if archivo.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="El archivo adjunto debe ser en formato PDF.")

    # 1. Administrado
    result_admin = await db.execute(
        select(Administrado).where(Administrado.numero_documento == numero_documento_destinatario)
    )
    administrado = result_admin.scalar_one_or_none()

    if not administrado:
        administrado = Administrado(
            tipo_documento=tipo_documento_destinatario,
            numero_documento=numero_documento_destinatario,
            razon_social_o_nombre=nombre_destinatario
        )
        db.add(administrado)
        await db.flush()

    # 2. Casilla MTC
    result_casilla = await db.execute(
        select(CasillaMTC).where(CasillaMTC.administrado_id == administrado.id)
    )
    casilla = result_casilla.scalar_one_or_none()
    if not casilla:
        casilla = CasillaMTC(
            administrado_id=administrado.id,
            codigo_casilla=f"CAS-{numero_documento_destinatario}",
            estado_casilla=EstadoCasilla.ACTIVA
        )
        db.add(casilla)
        await db.flush()

    # 3. Almacenamiento en MinIO y cálculo de SHA-256
    file_bytes = await archivo.read()
    notif_id = uuid.uuid4()
    storage_path = f"notificaciones/{notif_id}/original_{archivo.filename}"
    
    saved_path, sha256_hash, file_size = await storage_service.upload_document(
        file_bytes=file_bytes,
        destination_path=storage_path,
        content_type="application/pdf"
    )

    # 4. Notificación
    notificacion = Notificacion(
        id=notif_id,
        codigo_expediente=codigo_expediente,
        numero_acto_administrativo=numero_acto_administrativo,
        asunto=asunto,
        descripcion=descripcion,
        casilla_id=casilla.id,
        estado=EstadoNotificacion.BORRADOR
    )
    db.add(notificacion)

    # 5. Documento
    doc = NotificacionDocumento(
        notificacion_id=notificacion.id,
        tipo_documento=TipoDocumentoAdjunto.ACTO_ADMINISTRATIVO_ORIGINAL,
        nombre_archivo=archivo.filename,
        storage_path=saved_path,
        sha256_hash=sha256_hash,
        tamanio_bytes=file_size,
        mime_type="application/pdf"
    )
    db.add(doc)

    # 6. Bitácora de auditoría
    db.add(NotificacionBitacora(
        notificacion_id=notificacion.id,
        accion="CREACION_NOTIFICACION",
        estado_nuevo=EstadoNotificacion.BORRADOR.value,
        detalles={"archivo": archivo.filename, "sha256": sha256_hash}
    ))

    await db.commit()
    await db.refresh(notificacion)

    return await obtener_notificacion_por_id(notificacion.id, db)


@router.post("/{notificacion_id}/depositar", response_model=NotificacionResponse)
async def depositar_en_casilla_mtc(
    notificacion_id: uuid.UUID,
    id_categoria: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """
    4. Notificaciones externas.
    Deposita formalmente la notificación en la Casilla Electrónica MTC vía POST /notificaciones-externas.
    Obtiene idNotificacion y constanciaDeposito oficial emitido por el MTC.
    """
    notif = await _get_notificacion_or_404(notificacion_id, db)

    # 1. Obtener documento principal a notificar
    doc_adjunto = next(
        (d for d in notif.documentos if d.tipo_documento == TipoDocumentoAdjunto.DOCUMENTO_FIRMADO),
        None
    ) or next(
        (d for d in notif.documentos if d.tipo_documento == TipoDocumentoAdjunto.ACTO_ADMINISTRATIVO_ORIGINAL),
        None
    )

    if not doc_adjunto:
        raise HTTPException(status_code=400, detail="No se encontró documento PDF para adjuntar a la notificación.")

    # 2. Generar URL de descarga para que el servidor MTC recoja el PDF desde MinIO
    presigned_url = storage_service.get_presigned_url(doc_adjunto.storage_path, expires_seconds=86400)

    # 3. Extraer datos del destinatario
    administrado = notif.casilla.administrado if notif.casilla else None
    nro_doc = administrado.numero_documento if administrado else "00000000"
    cod_tipo_doc = "00002" if administrado and administrado.tipo_documento == TipoDocumentoIdentidad.DNI else "00001"

    # Construir mensaje HTML para la casilla
    cuerpo_html = f"""<p>Por medio de la presente, la Entidad le notifica formalmente el acto administrativo <strong>{notif.numero_acto_administrativo}</strong> (Expediente: {notif.codigo_expediente}).</p>
    <p><strong>Asunto:</strong> {notif.asunto}</p>
    <p>{notif.descripcion or ''}</p>"""

    adjuntos_payload = [
        {
            "url": presigned_url,
            "nombreArchivo": doc_adjunto.nombre_archivo
        }
    ]

    try:
        # Invocar POST /notificaciones-externas oficial del MTC
        resp_deposito = await mtc_client.registrar_notificacion_externa(
            nro_documento=nro_doc,
            asunto=notif.asunto,
            mensaje_html=cuerpo_html,
            adjuntos=adjuntos_payload,
            cod_tipo_persona="00001",
            cod_tipo_documento=cod_tipo_doc,
            id_categoria=id_categoria,
            con_sello_tiempo=True
        )
    except MTCIntegrationError as e:
        raise HTTPException(status_code=502, detail=f"Falla en depósito con MTC: {str(e)}")

    data_mtc = resp_deposito.get("data", {})
    id_notificacion_mtc = str(data_mtc.get("idNotificacion") or uuid.uuid4())
    constancia_deposito_uuid = data_mtc.get("constanciaDeposito", id_notificacion_mtc)

    notif.id_transaccion_mtc = id_notificacion_mtc
    notif.fecha_deposito = datetime.utcnow()
    notif.estado = EstadoNotificacion.DEPOSITADO
    notif.mtc_payload_deposito = resp_deposito

    # 4. Registrar Acuse de Depósito Oficial
    acuse_db = AcuseMTC(
        notificacion_id=notif.id,
        tipo_acuse=TipoAcuse.DEPOSITO,
        codigo_verificacion_mtc=constancia_deposito_uuid,
        storage_path=doc_adjunto.storage_path,
        sha256_hash=doc_adjunto.sha256_hash,
        fecha_hora_mtc=datetime.utcnow(),
        datos_tecnicos_mtc=resp_deposito
    )
    db.add(acuse_db)

    # 5. Bitácora de auditoría legal
    db.add(NotificacionBitacora(
        notificacion_id=notif.id,
        accion="DEPOSITO_CASILLA_MTC",
        estado_anterior=notif.estado.value,
        estado_nuevo=EstadoNotificacion.DEPOSITADO.value,
        detalles={"id_notificacion_mtc": id_notificacion_mtc, "constancia_deposito": constancia_deposito_uuid}
    ))

    await db.commit()
    return await obtener_notificacion_por_id(notif.id, db)


@router.post("/{notificacion_id}/sincronizar-constancias", response_model=NotificacionResponse)
async def sincronizar_constancias_mtc(
    notificacion_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    5. Constancias (Depósito y Lectura).
    Consulta el endpoint oficial GET /notificaciones/constancias/{idNotificacion}?tipo=base64
    para recuperar la constancia de lectura cuando el administrado la abre en su casilla.
    """
    notif = await _get_notificacion_or_404(notificacion_id, db)

    if not notif.id_transaccion_mtc or not notif.id_transaccion_mtc.isdigit():
        raise HTTPException(
            status_code=400,
            detail="La notificación no cuenta con un ID numérico de MTC para consultar constancias."
        )

    try:
        resp = await mtc_client.obtener_constancias(int(notif.id_transaccion_mtc), tipo="base64")
    except MTCIntegrationError as e:
        raise HTTPException(status_code=502, detail=f"Error consultando constancias en MTC: {str(e)}")

    data = resp.get("data", {})
    constancia_lectura_b64 = data.get("constanciaLectura")

    # Si ya se emitió la constancia de lectura por el MTC
    if constancia_lectura_b64:
        try:
            pdf_bytes = base64.b64decode(constancia_lectura_b64)
            storage_path = f"notificaciones/{notif.id}/acuses/acuse_lectura.pdf"
            saved_path, sha256_hash, _ = await storage_service.upload_document(
                file_bytes=pdf_bytes,
                destination_path=storage_path,
                content_type="application/pdf"
            )

            # Verificar si ya existe en BD para no duplicar
            existe_acuse = any(a.tipo_acuse == TipoAcuse.LECTURA_NOTIFICACION for a in notif.acuses)
            if not existe_acuse:
                acuse_lectura = AcuseMTC(
                    notificacion_id=notif.id,
                    tipo_acuse=TipoAcuse.LECTURA_NOTIFICACION,
                    codigo_verificacion_mtc=f"LEC-{notif.id_transaccion_mtc}",
                    storage_path=saved_path,
                    sha256_hash=sha256_hash,
                    fecha_hora_mtc=datetime.utcnow(),
                    datos_tecnicos_mtc=data
                )
                db.add(acuse_lectura)

            notif.estado = EstadoNotificacion.LEIDO_NOTIFICADO
            notif.fecha_notificacion_efectiva = datetime.utcnow()
            notif.mtc_payload_lectura = resp

            db.add(NotificacionBitacora(
                notificacion_id=notif.id,
                accion="LECTURA_EFECTIVA_MTC",
                estado_anterior=EstadoNotificacion.DEPOSITADO.value,
                estado_nuevo=EstadoNotificacion.LEIDO_NOTIFICADO.value,
                detalles={"sha256_lectura": sha256_hash}
            ))

            await db.commit()
        except Exception as e:
            logger.error(f"Error procesando PDF de constancia de lectura: {e}")
            raise HTTPException(status_code=500, detail="Error al decodificar la constancia de lectura.")

    return await obtener_notificacion_por_id(notif.id, db)


async def _get_notificacion_or_404(notificacion_id: uuid.UUID, db: AsyncSession) -> Notificacion:
    query = (
        select(Notificacion)
        .options(
            selectinload(Notificacion.casilla).selectinload(CasillaMTC.administrado),
            selectinload(Notificacion.documentos),
            selectinload(Notificacion.acuses)
        )
        .where(Notificacion.id == notificacion_id)
    )
    result = await db.execute(query)
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="Notificación no encontrada.")
    return notif


async def obtener_notificacion_por_id(notificacion_id: uuid.UUID, db: AsyncSession) -> Notificacion:
    notif = await _get_notificacion_or_404(notificacion_id, db)
    for doc in notif.documentos:
        doc.download_url = storage_service.get_presigned_url(doc.storage_path)
    for acuse in notif.acuses:
        acuse.download_url = storage_service.get_presigned_url(acuse.storage_path)
    return notif
