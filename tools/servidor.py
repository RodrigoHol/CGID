from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8000

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    print(f"Vista disponible en http://{HOST}:{PORT}/frontend/vue/index.html")
    print("Presiona Ctrl+C para detener el servidor.")
    ThreadingHTTPServer((HOST, PORT), SimpleHTTPRequestHandler).serve_forever()
