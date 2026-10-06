import json
import unittest
from crypto import monoalphabetic as mono, vigenere as vig, columnar as col, pipeline, frequency
from notes import encrypt_note, decrypt_note, FORMAT, MAX_FILE_BYTES

KEYS = {'mono': 'ZEBRAS', 'vigenere': 'LEMON', 'columnar': 'BALLOON'}

class AlgorithmTests(unittest.TestCase):
    def test_mono_vector(self):
        self.assertEqual(mono.encrypt('ATTACK', 'ZEBRAS'), 'ZQQZBH')
        self.assertEqual(mono.decrypt('Zqqzbh!', 'ZEBRAS'), 'Attack!')
        self.assertEqual(mono.encrypt('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'AAAA'), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    def test_vigenere_vector(self):
        self.assertEqual(vig.encrypt('ATTACKATDAWN', 'LEMON'), 'LXFOPVEFRNHR')
        self.assertEqual(vig.decrypt('Lxfopv ef rnhr!', 'LEMON'), 'Attack at dawn!')

    def test_vigenere_nonlatin_position(self):
        self.assertEqual(vig.encrypt('Aé A中A!', 'BC'), 'Bé C中B!')

    def test_columnar_vectors(self):
        self.assertEqual(col.encrypt('ABCDEFGH', 'CAB'), 'BEHCFADG')
        self.assertEqual(col.decrypt('BEHCFADG', 'CAB'), 'ABCDEFGH')
        self.assertEqual(col.encrypt('WEAREDISCOVEREDFLEEATONCE', 'ZEBRAS'), 'EVLNACDTESEAROFODEECWIREE')

    def test_repeated_column_key(self):
        self.assertEqual(col.encrypt('ABCDEFGH', 'BABA'), 'BFDHAECG')
        self.assertEqual(col.decrypt('BFDHAECG', 'BABA'), 'ABCDEFGH')

    def test_invalid_keys(self):
        for module in [mono, vig, col]:
            for key in ['', ' ', 'A B', '123', 'é', 'KEY!', None]:
                with self.subTest(module=module.__name__, key=key):
                    with self.assertRaises(ValueError): module.encrypt('', key)
                    with self.assertRaises(ValueError): module.decrypt('', key)

    def test_roundtrip_formats(self):
        for text in ['', 'a', 'AB', 'AbZz! 123', '  é中🙂\r\n\t𐍈\nßİ  ', 'X' * 10001]:
            for module, key in [(mono, 'BANANA'), (vig, 'LEMON'), (col, 'BALLOON')]:
                with self.subTest(module=module.__name__, length=len(text)):
                    self.assertEqual(module.decrypt(module.encrypt(text, key), key), text)

    def test_inverse_pipeline(self):
        text = 'AbZz 中🙂\n'
        first = mono.encrypt(text, KEYS['mono'])
        second = vig.encrypt(first, KEYS['vigenere'])
        cipher = col.encrypt(second, KEYS['columnar'])
        self.assertEqual(pipeline.encrypt(text, KEYS), cipher)
        self.assertEqual(pipeline.decrypt(cipher, KEYS), text)

    def test_200_lengths(self):
        alphabet = 'AaZz0123 .!?\r\n\t🙂中é𐍈'
        for length in range(200):
            text = ''.join(alphabet[(i * 7 + length) % len(alphabet)] for i in range(length))
            keys = {'mono': 'BANANA', 'vigenere': 'FIKTIF', 'columnar': 'A' * (length % 17 + 1)}
            self.assertEqual(pipeline.decrypt(pipeline.encrypt(text, keys), keys), text)

    def test_frequency_known(self):
        result = frequency.analyze('AaBbA !中é12')
        self.assertEqual(result['total'], 5)
        self.assertEqual(result['rows'][0], {'letter': 'A', 'count': 3, 'percent': 60.0})
        self.assertEqual(result['rows'][1], {'letter': 'B', 'count': 2, 'percent': 40.0})

    def test_frequency_empty(self):
        result = frequency.analyze('123中🙂')
        self.assertEqual(result['total'], 0)
        self.assertEqual(len(result['rows']), 26)
        self.assertTrue(all(row['percent'] == 0 for row in result['rows']))

class NoteTests(unittest.TestCase):
    def test_text_format_file_roundtrip(self):
        text = 'Catatan fiktif\r\nالعربية 中文 Ελληνικά Русский 🙂 café\n  akhir  '
        result = encrypt_note('K-001', text, KEYS)
        package = json.loads(json.dumps(result['package']))
        recovered = decrypt_note(package, KEYS)
        self.assertEqual(recovered['text'], text)
        self.assertEqual(recovered['code'], 'K-001')
        self.assertTrue(result['validated'])

    def test_file_privacy(self):
        text = 'RAHASIA FIKTIF YANG TIDAK BOLEH MUNCUL'
        result = encrypt_note('K-001', text, KEYS)
        file = json.dumps(result['package'])
        self.assertEqual(set(result['package']), {'format', 'ciphertext'})
        for secret in [text, 'K-001', *KEYS.values()]: self.assertNotIn(secret, file)
        self.assertEqual(result['filename'], 'K-001.json')

    def test_wrong_keys(self):
        package = encrypt_note('K', 'Data fiktif', KEYS)['package']
        for name in KEYS:
            bad = dict(KEYS, **{name: 'WRONG'})
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, 'Kunci salah atau data rusak'):
                    decrypt_note(package, bad)

    def test_corrupt_ciphertext_unchanged(self):
        package = encrypt_note('K', 'Data fiktif', KEYS)['package']
        package['ciphertext'] = 'Z' + package['ciphertext'][1:]
        original = dict(package)
        with self.assertRaisesRegex(ValueError, 'Kunci salah atau data rusak'): decrypt_note(package, KEYS)
        self.assertEqual(package, original)

    def test_invalid_packages(self):
        for value in [None, [], {}, {'format': 'old', 'ciphertext': 'ABC'}, {'format': FORMAT, 'ciphertext': ''},
                      {'format': FORMAT, 'ciphertext': 'ABC', 'key': 'SECRET'}]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError): decrypt_note(value, KEYS)

    def test_format_marker_required(self):
        encoded = json.dumps({'format': 'wrong', 'code': 'K', 'text': 'fiktif'})
        package = {'format': FORMAT, 'ciphertext': pipeline.encrypt(encoded, KEYS)}
        with self.assertRaisesRegex(ValueError, 'Kunci salah atau data rusak'): decrypt_note(package, KEYS)

    def test_invalid_input(self):
        for code, text in [('bad/name', 'fiktif'), ('', 'fiktif'), ('K', ''), ('K', ' \n')]:
            with self.assertRaises(ValueError): encrypt_note(code, text, KEYS)
        for keys in [{}, dict(KEYS, mono='123'), dict(KEYS, extra='ABC')]:
            with self.assertRaises(ValueError): encrypt_note('K', 'fiktif', keys)

    def test_large_files(self):
        with self.assertRaisesRegex(ValueError, '1 MB'): encrypt_note('K', 'x' * MAX_FILE_BYTES, KEYS)
        with self.assertRaisesRegex(ValueError, '1 MB'):
            decrypt_note({'format': FORMAT, 'ciphertext': 'A' * MAX_FILE_BYTES}, KEYS)

    def test_boundary_output(self):
        # Angka ukuran mencakup escape JSON final, bukan hanya panjang teks.
        package = encrypt_note('K', 'x', KEYS)['package']
        overhead = len(json.dumps(package, ensure_ascii=False, separators=(',', ':')).encode('utf-8')) - 1
        size = MAX_FILE_BYTES - overhead
        output = encrypt_note('K', 'x' * size, KEYS)
        self.assertEqual(len(json.dumps(output['package'], separators=(',', ':')).encode()), MAX_FILE_BYTES)
        with self.assertRaisesRegex(ValueError, '1 MB'): encrypt_note('K', 'x' * (size + 1), KEYS)

    def test_direct_pipeline_without_hex(self):
        keys = {'mono': 'mura', 'vigenere': 'cinta', 'columnar': 'mufik'}
        plain = json.dumps({'format': FORMAT, 'code': 'K-110', 'text': 'Kipeli'}, ensure_ascii=False, separators=(',', ':'))
        result = encrypt_note('K-110', 'Kipeli', keys)
        self.assertEqual(result['package']['ciphertext'], pipeline.encrypt(plain, keys))
        self.assertEqual(decrypt_note(result['package'], keys)['text'], 'Kipeli')
        with self.assertRaisesRegex(ValueError, 'encoding lama'):
            decrypt_note({'format': 'ruangcatat-file-v2', 'ciphertext': 'ABC123'}, keys)

if __name__ == '__main__':
    unittest.main()

