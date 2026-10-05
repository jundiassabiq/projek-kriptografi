import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch
from ruangcatat.app import App
from ruangcatat.ui.editor import NoteEditor


class UiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        try:
            self.app = App(Path(self.temp.name) / "test.db")
        except tk.TclError as exc:
            self.temp.cleanup()
            self.skipTest(f"Tk/display unavailable: {exc}")
        self.app.withdraw()
        self.app.update()

    def tearDown(self):
        if hasattr(self, "app"):
            self.app.close()
        self.temp.cleanup()

    def set_keys(self, fields):
        for variable, value in zip(fields.variables, ("ZEBRAS", "LEMON", "BALLOON")):
            variable.set(value)

    def test_demo_and_clear(self):
        demo = self.app.demo
        self.set_keys(demo.keys)
        demo.plaintext.set("Catatan fiktif 🙂\nBaris dua\r\n")
        demo.encrypt_text()
        demo.decrypt_text()
        self.assertIn("BERHASIL", demo.status.get())
        self.assertEqual(demo.stages[3].get(), demo.plaintext.get())
        demo.ciphertext.set("corrupt")
        demo.decrypt_text()
        self.assertIn("GAGAL", demo.status.get())
        demo.clear()
        self.assertEqual(demo.keys.variables[0].get(), "")
        self.assertEqual(demo.plaintext.get(), "")

    def test_empty_demo(self):
        self.set_keys(self.app.demo.keys)
        self.app.demo.encrypt_text()
        self.app.demo.decrypt_text()
        self.assertIn("BERHASIL", self.app.demo.status.get())

    def test_editor_save_open_edit_status(self):
        self.app.new_code.set("K-TEST")
        self.app.add_client()
        client_id = int(self.app.clients_tree.selection()[0])
        editor = NoteEditor(self.app, client_id, "K-TEST")
        self.set_keys(editor.keys)
        editor.topic.set("Sesi fiktif")
        editor.notes.set("Isi fiktif\n🙂")
        editor.follow_up.set("Tindak lanjut")
        with patch("ruangcatat.ui.editor.messagebox.showinfo"):
            editor.save()
        session_id = self.app.repository.sessions()[0]["id"]
        editor = NoteEditor(self.app, client_id, "K-TEST", session_id)
        self.assertEqual(str(editor.save_button["state"]), "disabled")
        self.assertEqual(editor.notes.get(), "")
        self.set_keys(editor.keys)
        editor.open_note()
        self.assertEqual(editor.notes.get(), "Isi fiktif\n🙂")
        editor.notes.set("Diubah")
        with patch("ruangcatat.ui.editor.messagebox.showinfo"):
            editor.save()
        self.app.clients_tree.selection_set(str(client_id))
        self.app.refresh_sessions()
        self.app.sessions_tree.selection_set(str(session_id))
        self.app.mark(self.app.sessions_tree, True)
        self.assertEqual(self.app.repository.counts(), (1, 1, 0))

    def test_wrong_key_editor_stays_locked(self):
        client_id = self.app.service.add_client("K-TEST")
        from ruangcatat.crypto import Keys
        session_id = self.app.service.save(client_id, "2026-10-05", "", "Topik", "Isi", "", Keys("ZEBRAS", "LEMON", "BALLOON"))
        editor = NoteEditor(self.app, client_id, "K-TEST", session_id)
        for variable in editor.keys.variables:
            variable.set("BAD")
        with patch("ruangcatat.ui.editor.messagebox.showerror") as error:
            editor.open_note()
        error.assert_called_once()
        self.assertFalse(editor.unlocked)
        self.assertEqual(str(editor.save_button["state"]), "disabled")
        editor.close()
