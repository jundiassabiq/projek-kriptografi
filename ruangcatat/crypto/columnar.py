"""Transposisi kolom tanpa padding: panjang asli tidak berubah."""
from .common import validate_key


def column_order(key: str) -> list[int]:
    key = validate_key(key)
    # Posisi asal menjadi pembeda untuk huruf kunci yang berulang.
    return sorted(range(len(key)), key=lambda index: (key[index], index))


def encrypt(text: str, key: str) -> str:
    order = column_order(key)
    width = len(key)
    return "".join(text[index::width] for index in order)


def decrypt(text: str, key: str) -> str:
    order = column_order(key)
    width = len(key)
    full_rows, remainder = divmod(len(text), width)
    columns, offset = {}, 0
    for index in order:
        # Kolom paling kiri mendapat satu karakter tambahan pada baris terakhir.
        size = full_rows + (index < remainder)
        columns[index] = text[offset:offset + size]
        offset += size
    return "".join(columns[position % width][position // width]
                   for position in range(len(text)))
