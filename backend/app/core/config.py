from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "Sistema de Notificaciones - Casilla Electrónica MTC / GORE PUNO"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "cambiar_esta_clave_secreta_super_segura_para_jwt_en_produccion"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # PostgreSQL
    POSTGRES_USER: str = "casillas_user"
    POSTGRES_PASSWORD: str = "casillas_secret_pass"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "casillas_db"
    DATABASE_URL: Optional[str] = None

    @computed_field
    def async_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Almacenamiento de Objetos RustFS / S3 (High-Performance Rust Object Storage)
    STORAGE_TYPE: str = "rustfs"
    RUSTFS_ENDPOINT: str = "rustfs:9000"
    RUSTFS_ACCESS_KEY: str = "rustfsadmin"
    RUSTFS_SECRET_KEY: str = "rustfsadmin123"
    RUSTFS_BUCKET_NAME: str = "casillas-notificaciones"
    RUSTFS_SECURE: bool = False
    RUSTFS_PUBLIC_URL_BASE: str = "http://localhost:9000"

    # Backward compatibility / aliases con MinIO
    MINIO_ENDPOINT: str = "rustfs:9000"
    MINIO_ROOT_USER: str = "rustfsadmin"
    MINIO_ROOT_PASSWORD: str = "rustfsadmin123"
    MINIO_BUCKET_NAME: str = "casillas-notificaciones"
    MINIO_SECURE: bool = False
    MINIO_PUBLIC_URL_BASE: str = "http://localhost:9000"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # API Casillas Electrónicas Oficial MTC (Oficina de Desarrollo Tecnológico y Digital)
    MTC_BASE_URL: str = "https://wscasilla.mtc.gob.pe/ms-notific/v2/servicios-publicos"
    MTC_ADMIN_BASE_URL: str = "https://wsapiadmcasilla.mtc.gob.pe"
    MTC_CLIENT_ID: str = "e8c61edc-f33b-4b64-b241-a2bc85c73402"
    MTC_CLIENT_SECRET: str = "wqetekyaQHPK3QwAksSKuNofH0Cp5kIzBwht8lC3VC6XdRTjTZysTEwJEfAGCyWi0FSGDUPXEAMl6dTBli9tBqrStLTmh8fj3b7whBaSUnHGvE6LYTIUuMgjjphqeiqJ"
    MTC_GRANT_TYPE: str = "authorization_code"
    MTC_POLLING_INTERVAL_SECONDS: int = 180

    # API Casillas Electrónicas Oficial DRTC Puno (Node-RED)
    # Desarrollo: casillas.transportespuno.gob.pe | Producción: mtc.transportespuno.gob.pe
    MTC_DRTC_DEV_URL: str = "https://casillas.transportespuno.gob.pe/api/v2"
    MTC_DRTC_PROD_URL: str = "https://mtc.transportespuno.gob.pe/api/v2"
    MTC_DRTC_BASE_URL: str = "https://casillas.transportespuno.gob.pe/api/v2"
    MTC_DRTC_API_KEY: str = "topSecret123"

    @computed_field
    def drtc_resolved_url(self) -> str:
        if self.ENVIRONMENT == "production":
            return self.MTC_DRTC_PROD_URL
        return self.MTC_DRTC_BASE_URL


settings = Settings()
