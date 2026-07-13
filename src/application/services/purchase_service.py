from typing import Dict, List
from src.domain.models.purchase import Purchase
from src.domain.exceptions import EntityNotFoundException
from src.ports.inbound.purchase_service_port import PurchaseServicePort
from src.ports.outbound.purchase_repository_port import PurchaseRepositoryPort
from src.ports.outbound.client_repository_port import ClientRepositoryPort


class PurchaseService(PurchaseServicePort):
    """Implementation of PurchaseServicePort for managing client buys."""

    def __init__(self, purchase_repo: PurchaseRepositoryPort, client_repo: ClientRepositoryPort):
        self.purchase_repo = purchase_repo
        self.client_repo = client_repo

    def register_purchase(self, client_id: int, concepto: str, monto: float, fecha_compra: str, notas: str = "") -> Purchase:
        client = self.client_repo.find_by_id(client_id)
        if not client:
            raise EntityNotFoundException(f"El cliente con ID {client_id} no existe.")

        purchase = Purchase(
            client_id=client_id,
            concepto=concepto.strip(),
            monto=float(monto),
            fecha_compra=fecha_compra.strip(),
            notas=notas.strip()
        )
        return self.purchase_repo.save(purchase)

    def get_purchases_by_client(self, client_id: int) -> List[Purchase]:
        return self.purchase_repo.find_by_client_id(client_id)

    def list_all_purchases(self) -> List[Purchase]:
        return self.purchase_repo.list_all()

    def delete_purchase(self, purchase_id: int) -> bool:
        purchase = self.purchase_repo.find_by_id(purchase_id)
        if not purchase:
            raise EntityNotFoundException(f"La compra con ID {purchase_id} no existe.")
        return self.purchase_repo.delete(purchase_id)

    def get_client_financial_summary(self, client_id: int) -> Dict[str, float]:
        client = self.client_repo.find_by_id(client_id)
        if not client:
            raise EntityNotFoundException(f"El cliente con ID {client_id} no existe.")

        total_compras = self.purchase_repo.get_total_monto_by_client(client_id)
        base_descuento = client.valor_a_descontar
        saldo_neto = base_descuento + total_compras

        return {
            "base_descuento": base_descuento,
            "total_compras": total_compras,
            "saldo_neto": saldo_neto
        }
