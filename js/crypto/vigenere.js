// Enkripsi: (P + K) mod 26. Dekripsi: (C - K + 26) mod 26.
function transform(text, key, direction) {
  if (typeof key !== 'string' || !/^[A-Za-z]+$/.test(key)) {
    throw new Error('Kunci Vigenère harus berisi huruf A–Z/a–z tanpa spasi atau angka.');
  }
  key = key.toUpperCase();
  let output = '', position = 0;
  for (const character of text) {
    const upper = character >= 'A' && character <= 'Z';
    const lower = character >= 'a' && character <= 'z';
    if (!upper && !lower) {
      output += character; // Non-Latin/tanda baca tidak menghabiskan posisi kunci.
      continue;
    }
    const base = upper ? 65 : 97;
    const shift = key.charCodeAt(position % key.length) - 65;
    output += String.fromCharCode(base + (character.charCodeAt(0) - base + direction * shift + 26) % 26);
    position++;
  }
  return output;
}
export function encrypt(text, key) { return transform(text, key, 1); }
export function decrypt(text, key) { return transform(text, key, -1); }
