"""
Mengubah hasil cipher menjadi pasangan huruf A–Z dan mengembalikannya saat dekripsi.
Encoding ini tidak memakai kunci dan bukan algoritma enkripsi keempat.
"""


def encode(text):
    result = []
    # Tiap byte 0–255 diwakili dua huruf dengan basis 26.
    for value in text.encode('utf-8'):
        first, second = divmod(value, 26)
        result.append(chr(65 + first) + chr(65 + second))
    return ''.join(result)

def decode(text):
    if not isinstance(text, str) or len(text) % 2 or any(not 'A' <= char <= 'Z' for char in text):
        raise ValueError('Encoding pasangan huruf tidak valid.')
    values = []
    for index in range(0, len(text), 2):
        value = (ord(text[index]) - 65) * 26 + ord(text[index + 1]) - 65
        if value > 255:
            raise ValueError('Encoding pasangan huruf tidak valid.')
        values.append(value)
    return bytes(values).decode('utf-8')
