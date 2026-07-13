from datetime import datetime
from typing import List, Optional
from src.domain.models.purchase import Purchase
from src.ports.outbound.purchase_repository_port import PurchaseRepositoryPort
from src.adapters.outbound.persistence.sqlite_connection import SQLiteConnectionManager


class SQLitePurchaseRepository(PurchaseRepositoryPort):
    """SQLite implementation of PurchaseRepositoryPort."""

    def __init__(self, db_manager: SQLiteConnectionManager):
        self.db_manager = db_manager

    def _row_to_purchase(self, row) -> Purchase:
        created_at = datetime.fromisoformat(row["created_at"]) if isinstance(row["created_at"], str) else row["created_at"]
        return Purchase(
            id=row["id"],
            client_id=row["client_id"],
            concepto=row["concepto"],
            monto=float(row["monto"]),
            fecha_compra=row["fecha_compra"],
            notas=row["notas"] or "",
            created_at=created_at
        )

    def save(self, purchase: Purchase) -> Purchase:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            if purchase.id is None:
                cursor.execute("""
                    INSERT INTO purchases (client_id, concepto, monto, fecha_compra, notas, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    purchase.client_id,
                    purchase.concepto,
                    purchase.monto,
                    purchase.fecha_compra,
                    purchase.notas,
                    purchase.created_at.isoformat() if isinstance(purchase.created_at, datetime) else str(purchase.created_at)
                ))
                purchase.id = cursor.lastrowid
            else:
                cursor.execute("""
                    UPDATE purchases
                    SET client_id = ?, concepto = ?, monto = ?, fecha_compra = ?, notas = ?
                    WHERE id = ?
                """, (
                    purchase.client_id,
                    purchase.concepto,
                    purchase.monto,
                    purchase.fecha_compra,
                    purchase.notas,
                    purchase.id
                ))
            conn.commit()
            return purchase

    def find_by_id(self, purchase_id: int) -> Optional[Purchase]:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM purchases WHERE id = ?", (purchase_id,))
            row = cursor.fetchone()
            return self._row_to_purchase(row) if row else None

    def find_by_client_id(self, client_id: int) -> List[Purchase]:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM purchases WHERE client_id = ? ORDER BY fecha_compra DESC, id DESC", (client_id,))
            rows = cursor.fetchall()
            return [self._row_to_purchase(row) for row in rows]

    def list_all(self) -> List[Purchase]:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM purchases ORDER BY fecha_compra DESC, id DESC")
            rows = cursor.fetchall()
            return [self._row_to_purchase(row) for row in rows]

    def delete(self, purchase_id: int) -> bool:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM purchases WHERE id = ?", (purchase_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_total_monto_by_client(self, client_id: int) -> float:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COALESCE(SUM(monto), 0.0) as total FROM purchases WHERE client_id = ?", (client_id,))
            row = cursor.fetchone()
            return float(row["total"]) if row else 0.0
