import re

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def validate_key(key: str) -> str:
    """Hanya huruf ASCII Latin; tidak diam-diam membuang karakter kunci."""
    if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z]+", key):
        raise ValueError("Kunci wajib berisi satu atau lebih huruf A-Z/a-z, tanpa spasi atau angka.")
    return key.upper()


def translate_letters(text: str, mapping: str) -> str:
    result = []
    for char in text:
        if "A" <= char <= "Z":
            result.append(mapping[ord(char) - ord("A")])
        elif "a" <= char <= "z":
            result.append(mapping[ord(char) - ord("a")].lower())
        else:
            result.append(char)
    return "".join(result)
