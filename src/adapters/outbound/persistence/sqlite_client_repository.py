from datetime import datetime
from typing import List, Optional
from src.domain.models.client import Client
from src.ports.outbound.client_repository_port import ClientRepositoryPort
from src.adapters.outbound.persistence.sqlite_connection import SQLiteConnectionManager


class SQLiteClientRepository(ClientRepositoryPort):
    """SQLite implementation of ClientRepositoryPort."""

    def __init__(self, db_manager: SQLiteConnectionManager):
        self.db_manager = db_manager

    def _row_to_client(self, row) -> Client:
        created_at = datetime.fromisoformat(row["created_at"]) if isinstance(row["created_at"], str) else row["created_at"]
        return Client(
            id=row["id"],
            nombre=row["nombre"],
            cedula=row["cedula"],
            proceso_desempeno=row["proceso_desempeno"],
            valor_a_descontar=float(row["valor_a_descontar"]),
            created_at=created_at
        )

    def save(self, client: Client) -> Client:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            if client.id is None:
                cursor.execute("""
                    INSERT INTO clients (nombre, cedula, proceso_desempeno, valor_a_descontar, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    client.nombre,
                    client.cedula,
                    client.proceso_desempeno,
                    client.valor_a_descontar,
                    client.created_at.isoformat() if isinstance(client.created_at, datetime) else str(client.created_at)
                ))
                client.id = cursor.lastrowid
            else:
                cursor.execute("""
                    UPDATE clients
                    SET nombre = ?, cedula = ?, proceso_desempeno = ?, valor_a_descontar = ?
                    WHERE id = ?
                """, (
                    client.nombre,
                    client.cedula,
                    client.proceso_desempeno,
                    client.valor_a_descontar,
                    client.id
                ))
            conn.commit()
            return client

    def find_by_id(self, client_id: int) -> Optional[Client]:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
            row = cursor.fetchone()
            return self._row_to_client(row) if row else None

    def find_by_cedula(self, cedula: str) -> Optional[Client]:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients WHERE cedula = ?", (cedula,))
            row = cursor.fetchone()
            return self._row_to_client(row) if row else None

    def list_all(self, search_query: str = "") -> List[Client]:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            if search_query:
                q = f"%{search_query.strip()}%"
                cursor.execute("""
                    SELECT * FROM clients
                    WHERE nombre LIKE ? OR cedula LIKE ? OR proceso_desempeno LIKE ?
                    ORDER BY id ASC
                """, (q, q, q))
            else:
                cursor.execute("SELECT * FROM clients ORDER BY id ASC")
            rows = cursor.fetchall()
            return [self._row_to_client(row) for row in rows]

    def delete(self, client_id: int) -> bool:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            conn.commit()
            return cursor.rowcount > 0

    def count(self) -> int:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as cnt FROM clients")
            row = cursor.fetchone()
            return row["cnt"] if row else 0
