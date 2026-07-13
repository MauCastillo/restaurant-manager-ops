from datetime import datetime
from typing import List, Optional
from src.domain.models.user import User
from src.ports.outbound.user_repository_port import UserRepositoryPort
from src.adapters.outbound.persistence.sqlite_connection import SQLiteConnectionManager


class SQLiteUserRepository(UserRepositoryPort):
    """SQLite implementation of the UserRepositoryPort."""

    def __init__(self, db_manager: SQLiteConnectionManager):
        self.db_manager = db_manager

    def _row_to_user(self, row) -> User:
        """Convert SQLite Row to User domain entity."""
        created_at = datetime.fromisoformat(row["created_at"]) if isinstance(row["created_at"], str) else row["created_at"]
        return User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            password_hash=row["password_hash"],
            role=row["role"],
            is_active=bool(row["is_active"]),
            created_at=created_at
        )

    def save(self, user: User) -> User:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            if user.id is None:
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, role, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user.username,
                    user.email,
                    user.password_hash,
                    user.role,
                    1 if user.is_active else 0,
                    user.created_at.isoformat() if isinstance(user.created_at, datetime) else str(user.created_at)
                ))
                user.id = cursor.lastrowid
            else:
                cursor.execute("""
                    UPDATE users
                    SET username = ?, email = ?, password_hash = ?, role = ?, is_active = ?
                    WHERE id = ?
                """, (
                    user.username,
                    user.email,
                    user.password_hash,
                    user.role,
                    1 if user.is_active else 0,
                    user.id
                ))
            conn.commit()
            return user

    def find_by_id(self, user_id: int) -> Optional[User]:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None

    def find_by_username(self, username: str) -> Optional[User]:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None

    def find_by_email(self, email: str) -> Optional[User]:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None

    def list_all(self) -> List[User]:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [self._row_to_user(row) for row in rows]

    def delete(self, user_id: int) -> bool:
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
