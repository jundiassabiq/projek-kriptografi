/*
Mengatur pilihan dan drag-and-drop file, memeriksa ekstensi/ukuran,
serta membaca file plaintext UTF-8. Tidak menjalankan algoritma kriptografi.
*/


export function validateFile(files, extension, maxBytes) {
  if (files.length !== 1) throw new Error('Pilih satu file saja.');
  const file = files[0];
  if (!file.name.toLowerCase().endsWith(extension)) throw new Error('Gunakan file ' + extension + ' untuk area ini.');
  if (file.size > maxBytes) throw new Error(extension === '.txt' ? 'Ukuran file .txt maksimal 500 KB.' : 'Ukuran file maksimal 1 MB.');
  if (!file.size) throw new Error('File tidak boleh kosong.');
  return file;
}

export async function readPlaintext(file) {
  let text;
  try { text = new TextDecoder('utf-8', {fatal: true}).decode(await file.arrayBuffer()); }
  catch { throw new Error('File .txt tidak dapat dibaca. Simpan sebagai teks UTF-8 lalu coba lagi.'); }
  if (!text.trim()) throw new Error('File .txt tidak boleh kosong atau hanya berisi spasi.');
  if (/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/.test(text)) throw new Error('File berisi data biner. Gunakan file teks biasa (.txt).');
  return text;
}

export function connectDropZone(zone, input, onFiles, isBusy) {
  let depth = 0;
  const reset = () => { depth = 0; zone.classList.remove('drag-active'); };
  zone.addEventListener('click', () => { if (!isBusy()) input.click(); });
  zone.addEventListener('keydown', event => {
    if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); if (!isBusy()) input.click(); }
  });
  zone.addEventListener('dragenter', event => {
    event.preventDefault(); if (!isBusy()) { depth++; zone.classList.add('drag-active'); }
  });
  zone.addEventListener('dragover', event => {
    event.preventDefault(); if (event.dataTransfer) event.dataTransfer.dropEffect = isBusy() ? 'none' : 'copy';
  });
  zone.addEventListener('dragleave', event => { event.preventDefault(); depth--; if (depth <= 0) reset(); });
  zone.addEventListener('drop', event => {
    event.preventDefault(); event.stopPropagation(); reset();
    if (!isBusy() && event.dataTransfer) onFiles(event.dataTransfer.files);
  });
  input.addEventListener('change', () => {
    if (!isBusy() && input.files.length) onFiles(input.files);
    input.value = ''; // File yang sama dapat dipilih lagi.
  });
}
