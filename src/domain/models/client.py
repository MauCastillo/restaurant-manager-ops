from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Client:
    """Client entity based on Consulta.html schema.
    
    Attributes:
        nombre: Client full name (Nombre)
        cedula: National ID or document number (Cedula)
        proceso_desempeno: Assigned process/department (Porceso de Desempeno)
        valor_a_descontar: Base discount or deduction value (Valor a Descontar)
        id: Optional DB primary key
        created_at: Creation timestamp
    """
    nombre: str
    cedula: str
    proceso_desempeno: str
    valor_a_descontar: float = 0.0
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def format_valor(self) -> str:
        """Return formatted currency representation of valor_a_descontar."""
        return f"${self.valor_a_descontar:,.2f}"
