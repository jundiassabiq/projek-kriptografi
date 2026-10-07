"""
Mengatur alur catatan: validasi input dan format file, pembentukan JSON, pemanggilan tiga algoritma, serta pemeriksaan hasil dekripsi identik. Tidak menyimpan catatan atau kunci.
"""


import json
import re
from crypto import pipeline, frequency, alphabetic
from crypto.keys import validate

FORMAT = 'ruangcatat-file-v4'
MAX_FILE_BYTES = 1024 * 1024
KEY_NAMES = {'mono', 'vigenere', 'columnar'}

def validate_keys(keys):
    if not isinstance(keys, dict) or set(keys) != KEY_NAMES:
        raise ValueError('Masukkan ketiga kunci.')
    for key in keys.values():
        validate(key)

def validate_note(code, text):
    if not isinstance(code, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,32}', code):
        raise ValueError('Kode klien: 1–32 huruf/angka, tanda - atau _.')
    if not isinstance(text, str) or not text.strip():
        raise ValueError('Isi catatan tidak boleh kosong.')

def file_text(package):
    return json.dumps(package, ensure_ascii=False, separators=(',', ':'))

def validate_package(package):
    if not isinstance(package, dict) or set(package) != {'format', 'ciphertext'} or package['format'] != FORMAT:
        raise ValueError('Format file tidak didukung. Gunakan file v4 dengan cipherteks A–Z.')
    cipher = package['ciphertext']
    if not isinstance(cipher, str) or not cipher or len(cipher) % 2 or any(not 'A' <= char <= 'Z' for char in cipher):
        raise ValueError('Kunci salah atau data rusak')
    # Byte UTF-8 hanya untuk ukuran file/HTTP, tidak sebagai tahap algoritma.
    if len(file_text(package).encode('utf-8')) > MAX_FILE_BYTES:
        raise ValueError('Ukuran file maksimal 1 MB.')

def unpack(package, keys):
    validate_package(package)
    try:
        text = pipeline.decrypt(alphabetic.decode(package['ciphertext']), keys)
        payload = json.loads(text)
        if not isinstance(payload, dict) or set(payload) != {'format', 'code', 'text'} or payload['format'] != FORMAT:
            raise ValueError()
        validate_note(payload['code'], payload['text'])
        return payload
    except (ValueError, TypeError, KeyError, UnicodeError):
        raise ValueError('Kunci salah atau data rusak') from None

def encrypt_note(code, text, keys):
    validate_keys(keys)
    validate_note(code, text)
    payload = {'format': FORMAT, 'code': code, 'text': text}
    # JSON masuk tiga algoritma, kemudian hasil akhirnya ditampilkan sebagai A–Z.
    plain = file_text(payload)
    if 2 * len(plain.encode('utf-8')) + len(file_text({'format': FORMAT, 'ciphertext': ''})) > MAX_FILE_BYTES:
        raise ValueError('Catatan terlalu panjang. Hasil file maksimal 1 MB.')
    package = {'format': FORMAT, 'ciphertext': alphabetic.encode(pipeline.encrypt(plain, keys))}
    # Ukur paket final; cipherteks telah berupa pasangan huruf A–Z.
    validate_package(package)
    if unpack(package, keys) != payload:
        raise ValueError('Validasi gagal. File tidak dibuat.')
    # Panel dan analisis frekuensi memakai cipherteks isi, tanpa kode/penanda JSON.
    note_raw_ciphertext = pipeline.encrypt(text, keys)
    note_ciphertext = alphabetic.encode(note_raw_ciphertext)
    if pipeline.decrypt(alphabetic.decode(note_ciphertext), keys) != text:
        raise ValueError('Validasi gagal. File tidak dibuat.')
    return {'package': package, 'filename': code + '.json', 'validated': True,
            'note_raw_ciphertext': note_raw_ciphertext,
            'note_ciphertext': note_ciphertext,
            'frequency': frequency.analyze(note_ciphertext)}

def decrypt_note(package, keys):
    validate_keys(keys)
    payload = unpack(package, keys)
    # Pulihkan cipherteks khusus isi dengan kunci yang sama agar analisis
    # konsisten dengan panel enkripsi, tanpa menyertakan kode/penanda JSON.
    note_ciphertext = alphabetic.encode(pipeline.encrypt(payload['text'], keys))
    return {'code': payload['code'], 'text': payload['text'],
            'frequency': frequency.analyze(note_ciphertext)}
