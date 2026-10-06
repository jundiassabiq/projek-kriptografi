import {encrypt, decrypt} from './crypto/pipeline.js';
import {loadNotes, addNote, removeNote, validateDate, StorageError} from './storage.js';
import {$, message, readKeys, resetKeys, setupKeyToggle, renderNotes, showProcess, clearResult} from './ui.js';

const NOTE_FORMAT = 'ruangcatat-mini-note-v1';
let openingId = null;
function today() {
  const current = new Date(); current.setMinutes(current.getMinutes() - current.getTimezoneOffset());
  return current.toISOString().slice(0, 10);
}
function handleError(error) {
  message(error.message, true);
  if (error instanceof StorageError && ['corrupt', 'unavailable'].includes(error.code)) {
    $('save-note').disabled = true;
  }
}
function refresh() {
  try {
    renderNotes(loadNotes(), {open: openNote, remove: deleteNote}); $('save-note').disabled = false;
  } catch (error) {
    $('empty-list').textContent = 'Daftar tidak bisa dibaca. Data yang tersimpan tidak diubah.';
    handleError(error);
  }
}
function findNote(id) {
  const note = loadNotes().find(record => record.id === id);
  if (!note) throw new Error('Catatan tidak ditemukan. Muat ulang daftar.');
  return note;
}
function openNote(id) {
  try {
    const note = findNote(id); clearResult();
    $('open-form').reset(); resetKeys('open-keys', 'show-open-keys');
    $('open-error').hidden = true; $('open-error').textContent = '';
    openingId = id; $('open-meta').textContent = note.clientCode + ' · ' + note.sessionDate;
    $('open-dialog').showModal();
  } catch (error) { handleError(error); }
}
function deleteNote(id) {
  try {
    const note = findNote(id);
    if (!window.confirm(`Hapus catatan ${note.clientCode} tanggal ${note.sessionDate}?`)) return;
    removeNote(id); clearResult(); refresh(); message('Catatan dihapus.');
  } catch (error) { handleError(error); }
}
$('note-form').addEventListener('submit', event => {
  event.preventDefault(); $('save-note').disabled = true;
  try {
    const clientCode = $('client-code').value.trim(), sessionDate = $('session-date').value;
    const notes = $('note-text').value;
    if (!/^[A-Za-z0-9_-]{1,32}$/.test(clientCode)) throw new Error('Kode klien: 1–32 huruf/angka, tanda - atau _.');
    if (!validateDate(sessionDate)) throw new Error('Tanggal sesi tidak valid.');
    if (!notes.trim()) throw new Error('Isi catatan tidak boleh kosong.');
    const keys = readKeys('create-keys');
    // Penanda format turut dienkripsi; yang disimpan bukan JSON catatan terbuka.
    const payload = JSON.stringify({format: NOTE_FORMAT, notes});
    const result = encrypt(payload, keys), recovered = decrypt(result.text, keys).text;
    if (recovered !== payload || JSON.parse(recovered).notes !== notes) {
      throw new Error('Validasi dekripsi gagal. Catatan tidak disimpan.');
    }
    const current = Date.now();
    const id = current.toString(36) + '_' + Math.random().toString(36).slice(2, 12);
    addNote({id, clientCode, sessionDate, createdAt: current, ciphertext: result.text});
    // Formulir baru dibersihkan setelah localStorage benar-benar berhasil ditulis.
    $('note-form').reset(); $('session-date').value = today(); resetKeys('create-keys', 'show-create-keys');
    clearResult(); showProcess(result, 'Enkripsi: Substitusi → Vigenère → Kolom. Penanda format ikut dienkripsi.');
    refresh(); message('Validasi berhasil: hasil dekripsi identik. Catatan tersandi disimpan.');
  } catch (error) { handleError(error); }
  finally {
    // Jangan mengaktifkan kembali tombol bila data tersimpan rusak/tidak dapat dibaca.
    try { loadNotes(); $('save-note').disabled = false; } catch { $('save-note').disabled = true; }
  }
});
$('open-form').addEventListener('submit', event => {
  event.preventDefault();
  try {
    const note = findNote(openingId), keys = readKeys('open-keys');
    const result = decrypt(note.ciphertext, keys);
    let payload;
    try {
      payload = JSON.parse(result.text);
      if (!payload || payload.format !== NOTE_FORMAT || Object.keys(payload).length !== 2 ||
          typeof payload.notes !== 'string' || !payload.notes.trim()) throw new Error();
    } catch { throw new Error('Kunci salah atau data rusak.'); }
    $('result-meta').textContent = note.clientCode + ' · ' + note.sessionDate;
    $('result-text').textContent = payload.notes; $('result-panel').hidden = false;
    showProcess(result, 'Dekripsi: balik Kolom → balik Vigenère → balik Substitusi.');
    $('open-dialog').close(); message('Catatan berhasil dibuka.');
  } catch (error) {
    $('open-error').textContent = error.message; $('open-error').hidden = false;
    if (error instanceof StorageError) handleError(error);
  }
});
$('cancel-open').addEventListener('click', () => $('open-dialog').close());
$('open-dialog').addEventListener('close', () => {
  $('open-form').reset(); resetKeys('open-keys', 'show-open-keys');
  $('open-error').hidden = true; $('open-error').textContent = ''; openingId = null;
});
$('close-result').addEventListener('click', clearResult);
setupKeyToggle('create-keys', 'show-create-keys'); setupKeyToggle('open-keys', 'show-open-keys');
$('session-date').value = today(); refresh();
window.addEventListener('storage', event => {
  if (event.key === 'ruangcatat-mini:v1' || event.key === null) { clearResult(); refresh(); }
});
