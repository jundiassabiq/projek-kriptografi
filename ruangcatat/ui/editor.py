from datetime import date
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .widgets import KeyFields, TextBox


class NoteEditor(tk.Toplevel):
    def __init__(self, app, client_id, code, session_id=None):
        super().__init__(app)
        self.app, self.client_id, self.session_id = app, client_id, session_id
        self.unlocked = session_id is None
        self.title(f"Catatan sesi — {code}")
        self.geometry("850x730")
        self.minsize(760, 650)
        self.transient(app)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.close)
        body = ttk.Frame(self, padding=16)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=f"Klien {code}", style="Title.TLabel").pack(anchor="w")
        self.keys = KeyFields(body)
        self.keys.pack(fill="x", pady=8)
        dates = ttk.Frame(body)
        dates.pack(fill="x")
        self.session_date = tk.StringVar(value=date.today().isoformat())
        self.next_date = tk.StringVar()
        ttk.Label(dates, text="Tanggal sesi (YYYY-MM-DD)").pack(side="left")
        ttk.Entry(dates, textvariable=self.session_date, width=14).pack(side="left", padx=8)
        ttk.Label(dates, text="Jadwal berikutnya (opsional)").pack(side="left")
        ttk.Entry(dates, textvariable=self.next_date, width=14).pack(side="left", padx=8)
        ttk.Label(body, text="Topik").pack(anchor="w", pady=(8, 2))
        self.topic = tk.StringVar()
        self.topic_entry = ttk.Entry(body, textvariable=self.topic)
        self.topic_entry.pack(fill="x")
        ttk.Label(body, text="Isi catatan").pack(anchor="w", pady=(8, 2))
        self.notes = TextBox(body, height=8)
        self.notes.pack(fill="both", expand=True)
        ttk.Label(body, text="Rencana tindak lanjut").pack(anchor="w", pady=(8, 2))
        self.follow_up = TextBox(body, height=4)
        self.follow_up.pack(fill="both", expand=True)
        actions = ttk.Frame(body)
        actions.pack(fill="x", pady=10)
        self.open_button = ttk.Button(actions, text="Buka dengan kunci", command=self.open_note)
        self.open_button.pack(side="left", padx=(0, 8))
        self.load_button = ttk.Button(actions, text="Isi dari .txt", command=self.load_text)
        self.load_button.pack(side="left")
        self.save_button = ttk.Button(actions, text="Simpan tersandi", command=self.save)
        self.save_button.pack(side="right")
        ttk.Button(actions, text="Tutup", command=self.close).pack(side="right", padx=8)
        self.status = tk.StringVar(value="Isi catatan dan tiga kunci untuk menyimpan.")
        ttk.Label(body, textvariable=self.status, wraplength=760).pack(anchor="w")
        if session_id is not None:
            row = app.repository.get_session(session_id)
            self.session_date.set(row["session_date"])
            self.next_date.set(row["next_date"])
            self.status.set("Catatan terkunci. Masukkan tiga kunci, lalu pilih Buka dengan kunci.")
        else:
            self.open_button.configure(state="disabled")
        self.lock_fields(not self.unlocked)

    def lock_fields(self, locked):
        state = "disabled" if locked else "normal"
        self.topic_entry.configure(state=state)
        self.notes.text.configure(state=state)
        self.follow_up.text.configure(state=state)
        self.save_button.configure(state=state)
        self.load_button.configure(state=state)

    def open_note(self):
        try:
            payload = self.app.service.open(self.session_id, self.keys.keys())
            self.lock_fields(False)
            self.topic.set(payload["topic"])
            self.notes.set(payload["notes"])
            self.follow_up.set(payload["follow_up"])
            self.unlocked = True
            self.status.set("Catatan terbuka. Kunci saat Simpan dipakai untuk enkripsi ulang.")
        except (ValueError, OSError) as exc:
            messagebox.showerror("Tidak bisa membuka", str(exc), parent=self)

    def load_text(self):
        path = filedialog.askopenfilename(parent=self, filetypes=[("Teks UTF-8", "*.txt")])
        if path:
            try:
                # newline='' mencegah normalisasi CRLF pada input file.
                with open(path, encoding="utf-8-sig", newline="") as source:
                    self.notes.set(source.read())
            except (OSError, UnicodeError) as exc:
                messagebox.showerror("Gagal membaca", str(exc), parent=self)

    def save(self):
        if not self.unlocked:
            return
        try:
            self.session_id = self.app.service.save(self.client_id, self.session_date.get(),
                self.next_date.get(), self.topic.get(), self.notes.get(), self.follow_up.get(),
                self.keys.keys(), self.session_id)
            self.app.refresh()
            messagebox.showinfo("Tersimpan", "Catatan tersandi disimpan. Validasi dekripsi identik berhasil.", parent=self)
            self.close()
        except (ValueError, OSError) as exc:
            messagebox.showerror("Gagal menyimpan", str(exc), parent=self)

    def close(self):
        self.keys.clear()
        self.topic.set("")
        self.notes.set("")
        self.follow_up.set("")
        self.destroy()
