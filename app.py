import os
from flask import Flask, render_template, session, g
from config import get_config

from src.adapters.outbound.persistence.sqlite_connection import SQLiteConnectionManager
from src.adapters.outbound.persistence.sqlite_user_repository import SQLiteUserRepository
from src.adapters.outbound.persistence.sqlite_client_repository import SQLiteClientRepository
from src.adapters.outbound.persistence.sqlite_purchase_repository import SQLitePurchaseRepository
from src.adapters.outbound.security.password_hasher import PasswordHasher
from src.adapters.outbound.reports.excel_report_generator import OpenpyxlReportGenerator
from src.adapters.outbound.email.gmail_smtp_sender import GmailSmtpSender
from src.adapters.outbound.ai.gemini_ocr_adapter import GeminiOcrAdapter

from src.application.services.auth_service import AuthService
from src.application.services.client_service import ClientService
from src.application.services.purchase_service import PurchaseService
from src.application.services.report_service import ReportService
from src.application.services.ocr_service import OcrService

from src.adapters.inbound.web.auth_controller import auth_bp
from src.adapters.inbound.web.client_controller import client_bp
from src.adapters.inbound.web.purchase_controller import purchase_bp
from src.adapters.inbound.web.dashboard_controller import dashboard_bp
from src.adapters.inbound.web.report_controller import report_bp
from seed_data import seed_all


def create_app(config_class=None):
    """Application factory for Hexagonal Architecture Flask application."""
    if config_class is None:
        config_class = get_config()

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize SQLite Connection Manager & Infrastructure Adapters
    db_manager = SQLiteConnectionManager(app.config["DATABASE_PATH"])
    user_repo = SQLiteUserRepository(db_manager)
    client_repo = SQLiteClientRepository(db_manager)
    purchase_repo = SQLitePurchaseRepository(db_manager)
    hasher = PasswordHasher()
    report_gen = OpenpyxlReportGenerator()
    email_sender = GmailSmtpSender()
    ocr_adapter = GeminiOcrAdapter()

    # Initialize Application Use Case Services
    app.auth_service = AuthService(user_repo, hasher)
    app.client_service = ClientService(client_repo)
    app.purchase_service = PurchaseService(purchase_repo, client_repo)
    app.report_service = ReportService(client_repo, purchase_repo, report_gen, email_sender)
    app.ocr_service = OcrService(ocr_adapter, client_repo)

    # Register Blueprints (Driving Adapters)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(purchase_bp)
    app.register_blueprint(report_bp)

    # Seed initial data on startup if database is fresh
    with app.app_context():
        seed_all(app.config["DATABASE_PATH"], app.config["DEFAULT_CONSULTA_HTML_PATH"])

    @app.before_request
    def load_logged_in_user():
        user_id = session.get("user_id")
        if user_id:
            g.user = app.auth_service.get_user_by_id(user_id)
        else:
            g.user = None

    @app.context_processor
    def inject_app_context():
        return {
            "app_name": app.config.get("APP_NAME", "Gestor de Clientes & Compras"),
            "current_user": getattr(g, "user", None)
        }

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("base.html", error_title="404 - Página no encontrada", error_msg="La ruta especificada no existe."), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("base.html", error_title="500 - Error Interno", error_msg="Ocurrió un error inesperado en el servidor."), 500

    @app.cli.command("seed")
    def seed_command():
        """Seed initial admin user and import clients from Consulta.html."""
        seed_all(app.config["DATABASE_PATH"], app.config["DEFAULT_CONSULTA_HTML_PATH"])

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
