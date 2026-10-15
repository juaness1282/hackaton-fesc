"""subsidios-app — registra retiros de afiliados (SÍ se puede modificar).

Hoy llama directamente al procedimiento legacy sp_registrar_retiro.
El reto pide que pase a usar el servicio nuevo (gateway) sin perder el camino legacy.

POST /retiros  {"documento": "...", "fecha": "YYYY-MM-DD", "motivo": "..."}  (puerto 8091)
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import psycopg2
import gateway_client
from pathlib import Path

def is_legacy():
    path=Path("/state/domains.json")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))["affiliations"]=="LEGACY"
    return os.getenv("SUBSIDIOS_MODE","gateway")=="legacy"



def connect():
    return psycopg2.connect(
        host=os.environ.get("LEGACY_DB_HOST", "legacy-db"),
        port=int(os.environ.get("LEGACY_DB_PORT", "5432")),
        dbname=os.environ.get("POSTGRES_DB", "legacy"),
        user=os.environ.get("POSTGRES_USER", "legacy"),
        password=os.environ.get("POSTGRES_PASSWORD", ""),
        connect_timeout=2,
    )


def registrar_retiro(documento, fecha, motivo):
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT sp_registrar_retiro(%s, %s, %s, %s)", (documento, fecha, motivo, "SUBSIDIOS"))
            movimiento = cur.fetchone()[0]
        conn.commit()
        return movimiento
    finally:
        conn.close()


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"status": "UP", "modo": "legacy" if is_legacy() else "gateway"})
        return self._send(404, {"error": "ruta no encontrada"})

    def do_POST(self):
        if self.path != "/retiros":
            return self._send(404, {"error": "ruta no encontrada"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 <= length <= 16384:
                return self._send(413, {"message":"Solicitud demasiado grande"})
            data = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(data, dict):
                raise ValueError()
            if not is_legacy():
                status, payload = gateway_client.send(data, self.headers.get("Idempotency-Key"))
                return self._send(status, payload)
            movimiento = registrar_retiro(data["documento"], data["fecha"], data.get("motivo", "RETIRO"))
        except (KeyError, ValueError, TypeError):
            return self._send(422, {"message":"Solicitud inválida"})
        except psycopg2.Error:
            return self._send(503, {"message":"Base no disponible"})
        return self._send(201, {"movimiento": movimiento})

    def log_message(self, fmt, *args):
        return


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8091), Handler).serve_forever()
