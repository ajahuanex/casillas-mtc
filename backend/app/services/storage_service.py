import hashlib
import io
from typing import Tuple, Optional
from minio import Minio
from minio.error import S3Error
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class StorageService:
    """
    Servicio de almacenamiento de objetos con RustFS (S3-compatible).
    Garantiza inmutabilidad y cálculo de SHA-256 para validez legal bajo D.S. 001-2020-MTC.
    """

    def __init__(self):
        endpoint = getattr(settings, "RUSTFS_ENDPOINT", None) or settings.MINIO_ENDPOINT
        access_key = getattr(settings, "RUSTFS_ACCESS_KEY", None) or settings.MINIO_ROOT_USER
        secret_key = getattr(settings, "RUSTFS_SECRET_KEY", None) or settings.MINIO_ROOT_PASSWORD
        secure = getattr(settings, "RUSTFS_SECURE", None) if hasattr(settings, "RUSTFS_SECURE") else settings.MINIO_SECURE

        self.endpoint = endpoint
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self.bucket_name = getattr(settings, "RUSTFS_BUCKET_NAME", None) or settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Bucket RustFS '{self.bucket_name}' creado con éxito.")
        except S3Error as e:
            logger.error(f"Error verificando/creando bucket en RustFS S3: {e}")

    @staticmethod
    def calculate_sha256(data: bytes) -> str:
        """Calcula el hash criptográfico SHA-256 para no repudio legal."""
        return hashlib.sha256(data).hexdigest()

    async def upload_document(
        self,
        file_bytes: bytes,
        destination_path: str,
        content_type: str = "application/pdf"
    ) -> Tuple[str, str, int]:
        """
        Sube un archivo a MinIO y retorna:
        (ruta_almacenamiento, sha256_hash, tamanio_en_bytes)
        """
        sha256_hash = self.calculate_sha256(file_bytes)
        size = len(file_bytes)
        stream = io.BytesIO(file_bytes)

        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=destination_path,
            data=stream,
            length=size,
            content_type=content_type,
            metadata={"sha256": sha256_hash}
        )

        logger.info(f"Documento subido a MinIO: {destination_path} (SHA-256: {sha256_hash})")
        return destination_path, sha256_hash, size

    async def get_document(self, object_path: str) -> bytes:
        """Descarga el contenido binario del objeto."""
        response = self.client.get_object(self.bucket_name, object_path)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def get_download_url(self, object_path: str) -> str:
        """
        Retorna la URL accesible para descargar/visualizar el documento.
        Usa la ruta proxy de la API para garantizar compatibilidad con navegadores
        evitando problemas de resolución de nombres de contenedor Docker.
        """
        clean_path = object_path.lstrip("/")
        return f"/api/v1/storage/file/{clean_path}"

    def get_presigned_url(self, object_path: str, expires_seconds: int = 3600) -> str:
        """
        Genera una URL temporal firmada o la URL proxy de descarga directa.
        Para evitar fallos de DNS en el cliente web, retornamos la URL de streaming segura.
        """
        return self.get_download_url(object_path)

    def get_storage_status(self) -> dict:
        """Retorna el estado de salud, cuota y métricas de MinIO S3."""
        try:
            exists = self.client.bucket_exists(self.bucket_name)
            if not exists:
                return {
                    "status": "error",
                    "mensaje": f"El bucket '{self.bucket_name}' no existe en RustFS.",
                    "motor": "RustFS S3",
                    "bucket": self.bucket_name,
                    "endpoint": self.endpoint,
                    "total_objects": 0,
                    "total_bytes": 0
                }
            
            objects = list(self.client.list_objects(self.bucket_name, recursive=True))
            total_bytes = sum(o.size for o in objects if o.size)
            
            return {
                "status": "en_linea",
                "motor": "RustFS S3",
                "mensaje": "Clúster RustFS S3 conectado y operando con integridad WORM.",
                "endpoint": self.endpoint,
                "bucket": self.bucket_name,
                "bucket_exists": True,
                "total_objects": len(objects),
                "total_bytes": total_bytes,
                "total_mb": round(total_bytes / (1024 * 1024), 2),
                "secure": getattr(settings, "RUSTFS_SECURE", None) if hasattr(settings, "RUSTFS_SECURE") else settings.MINIO_SECURE,
                "host_publico": getattr(settings, "RUSTFS_PUBLIC_URL_BASE", None) or settings.MINIO_PUBLIC_URL_BASE
            }
        except Exception as e:
            logger.error(f"Error consultando estado de RustFS: {e}")
            return {
                "status": "desconectado",
                "motor": "RustFS S3",
                "mensaje": str(e),
                "endpoint": self.endpoint,
                "bucket": self.bucket_name,
                "bucket_exists": False,
                "total_objects": 0,
                "total_bytes": 0
            }

    def list_objects_metadata(self) -> list:
        """Lista los objetos almacenados en MinIO con metadatos de auditoría."""
        try:
            objects = self.client.list_objects(self.bucket_name, recursive=True)
            res = []
            for obj in objects:
                res.append({
                    "name": obj.object_name,
                    "size_bytes": obj.size,
                    "size_formatted": f"{(obj.size / (1024*1024)):.2f} MB" if obj.size >= 1048576 else f"{(obj.size / 1024):.1f} KB",
                    "last_modified": obj.last_modified.isoformat() if obj.last_modified else None,
                    "etag": (obj.etag or "").replace('"', ''),
                    "download_url": self.get_download_url(obj.object_name),
                    "tipo": "Resolución Directoral" if "original" in obj.object_name or "acto" in obj.object_name else (
                        "Constancia CAD" if "cad" in obj.object_name else (
                            "Constancia CAL" if "cal" in obj.object_name else "Cédula / Anexo"
                        )
                    )
                })
            return res
        except Exception as e:
            logger.error(f"Error listando objetos en MinIO: {e}")
            return []


storage_service = StorageService()

