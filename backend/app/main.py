from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
# Import all entities to register them with metadata
import app.models.entities # noqa


import asyncio
from app.workers.sync_worker import iniciar_worker_loop

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Crear tablas si estamos en desarrollo
    if settings.ENVIRONMENT == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
    # Iniciar Worker en segundo plano para sondeo de constancias de lectura MTC
    worker_task = asyncio.create_task(iniciar_worker_loop())
    yield
    # Shutdown
    worker_task.cancel()
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    version="1.0.0",
    description="Sistema de Notificaciones Administrativas con integración a la Casilla Electrónica del MTC."
)

# CORS para comunicación con el frontend en Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "minio_endpoint": settings.MINIO_ENDPOINT,
        "mtc_endpoint": settings.MTC_BASE_URL
    }


from app.api.v1.router import api_router

# Router principal
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get(f"{settings.API_V1_STR}/", tags=["Root"])
async def root():
    return {"message": "API de Casillas Electrónicas MTC operativa"}
