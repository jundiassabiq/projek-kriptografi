"""Substitusi monoalfabetik berbasis kata kunci, dibuat tanpa library kripto."""
from .common import ALPHABET, validate_key, translate_letters


def key_alphabet(key: str) -> str:
    # Kata kunci tanpa duplikasi, dilanjutkan huruf alfabet yang belum ada.
    return "".join(dict.fromkeys(validate_key(key) + ALPHABET))


def encrypt(text: str, key: str) -> str:
    return translate_letters(text, key_alphabet(key))


def decrypt(text: str, key: str) -> str:
    alphabet = key_alphabet(key)
    inverse = "".join(ALPHABET[alphabet.index(char)] for char in ALPHABET)
    return translate_letters(text, inverse)
