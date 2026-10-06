// Pemetaan satu alfabet ke alfabet hasil kata kunci. Tidak memakai library.
function alphabetFor(key) {
  if (typeof key !== 'string' || !/^[A-Za-z]+$/.test(key)) {
    throw new Error('Kunci substitusi harus berisi huruf A–Z/a–z tanpa spasi atau angka.');
  }
  let alphabet = '';
  for (const letter of key.toUpperCase() + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ') {
    if (!alphabet.includes(letter)) alphabet += letter;
  }
  return alphabet;
}
function transform(text, from, to) {
  let output = '';
  for (const character of text) {
    const index = from.indexOf(character.toUpperCase());
    // Pemeriksaan ASCII mencegah huruf Unicode tersubstitusi secara tidak sengaja.
    if (character >= 'A' && character <= 'Z') output += to[index];
    else if (character >= 'a' && character <= 'z') output += to[index].toLowerCase();
    else output += character;
  }
  return output;
}
export function encrypt(text, key) {
  return transform(text, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', alphabetFor(key));
}
export function decrypt(text, key) {
  return transform(text, alphabetFor(key), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ');
}
