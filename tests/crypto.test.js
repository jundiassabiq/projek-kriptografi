import test from 'node:test';
import assert from 'node:assert/strict';
import * as mono from '../js/crypto/monoalphabetic.js';
import * as vigenere from '../js/crypto/vigenere.js';
import * as columnar from '../js/crypto/columnar.js';
import {encrypt, decrypt} from '../js/crypto/pipeline.js';
const KEYS = {mono: 'ZEBRAS', vigenere: 'LEMON', columnar: 'BALLOON'};

test('Monoalfabetik: vektor diketahui dan kapitalisasi', () => {
  assert.equal(mono.encrypt('ATTACK', 'ZEBRAS'), 'ZQQZBH');
  assert.equal(mono.decrypt('Zqqzbh!', 'ZEBRAS'), 'Attack!');
  assert.equal(mono.encrypt('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'AAAA'), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ');
});
test('Vigenere: vektor diketahui', () => {
  assert.equal(vigenere.encrypt('ATTACKATDAWN', 'LEMON'), 'LXFOPVEFRNHR');
  assert.equal(vigenere.decrypt('Lxfopv ef rnhr!', 'LEMON'), 'Attack at dawn!');
});
test('Vigenere tidak memakai posisi kunci untuk non-ASCII', () => {
  assert.equal(vigenere.encrypt('Aé A中A!', 'BC'), 'Bé C中B!');
});
test('Kolom: vektor diketahui dan kolom tidak penuh', () => {
  assert.equal(columnar.encrypt('ABCDEFGH', 'CAB'), 'BEHCFADG');
  assert.equal(columnar.decrypt('BEHCFADG', 'CAB'), 'ABCDEFGH');
  assert.equal(columnar.encrypt('WEAREDISCOVEREDFLEEATONCE', 'ZEBRAS'), 'EVLNACDTESEAROFODEECWIREE');
});
test('Kolom: huruf kunci berulang', () => {
  assert.equal(columnar.encrypt('ABCDEFGH', 'BABA'), 'BFDHAECG');
  assert.equal(columnar.decrypt('BFDHAECG', 'BABA'), 'ABCDEFGH');
});
test('Urutan invers pipeline dan tiga hasil antara', () => {
  const result = encrypt('Catatan fiktif 🙂', KEYS), back = decrypt(result.text, KEYS);
  assert.equal(result.stages.length, 3); assert.equal(back.stages.length, 3);
  assert.equal(back.stages[0].text, result.stages[1].text);
  assert.equal(back.stages[1].text, result.stages[0].text);
  assert.equal(back.text, 'Catatan fiktif 🙂');
});
test('Semua algoritma menolak kunci kosong/non-Latin termasuk pada teks kosong', () => {
  for (const module of [mono, vigenere, columnar]) {
    for (const key of ['', ' ', 'A B', '123', 'é', 'KEY!', null]) {
      assert.throws(() => module.encrypt('', key)); assert.throws(() => module.decrypt('', key));
    }
  }
});
test('Round-trip kosong, pendek, panjang, emoji, Unicode, whitespace dan CRLF', () => {
  for (const text of ['', 'a', 'AB', 'AbZz! 123', '  é中🙂\r\n\t𐍈\nßİ  ', 'X'.repeat(10001)]) {
    const result = encrypt(text, KEYS);
    assert.equal(decrypt(result.text, KEYS).text, text);
    assert.equal(Array.from(result.text).length, Array.from(text).length);
  }
});
test('200 variasi panjang, kunci berulang dan pesan deterministik', () => {
  const alphabet = Array.from('AaZz0123 .!?\r\n\t🙂中é𐍈');
  for (let length = 0; length < 200; length++) {
    const text = Array.from({length}, (_, i) => alphabet[(i * 7 + length) % alphabet.length]).join('');
    const keys = {mono:'BANANA', vigenere:'FIKTIF', columnar:'A'.repeat(length % 17 + 1)};
    assert.equal(decrypt(encrypt(text, keys).text, keys).text, text);
    for (const [module, key] of [[mono,keys.mono],[vigenere,keys.vigenere],[columnar,keys.columnar]]) {
      assert.equal(module.decrypt(module.encrypt(text,key),key),text);
    }
  }
});
