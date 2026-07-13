from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from src.domain.models.purchase import Purchase


class PurchaseServicePort(ABC):
    """Primary inbound port for client purchase / buy registration and management."""

    @abstractmethod
    def register_purchase(self, client_id: int, concepto: str, monto: float, fecha_compra: str, notas: str = "") -> Purchase:
        """Create a new buy record for a client."""
        pass

    @abstractmethod
    def get_purchases_by_client(self, client_id: int) -> List[Purchase]:
        """List all buy records for a client."""
        pass

    @abstractmethod
    def list_all_purchases(self) -> List[Purchase]:
        """List all recorded purchases."""
        pass

    @abstractmethod
    def delete_purchase(self, purchase_id: int) -> bool:
        """Delete a purchase record."""
        pass

    @abstractmethod
    def get_client_financial_summary(self, client_id: int) -> Dict[str, float]:
        """Return financial summary for a client: base discount value, total purchases, and net total."""
        pass
