"""Perakitan antarmuka; algoritma dan penyimpanan berada di modul terpisah."""
from pathlib import Path
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from .storage import Repository
from .services import NoteService
from .ui.widgets import KeyFields, session_table, fill_sessions, selected_id
from .ui.editor import NoteEditor
from .ui.demo import DemoView

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class App(tk.Tk):
    def __init__(self, db_path=None):
        super().__init__()
        self.title("RuangCatat — Catatan Konseling | Prototipe Kriptografi Klasik")
        self.geometry("1180x820")
        self.minsize(1100, 740)
        self.repository = Repository(db_path or PROJECT_ROOT / "data" / "ruangcatat.sqlite3")
        self.service = NoteService(self.repository)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.report_callback_exception = self.callback_error
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f2f5f7")
        style.configure("TLabel", background="#f2f5f7", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground="#17384a")
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        header = ttk.Frame(self, padding=(20, 14))
        header.pack(fill="x")
        ttk.Label(header, text="RuangCatat", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="PROTOTIPE TUGAS • Gunakan data fiktif. Enkripsi klasik bukan untuk catatan klien asli.").pack(anchor="w", pady=(3, 0))
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self.dashboard = ttk.Frame(notebook, padding=14)
        self.client_view = ttk.Frame(notebook, padding=14)
        self.demo = DemoView(notebook)
        notebook.add(self.dashboard, text="Dashboard")
        notebook.add(self.client_view, text="Klien & catatan")
        notebook.add(self.demo, text="Demo kriptografi")
        self.build_dashboard()
        self.build_clients()
        self.refresh()

    def callback_error(self, exc_type, exc, traceback):
        if isinstance(exc, (ValueError, OSError, sqlite3.Error)):
            messagebox.showerror("Operasi gagal", str(exc), parent=self)
        else:
            messagebox.showerror("Kesalahan aplikasi", "Terjadi kesalahan. Lihat terminal untuk detail.", parent=self)
            import traceback as trace
            trace.print_exception(exc_type, exc, traceback)

    def build_dashboard(self):
        self.summary = tk.StringVar()
        ttk.Label(self.dashboard, textvariable=self.summary, style="Title.TLabel").pack(anchor="w", pady=(0, 12))
        ttk.Label(self.dashboard, text="Tindak lanjut belum selesai (klik dua kali untuk membuka catatan)").pack(anchor="w", pady=6)
        frame, self.pending_tree = session_table(self.dashboard)
        frame.pack(fill="both", expand=True)
        self.pending_tree.bind("<Double-1>", lambda event: self.open_selected(self.pending_tree))
        actions = ttk.Frame(self.dashboard)
        actions.pack(fill="x", pady=10)
        ttk.Button(actions, text="Buka catatan", command=lambda: self.open_selected(self.pending_tree)).pack(side="left")
        ttk.Button(actions, text="Tandai selesai", command=lambda: self.mark(self.pending_tree, True)).pack(side="left", padx=8)
        ttk.Button(actions, text="Segarkan", command=self.refresh).pack(side="right")

    def build_clients(self):
        top = ttk.Frame(self.client_view)
        top.pack(fill="x", pady=(0, 10))
        self.new_code = tk.StringVar()
        ttk.Label(top, text="Kode klien baru").pack(side="left")
        ttk.Entry(top, textvariable=self.new_code, width=22).pack(side="left", padx=8)
        ttk.Button(top, text="Tambah klien", command=self.add_client).pack(side="left")
        ttk.Button(top, text="Impor paket tersandi", command=self.import_package).pack(side="right")
        self.search = tk.StringVar()
        ttk.Label(top, text="Cari kode").pack(side="left", padx=(20, 8))
        search_entry = ttk.Entry(top, textvariable=self.search, width=22)
        search_entry.pack(side="left")
        self.search.trace_add("write", lambda *args: self.refresh_clients())
        pane = ttk.Panedwindow(self.client_view, orient="horizontal")
        pane.pack(fill="both", expand=True)
        left, right = ttk.Frame(pane), ttk.Frame(pane)
        pane.add(left, weight=1)
        pane.add(right, weight=4)
        self.clients_tree = ttk.Treeview(left, columns=("code",), show="headings", selectmode="browse", height=15)
        self.clients_tree.heading("code", text="Kode samaran")
        self.clients_tree.column("code", width=180)
        client_bar = ttk.Scrollbar(left, orient="vertical", command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=client_bar.set)
        self.clients_tree.pack(side="left", fill="both", expand=True, padx=(0, 4))
        client_bar.pack(side="right", fill="y")
        self.clients_tree.bind("<<TreeviewSelect>>", lambda event: self.refresh_sessions())
        self.client_heading = tk.StringVar(value="Pilih klien untuk melihat riwayat")
        ttk.Label(right, textvariable=self.client_heading).pack(anchor="w", pady=6)
        frame, self.sessions_tree = session_table(right)
        frame.pack(fill="both", expand=True)
        self.sessions_tree.bind("<Double-1>", lambda event: self.open_selected(self.sessions_tree))
        actions = ttk.Frame(right)
        actions.pack(fill="x", pady=10)
        for label, command in (("Tambah sesi", self.new_note),
            ("Buka / edit", lambda: self.open_selected(self.sessions_tree)),
            ("Selesai", lambda: self.mark(self.sessions_tree, True)),
            ("Belum selesai", lambda: self.mark(self.sessions_tree, False)),
            ("Ekspor JSON", self.export_package)):
            ttk.Button(actions, text=label, command=command).pack(side="left", padx=(0, 5))
        ttk.Label(self.client_view, text="Metadata tanggal, kode, dan status tidak dienkripsi. Topik, isi, dan rencana tersimpan sebagai cipherteks.", wraplength=1050).pack(anchor="w", pady=6)

    def add_client(self):
        client_id = self.service.add_client(self.new_code.get())
        self.new_code.set("")
        self.search.set("")
        self.refresh()
        self.clients_tree.selection_set(str(client_id))
        self.refresh_sessions()

    def refresh_clients(self):
        selected = self.clients_tree.selection()
        self.clients_tree.delete(*self.clients_tree.get_children())
        for row in self.repository.clients(self.search.get()):
            self.clients_tree.insert("", "end", iid=str(row["id"]), values=(row["code"],))
        if selected and self.clients_tree.exists(selected[0]):
            self.clients_tree.selection_set(selected[0])
        self.refresh_sessions()

    def refresh_sessions(self):
        selection = self.clients_tree.selection()
        if not selection:
            fill_sessions(self.sessions_tree, [])
            self.client_heading.set("Pilih klien untuk melihat riwayat")
            return
        client_id = int(selection[0])
        code = self.clients_tree.item(selection[0], "values")[0]
        self.client_heading.set(f"Riwayat sesi — {code}")
        fill_sessions(self.sessions_tree, self.repository.sessions(client_id))

    def refresh(self):
        clients, sessions, pending = self.repository.counts()
        self.summary.set(f"{clients} klien   •   {sessions} sesi   •   {pending} tindak lanjut belum selesai")
        fill_sessions(self.pending_tree, self.repository.sessions(pending=True))
        self.refresh_clients()

    def new_note(self):
        client_id = selected_id(self.clients_tree)
        code = self.clients_tree.item(str(client_id), "values")[0]
        NoteEditor(self, client_id, code)

    def open_selected(self, tree):
        session_id = selected_id(tree)
        row = self.repository.get_session(session_id)
        NoteEditor(self, row["client_id"], row["code"], session_id)

    def mark(self, tree, done):
        self.repository.set_done(selected_id(tree), done)
        self.refresh()

    def export_package(self):
        session_id = selected_id(self.sessions_tree)
        path = filedialog.asksaveasfilename(parent=self, defaultextension=".json", initialfile=f"catatan-{session_id}.json", filetypes=[("Paket RuangCatat", "*.json")])
        if path:
            self.service.export_file(session_id, path)
            messagebox.showinfo("Ekspor selesai", "Paket tersandi disimpan tanpa kunci atau plainteks.", parent=self)

    def import_package(self):
        path = filedialog.askopenfilename(parent=self, filetypes=[("Paket RuangCatat", "*.json")])
        if not path:
            return
        dialog = tk.Toplevel(self)
        dialog.title("Verifikasi kunci paket impor")
        dialog.transient(self)
        dialog.grab_set()
        ttk.Label(dialog, text="Masukkan kunci paket. Setiap impor membuat sesi baru.").pack(padx=12, pady=12)
        fields = KeyFields(dialog)
        fields.pack(fill="x", padx=12, pady=6)
        def close():
            fields.clear()
            dialog.destroy()
        def submit():
            try:
                self.service.import_file(path, fields.keys())
                self.refresh()
                close()
                messagebox.showinfo("Impor selesai", "Paket diverifikasi dan ditambahkan sebagai sesi baru.", parent=self)
            except (ValueError, OSError) as exc:
                messagebox.showerror("Impor gagal", str(exc), parent=dialog)
        ttk.Button(dialog, text="Verifikasi & impor", command=submit).pack(pady=12)
        dialog.protocol("WM_DELETE_WINDOW", close)

    def close(self):
        self.demo.clear()
        self.repository.close()
        self.destroy()


def main():
    app = App()
    app.mainloop()
