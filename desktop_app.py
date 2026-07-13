#!/usr/bin/env python3
"""
HexOPS Manager - Desktop Web Application Entry Point
====================================================
Lanza el servidor Flask embebido y abre una ventana nativa de escritorio
utilizando pywebview (Microsoft Edge WebView2 en Windows 11).
"""

import os
import sys
import time
import threading
import urllib.request
from app import create_app

PORT = 5001
HOST = "127.0.0.1"

def start_server():
    """Inicia el servidor Flask en modo de producción embebida."""
    app = create_app()
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)

def wait_for_server():
    """Espera a que el servidor Flask esté listo antes de abrir la ventana."""
    url = f"http://{HOST}:{PORT}/"
    for _ in range(30):
        try:
            with urllib.request.urlopen(url, timeout=1):
                break
        except Exception:
            time.sleep(0.1)

def main():
    try:
        import webview
    except ImportError:
        print("Error: pywebview no está instalado. Instálalo con: pip install pywebview")
        sys.exit(1)

    # Iniciar servidor Flask en un hilo secundario
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Esperar confirmación del servidor
    wait_for_server()

    # Crear ventana nativa de escritorio
    window = webview.create_window(
        title="HexOPS Manager — Sistema Ejecutivo de Gestión",
        url=f"http://{HOST}:{PORT}",
        width=1366,
        height=850,
        min_size=(1024, 680),
        confirm_close=True
    )

    # Iniciar bucle GUI de pywebview
    webview.start()

if __name__ == "__main__":
    main()
