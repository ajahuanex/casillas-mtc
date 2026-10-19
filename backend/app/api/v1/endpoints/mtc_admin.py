from fastapi import APIRouter, Depends, Header, HTTPException, status, Query
from typing import Optional, Dict, Any

from app.schemas.mtc_admin import (
    LoginAdminRequest,
    CaptchaResponse,
    SelectRolRequest,
    BuscarAdministradoResponse,
    ConsultaAutomaticaRequest
)
from app.services.mtc_admin_service import mtc_admin_service
from app.services.captcha_ocr_service import resolve_ocr

router = APIRouter()


@router.post("/captcha", response_model=CaptchaResponse)
async def obtener_captcha_endpoint(
    auto_resolve: bool = Query(True, description="Si es True, ejecuta OCR para resolver el texto del captcha")
) -> Dict[str, Any]:
    """
    Obtiene un nuevo Captcha del MTC (POST /ms-seguridad/seguridad/captcha)
    y opcionalmente resuelve el texto mediante OCR asegurando exactamente 6 caracteres.
    """
    b64_img = ""
    key = ""
    resolved = None

    if auto_resolve:
        # Intentar hasta 3 veces obtener un captcha que resuelva estrictamente a 6 caracteres
        for _ in range(3):
            captcha_data = await mtc_admin_service.obtener_captcha()
            b64_img = captcha_data.get("img", "")
            key = captcha_data.get("key", "")
            if b64_img:
                try:
                    candidate = resolve_ocr(b64_img, strict_6_chars=True)
                    if candidate and len(candidate) == 6:
                        resolved = candidate
                        break
                except Exception:
                    resolved = None
    else:
        captcha_data = await mtc_admin_service.obtener_captcha()
        b64_img = captcha_data.get("img", "")
        key = captcha_data.get("key", "")

    return {
        "img": b64_img,
        "key": key,
        "resolved_text": resolved
    }


@router.post("/ocr-solve")
async def resolver_ocr_endpoint(payload: Dict[str, str]) -> Dict[str, Any]:
    """
    Endpoint de utilidad para probar la función resolve_ocr directamente.
    Payload: {"base64_img": "..."}
    """
    b64 = payload.get("base64_img") or payload.get("img")
    if not b64:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar el campo 'base64_img' o 'img'."
        )
    
    try:
        texto = resolve_ocr(b64)
        return {
            "success": True,
            "captcha_text": texto,
            "length": len(texto)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al resolver OCR: {str(e)}"
        )


@router.post("/login")
async def login_admin(payload: LoginAdminRequest) -> Dict[str, Any]:
    """
    1. Si is_automatic es True, obtiene un captcha nuevo de la API MTC
       (POST /ms-seguridad/seguridad/captcha), resuelve la imagen con OCR
       y luego intenta el login.
    2. Si es False, usa captcha_text y captcha_key proporcionados por el usuario.
    3. El login se envía a https://wsapiadmcasilla.mtc.gob.pe/ms-seguridad/auth/login-admin-casilla.
    4. Maneja errores: si el OCR falla o el MTC devuelve 'captcha incorrecto',
       retorna un error 400 descriptivo.
    """
    resultado = await mtc_admin_service.login_admin(
        username=payload.username,
        password=payload.password,
        captcha_text=payload.captcha_text,
        captcha_key=payload.captcha_key,
        is_automatic=payload.is_automatic
    )
    return resultado


@router.get("/roles")
async def listar_roles(
    authorization: Optional[str] = Header(None, description="Bearer token obtenido en el login"),
    token: Optional[str] = Query(None, description="Token alternativo por Query param")
) -> Dict[str, Any]:
    """
    Usa el token del login para obtener la lista de roles desde:
    GET /ms-usuario/usuario/identity/roles-admin
    """
    bearer_token = token
    if authorization and authorization.lower().startswith("bearer "):
        bearer_token = authorization.split(" ", 1)[1]
    elif authorization:
        bearer_token = authorization

    if not bearer_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere el header 'Authorization: Bearer <token>' para listar roles."
        )

    roles = await mtc_admin_service.obtener_roles(token=bearer_token)
    return {
        "success": True,
        "message": "Roles obtenidos con éxito",
        "data": roles
    }


@router.post("/select-rol")
async def seleccionar_rol(
    payload: SelectRolRequest,
    authorization: Optional[str] = Header(None, description="Bearer token obtenido en el login"),
    token: Optional[str] = Query(None, description="Token alternativo por Query param")
) -> Dict[str, Any]:
    """
    Recibe el idRol, llama a /ms-seguridad/auth/login-rol-admin-casilla
    y devuelve el nuevo accessToken final.
    """
    bearer_token = token
    if authorization and authorization.lower().startswith("bearer "):
        bearer_token = authorization.split(" ", 1)[1]
    elif authorization:
        bearer_token = authorization

    if not bearer_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere el header 'Authorization: Bearer <token>' para seleccionar rol."
        )

    resultado = await mtc_admin_service.seleccionar_rol(
        id_rol=payload.idRol,
        token=bearer_token
    )
    return resultado


@router.get("/buscar/{termino}", response_model=BuscarAdministradoResponse)
async def buscar_administrado(
    termino: str,
    authorization: Optional[str] = Header(None, description="Bearer token de rol"),
    token: Optional[str] = Query(None, description="Token alternativo por Query param")
) -> Dict[str, Any]:
    """
    Recibe un DNI o RUC y realiza la consulta GET al endpoint de búsqueda de
    administrados usando el token de rol. Entrega el objeto 'data' limpio
    que contiene la información del administrado conforme al esquema solicitado.
    """
    bearer_token = token or "token_autorizado"
    if authorization and authorization.lower().startswith("bearer "):
        bearer_token = authorization.split(" ", 1)[1]
    elif authorization:
        bearer_token = authorization

    resultado = await mtc_admin_service.buscar_administrado(
        termino=termino,
        token_rol=bearer_token
    )
    return resultado


@router.get("/session-status")
async def consultar_estado_sesion() -> Dict[str, Any]:
    """
    Informa si las credenciales temporales de sesión MTC siguen activas en memoria,
    cuántos minutos restan de vigencia y si se requerirá resolver Captcha en la próxima consulta.
    """
    return mtc_admin_service.get_session_status()


@router.post("/logout-session")
async def cerrar_sesion_mtc() -> Dict[str, Any]:
    """
    Invalida manualmente la sesión en caché forzando una nueva autenticación con Captcha.
    """
    mtc_admin_service.clear_session()
    return {
        "success": True,
        "message": "Sesión temporal de MTC invalidada con éxito."
    }


@router.post("/consulta-automatica")
async def consulta_automatica_endpoint(payload: ConsultaAutomaticaRequest) -> Dict[str, Any]:
    """
    Endpoint todo-en-uno que realiza el flujo optimizado de consulta:
    1. Si la sesión previa está activa (vigente por ~50 min), omite el Captcha y consulta directo.
    2. Si no hay sesión o expiró:
       - Si el usuario envió captcha_text + captcha_key, utiliza el ingreso manual.
       - Si no, ejecuta OCR automático con un límite estricto de máximo 2 intentos.
    3. Retorna la información limpia del administrado junto con el estado de la sesión.
    """
    resultado = await mtc_admin_service.consulta_automatica(
        target_doc=payload.target_doc,
        username=payload.username or "40396522",
        password=payload.password or "Ajahuana40396522%",
        id_rol=payload.id_rol or "1",
        captcha_text=payload.captcha_text,
        captcha_key=payload.captcha_key,
        force_refresh=payload.force_refresh
    )
    return resultado
