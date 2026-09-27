from fastapi import APIRouter
from app.api.v1.endpoints import notificaciones

api_router = APIRouter()
api_router.include_router(notificaciones.router, prefix="/notificaciones", tags=["Notificaciones"])
