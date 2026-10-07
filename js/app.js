/*
Mengatur interaksi halaman: membaca formulir dan kunci, mengirim permintaan ke Python, menangani unggah/unduh file, serta menampilkan hasil dan frekuensi. Algoritma tidak dijalankan di file ini.
*/


import {validateFile, readPlaintext, connectDropZone} from './files.js';
import {initAnalysis, renderAnalysis, clearAnalysis, setAnalysisBusy} from './analysis.js';

const $ = id => document.getElementById(id);
const MAX_FILE_BYTES = 1024 * 1024;
let busy = false;
let cipherFile = null;

function message(text, error = false) {
  $('message').textContent = text;
  $('message').setAttribute('role', error ? 'alert' : 'status');
  $('message').className = error
    ? 'rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800'
    : 'rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800';
  $('message').hidden = false;
}
function keys() {
  const values = {};
  for (const input of document.querySelectorAll('[data-key]')) {
    if (!/^[A-Za-z]+$/.test(input.value)) throw new Error('Ketiga kunci wajib huruf A–Z/a–z tanpa spasi atau angka.');
    values[input.dataset.key] = input.value;
  }
  return values;
}
function setBusy(value) {
  busy = value; setAnalysisBusy(value);
  for (const element of $('note-form').querySelectorAll('input, textarea, button')) element.disabled = value;
  $('decrypt').disabled = value || !cipherFile;
  for (const id of ['plain-drop', 'cipher-drop']) {
    $(id).setAttribute('aria-disabled', String(value)); $(id).tabIndex = value ? -1 : 0;
  }
}
function clearOutput() {
  $('encryption-result').hidden = true; $('encryption-code').textContent = '';
  $('plaintext-preview').textContent = ''; $('raw-ciphertext-preview').textContent = ''; $('ciphertext-preview').textContent = '';
  $('result').hidden = true; $('result-code').textContent = ''; $('result-text').textContent = '';
  clearAnalysis(); $('analysis').open = false;
}
async function request(action, data) {
  let response;
  try {
    response = await fetch('/api/' + action, {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data), signal: AbortSignal.timeout(30000)});
  } catch { throw new Error('Server tidak dapat dihubungi. Periksa koneksi, atau jalankan python server.py untuk versi lokal.'); }
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Catatan belum dapat diproses. Coba kembali.');
  return result;
}
$('note-form').addEventListener('submit', async event => {
  event.preventDefault(); if (busy) return; clearOutput();
  try {
    const code = $('client-code').value.trim(), text = $('note-text').value, values = keys();
    if (!/^[A-Za-z0-9_-]{1,32}$/.test(code)) throw new Error('Kode klien samaran: 1–32 huruf/angka, tanda - atau _.');
    if (!text.trim()) throw new Error('Tuliskan catatan sesi atau muat dari file .txt terlebih dahulu.');
    setBusy(true);
    const result = await request('encrypt', {code, text, keys: values});
    if (!result.validated) throw new Error('Validasi gagal. File tidak diunduh.');
    // Snapshot input dan hasil Python ditampilkan sebagai teks, bukan HTML.
    $('encryption-code').textContent = 'Kode klien samaran: ' + code;
    $('plaintext-preview').textContent = text;
    $('raw-ciphertext-preview').textContent = result.note_raw_ciphertext;
    $('ciphertext-preview').textContent = result.note_ciphertext;
    $('encryption-result').hidden = false;
    const blob = new Blob([JSON.stringify(result.package)], {type:'application/json;charset=utf-8'});
    const url = URL.createObjectURL(blob), link = document.createElement('a');
    link.href = url; link.download = result.filename; document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    renderAnalysis(result.analysis); message('Validasi berhasil: hasil dekripsi identik. Unduhan catatan konseling tersandi telah dimulai. Simpan file untuk dibuka kembali.');
  } catch (error) { message(error.message, true); }
  finally { setBusy(false); }
});
async function selectPlaintext(files) {
  if (busy) return;
  try {
    const file = validateFile(files, '.txt', 500 * 1024);
    setBusy(true);
    const text = await readPlaintext(file);
    if ($('note-text').value && $('note-text').value !== text && !window.confirm('Ganti catatan sesi yang sedang ditulis dengan isi file ' + file.name + '?')) return;
    $('note-text').value = text; clearOutput();
    $('plain-file-name').textContent = 'Catatan sesi dimuat dari: ' + file.name;
    message('Catatan sesi dari file .txt sudah dimuat. Tinjau isinya, isi kode klien dan tiga kunci, lalu klik Enkripsi & unduh catatan.');
  } catch (error) { message(error.message, true); }
  finally { setBusy(false); }
}
function selectCiphertext(files) {
  if (busy) return;
  try {
    const file = validateFile(files, '.json', MAX_FILE_BYTES);
    cipherFile = file; clearOutput();
    $('cipher-file-name').textContent = 'File catatan: ' + file.name;
    $('decrypt').disabled = false;
    message('File catatan konseling dipilih. Masukkan tiga kunci saat enkripsi, lalu klik Buka catatan.');
  } catch (error) { message(error.message, true); }
}
connectDropZone($('plain-drop'), $('plain-file'), selectPlaintext, () => busy);
connectDropZone($('cipher-drop'), $('cipher-file'), selectCiphertext, () => busy);
// Mencegah browser membuka file ketika dijatuhkan di luar kedua area.
for (const name of ['dragover', 'drop']) {
  document.addEventListener(name, event => {
    if (event.dataTransfer?.types.includes('Files')) event.preventDefault();
  });
}
$('decrypt').addEventListener('click', async () => {
  if (busy) return; clearOutput();
  try {
    const values = keys(), file = cipherFile;
    if (!file) throw new Error('Pilih file catatan konseling tersandi (.json) terlebih dahulu.');
    if (file.size > MAX_FILE_BYTES) throw new Error('Ukuran file maksimal 1 MB.');
    setBusy(true);
    let packageData;
    try { packageData = JSON.parse(await file.text()); }
    catch { throw new Error('File JSON rusak atau tidak valid.'); }
    const result = await request('decrypt', {package: packageData, keys: values});
    $('result-code').textContent = 'Kode klien samaran: ' + result.code; $('result-text').textContent = result.text; $('result').hidden = false;
    renderAnalysis(result.analysis); message('Catatan konseling berhasil dibuka kembali.');
  } catch (error) { message(error.message, true); }
  finally { setBusy(false); }
});
$('clear').addEventListener('click', () => {
  $('note-form').reset(); toggleKeys(); clearOutput(); $('message').hidden = true; $('message').textContent = '';
  cipherFile = null;
  $('plain-file-name').textContent = 'Sudah menulis catatan di file .txt? Muat di sini, lalu tinjau atau edit isinya.';
  $('cipher-file-name').textContent = 'Belum ada file catatan yang dipilih.';
  for (const id of ['plain-drop', 'cipher-drop']) $(id).classList.remove('drag-active');
  $('decrypt').disabled = true;
});

function toggleKeys() {
  for (const input of document.querySelectorAll('[data-key]')) {
    input.type = $('show-keys').checked ? 'text' : 'password';
  }
}
$('show-keys').addEventListener('change', toggleKeys);


initAnalysis(request);
clearAnalysis();
