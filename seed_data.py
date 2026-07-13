"""Database seed utility to populate default admin user and import clients from Consulta.html."""

import os
from pathlib import Path
from config import get_config
from src.adapters.outbound.persistence.sqlite_connection import SQLiteConnectionManager
from src.adapters.outbound.persistence.sqlite_user_repository import SQLiteUserRepository
from src.adapters.outbound.persistence.sqlite_client_repository import SQLiteClientRepository
from src.adapters.outbound.persistence.sqlite_purchase_repository import SQLitePurchaseRepository
from src.adapters.outbound.security.password_hasher import PasswordHasher
from src.application.services.auth_service import AuthService
from src.application.services.client_service import ClientService
from src.application.services.purchase_service import PurchaseService
from src.domain.exceptions import DuplicateEntityException


def seed_all(db_path: str = None, consulta_html_path: str = None) -> None:
    config = get_config()()
    db_path = db_path or config.DATABASE_PATH
    consulta_html_path = consulta_html_path or config.DEFAULT_CONSULTA_HTML_PATH

    print(f"[*] Inicializando base de datos en: {db_path}")
    db_manager = SQLiteConnectionManager(db_path)

    # Initialize repositories & adapters
    user_repo = SQLiteUserRepository(db_manager)
    client_repo = SQLiteClientRepository(db_manager)
    purchase_repo = SQLitePurchaseRepository(db_manager)
    hasher = PasswordHasher()

    # Initialize services
    auth_service = AuthService(user_repo, hasher)
    client_service = ClientService(client_repo)
    purchase_service = PurchaseService(purchase_repo, client_repo)

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

    # 2. Seed clients from Consulta.html
    html_path = Path(consulta_html_path)
    if html_path.exists():
        print(f"[*] Importando clientes desde: {html_path}")
        try:
            imported, skipped = client_service.import_from_html_file(str(html_path))
            print(f"[+] Importación de Consulta.html terminada: {imported} importados, {skipped} actualizados/existentes.")
        except Exception as e:
            print(f"[-] Error importando Consulta.html: {e}")
    else:
        print(f"[*] Archivo {consulta_html_path} no encontrado, verificando si se requieren clientes de demostración.")
        if client_repo.count() == 0:
            sample_clients = [
                ("Carlos Alverto Hurtado", "16848254", "Pool de Ambulancia", 270500.0),
                ("Luis Hernesto Dias", "1098643975", "Pool de Ambulancia", 205000.0),
                ("Wilmar Rodrigues", "14696250", "Pool de Ambulancia", 90000.0),
                ("Fernando Erazo Tello", "1144100477", "Pool de Ambulancia", 3924500.0),
            ]
            for nom, ced, proc, val in sample_clients:
                try:
                    client_service.register_client(nom, ced, proc, val)
                except DuplicateEntityException:
                    pass
            print("[+] Clientes iniciales cargados en la base de datos.")


if __name__ == "__main__":
    seed_all()
