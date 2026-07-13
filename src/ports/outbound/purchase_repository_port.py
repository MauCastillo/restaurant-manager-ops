from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models.purchase import Purchase


class PurchaseRepositoryPort(ABC):
    """Outbound port interface for Purchase persistence."""

    @abstractmethod
    def save(self, purchase: Purchase) -> Purchase:
        """Create or update a Purchase entity."""
        pass

    @abstractmethod
    def find_by_id(self, purchase_id: int) -> Optional[Purchase]:
        """Find a Purchase by ID."""
        pass

    @abstractmethod
    def find_by_client_id(self, client_id: int) -> List[Purchase]:
        """List all purchases belonging to a specific client."""
        pass

    @abstractmethod
    def list_all(self) -> List[Purchase]:
        """List all purchases across all clients."""
        pass

    @abstractmethod
    def delete(self, purchase_id: int) -> bool:
        """Delete a Purchase record."""
        pass

    @abstractmethod
    def get_total_monto_by_client(self, client_id: int) -> float:
        """Calculate the total amount of purchases for a client."""
        pass
