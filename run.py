import sys
import os
import threading
import time
import webview
import socket
import signal  # <--- IMPORTANTE
from streamlit.web import cli as stcli

# --- CONFIGURACIÓN ---
PORT = 8501
TITLE = "Biblioteca Chatos"

def resolve_path(path):
    if getattr(sys, "frozen", False):
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)

def start_streamlit():
    """Inicia Streamlit en hilo secundario evitando el error de señales"""
    
    # --- TRUCO DE MAGIA (SOLUCIÓN AL ERROR) ---
    # Streamlit falla si intenta registrar señales (Ctrl+C) fuera del hilo principal.
    # Aquí desactivamos esa función reemplazándola por una que no hace nada.
    try:
        signal.signal = lambda x, y: None
    except:
        pass # Por si acaso falla, ignoramos
    
    sys.argv = [
        "streamlit",
        "run",
        resolve_path("app.py"),
        "--global.developmentMode=false",
        "--server.headless=true",
        f"--server.port={PORT}",
    ]
    stcli.main()

def wait_for_server(port):
    """Espera inteligentemente a que el servidor arranque"""
    retries = 0
    while retries < 20: # Intenta durante 10 segundos máximo
        try:
            with socket.create_connection(("localhost", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.5)
            retries += 1
    return False

if __name__ == '__main__':
    # 1. Arrancar Streamlit en hilo separado (Ahora ya no fallará)
    t = threading.Thread(target=start_streamlit)
    t.daemon = True
    t.start()

    # 2. Esperar a que arranque de verdad (Evita la pantalla negra vacía)
    server_ready = wait_for_server(PORT)

    if server_ready:
        # 3. Si arrancó bien, abrimos la ventana
        webview.create_window(TITLE, f"http://localhost:{PORT}", width=1200, height=800)
        webview.start()
    else:
        # Si falló, mostramos un aviso (puedes verlo si ejecutas con consola)
        print("Error: El servidor de Streamlit no respondió a tiempo.")