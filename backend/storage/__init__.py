import logging

from storage.base import StorageBackend

logger = logging.getLogger(__name__)

_storage: StorageBackend | None = None


def get_storage() -> StorageBackend:
    """Factory singleton. Escolhe o backend via env STORAGE_BACKEND (gcs | local)."""
    global _storage
    if _storage is None:
        from core.config import settings
        backend = settings.STORAGE_BACKEND.lower()
        if backend == "local":
            from storage.local import LocalStorage
            _storage = LocalStorage()
            logger.info("Storage: LocalStorage (dev)")
        else:
            from storage.gcs import GCSStorage
            _storage = GCSStorage()
            logger.info("Storage: GCSStorage")
    return _storage
