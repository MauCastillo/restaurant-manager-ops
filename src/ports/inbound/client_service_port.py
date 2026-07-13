from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from src.domain.models.client import Client


class ClientServicePort(ABC):
    """Primary inbound port for client registration and management."""

    @abstractmethod
    def register_client(self, nombre: str, cedula: str, proceso_desempeno: str, valor_a_descontar: float) -> Client:
        """Register a new client."""
        pass

    @abstractmethod
    def update_client(self, client_id: int, nombre: str, cedula: str, proceso_desempeno: str, valor_a_descontar: float) -> Client:
        """Update an existing client."""
        pass

    @abstractmethod
    def get_client(self, client_id: int) -> Optional[Client]:
        """Get a client by ID."""
        pass

    @abstractmethod
    def get_client_by_cedula(self, cedula: str) -> Optional[Client]:
        """Get a client by unique national ID / cédula."""
        pass

    @abstractmethod
    def list_clients(self, search_query: str = "") -> List[Client]:
        """List clients matching optional search query."""
        pass

    @abstractmethod
    def delete_client(self, client_id: int) -> bool:
        """Delete a client."""
        pass

    @abstractmethod
    def import_from_html_file(self, file_path: str) -> Tuple[int, int]:
        """Parse and register clients from Consulta.html file. Returns (imported_count, skipped_count)."""
        pass
