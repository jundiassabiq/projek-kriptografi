"""Aturan aplikasi, validasi catatan, dan paket impor/ekspor."""
from datetime import date
from pathlib import Path
import json
import re
from .crypto import Keys, encrypt, decrypt

FORMAT = "ruangcatat-classical-v1"
ALGORITHMS = ["monoalphabetic", "vigenere", "columnar"]
FIELDS = {"format", "topic", "notes", "follow_up"}


def validate_code(code):
    if not isinstance(code, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", code):
        raise ValueError("Gunakan kode samaran 1-32 karakter: huruf, angka, '-' atau '_'.")
    return code


def validate_dates(session_date, next_date):
    for value in (session_date, next_date):
        if not isinstance(value, str):
            raise ValueError("Tanggal harus berupa teks YYYY-MM-DD.")
    try:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", session_date):
            raise ValueError()
        first = date.fromisoformat(session_date)
        if next_date:
            if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", next_date):
                raise ValueError()
            if date.fromisoformat(next_date) < first:
                raise ValueError("Jadwal berikutnya tidak boleh sebelum tanggal sesi.")
    except ValueError as exc:
        raise ValueError("Tanggal tidak valid. Gunakan YYYY-MM-DD dan jadwal berikutnya >= tanggal sesi.") from exc


def decode_note(ciphertext, keys):
    result = decrypt(ciphertext, keys)
    try:
        payload = json.loads(result.text)
    except (ValueError, TypeError) as exc:
        raise ValueError("Kunci salah atau data catatan rusak.") from exc
    if (not isinstance(payload, dict) or set(payload) != FIELDS or
        payload.get("format") != FORMAT or
        any(not isinstance(payload.get(field), str) for field in ("topic", "notes", "follow_up")) or
        not payload["topic"].strip() or not payload["notes"].strip()):
        raise ValueError("Kunci salah atau struktur catatan rusak.")
    return payload


class NoteService:
    def __init__(self, repository):
        self.repository = repository

    def add_client(self, code):
        return self.repository.add_client(validate_code(code.strip()))

    def save(self, client_id, session_date, next_date, topic, notes, follow_up, keys, session_id=None):
        validate_dates(session_date, next_date)
        if not topic.strip() or not notes.strip():
            raise ValueError("Topik dan isi catatan wajib diisi.")
        payload = {"format": FORMAT, "topic": topic, "notes": notes, "follow_up": follow_up}
        plain = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        cipher = encrypt(plain, keys).text
        # Validasi round-trip dilakukan sebelum menyimpan, tanpa menyimpan plainteks.
        if decrypt(cipher, keys).text != plain:
            raise ValueError("Validasi dekripsi gagal; catatan tidak disimpan.")
        return self.repository.save_session(client_id, session_date, next_date, cipher, session_id)

    def open(self, session_id, keys):
        return decode_note(self.repository.get_session(session_id)["ciphertext"], keys)

    def export_package(self, session_id):
        row = self.repository.get_session(session_id)
        package = {"format": FORMAT, "algorithms": ALGORITHMS, "client_code": row["code"],
                   "session_date": row["session_date"], "next_date": row["next_date"],
                   "done": bool(row["done"]), "ciphertext": row["ciphertext"]}
        return package

    def export_file(self, session_id, path):
        package = self.export_package(session_id)
        Path(path).write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")

    def import_file(self, path, keys):
        try:
            package = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        except (ValueError, UnicodeError) as exc:
            raise ValueError("File bukan paket JSON RuangCatat yang valid.") from exc
        return self.import_package(package, keys)

    def import_package(self, package, keys):
        expected = {"format", "algorithms", "client_code", "session_date", "next_date", "done", "ciphertext"}
        if (not isinstance(package, dict) or set(package) != expected or
            package.get("format") != FORMAT or package.get("algorithms") != ALGORITHMS or
            type(package.get("done")) is not bool or
            not isinstance(package.get("ciphertext"), str)):
            raise ValueError("Struktur atau versi paket tidak didukung.")
        validate_code(package["client_code"])
        validate_dates(package["session_date"], package["next_date"])
        # Verifikasi dengan kunci sebelum transaksi impor dilakukan.
        decode_note(package["ciphertext"], keys)
        return self.repository.import_session(package["client_code"], package["session_date"],
            package["next_date"], package["done"], package["ciphertext"])
