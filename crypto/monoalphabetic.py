"""
Mengenkripsi huruf melalui alfabet yang dibentuk dari kata kunci. Dekripsi memakai pemetaan terbalik; besar-kecil huruf dan karakter non-Latin dipertahankan.
"""


from .keys import validate

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def alphabet_for(key):
    # Hapus huruf kunci berulang, kemudian tambahkan huruf alfabet yang tersisa.
    result = ''
    for letter in validate(key) + ALPHABET:
        if letter not in result:
            result += letter
    return result

def transform(text, source, target):
    result = []
    for char in text:
        if 'A' <= char <= 'Z':
            result.append(target[source.index(char)])
        elif 'a' <= char <= 'z':
            result.append(target[source.index(char.upper())].lower())
        else:
            result.append(char)
    return ''.join(result)

def encrypt(text, key):
    return transform(text, ALPHABET, alphabet_for(key))

def decrypt(text, key):
    return transform(text, alphabet_for(key), ALPHABET)
