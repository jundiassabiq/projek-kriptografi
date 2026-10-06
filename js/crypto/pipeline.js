// Import hanya fungsi lokal buatan proyek, bukan library algoritma.
import * as mono from './monoalphabetic.js';
import * as vigenere from './vigenere.js';
import * as columnar from './columnar.js';

export function encrypt(text, keys) {
  const first = mono.encrypt(text, keys.mono);
  const second = vigenere.encrypt(first, keys.vigenere);
  const third = columnar.encrypt(second, keys.columnar);
  return {text: third, stages: [
    {title: '1. Substitusi Monoalfabetik', text: first},
    {title: '2. Vigenère', text: second},
    {title: '3. Transposisi Kolom', text: third}
  ]};
}
export function decrypt(text, keys) {
  const first = columnar.decrypt(text, keys.columnar);
  const second = vigenere.decrypt(first, keys.vigenere);
  const third = mono.decrypt(second, keys.mono);
  return {text: third, stages: [
    {title: '1. Balik Transposisi Kolom', text: first},
    {title: '2. Balik Vigenère', text: second},
    {title: '3. Balik Substitusi Monoalfabetik', text: third}
  ]};
}
