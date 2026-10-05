from dataclasses import dataclass
from . import monoalphabetic, vigenere, columnar
from .common import validate_key


@dataclass(frozen=True)
class Keys:
    mono: str
    vigenere: str
    columnar: str

    def validate(self):
        for key in (self.mono, self.vigenere, self.columnar):
            validate_key(key)


@dataclass(frozen=True)
class Result:
    text: str
    stages: tuple[tuple[str, str], ...]


def encrypt(text: str, keys: Keys) -> Result:
    keys.validate()
    first = monoalphabetic.encrypt(text, keys.mono)
    second = vigenere.encrypt(first, keys.vigenere)
    third = columnar.encrypt(second, keys.columnar)
    return Result(third, (("Substitusi Monoalfabetik", first),
                         ("Vigenere", second), ("Transposisi Kolom", third)))


def decrypt(text: str, keys: Keys) -> Result:
    keys.validate()
    first = columnar.decrypt(text, keys.columnar)
    second = vigenere.decrypt(first, keys.vigenere)
    third = monoalphabetic.decrypt(second, keys.mono)
    return Result(third, (("Balik Transposisi Kolom", first),
                         ("Balik Vigenere", second), ("Balik Substitusi", third)))
