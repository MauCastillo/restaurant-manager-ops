from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models.client import Client


class ClientRepositoryPort(ABC):
    """Outbound port interface for Client persistence."""

    @abstractmethod
    def save(self, client: Client) -> Client:
        """Create or update a Client entity."""
        pass

    @abstractmethod
    def find_by_id(self, client_id: int) -> Optional[Client]:
        """Find a Client by ID."""
        pass

    @abstractmethod
    def find_by_cedula(self, cedula: str) -> Optional[Client]:
        """Find a Client by unique Cédula."""
        pass

    @abstractmethod
    def list_all(self, search_query: str = "") -> List[Client]:
        """List clients optionally filtered by search term (nombre or cedula)."""
        pass

    @abstractmethod
    def delete(self, client_id: int) -> bool:
        """Delete a Client by ID."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Return total number of registered clients."""
        pass
