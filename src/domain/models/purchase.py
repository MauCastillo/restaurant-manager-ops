from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Purchase:
    """Purchase entity representing a buy record for a registered client."""
    client_id: int
    concepto: str
    monto: float
    fecha_compra: str
    notas: str = ""
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def format_monto(self) -> str:
        """Return formatted currency representation of monto."""
        return f"${self.monto:,.2f}"
