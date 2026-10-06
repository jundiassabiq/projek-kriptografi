"""
Menyediakan endpoint /api/encrypt pada Vercel. Permintaan POST diteruskan ke handler aplikasi yang memanggil proses enkripsi Python.
"""


from server import Handler

class handler(Handler):
    def do_GET(self):
        self.send_json(405, {'error': 'Gunakan POST untuk proses catatan.'})
