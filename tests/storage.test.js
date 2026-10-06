import test from 'node:test';
import assert from 'node:assert/strict';
import {loadNotes, addNote, removeNote, validateDate, STORAGE_KEY, StorageError} from '../js/storage.js';
import {encrypt, decrypt} from '../js/crypto/pipeline.js';
function memory() {
  const values = new Map();
  return {getItem: key => values.get(key) ?? null, setItem: (key,value) => values.set(key,value)};
}
const record = (id, createdAt = 100) => ({id,clientCode:'K-001',sessionDate:'2026-10-06',createdAt,ciphertext:'ciphertext'});

test('Penyimpanan awal kosong', () => assert.deepEqual(loadNotes(memory()), []));
test('Simpan, baca ulang dan urutkan terbaru dahulu', () => {
  const store = memory();addNote(record('first',100),store);addNote(record('second',200),store);
  assert.deepEqual(loadNotes(store).map(note=>note.id),['second','first']);
});
test('Waktu sama: penambahan terakhir muncul pertama', () => {
  const store = memory();addNote(record('z',100),store);addNote(record('a',100),store);
  assert.deepEqual(loadNotes(store).map(note=>note.id),['a','z']);
});
test('Hapus hanya ID yang dipilih', () => {
  const store = memory();addNote(record('first'),store);addNote(record('second'),store);removeNote('first',store);
  assert.deepEqual(loadNotes(store).map(note=>note.id),['second']);
});
test('ID tidak ditemukan dan duplikasi tidak mengubah arsip', () => {
  const store = memory();addNote(record('first'),store);const before=store.getItem(STORAGE_KEY);
  assert.throws(()=>addNote(record('first'),store));assert.throws(()=>removeNote('missing',store));
  assert.equal(store.getItem(STORAGE_KEY),before);
});
test('Metadata dan properti ekstra ditolak', () => {
  const store = memory();
  for (const changed of [{clientCode:'Nama Asli'},{sessionDate:'2026-02-30'},{createdAt:-1},{ciphertext:''},{notes:'plaintext'}]) {
    assert.throws(()=>addNote({...record('id'),...changed},store));
  }
  assert.equal(store.getItem(STORAGE_KEY),null);
});
test('Tanggal kalender valid termasuk tahun kabisat', () => {
  assert.equal(validateDate('2024-02-29'),true);
  for(const value of ['2026-02-29','2026-02-30','2026-13-01','20261006','bad',null])assert.equal(validateDate(value),false);
});
test('JSON rusak dan format salah tidak direset saat baca atau simpan', () => {
  for(const raw of ['not json','[]','{}',JSON.stringify({version:99,notes:[]}),JSON.stringify({version:1,notes:[{}]})]) {
    const store=memory();store.setItem(STORAGE_KEY,raw);
    assert.throws(()=>loadNotes(store),error=>error instanceof StorageError&&error.code==='corrupt');
    assert.throws(()=>addNote(record('id'),store));assert.equal(store.getItem(STORAGE_KEY),raw);
  }
});
test('ID duplikat pada data tersimpan ditolak', () => {
  const store=memory();store.setItem(STORAGE_KEY,JSON.stringify({version:1,notes:[record('id'),record('id')]}));
  assert.throws(()=>loadNotes(store));
});
test('Akses penyimpanan ditolak', () => {
  const store={getItem(){throw new Error('blocked');}};
  assert.throws(()=>loadNotes(store),error=>error.code==='unavailable');
});
test('Kuota penuh tidak mengubah data lama', () => {
  const store=memory();addNote(record('first'),store);const before=store.getItem(STORAGE_KEY);
  store.setItem=()=>{throw new Error('QuotaExceededError');};
  assert.throws(()=>addNote(record('second'),store),error=>error.code==='write');
  assert.equal(store.getItem(STORAGE_KEY),before);assert.equal(loadNotes(store).length,1);
});
test('Kunci dan plaintext tidak disimpan; cipherteks dapat dipulihkan', () => {
  const store=memory(),keys={mono:'ZEBRAS',vigenere:'LEMON',columnar:'BALLOON'};
  const payload=JSON.stringify({format:'ruangcatat-mini-note-v1',notes:'IsiUnikFiktif987 🙂\nBaris dua'});
  const cipher=encrypt(payload,keys).text;addNote({...record('id'),ciphertext:cipher},store);
  const raw=store.getItem(STORAGE_KEY);
  for(const secret of ['IsiUnikFiktif987','ZEBRAS','LEMON','BALLOON'])assert(!raw.includes(secret));
  const saved=loadNotes(store)[0];assert.equal(decrypt(saved.ciphertext,keys).text,payload);
  assert.deepEqual(Object.keys(saved).sort(),['ciphertext','clientCode','createdAt','id','sessionDate']);
});
