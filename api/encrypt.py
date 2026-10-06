"""Penghubung Vercel; logika HTTP dan algoritma tetap di modul aplikasi."""
from server import Handler

class handler(Handler):
    def do_GET(self):
        self.send_json(405, {'error': 'Gunakan POST untuk proses catatan.'})
