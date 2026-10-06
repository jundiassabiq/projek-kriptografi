from . import monoalphabetic, vigenere, columnar

def encrypt(text, keys):
    text = monoalphabetic.encrypt(text, keys['mono'])
    text = vigenere.encrypt(text, keys['vigenere'])
    return columnar.encrypt(text, keys['columnar'])

def decrypt(text, keys):
    text = columnar.decrypt(text, keys['columnar'])
    text = vigenere.decrypt(text, keys['vigenere'])
    return monoalphabetic.decrypt(text, keys['mono'])
