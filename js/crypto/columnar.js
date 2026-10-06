// Pengacakan posisi karakter tanpa padding. Array.from menjaga pasangan surrogate Unicode.
function orderFor(key) {
  if (typeof key !== 'string' || !/^[A-Za-z]+$/.test(key)) {
    throw new Error('Kunci kolom harus berisi huruf A–Z/a–z tanpa spasi atau angka.');
  }
  key = key.toUpperCase();
  const order = Array.from({length: key.length}, (_, index) => index);
  // Huruf kunci sama dibedakan berdasarkan posisi asal, bukan dihapus.
  order.sort((a, b) => key.charCodeAt(a) - key.charCodeAt(b) || a - b);
  return order;
}
export function encrypt(text, key) {
  const order = orderFor(key), characters = Array.from(text);
  let output = '';
  for (const column of order) {
    for (let index = column; index < characters.length; index += key.length) output += characters[index];
  }
  return output;
}
export function decrypt(text, key) {
  const order = orderFor(key), characters = Array.from(text), width = key.length;
  const rows = Math.floor(characters.length / width), remainder = characters.length % width;
  const columns = []; let offset = 0;
  for (const column of order) {
    // Sisa karakter baris terakhir berada di kolom paling kiri.
    const length = rows + (column < remainder ? 1 : 0);
    columns[column] = characters.slice(offset, offset + length);
    offset += length;
  }
  let output = '';
  for (let index = 0; index < characters.length; index++) {
    output += columns[index % width][Math.floor(index / width)];
  }
  return output;
}
