import random
import string
import unittest
from ruangcatat.crypto import Keys, encrypt, decrypt
from ruangcatat.crypto import monoalphabetic, vigenere, columnar

KEYS = Keys("ZEBRAS", "LEMON", "BALLOON")


class CryptoTests(unittest.TestCase):
    def test_mono_known_vector(self):
        self.assertEqual(monoalphabetic.key_alphabet("zebras"), "ZEBRASCDFGHIJKLMNOPQTUVWXY")
        self.assertEqual(monoalphabetic.encrypt("ATTACK", "ZEBRAS"), "ZQQZBH")
        self.assertEqual(monoalphabetic.decrypt("Zqqzbh!", "ZEBRAS"), "Attack!")

    def test_vigenere_known_vector(self):
        self.assertEqual(vigenere.encrypt("ATTACKATDAWN", "LEMON"), "LXFOPVEFRNHR")
        self.assertEqual(vigenere.decrypt("Lxfopv ef rnhr!", "LEMON"), "Attack at dawn!")
        self.assertEqual(vigenere.encrypt("Aé A中A!", "BC"), "Bé C中B!")

    def test_columnar_known_vector(self):
        self.assertEqual(columnar.encrypt("ABCDEFGH", "CAB"), "BEHCFADG")
        self.assertEqual(columnar.decrypt("BEHCFADG", "CAB"), "ABCDEFGH")
        self.assertEqual(columnar.encrypt("ABCDEFGH", "BABA"), "BFDHAECG")
        self.assertEqual(columnar.decrypt("BFDHAECG", "BABA"), "ABCDEFGH")
        self.assertEqual(columnar.encrypt("WEAREDISCOVEREDFLEEATONCE", "ZEBRAS"), "EVLNACDTESEAROFODEECWIREE")

    def test_roundtrip_edges(self):
        for text in ("", "a", "AB", "Catatan Fiktif: 123!", "é中🙂\n\r\n\t AaZz ", "X" * 10001):
            with self.subTest(text=text[:30]):
                result = encrypt(text, KEYS)
                self.assertEqual(decrypt(result.text, KEYS).text, text)
                self.assertEqual(len(result.text), len(text))
                self.assertEqual(len(result.stages), 3)

    def test_randomized_roundtrips(self):
        rng = random.Random(2026)
        charset = string.ascii_letters + string.digits + " .,!?\r\n\t🙂é中"
        for length in range(180):
            text = "".join(rng.choice(charset) for _ in range(length))
            keys = Keys("BANANA", "FIKTIF", "A" * (length % 15 + 1))
            for module, key in ((monoalphabetic, keys.mono), (vigenere, keys.vigenere), (columnar, keys.columnar)):
                self.assertEqual(module.decrypt(module.encrypt(text, key), key), text)
            self.assertEqual(decrypt(encrypt(text, keys).text, keys).text, text)

    def test_invalid_keys(self):
        for key in ("", " ", "a b", "123", "é", "ABC!", None):
            for module in (monoalphabetic, vigenere, columnar):
                with self.subTest(module=module.__name__, key=key):
                    with self.assertRaises(ValueError):
                        module.encrypt("", key)
                    with self.assertRaises(ValueError):
                        module.decrypt("", key)

    def test_inverse_stage_order(self):
        result = encrypt("Teks\nUji 🙂", KEYS)
        back = decrypt(result.text, KEYS)
        self.assertEqual(back.stages[0][1], result.stages[1][1])
        self.assertEqual(back.stages[1][1], result.stages[0][1])
        self.assertEqual(back.text, "Teks\nUji 🙂")
