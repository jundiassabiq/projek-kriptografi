from .keys import validate

def order_for(key):
    key = validate(key)
    # Urut huruf kunci, lalu posisi asal untuk huruf yang sama.
    return sorted(range(len(key)), key=lambda index: (key[index], index))

def encrypt(text, key):
    order = order_for(key)
    return ''.join(text[column::len(key)] for column in order)

def decrypt(text, key):
    order = order_for(key)
    width = len(key)
    rows, remainder = divmod(len(text), width)
    columns, offset = [''] * width, 0
    for column in order:
        # Kolom kiri memuat sisa karakter di baris terakhir; tanpa padding.
        length = rows + (1 if column < remainder else 0)
        columns[column] = text[offset:offset + length]
        offset += length
    return ''.join(columns[index % width][index // width] for index in range(len(text)))
