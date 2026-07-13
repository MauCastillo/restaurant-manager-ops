import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-super-secret-key-change-in-prod-2026")
    
    # SQLite Database Configuration
    INSTANCE_DIR = BASE_DIR / "instance"
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(INSTANCE_DIR / "app.db"))
    
    # Application settings
    APP_NAME = "Gestor de Clientes & Compras"
    APP_VERSION = "2.0.0"


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration suitable for Render deployment."""
    DEBUG = False


def get_config():
    """Retrieve active configuration based on environment."""
    env = os.environ.get("FLASK_ENV", "development").lower()
    if env == "production":
        return ProductionConfig
    return DevelopmentConfig
