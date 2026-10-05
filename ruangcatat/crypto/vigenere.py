"""Vigenere modulo 26 dengan pelestarian format dan Unicode."""
from .common import validate_key


def _transform(text: str, key: str, direction: int) -> str:
    shifts = [ord(char) - ord("A") for char in validate_key(key)]
    result, position = [], 0
    for char in text:
        if "A" <= char <= "Z" or "a" <= char <= "z":
            base = ord("A") if char.isupper() else ord("a")
            # Pengurangan untuk dekripsi adalah kebalikan penjumlahan enkripsi.
            shift = shifts[position % len(shifts)]
            result.append(chr(base + (ord(char) - base + direction * shift) % 26))
            position += 1
        else:
            # Tanda baca dan huruf non-Latin tidak menghabiskan posisi kunci.
            result.append(char)
    return "".join(result)


def encrypt(text: str, key: str) -> str:
    return _transform(text, key, 1)


def decrypt(text: str, key: str) -> str:
    return _transform(text, key, -1)
