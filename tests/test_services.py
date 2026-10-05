import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from ruangcatat.storage import Repository
from ruangcatat.services import NoteService
from ruangcatat.crypto import Keys

KEYS = Keys("ZEBRAS", "LEMON", "BALLOON")
SECRET = "IsiUnikFiktif987: baris satu\nBaris dua 🙂\r\n"


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)
        self.db = self.path / "test.db"
        self.repo = Repository(self.db)
        self.service = NoteService(self.repo)
        self.client_id = self.service.add_client("K-001")

    def tearDown(self):
        self.repo.close()
        self.temp.cleanup()

    def save_note(self):
        return self.service.save(self.client_id, "2026-10-05", "2026-10-12",
            "TopikUnikFiktif", SECRET, "TindakLanjutUnik", KEYS)

    def test_create_open_update_and_status(self):
        session_id = self.save_note()
        self.assertEqual(self.service.open(session_id, KEYS)["notes"], SECRET)
        self.repo.set_done(session_id, True)
        self.assertEqual(self.repo.counts(), (1, 1, 0))
        self.service.save(self.client_id, "2026-10-06", "", "Topik baru", "Isi baru", "", KEYS, session_id)
        self.assertEqual(self.service.open(session_id, KEYS)["notes"], "Isi baru")
        self.assertEqual(self.repo.get_session(session_id)["done"], 1)
        self.repo.set_done(session_id, False)
        self.assertEqual(len(self.repo.sessions(pending=True)), 1)

    def test_reopen_database(self):
        session_id = self.save_note()
        self.repo.close()
        self.repo = Repository(self.db)
        self.service = NoteService(self.repo)
        self.assertEqual(self.service.open(session_id, KEYS)["notes"], SECRET)

    def test_duplicate_codes_search_and_history(self):
        with self.assertRaises(ValueError):
            self.service.add_client("k-001")
        other = self.service.add_client("K-002")
        self.save_note()
        self.assertEqual(len(self.repo.clients("001")), 1)
        self.assertEqual(len(self.repo.clients("%")), 0)
        self.assertEqual(self.repo.sessions(other), [])
        self.assertEqual(self.repo.counts(), (2, 1, 1))

    def test_wrong_keys_leave_data_unchanged(self):
        session_id = self.save_note()
        before = self.repo.get_session(session_id)
        for keys in (Keys("BAD", "LEMON", "BALLOON"), Keys("ZEBRAS", "BAD", "BALLOON"), Keys("ZEBRAS", "LEMON", "BAD")):
            with self.assertRaises(ValueError):
                self.service.open(session_id, keys)
        self.assertEqual(self.repo.get_session(session_id), before)

    def test_export_import_privacy(self):
        session_id = self.save_note()
        path = self.path / "export.json"
        self.repo.set_done(session_id, True)
        self.service.export_file(session_id, path)
        package = json.loads(path.read_text(encoding="utf-8"))
        self.assertNotIn("keys", package)
        self.assertNotIn("notes", package)
        for secret in (SECRET, "TopikUnikFiktif", "TindakLanjutUnik", "ZEBRAS", "LEMON", "BALLOON"):
            self.assertNotIn(secret, path.read_text(encoding="utf-8"))
            self.assertNotIn(secret.encode("utf-8"), self.db.read_bytes())
        imported = self.service.import_file(path, KEYS)
        self.assertNotEqual(imported, session_id)
        self.assertEqual(self.service.open(imported, KEYS)["notes"], SECRET)
        self.assertEqual(self.repo.get_session(imported)["done"], 1)
        self.assertEqual(self.repo.counts(), (1, 2, 0))

    def test_import_creates_client_atomically(self):
        session_id = self.save_note()
        path = self.path / "export.json"
        self.service.export_file(session_id, path)
        package = json.loads(path.read_text(encoding="utf-8"))
        package["client_code"] = "K-NEW"
        path.write_text(json.dumps(package), encoding="utf-8")
        self.service.import_file(path, KEYS)
        self.assertEqual(self.repo.counts(), (2, 2, 2))

    def test_invalid_import_no_mutation(self):
        session_id = self.save_note()
        path = self.path / "export.json"
        self.service.export_file(session_id, path)
        original = path.read_text(encoding="utf-8")
        package = json.loads(original)
        cases = ["not json", "[]", "{}"]
        for field, value in (("format", "wrong"), ("algorithms", []), ("done", 1),
                             ("session_date", "2026-02-30"), ("client_code", "Nama asli"),
                             ("ciphertext", "broken"), ("ciphertext", None)):
            changed = dict(package)
            changed[field] = value
            cases.append(json.dumps(changed))
        for content in cases:
            path.write_text(content, encoding="utf-8")
            with self.assertRaises(ValueError):
                self.service.import_file(path, KEYS)
            self.assertEqual(self.repo.counts(), (1, 1, 1))
        path.write_text(original, encoding="utf-8")
        with self.assertRaises(ValueError):
            self.service.import_file(path, Keys("BAD", "BAD", "BAD"))
        self.assertEqual(self.repo.counts(), (1, 1, 1))

    def test_invalid_dates_fields_keys_and_codes(self):
        for code in ("", "Nama Asli", "a" * 33, "中"):
            with self.assertRaises(ValueError):
                self.service.add_client(code)
        for first, next_date in (("2026-02-30", ""), ("20261005", ""), ("2026-10-05", "2026-10-04")):
            with self.assertRaises(ValueError):
                self.service.save(self.client_id, first, next_date, "Topik", "Isi", "", KEYS)
        with self.assertRaises(ValueError):
            self.service.save(self.client_id, "2026-10-05", "", " ", "Isi", "", KEYS)
        with self.assertRaises(ValueError):
            self.service.save(self.client_id, "2026-10-05", "", "Topik", "Isi", "", Keys("", "A", "B"))
        self.assertEqual(self.repo.counts(), (1, 0, 0))

    def test_missing_records(self):
        with self.assertRaises(ValueError):
            self.repo.get_session(999)
        with self.assertRaises(ValueError):
            self.repo.set_done(999, True)
        with self.assertRaises(ValueError):
            self.service.save(self.client_id, "2026-10-05", "", "A", "B", "", KEYS, 999)
