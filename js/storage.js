// Modul penyimpanan hanya menerima metadata + cipherteks, tidak menerima kunci/plainteks.
export const STORAGE_KEY = 'ruangcatat-mini:v1';
const RECORD_FIELDS = ['id', 'clientCode', 'sessionDate', 'createdAt', 'ciphertext'];

export class StorageError extends Error {
  constructor(message, code) { super(message); this.name = 'StorageError'; this.code = code; }
}
export function validateDate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const parsed = new Date(value + 'T00:00:00Z');
  return !Number.isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value;
}
function validateRecord(record) {
  return record && typeof record === 'object' && !Array.isArray(record) &&
    Object.keys(record).length === RECORD_FIELDS.length && RECORD_FIELDS.every(key => Object.hasOwn(record, key)) &&
    typeof record.id === 'string' && /^[A-Za-z0-9_-]+$/.test(record.id) &&
    typeof record.clientCode === 'string' && /^[A-Za-z0-9_-]{1,32}$/.test(record.clientCode) &&
    validateDate(record.sessionDate) && Number.isSafeInteger(record.createdAt) && record.createdAt >= 0 &&
    typeof record.ciphertext === 'string' && record.ciphertext.length > 0;
}
function resolveStorage(storage) {
  try { return storage ?? globalThis.localStorage; }
  catch { throw new StorageError('Penyimpanan browser tidak tersedia. Periksa izin browser.', 'unavailable'); }
}
function read(storage) {
  const target = resolveStorage(storage);
  let raw;
  try { raw = target.getItem(STORAGE_KEY); }
  catch { throw new StorageError('Penyimpanan browser tidak dapat dibaca.', 'unavailable'); }
  if (raw === null) return [];
  try {
    const data = JSON.parse(raw);
    if (!data || data.version !== 1 || Object.keys(data).length !== 2 || !Array.isArray(data.notes) ||
        !data.notes.every(validateRecord) || new Set(data.notes.map(note => note.id)).size !== data.notes.length) throw new Error();
    return data.notes;
  } catch {
    // Jangan menghapus/menimpa data rusak dengan daftar kosong.
    throw new StorageError('Data browser rusak atau formatnya tidak didukung. Data tidak diubah.', 'corrupt');
  }
}
function write(notes, storage) {
  const target = resolveStorage(storage);
  try { target.setItem(STORAGE_KEY, JSON.stringify({version: 1, notes})); }
  catch { throw new StorageError('Catatan tidak tersimpan. Penyimpanan penuh atau browser menolak akses.', 'write'); }
}
export function loadNotes(storage) {
  return read(storage).slice().reverse().sort((a, b) => b.createdAt - a.createdAt);
}
export function addNote(record, storage) {
  if (!validateRecord(record)) throw new Error('Metadata catatan tidak valid.');
  const notes = read(storage);
  if (notes.some(note => note.id === record.id)) throw new Error('ID catatan sudah digunakan.');
  write([...notes, record], storage);
}
export function removeNote(id, storage) {
  const notes = read(storage);
  if (!notes.some(note => note.id === id)) throw new Error('Catatan tidak ditemukan.');
  write(notes.filter(note => note.id !== id), storage);
}
