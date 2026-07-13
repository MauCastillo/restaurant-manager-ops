"""Database seed utility to populate default admin user."""

import os
from config import get_config
from src.adapters.outbound.persistence.sqlite_connection import SQLiteConnectionManager
from src.adapters.outbound.persistence.sqlite_user_repository import SQLiteUserRepository
from src.adapters.outbound.security.password_hasher import PasswordHasher
from src.application.services.auth_service import AuthService
from src.domain.exceptions import DuplicateEntityException


def seed_all(db_path: str = None, consulta_html_path: str = None) -> None:
    config = get_config()()
    db_path = db_path or config.DATABASE_PATH

    print(f"[*] Inicializando base de datos en: {db_path}")
    db_manager = SQLiteConnectionManager(db_path)

    # Initialize repositories & adapters
    user_repo = SQLiteUserRepository(db_manager)
    hasher = PasswordHasher()

    # Initialize services
    auth_service = AuthService(user_repo, hasher)

    # 1. Seed default secure Admin account
    default_admin_user = os.environ.get("ADMIN_USER", "admin")
    default_admin_email = os.environ.get("ADMIN_EMAIL", "admin@manager.ops")
    default_admin_pass = os.environ.get("ADMIN_PASSWORD", "admin123")

    try:
        auth_service.register_user(
            username=default_admin_user,
            email=default_admin_email,
            password=default_admin_pass,
            role="admin"
        )
        print(f"[+] Usuario Administrador creado: {default_admin_user} / {default_admin_pass}")
    except DuplicateEntityException:
        print(f"[*] El usuario administrador '{default_admin_user}' ya se encuentra registrado.")


if __name__ == "__main__":
    seed_all()

