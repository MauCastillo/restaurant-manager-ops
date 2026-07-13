import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Detect if running as a frozen PyInstaller executable
if getattr(sys, 'frozen', False):
    APP_DIR = Path(sys.executable).resolve().parent
    BASE_DIR = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else APP_DIR
else:
    APP_DIR = Path(__file__).resolve().parent
    BASE_DIR = APP_DIR

# Load .env primarily from the folder containing the executable (or app root)
load_dotenv(APP_DIR / ".env")
load_dotenv(BASE_DIR / ".env")

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-super-secret-key-change-in-prod-2026")
    
    # SQLite Database Configuration (persists in app folder next to .exe)
    INSTANCE_DIR = APP_DIR / "instance"
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
