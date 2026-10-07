"""
Menyediakan endpoint /api/analysis pada Vercel untuk simulasi brute force.
Hanya menerima panjang kunci dan asumsi percobaan; tidak menerima isi/kunci catatan.
"""


from server import Handler


class handler(Handler):
    def do_GET(self):
        self.send_json(405, {'error': 'Gunakan POST untuk analisis.'})
