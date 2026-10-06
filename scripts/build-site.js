/*
Menyalin HTML, CSS lokal, dan JavaScript aplikasi ke folder public untuk deployment Vercel. Source Python tetap dipakai sebagai fungsi backend.
*/


import { cpSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";

// Hasil publik hanya HTML, CSS, JS. Source Python dipakai Vercel Functions.
const root = new URL("../", import.meta.url);
const output = new URL("public/", root);
mkdirSync(fileURLToPath(output), { recursive: true });
for (const name of ["index.html", "css/style.css", "js/app.js"]) {
  cpSync(
    fileURLToPath(new URL(name, root)),
    fileURLToPath(new URL(name, output)),
    { recursive: true },
  );
}
console.log("Aset publik siap.");
