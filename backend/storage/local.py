import logging
import os
import shutil

from storage.base import StorageBackend

logger = logging.getLogger(__name__)


class LocalStorage(StorageBackend):
    """Storage local em disco — para desenvolvimento sem GCS.
    Ativa via env: STORAGE_BACKEND=local
    """

    def __init__(self, base_dir: str | None = None):
        if base_dir is None:
            from core.config import settings
            base_dir = settings.LOCAL_STORAGE_DIR
        self._base = base_dir
        os.makedirs(self._base, exist_ok=True)
        logger.info("LocalStorage inicializado em %s", self._base)

    def _path(self, key: str) -> str:
        full_path = os.path.join(self._base, key)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        return full_path

    def upload(self, source_path: str, destination_key: str) -> str:
        dest = self._path(destination_key)
        shutil.copy2(source_path, dest)
        logger.info("LocalStorage upload: %s -> %s", source_path, dest)
        return destination_key

    def download(self, key: str, destination_path: str) -> None:
        src = self._path(key)
        shutil.copy2(src, destination_path)
        logger.info("LocalStorage download: %s -> %s", src, destination_path)

    def read_bytes(self, key: str) -> bytes:
        with open(self._path(key), "rb") as f:
            return f.read()

    def delete(self, key: str) -> None:
        path = self._path(key)
        if os.path.exists(path):
            os.remove(path)
            logger.info("LocalStorage delete: %s", path)
