import tkinter as tk
from tkinter import ttk
from ..crypto import Keys


class KeyFields(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="Tiga kunci — hanya huruf A-Z/a-z", padding=10)
        self.variables = [tk.StringVar() for _ in range(3)]
        for index, label in enumerate(("Substitusi", "Vigenere", "Kolom")):
            ttk.Label(self, text=label).grid(row=0, column=index * 2, padx=(0, 6))
            ttk.Entry(self, textvariable=self.variables[index], show="*", width=16).grid(
                row=0, column=index * 2 + 1, padx=(0, 12), sticky="ew")
            self.columnconfigure(index * 2 + 1, weight=1)
        visible = tk.BooleanVar(value=False)
        def toggle():
            for widget in self.winfo_children():
                if isinstance(widget, ttk.Entry):
                    widget.configure(show="" if visible.get() else "*")
        ttk.Checkbutton(self, text="Tampilkan kunci", variable=visible, command=toggle).grid(
            row=1, column=0, columnspan=6, sticky="w", pady=(8, 0))

    def keys(self):
        keys = Keys(*(variable.get() for variable in self.variables))
        keys.validate()
        return keys

    def clear(self):
        for variable in self.variables:
            variable.set("")


class TextBox(ttk.Frame):
    def __init__(self, parent, height=6, readonly=False):
        super().__init__(parent)
        self.text = tk.Text(self, height=height, wrap="word", font=("Segoe UI", 10),
                            undo=True, borderwidth=1, relief="solid", padx=8, pady=6)
        scroll = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=scroll.set)
        self.text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.readonly = readonly
        if readonly:
            self.text.configure(state="disabled")

    def get(self):
        # end-1c menghilangkan newline otomatis Tk, bukan newline milik pengguna.
        return self.text.get("1.0", "end-1c")

    def set(self, value):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", value)
        self.text.edit_reset()  # Jangan simpan teks lama dalam riwayat undo saat ganti/bersihkan.
        if self.readonly:
            self.text.configure(state="disabled")


def session_table(parent):
    frame = ttk.Frame(parent)
    columns = ("code", "date", "next", "status")
    tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
    for column, heading, width in zip(columns,
            ("Kode klien", "Tanggal sesi", "Jadwal berikutnya", "Tindak lanjut"), (150, 150, 170, 160)):
        tree.heading(column, text=heading)
        tree.column(column, width=width, minwidth=100)
    bar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=bar.set)
    tree.pack(side="left", fill="both", expand=True)
    bar.pack(side="right", fill="y")
    return frame, tree


def fill_sessions(tree, rows):
    tree.delete(*tree.get_children())
    for row in rows:
        tree.insert("", "end", iid=str(row["id"]), values=(row["code"], row["session_date"],
            row["next_date"] or "—", "Selesai" if row["done"] else "Belum selesai"))


def selected_id(tree):
    selection = tree.selection()
    if not selection:
        raise ValueError("Pilih satu baris terlebih dahulu.")
    return int(selection[0])
