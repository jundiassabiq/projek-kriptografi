import json
import threading
import unittest
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from server import Handler, MAX_REQUEST_BYTES

KEYS = {'mono':'ZEBRAS', 'vigenere':'LEMON', 'columnar':'BALLOON'}

class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = 'http://127.0.0.1:' + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()

    def post(self, route, data):
        request = Request(self.base + route, data=json.dumps(data).encode(), headers={'Content-Type':'application/json'})
        try:
            with urlopen(request, timeout=5) as response: return response.status, json.load(response)
        except HTTPError as error: return error.code, json.load(error)

    def test_http_roundtrip(self):
        status, result = self.post('/api/encrypt', {'code':'K', 'text':'fiktif 中🙂', 'keys':KEYS})
        self.assertEqual(status, 200)
        status, back = self.post('/api/decrypt', {'package':result['package'], 'keys':KEYS})
        self.assertEqual(status, 200); self.assertEqual(back['text'], 'fiktif 中🙂')

    def test_error_status(self):
        status, result = self.post('/api/encrypt', {'code':'K', 'text':'fiktif', 'keys':{}})
        self.assertEqual(status, 400); self.assertIn('error', result)

    def test_bad_json(self):
        request = Request(self.base+'/api/encrypt', data=b'{bad', headers={'Content-Type':'application/json'})
        with self.assertRaises(HTTPError) as caught: urlopen(request)
        self.assertEqual(caught.exception.code, 400)

    def test_wrong_content_type(self):
        request = Request(self.base+'/api/encrypt', data=b'{}')
        with self.assertRaises(HTTPError) as caught: urlopen(request)
        self.assertEqual(caught.exception.code, 415)

    def test_request_limit(self):
        request = Request(self.base+'/api/encrypt', data=b'{}', headers={'Content-Type':'application/json', 'Content-Length':str(MAX_REQUEST_BYTES+1)})
        with self.assertRaises(HTTPError) as caught: urlopen(request)
        self.assertEqual(caught.exception.code, 413)

    def test_static_allowlist(self):
        for route in ['/', '/css/style.css', '/js/app.js']:
            with urlopen(self.base+route) as response: self.assertEqual(response.status, 200)
        for route in ['/server.py', '/data-lama/ruangcatat.sqlite3', '/../notes.py', '/api/missing']:
            with self.assertRaises(HTTPError) as caught: urlopen(self.base+route)
            self.assertEqual(caught.exception.code, 404)

if __name__ == '__main__':
    unittest.main()
