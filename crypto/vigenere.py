"""
Mengenkripsi dan mendekripsi dengan pergeseran huruf berdasarkan kunci berulang. Angka dan tanda baca tidak menghabiskan posisi kunci.
"""


from .keys import validate

def transform(text, key, direction):
    key = validate(key)
    result, position = [], 0
    for char in text:
        if 'A' <= char <= 'Z' or 'a' <= char <= 'z':
            base = ord('A') if char.isupper() else ord('a')
            shift = ord(key[position % len(key)]) - ord('A')
            # Enkripsi (P+K) mod 26; dekripsi (C-K) mod 26.
            result.append(chr(base + (ord(char) - base + direction * shift) % 26))
            position += 1
        else:
            result.append(char)  # Non-Latin tidak menghabiskan posisi kunci.
    return ''.join(result)

def encrypt(text, key):
    return transform(text, key, 1)

def decrypt(text, key):
    return transform(text, key, -1)
