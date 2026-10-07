"""
Menjalankan server web lokal, menyajikan HTML/CSS/JavaScript, dan menerima permintaan enkripsi serta dekripsi dari browser. Jalankan dengan python server.py.
"""


import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from notes import encrypt_note, decrypt_note, MAX_FILE_BYTES
from crypto.analysis import estimate

ROOT = Path(__file__).resolve().parent
MAX_REQUEST_BYTES = 2 * MAX_FILE_BYTES
STATIC = {'/': ('index.html', 'text/html'), '/index.html': ('index.html', 'text/html'),
          '/css/style.css': ('css/style.css', 'text/css'), '/js/app.js': ('js/app.js', 'text/javascript'),
          '/js/files.js': ('js/files.js', 'text/javascript'),
          '/js/analysis.js': ('js/analysis.js', 'text/javascript')}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass  # Isi request dan kunci tidak ditulis ke log.

    def send(self, status, body, content_type):
        self.send_response(status)
        self.send_header('Content-Type', content_type + '; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status, value):
        self.send(status, json.dumps(value, ensure_ascii=False).encode('utf-8'), 'application/json')

    def do_GET(self):
        route = self.path.split('?')[0]
        if route not in STATIC:
            self.send_json(404, {'error': 'Halaman tidak ditemukan.'})
            return
        file, content_type = STATIC[route]
        try:
            self.send(200, (ROOT / file).read_bytes(), content_type)
        except OSError:
            self.send_json(404, {'error': 'File web tidak ditemukan.'})

    def do_POST(self):
        if self.path not in ('/api/encrypt', '/api/decrypt', '/api/analysis'):
            self.send_json(404, {'error': 'Endpoint tidak ditemukan.'})
            return
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            self.send_json(415, {'error': 'Permintaan harus berupa JSON.'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length < 1 or length > MAX_REQUEST_BYTES:
                self.send_json(413, {'error': 'Permintaan terlalu besar atau kosong.'})
                return
            data = json.loads(self.rfile.read(length).decode('utf-8'))
            if not isinstance(data, dict):
                raise ValueError('Permintaan tidak valid.')
            if self.path == '/api/encrypt':
                result = encrypt_note(data.get('code'), data.get('text'), data.get('keys'))
            elif self.path == '/api/analysis':
                result = estimate(data.get('length'), data.get('rate'), data.get('seconds'))
            else:
                result = decrypt_note(data.get('package'), data.get('keys'))
            self.send_json(200, result)
        except (ValueError, UnicodeError) as error:
            self.send_json(400, {'error': 'JSON permintaan tidak valid.' if not isinstance(locals().get('data'), dict) else str(error)})
        except Exception:
            self.send_json(500, {'error': 'Proses gagal. Coba ulang.'})

if __name__ == '__main__':
    try:
        server = ThreadingHTTPServer(('127.0.0.1', 8000), Handler)
    except OSError:
        raise SystemExit('Port 8000 sedang digunakan. Tutup server lama lalu coba ulang.')
    print('RuangCatat File: http://127.0.0.1:8000 — Ctrl+C untuk berhenti.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

