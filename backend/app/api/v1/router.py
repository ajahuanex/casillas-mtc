from fastapi import APIRouter
from app.api.v1.endpoints import notificaciones, dashboard, storage, casilla, plantillas

api_router = APIRouter()
api_router.include_router(notificaciones.router, prefix="/notificaciones", tags=["Notificaciones"])
api_router.include_router(plantillas.router, prefix="/plantillas", tags=["Plantillas de Notificaciones"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(storage.router, prefix="/storage", tags=["Bóveda MinIO S3"])
api_router.include_router(casilla.router, prefix="/casilla", tags=["Casilla DRTC Puno"])


