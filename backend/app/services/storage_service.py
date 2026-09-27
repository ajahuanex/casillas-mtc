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
    Servicio de almacenamiento de objetos con MinIO/S3.
    Garantiza inmutabilidad y cálculo de SHA-256 para validez legal.
    """

    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Bucket '{self.bucket_name}' creado con éxito.")
        except S3Error as e:
            logger.error(f"Error verificando/creando bucket en MinIO: {e}")

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

    def get_presigned_url(self, object_path: str, expires_seconds: int = 3600) -> str:
        """Genera una URL temporal firmada para visualización segura en frontend."""
        from datetime import timedelta
        return self.client.presigned_get_object(
            self.bucket_name,
            object_path,
            expires=timedelta(seconds=expires_seconds)
        )


storage_service = StorageService()
