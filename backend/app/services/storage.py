"""MinIO storage service for document management."""

import io
import logging
import uuid
from datetime import timedelta
from typing import Optional

from minio import Minio
from minio.error import S3Error

from app.config import get_settings

logger = logging.getLogger(__name__)

_storage_service: Optional["StorageService"] = None


class StorageService:
    """Service for managing file storage in MinIO."""

    def __init__(self):
        settings = get_settings()
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self.bucket = settings.minio_bucket

    def ensure_bucket(self) -> None:
        """Create bucket if it doesn't exist."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info("Bucket '%s' created successfully.", self.bucket)
            else:
                logger.debug("Bucket '%s' already exists.", self.bucket)
        except S3Error as e:
            logger.error("Failed to ensure bucket '%s': %s", self.bucket, e)
            raise

    def upload_file(
        self,
        filename: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload a file to MinIO.

        Generates a unique stored filename with a UUID prefix to avoid
        collisions while preserving the original extension.

        Args:
            filename: Original filename (used for extension extraction).
            data: Raw file bytes to upload.
            content_type: MIME type of the file.

        Returns:
            The stored filename (UUID-prefixed) in the bucket.
        """
        # Build a unique stored filename: <uuid>_<original_filename>
        stored_filename = f"{uuid.uuid4().hex}_{filename}"

        try:
            self.ensure_bucket()
            data_stream = io.BytesIO(data)
            data_length = len(data)

            self.client.put_object(
                self.bucket,
                stored_filename,
                data_stream,
                length=data_length,
                content_type=content_type,
            )
            logger.info(
                "File '%s' uploaded as '%s' (%d bytes).",
                filename,
                stored_filename,
                data_length,
            )
            return stored_filename
        except S3Error as e:
            logger.error("Failed to upload file '%s': %s", filename, e)
            raise

    def download_file(self, filename: str) -> bytes:
        """Download a file from MinIO.

        Args:
            filename: The stored filename in the bucket.

        Returns:
            The raw bytes of the file.
        """
        response = None
        try:
            response = self.client.get_object(self.bucket, filename)
            data = response.read()
            logger.info(
                "File '%s' downloaded (%d bytes).", filename, len(data)
            )
            return data
        except S3Error as e:
            logger.error("Failed to download file '%s': %s", filename, e)
            raise
        finally:
            if response is not None:
                response.close()
                response.release_conn()

    def delete_file(self, filename: str) -> bool:
        """Delete a file from MinIO.

        Args:
            filename: The stored filename in the bucket.

        Returns:
            True if deletion succeeded, False otherwise.
        """
        try:
            self.client.remove_object(self.bucket, filename)
            logger.info("File '%s' deleted.", filename)
            return True
        except S3Error as e:
            logger.error("Failed to delete file '%s': %s", filename, e)
            return False

    def get_presigned_url(
        self, filename: str, expires_hours: int = 1
    ) -> str:
        """Get a presigned URL for temporary access to a file.

        Args:
            filename: The stored filename in the bucket.
            expires_hours: Number of hours the URL remains valid.

        Returns:
            A presigned URL string.
        """
        try:
            url = self.client.presigned_get_object(
                self.bucket,
                filename,
                expires=timedelta(hours=expires_hours),
            )
            logger.info(
                "Presigned URL generated for '%s' (expires in %dh).",
                filename,
                expires_hours,
            )
            return url
        except S3Error as e:
            logger.error(
                "Failed to generate presigned URL for '%s': %s",
                filename,
                e,
            )
            raise


def get_storage_service() -> StorageService:
    """Get storage service singleton.

    Returns:
        A shared StorageService instance.
    """
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
