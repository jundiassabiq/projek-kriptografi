import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from ruangcatat.web.server import create_server

KEYS = {"mono":"ZEBRAS","vigenere":"LEMON","columnar":"BALLOON"}


class WebTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.server = create_server(Path(self.temp.name)/"web.db", port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.token = self.server.token

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def request(self, path, data=None, headers=None, raw=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        request_headers = {"X-RuangCatat-Token":self.token}
        if headers:
            request_headers.update(headers)
        body = None
        if data is not None or raw is not None:
            body = raw if raw is not None else json.dumps(data).encode("utf-8")
            request_headers["Content-Type"] = "application/json"
        conn.request("POST" if body is not None else "GET", path, body, request_headers)
        response = conn.getresponse()
        payload = response.read()
        result_headers = dict(response.getheaders())
        status = response.status
        conn.close()
        return status, payload, result_headers

    def api(self, path, data=None):
        status, body, _ = self.request("/api/"+path, data)
        return status, json.loads(body)

    def create_note(self):
        status, client = self.api("clients", {"code":"K-WEB"})
        self.assertEqual(status, 200)
        data = {"client_id":client["id"], "session_date":"2026-10-05", "next_date":"2026-10-12",
                "topic":"Fiktif", "notes":"Catatan fiktif 🙂\r\nBaris dua", "follow_up":"Tindak lanjut", "keys":KEYS}
        status, note = self.api("sessions/save", data)
        self.assertEqual(status, 200)
        return client["id"], note["id"], data

    def test_static_and_bootstrap(self):
        for path in ("/", "/style.css", "/app.js", "/api.js", "/notes.js", "/demo.js", "/ui.js"):
            status, body, headers = self.request(path)
            self.assertEqual(status, 200)
            self.assertTrue(body)
            self.assertEqual(headers["Cache-Control"], "no-store")
        status, data = self.api("bootstrap")
        self.assertEqual(data["token"], self.token)
        self.assertEqual(self.request("/../services.py")[0], 404)

    def test_access_checks(self):
        self.assertEqual(self.request("/api/dashboard", headers={"X-RuangCatat-Token":"wrong"})[0], 403)
        self.assertEqual(self.request("/api/bootstrap", headers={"Origin":"https://example.com"})[0], 403)
        self.assertEqual(self.request("/", headers={"Host":"evil.example"})[0], 403)
        self.assertEqual(self.request("/api/clients", {"code":"K"}, {"Origin":"https://example.com"})[0], 403)

    def test_create_open_status_dashboard(self):
        client_id, note_id, original = self.create_note()
        status, result = self.api("sessions/open", {"id":note_id,"keys":KEYS})
        self.assertEqual(result["notes"], original["notes"])
        status, sessions = self.api("sessions?client_id="+str(client_id))
        self.assertEqual(len(sessions), 1)
        self.assertNotIn("ciphertext", sessions[0])
        self.assertNotIn("notes", sessions[0])
        self.api("sessions/status", {"id":note_id,"done":True})
        status, dashboard = self.api("dashboard")
        self.assertEqual((dashboard["clients"],dashboard["sessions"],dashboard["pending"]), (1,1,0))

    def test_update_requires_old_keys_and_supports_rekey(self):
        client_id, note_id, data = self.create_note()
        update = dict(data, id=note_id, notes="Isi baru", keys={"mono":"KATA","vigenere":"BARU","columnar":"KUNCI"})
        self.assertEqual(self.api("sessions/save", update)[0], 400)
        update["previous_keys"] = {"mono":"BAD","vigenere":"BAD","columnar":"BAD"}
        self.assertEqual(self.api("sessions/save", update)[0], 400)
        self.assertEqual(self.api("sessions/open", {"id":note_id,"keys":KEYS})[1]["notes"], data["notes"])
        update["previous_keys"] = KEYS
        self.assertEqual(self.api("sessions/save", update)[0], 200)
        self.assertEqual(self.api("sessions/open", {"id":note_id,"keys":update["keys"]})[1]["notes"], "Isi baru")

    def test_import_export(self):
        client_id, note_id, data = self.create_note()
        status, pack = self.api("sessions/export", {"id":note_id})
        self.assertEqual(status,200)
        self.assertNotIn("keys",pack)
        self.assertNotIn(data["notes"],json.dumps(pack))
        status,result = self.api("sessions/import", {"package":pack,"keys":KEYS})
        self.assertEqual(status,200)
        self.assertNotEqual(result["id"],note_id)
        self.assertEqual(self.api("sessions/open", {"id":result["id"],"keys":KEYS})[1]["notes"],data["notes"])
        self.assertEqual(self.api("sessions/import", {"package":{},"keys":KEYS})[0],400)

    def test_demo_preserves_formats(self):
        for plain in ("", "A", "Catatan 🙂\r\n多言語 é\n", "AB" * 1000):
            status,result = self.api("demo", {"action":"encrypt","text":plain,"keys":KEYS})
            self.assertEqual(status,200)
            self.assertEqual(len(result["stages"]),3)
            status,back = self.api("demo", {"action":"decrypt","text":result["text"],"keys":KEYS})
            self.assertEqual(back["text"],plain)

    def test_bad_requests_and_wrong_keys(self):
        self.assertEqual(self.request("/api/clients", raw=b"not-json")[0],400)
        self.assertEqual(self.request("/api/clients", raw=b"[]")[0],400)
        self.assertEqual(self.api("clients", {"code":None})[0],400)
        client_id, note_id, data = self.create_note()
        self.assertEqual(self.api("sessions/open", {"id":note_id,"keys":{"mono":"BAD","vigenere":"BAD","columnar":"BAD"}})[0],400)
        self.assertEqual(self.api("sessions/status", {"id":note_id,"done":1})[0],400)
        self.assertEqual(self.api("sessions?client_id=no")[0],400)
        self.assertEqual(self.api("demo", {"action":"other","text":"","keys":KEYS})[0],400)
        self.assertEqual(self.api("missing")[0],404)
