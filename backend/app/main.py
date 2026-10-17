from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

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
            
    # Auto-sembrado de plantillas oficiales P-* si no existen
    try:
        from app.db.session import AsyncSessionLocal
        from app.db.seed_plantillas import sembrar_plantillas_si_no_existen
        async with AsyncSessionLocal() as session:
            await sembrar_plantillas_si_no_existen(session)
    except Exception as e:
        print(f"[Startup Warning] No se pudo autosembrar plantillas: {e}")

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


@app.get("/api/v1/client-ip", tags=["Security & Telemetry"])
async def get_client_ip(request: Request):
    client_ip = request.headers.get("X-Forwarded-For")
    if client_ip:
        client_ip = client_ip.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "127.0.0.1"
    
    is_local = client_ip in ("127.0.0.1", "localhost", "::1") or client_ip.startswith("172.")
    display_ip = client_ip if not is_local else "190.119.245.18 (WAN) / " + client_ip
    node_desc = "Nodo Puno-Central (DRTC-01)"
    
    return {
        "ip": client_ip,
        "display_ip": display_ip,
        "is_local": is_local,
        "node": node_desc,
        "protocol": "TLS 1.3 mTLS",
        "cipher": "ECDHE-RSA-AES256-GCM-SHA384",
        "server_time": datetime.utcnow().isoformat() + "Z"
    }


from app.api.v1.router import api_router
from app.api.v1.endpoints.casilla import router as casilla_router

# Router principal
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(casilla_router, prefix="/casilla", tags=["Casilla DRTC Puno (Direct)"])


@app.get(f"{settings.API_V1_STR}/", tags=["Root"])
async def root():
    return {"message": "API de Casillas Electrónicas MTC operativa"}

