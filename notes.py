"""Format file dan alur catatan. Tidak menyimpan data atau kunci di server."""
import json
import re
from crypto import pipeline, frequency
from crypto.keys import validate

FORMAT = 'ruangcatat-file-v2'
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
        raise ValueError('Format file tidak didukung. Pilih file RuangCatat File v2.')
    cipher = package['ciphertext']
    if not isinstance(cipher, str) or not cipher or any(c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' for c in cipher):
        raise ValueError('Kunci salah atau data rusak')
    if len(file_text(package).encode('utf-8')) > MAX_FILE_BYTES:
        raise ValueError('Ukuran file maksimal 1 MB.')

def unpack(package, keys):
    validate_package(package)
    try:
        hex_text = pipeline.decrypt(package['ciphertext'], keys)
        # fromhex menerima spasi, maka pastikan hasil benar-benar hex kapital genap.
        if len(hex_text) % 2 or any(c not in '0123456789ABCDEF' for c in hex_text):
            raise ValueError()
        payload = json.loads(bytes.fromhex(hex_text).decode('utf-8'))
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
    # Encoding adalah persiapan data Unicode, bukan algoritma kriptografi keempat.
    encoded = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8').hex().upper()
    # Tiga algoritma mempertahankan panjang hex. Tolak sebelum memproses file besar.
    if len(encoded) + len(file_text({'format': FORMAT, 'ciphertext': ''})) > MAX_FILE_BYTES:
        raise ValueError('Catatan terlalu panjang. Hasil file maksimal 1 MB.')
    package = {'format': FORMAT, 'ciphertext': pipeline.encrypt(encoded, keys)}
    if unpack(package, keys) != payload:
        raise ValueError('Validasi gagal. File tidak dibuat.')
    return {'package': package, 'filename': code + '.json', 'validated': True,
            'frequency': frequency.analyze(package['ciphertext'])}

def decrypt_note(package, keys):
    validate_keys(keys)
    payload = unpack(package, keys)
    return {'code': payload['code'], 'text': payload['text'],
            'frequency': frequency.analyze(package['ciphertext'])}
