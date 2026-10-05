import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ..crypto import encrypt, decrypt
from .widgets import KeyFields, TextBox


class DemoView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=14)
        self.baseline = None
        ttk.Label(self, text="Demo tiga lapisan enkripsi", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self, text="Substitusi Monoalfabetik → Vigenere → Transposisi Kolom").pack(anchor="w", pady=4)
        self.keys = KeyFields(self)
        self.keys.pack(fill="x", pady=8)
        pane = ttk.Panedwindow(self, orient="horizontal")
        pane.pack(fill="both", expand=True)
        left, right = ttk.Frame(pane), ttk.Frame(pane)
        pane.add(left, weight=1)
        pane.add(right, weight=1)
        ttk.Label(left, text="Plainteks / teks awal").pack(anchor="w")
        self.plaintext = TextBox(left, 8)
        self.plaintext.pack(fill="both", expand=True, padx=(0, 8))
        ttk.Label(right, text="Cipherteks (bisa diubah atau dimuat dari file)").pack(anchor="w")
        self.ciphertext = TextBox(right, 8)
        self.ciphertext.pack(fill="both", expand=True)
        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=10)
        for label, command in (("Muat plainteks .txt", self.load_plain),
                ("Enkripsi", self.encrypt_text), ("Dekripsi & validasi", self.decrypt_text),
                ("Muat cipherteks", self.load_cipher), ("Simpan cipherteks", self.save_cipher),
                ("Bersihkan", self.clear)):
            ttk.Button(actions, text=label, command=command).pack(side="left", padx=(0, 5))
        self.status = tk.StringVar(value="Masukkan teks dan tiga kunci. Teks kosong juga dapat diuji.")
        ttk.Label(self, textvariable=self.status, wraplength=1050).pack(anchor="w", pady=4)
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)
        self.stages = []
        for label in ("Tahap 1", "Tahap 2", "Tahap 3", "Hasil dekripsi"):
            box = TextBox(notebook, 7, readonly=True)
            notebook.add(box, text=label)
            self.stages.append(box)
        self.stage_notebook = notebook
        ttk.Label(self, text="Validasi hanya membuktikan pemulihan teks, bukan kekuatan keamanan.").pack(anchor="w", pady=(8, 0))

    def show_stages(self, result):
        for index, (label, value) in enumerate(result.stages):
            self.stage_notebook.tab(index, text=label)
            self.stages[index].set(value)

    def encrypt_text(self):
        try:
            keys = self.keys.keys()
            plain = self.plaintext.get()
            result = encrypt(plain, keys)
            self.baseline = plain
            self.ciphertext.set(result.text)
            self.show_stages(result)
            self.stages[3].set("")
            self.status.set("Enkripsi selesai. Pilih Dekripsi & validasi untuk membandingkan teks.")
        except ValueError as exc:
            messagebox.showerror("Kunci tidak valid", str(exc), parent=self)

    def decrypt_text(self):
        try:
            result = decrypt(self.ciphertext.get(), self.keys.keys())
            self.show_stages(result)
            self.stages[3].set(result.text)
            # Bandingkan terhadap input yang terlihat saat ini, bukan snapshot tersembunyi.
            expected = self.plaintext.get()
            if self.baseline is None and expected == "":
                self.status.set("Dekripsi selesai. Isi plainteks pembanding untuk validasi kesamaan.")
            elif result.text == expected:
                self.status.set("VALIDASI BERHASIL — hasil dekripsi identik dengan teks awal.")
            else:
                self.status.set("VALIDASI GAGAL — hasil berbeda. Periksa kunci, cipherteks, dan teks pembanding.")
        except ValueError as exc:
            messagebox.showerror("Kunci tidak valid", str(exc), parent=self)

    def load(self, target):
        path = filedialog.askopenfilename(filetypes=[("Teks UTF-8", "*.txt")])
        if path:
            try:
                with open(path, encoding="utf-8-sig", newline="") as source:
                    target.set(source.read())
                self.baseline = None
                self.status.set("File dimuat. Jalankan enkripsi atau dekripsi untuk hasil terbaru.")
                for box in self.stages:
                    box.set("")
            except (OSError, UnicodeError) as exc:
                messagebox.showerror("Gagal membaca", str(exc), parent=self)

    def load_plain(self):
        self.load(self.plaintext)

    def load_cipher(self):
        self.load(self.ciphertext)

    def save_cipher(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Teks", "*.txt")])
        if path:
            try:
                with open(path, "w", encoding="utf-8", newline="") as target:
                    target.write(self.ciphertext.get())
                self.status.set("Cipherteks disimpan ke file.")
            except OSError as exc:
                messagebox.showerror("Gagal menyimpan", str(exc), parent=self)

    def clear(self):
        self.keys.clear()
        self.plaintext.set("")
        self.ciphertext.set("")
        for box in self.stages:
            box.set("")
        self.baseline = None
        self.status.set("Teks dan kunci demo dibersihkan.")
