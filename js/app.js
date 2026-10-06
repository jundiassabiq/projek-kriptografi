/*
Mengatur interaksi halaman: membaca formulir dan kunci, mengirim permintaan ke Python, menangani unggah/unduh file, serta menampilkan hasil dan frekuensi. Algoritma tidak dijalankan di file ini.
*/


import {validateFile, readPlaintext, connectDropZone} from './files.js';

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
  busy = value;
  for (const element of $('note-form').querySelectorAll('input, textarea, button')) element.disabled = value;
  $('decrypt').disabled = value || !cipherFile;
  for (const id of ['plain-drop', 'cipher-drop']) {
    $(id).setAttribute('aria-disabled', String(value)); $(id).tabIndex = value ? -1 : 0;
  }
}
function clearOutput() {
  $('encryption-result').hidden = true; $('encryption-code').textContent = '';
  $('plaintext-preview').textContent = ''; $('ciphertext-preview').textContent = '';
  $('result').hidden = true; $('result-code').textContent = ''; $('result-text').textContent = '';
  $('frequency-body').replaceChildren(); $('frequency-table').hidden = true;
  $('frequency-info').textContent = 'Hasil muncul setelah enkripsi atau dekripsi.';
  $('analysis').open = false;
}
function frequency(data) {
  $('frequency-body').replaceChildren();
  for (const item of data.rows) {
    const row = document.createElement('tr'); row.className = 'border-b border-zinc-100';
    for (const value of [item.letter, item.count, item.percent.toFixed(2) + '%']) {
      const cell = document.createElement('td'); cell.className = 'py-2'; cell.textContent = value; row.append(cell);
    }
    $('frequency-body').append(row);
  }
  $('frequency-info').textContent = 'Total huruf A–Z: ' + data.total;
  $('frequency-table').hidden = false;
}
async function request(action, data) {
  let response;
  try {
    response = await fetch('/api/' + action, {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data), signal: AbortSignal.timeout(30000)});
  } catch { throw new Error('Server tidak dapat dihubungi. Periksa koneksi, atau jalankan python server.py untuk versi lokal.'); }
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Proses gagal.');
  return result;
}
$('note-form').addEventListener('submit', async event => {
  event.preventDefault(); if (busy) return; clearOutput();
  try {
    const code = $('client-code').value.trim(), text = $('note-text').value, values = keys();
    if (!/^[A-Za-z0-9_-]{1,32}$/.test(code)) throw new Error('Kode klien: 1–32 huruf/angka, tanda - atau _.');
    if (!text.trim()) throw new Error('Isi catatan tidak boleh kosong.');
    setBusy(true);
    const result = await request('encrypt', {code, text, keys: values});
    if (!result.validated) throw new Error('Validasi gagal. File tidak diunduh.');
    // Snapshot input dan hasil Python ditampilkan sebagai teks, bukan HTML.
    $('encryption-code').textContent = 'Kode klien: ' + code;
    $('plaintext-preview').textContent = text;
    $('ciphertext-preview').textContent = result.note_ciphertext;
    $('encryption-result').hidden = false;
    const blob = new Blob([JSON.stringify(result.package)], {type:'application/json;charset=utf-8'});
    const url = URL.createObjectURL(blob), link = document.createElement('a');
    link.href = url; link.download = result.filename; document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    frequency(result.frequency); message('Validasi berhasil: hasil dekripsi identik. Unduhan file telah dimulai.');
  } catch (error) { message(error.message, true); }
  finally { setBusy(false); }
});
async function selectPlaintext(files) {
  if (busy) return;
  try {
    const file = validateFile(files, '.txt', 500 * 1024);
    setBusy(true);
    const text = await readPlaintext(file);
    if ($('note-text').value && $('note-text').value !== text && !window.confirm('Ganti isi catatan yang sekarang dengan isi file ' + file.name + '?')) return;
    $('note-text').value = text; clearOutput();
    $('plain-file-name').textContent = 'Catatan diambil dari: ' + file.name;
    message('Isi file .txt dimuat. Periksa catatan, isi kode dan tiga kunci, lalu klik Enkripsi & unduh.');
  } catch (error) { message(error.message, true); }
  finally { setBusy(false); }
}
function selectCiphertext(files) {
  if (busy) return;
  try {
    const file = validateFile(files, '.json', MAX_FILE_BYTES);
    cipherFile = file; clearOutput();
    $('cipher-file-name').textContent = 'File dipilih: ' + file.name;
    $('decrypt').disabled = false;
    message('File tersandi dipilih. Masukkan tiga kunci, lalu klik Dekripsi.');
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
    if (!file) throw new Error('Pilih file tersandi terlebih dahulu.');
    if (file.size > MAX_FILE_BYTES) throw new Error('Ukuran file maksimal 1 MB.');
    setBusy(true);
    let packageData;
    try { packageData = JSON.parse(await file.text()); }
    catch { throw new Error('File JSON rusak atau tidak valid.'); }
    const result = await request('decrypt', {package: packageData, keys: values});
    $('result-code').textContent = result.code; $('result-text').textContent = result.text; $('result').hidden = false;
    frequency(result.frequency); message('Catatan berhasil didekripsi.');
  } catch (error) { message(error.message, true); }
  finally { setBusy(false); }
});
$('clear').addEventListener('click', () => {
  $('note-form').reset(); toggleKeys(); clearOutput(); $('message').hidden = true; $('message').textContent = '';
  cipherFile = null;
  $('plain-file-name').textContent = 'Opsional: isi file akan masuk ke kolom catatan dan bisa diedit.';
  $('cipher-file-name').textContent = 'Belum ada file tersandi dipilih.';
  for (const id of ['plain-drop', 'cipher-drop']) $(id).classList.remove('drag-active');
  $('decrypt').disabled = true;
});

function toggleKeys() {
  for (const input of document.querySelectorAll('[data-key]')) {
    input.type = $('show-keys').checked ? 'text' : 'password';
  }
}
$('show-keys').addEventListener('change', toggleKeys);

