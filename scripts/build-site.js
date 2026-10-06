import {cpSync, mkdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';

// Hanya aset aplikasi yang menjadi hasil hosting. Arsip/database tidak disalin.
const root = new URL('../', import.meta.url);
const output = new URL('dist/', root);
mkdirSync(fileURLToPath(output), {recursive: true});
for (const name of ['index.html', 'js', 'css/style.css']) {
  cpSync(fileURLToPath(new URL(name, root)), fileURLToPath(new URL(name, output)), {recursive: true});
}
console.log('Aset web siap di dist/');
