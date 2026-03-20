import logging

from core.config import settings
from storage.base import StorageBackend

logger = logging.getLogger(__name__)


class GCSStorage(StorageBackend):
    """Implementação GCS usando Application Default Credentials (SA da VM).
    Conexão é lazy — só abre na primeira operação, não no import.
    """

    def __init__(self):
        self._client = None
        self._bucket = None

    def _ensure_connected(self):
        if self._client is None:
            from google.cloud import storage as gcs
            self._client = gcs.Client(project=settings.GCS_PROJECT_ID)
            self._bucket = self._client.bucket(settings.GCS_BUCKET_NAME)
            logger.info(
                "GCS conectado: projeto=%s bucket=%s",
                settings.GCS_PROJECT_ID,
                settings.GCS_BUCKET_NAME,
            )

    def upload(self, source_path: str, destination_key: str) -> str:
        self._ensure_connected()
        blob = self._bucket.blob(destination_key)
        blob.upload_from_filename(source_path)
        logger.info("GCS upload: %s -> gs://%s/%s", source_path, settings.GCS_BUCKET_NAME, destination_key)
        return destination_key

    def download(self, key: str, destination_path: str) -> None:
        self._ensure_connected()
        blob = self._bucket.blob(key)
        blob.download_to_filename(destination_path)
        logger.info("GCS download: gs://%s/%s -> %s", settings.GCS_BUCKET_NAME, key, destination_path)

    def read_bytes(self, key: str) -> bytes:
        self._ensure_connected()
        blob = self._bucket.blob(key)
        return blob.download_as_bytes()

    def delete(self, key: str) -> None:
        self._ensure_connected()
        blob = self._bucket.blob(key)
        blob.delete()
        logger.info("GCS delete: gs://%s/%s", settings.GCS_BUCKET_NAME, key)
