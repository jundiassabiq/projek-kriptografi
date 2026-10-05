"""HTTP lokal memakai pustaka standar. Setiap request memiliki koneksi SQLite sendiri."""
import argparse
import json
from pathlib import Path
import secrets
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs
import webbrowser
from ..storage import Repository
from ..services import NoteService
from ..crypto import Keys, encrypt, decrypt

STATIC = Path(__file__).resolve().parent / "static"
DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "ruangcatat.sqlite3"
MAX_BODY = 2 * 1024 * 1024


def text(data, name, default=None):
    value = data.get(name, default)
    if not isinstance(value, str):
        raise ValueError(f"{name} harus berupa teks.")
    return value


def identifier(value):
    if isinstance(value, bool):
        raise ValueError("ID tidak valid.")
    try:
        result = int(value)
    except (ValueError, TypeError):
        raise ValueError("ID tidak valid.") from None
    if result < 1 or str(result) != str(value):
        raise ValueError("ID tidak valid.")
    return result


def keys_from(data):
    keys = data.get("keys")
    if not isinstance(keys, dict):
        raise ValueError("Tiga kunci wajib diisi.")
    result = Keys(text(keys, "mono"), text(keys, "vigenere"), text(keys, "columnar"))
    result.validate()
    return result


def metadata(row):
    return {key: value for key, value in row.items() if key != "ciphertext"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        # Tidak mencatat payload, kunci, atau isi catatan ke terminal/log.
        pass

    def send_bytes(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(body)

    def respond(self, status, data):
        self.send_bytes(status, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def origin_valid(self):
        # Host ketat menolak DNS rebinding. Request browser lintas origin tidak diizinkan.
        if self.headers.get("Host") != self.server.allowed_host:
            return False
        origin = self.headers.get("Origin")
        return origin is None or origin == "http://" + self.server.allowed_host

    def do_GET(self):
        if not self.origin_valid():
            self.respond(403, {"error": "Origin atau host tidak diizinkan."})
            return
        parsed = urlsplit(self.path)
        if parsed.path == "/api/bootstrap":
            self.respond(200, {"token": self.server.token})
            return
        if parsed.path.startswith("/api/"):
            if self.headers.get("X-RuangCatat-Token") != self.server.token:
                self.respond(403, {"error": "Token sesi tidak valid. Muat ulang halaman."})
                return
            self.api("GET", parsed, {})
            return
        allowed = {"/": ("index.html", "text/html"), "/index.html": ("index.html", "text/html"),
                   "/style.css": ("style.css", "text/css"),
                   **{f"/{name}.js": (f"{name}.js", "text/javascript")
                      for name in ("app", "api", "ui", "notes", "demo")}}
        item = allowed.get(parsed.path)
        if not item:
            self.respond(404, {"error": "Halaman tidak ditemukan."})
            return
        self.send_bytes(200, (STATIC / item[0]).read_bytes(), item[1] + "; charset=utf-8")

    def do_POST(self):
        if not self.origin_valid() or self.headers.get("X-RuangCatat-Token") != self.server.token:
            self.respond(403, {"error": "Token atau origin tidak valid. Muat ulang halaman."})
            return
        try:
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                raise ValueError("Request wajib berformat JSON.")
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > MAX_BODY:
                raise ValueError("Ukuran request harus 1 byte sampai 2 MiB.")
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Request wajib berupa objek JSON.")
        except (ValueError, UnicodeError) as exc:
            self.respond(400, {"error": str(exc)})
            return
        self.api("POST", urlsplit(self.path), data)

    def api(self, method, parsed, data):
        repo = None
        try:
            repo = Repository(self.server.db_path)
            service = NoteService(repo)
            query = parse_qs(parsed.query)
            path = parsed.path
            if method == "GET" and path == "/api/dashboard":
                clients, sessions, pending = repo.counts()
                result = {"clients": clients, "sessions": sessions, "pending": pending,
                          "records": [metadata(row) for row in repo.sessions(pending=True)]}
            elif method == "GET" and path == "/api/clients":
                result = repo.clients(query.get("search", [""])[0])
            elif method == "GET" and path == "/api/sessions":
                client_id = identifier(query.get("client_id", [None])[0])
                result = [metadata(row) for row in repo.sessions(client_id)]
            elif method == "POST" and path == "/api/clients":
                result = {"id": service.add_client(text(data, "code"))}
            elif method == "POST" and path == "/api/sessions/save":
                client_id = identifier(data.get("client_id"))
                session_id = data.get("id")
                if session_id is not None:
                    session_id = identifier(session_id)
                    row = repo.get_session(session_id)
                    # Verifikasi kunci lama di server sebelum memperbarui arsip.
                    if row["client_id"] != client_id:
                        raise ValueError("Catatan bukan milik klien yang dipilih.")
                    service.open(session_id, keys_from({"keys": data.get("previous_keys")}))
                result = {"id": service.save(client_id, text(data, "session_date"), text(data, "next_date", ""),
                    text(data, "topic"), text(data, "notes"), text(data, "follow_up", ""), keys_from(data), session_id),
                    "validated": True}
            elif method == "POST" and path == "/api/sessions/open":
                result = service.open(identifier(data.get("id")), keys_from(data))
            elif method == "POST" and path == "/api/sessions/status":
                if type(data.get("done")) is not bool:
                    raise ValueError("Status harus boolean.")
                repo.set_done(identifier(data.get("id")), data["done"])
                result = {"ok": True}
            elif method == "POST" and path == "/api/sessions/export":
                result = service.export_package(identifier(data.get("id")))
            elif method == "POST" and path == "/api/sessions/import":
                result = {"id": service.import_package(data.get("package"), keys_from(data))}
            elif method == "POST" and path == "/api/demo":
                action = data.get("action")
                if action not in ("encrypt", "decrypt"):
                    raise ValueError("Aksi demo tidak valid.")
                transformed = (encrypt if action == "encrypt" else decrypt)(text(data, "text"), keys_from(data))
                result = {"text": transformed.text, "stages": transformed.stages}
            else:
                self.respond(404, {"error": "Endpoint tidak ditemukan."})
                return
            self.respond(200, result)
        except (ValueError, sqlite3.IntegrityError) as exc:
            self.respond(400, {"error": str(exc) if not isinstance(exc, sqlite3.IntegrityError) else "Klien atau data referensi tidak valid."})
        except (OSError, sqlite3.Error):
            self.respond(500, {"error": "Penyimpanan tidak tersedia. Periksa akses folder database."})
        finally:
            if repo:
                repo.close()


def create_server(db_path=DEFAULT_DB, port=8765):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.daemon_threads = True
    server.db_path = Path(db_path)
    server.token = secrets.token_urlsafe(32)
    server.allowed_host = "127.0.0.1:" + str(server.server_port)
    return server


def main():
    parser = argparse.ArgumentParser(description="RuangCatat web lokal")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Lokasi database (opsional)")
    args = parser.parse_args()
    try:
        server = create_server(db_path=args.db, port=args.port)
    except OSError as exc:
        parser.exit(1, f"Server tidak bisa dimulai: {exc}. Coba --port 8766.\n")
    url = "http://" + server.allowed_host
    print(f"RuangCatat: {url}\nGunakan data fiktif. Tekan Ctrl+C untuk menghentikan server.")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
