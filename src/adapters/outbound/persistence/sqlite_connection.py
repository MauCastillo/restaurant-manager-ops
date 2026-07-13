import sqlite3
from pathlib import Path
from typing import Optional


class SQLiteConnectionManager:
    """Manages SQLite database connections and schema initialization."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db_directory()
        self.init_schema()

    def _ensure_db_directory(self) -> None:
        """Create parent directories if they don't exist."""
        path = Path(self.db_path)
        path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Return a configured SQLite connection with Row factory enabled."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_schema(self) -> None:
        """Create required SQLite database tables if they do not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Users table (Security User Account Manager)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'operator',
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Clients table based on Consulta.html schema
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    cedula TEXT UNIQUE NOT NULL,
                    proceso_desempeno TEXT NOT NULL,
                    valor_a_descontar REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_clients_cedula ON clients(cedula);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_clients_nombre ON clients(nombre);")

            # Purchases table (Buys / Transacciones)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    concepto TEXT NOT NULL,
                    monto REAL NOT NULL,
                    fecha_compra TEXT NOT NULL,
                    notas TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
                );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchases_client_id ON purchases(client_id);")

            conn.commit()
