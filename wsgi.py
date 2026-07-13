"""WSGI entry point for production deployment on Render (Gunicorn)."""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
