from fastapi import APIRouter
from app.api.v1.endpoints import notificaciones, dashboard, storage, casilla, plantillas, mtc_admin

api_router = APIRouter()
api_router.include_router(notificaciones.router, prefix="/notificaciones", tags=["Notificaciones"])
api_router.include_router(plantillas.router, prefix="/plantillas", tags=["Plantillas de Notificaciones"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(storage.router, prefix="/storage", tags=["Bóveda RustFS S3"])
api_router.include_router(casilla.router, prefix="/casilla", tags=["Casilla DRTC Puno"])
api_router.include_router(mtc_admin.router, prefix="/mtc-admin", tags=["MTC Admin Casilla"])
api_router.include_router(mtc_admin.router, prefix="", tags=["MTC Admin Casilla (Raíz)"])


