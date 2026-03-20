from abc import ABC, abstractmethod


class StorageBackend(ABC):
    """Interface abstrata de storage. Trocar implementação sem alterar contratos."""

    @abstractmethod
    def upload(self, source_path: str, destination_key: str) -> str:
        """Faz upload de um arquivo local para o storage. Retorna a key."""

    @abstractmethod
    def download(self, key: str, destination_path: str) -> None:
        """Baixa um arquivo do storage para um path local."""

    @abstractmethod
    def read_bytes(self, key: str) -> bytes:
        """Lê o conteúdo de um arquivo como bytes."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove um arquivo do storage."""
