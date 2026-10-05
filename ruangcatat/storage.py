"""Penyimpanan hanya metadata dan cipherteks; tidak menerima kunci."""
from pathlib import Path
import sqlite3


class Repository:
    def __init__(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY,
                code TEXT NOT NULL UNIQUE COLLATE NOCASE
            );
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                client_id INTEGER NOT NULL REFERENCES clients(id),
                session_date TEXT NOT NULL,
                next_date TEXT NOT NULL DEFAULT '',
                done INTEGER NOT NULL DEFAULT 0 CHECK(done IN (0,1)),
                ciphertext TEXT NOT NULL
            );
        """)
        self.connection.commit()

    def close(self):
        self.connection.close()

    def add_client(self, code):
        try:
            with self.connection:
                cursor = self.connection.execute("INSERT INTO clients(code) VALUES (?)", (code,))
            return cursor.lastrowid
        except sqlite3.IntegrityError as exc:
            raise ValueError("Kode klien sudah digunakan.") from exc

    def clients(self, search=""):
        # instr menjadikan pencarian literal, bukan pola SQL LIKE.
        return [dict(row) for row in self.connection.execute(
            "SELECT * FROM clients WHERE instr(lower(code),lower(?))>0 ORDER BY code", (search,))]

    def sessions(self, client_id=None, pending=False):
        conditions, params = [], []
        if client_id is not None:
            conditions.append("s.client_id=?")
            params.append(client_id)
        if pending:
            conditions.append("s.done=0")
        where = " WHERE " + " AND ".join(conditions) if conditions else ""
        query = ("SELECT s.*, c.code FROM sessions s JOIN clients c ON c.id=s.client_id" +
                 where + " ORDER BY s.session_date DESC, s.id DESC")
        return [dict(row) for row in self.connection.execute(query, params)]

    def get_session(self, session_id):
        row = self.connection.execute(
            "SELECT s.*, c.code FROM sessions s JOIN clients c ON c.id=s.client_id WHERE s.id=?",
            (session_id,)).fetchone()
        if row is None:
            raise ValueError("Catatan tidak ditemukan.")
        return dict(row)

    def save_session(self, client_id, session_date, next_date, ciphertext, session_id=None):
        with self.connection:
            if session_id is None:
                cursor = self.connection.execute(
                    "INSERT INTO sessions(client_id,session_date,next_date,ciphertext) VALUES (?,?,?,?)",
                    (client_id, session_date, next_date, ciphertext))
                return cursor.lastrowid
            cursor = self.connection.execute(
                "UPDATE sessions SET session_date=?,next_date=?,ciphertext=? WHERE id=? AND client_id=?",
                (session_date, next_date, ciphertext, session_id, client_id))
            if cursor.rowcount != 1:
                raise ValueError("Catatan tidak ditemukan untuk klien ini.")
            return session_id

    def set_done(self, session_id, done):
        with self.connection:
            cursor = self.connection.execute("UPDATE sessions SET done=? WHERE id=?", (int(done), session_id))
            if cursor.rowcount != 1:
                raise ValueError("Catatan tidak ditemukan.")

    def counts(self):
        clients = self.connection.execute("SELECT count(*) FROM clients").fetchone()[0]
        sessions = self.connection.execute("SELECT count(*) FROM sessions").fetchone()[0]
        pending = self.connection.execute("SELECT count(*) FROM sessions WHERE done=0").fetchone()[0]
        return clients, sessions, pending

    def import_session(self, code, session_date, next_date, done, ciphertext):
        # Klien dan sesi ditulis dalam satu transaksi: kegagalan tidak menyisakan klien baru.
        with self.connection:
            row = self.connection.execute("SELECT id FROM clients WHERE code=?", (code,)).fetchone()
            if row:
                client_id = row[0]
            else:
                client_id = self.connection.execute("INSERT INTO clients(code) VALUES (?)", (code,)).lastrowid
            return self.connection.execute(
                "INSERT INTO sessions(client_id,session_date,next_date,done,ciphertext) VALUES (?,?,?,?,?)",
                (client_id, session_date, next_date, int(done), ciphertext)).lastrowid
