# RuangCatat Mini

Prototipe tugas kriptografi klasik untuk catatan konseling **fiktif**. Satu halaman
HTML, JavaScript vanilla modular, dan Tailwind yang sudah dikompilasi lokal.
Tidak memerlukan backend, database aktif, atau koneksi internet saat digunakan.

## Menjalankan
1. Buka folder proyek ini di VS Code.
2. Pastikan ekstensi **Live Server** tersedia.
3. Klik kanan **index.html**, pilih **Open with Live Server**.
4. Gunakan alamat localhost/127.0.0.1 yang dibuka ekstensi.

Jangan membuka HTML melalui file:// karena proyek menggunakan modul JavaScript.
Tidak perlu menjalankan npm, Python, atau proses build bersamaan dengan aplikasi.

## Menggunakan
1. Isi kode samaran (1–32 huruf/angka, - atau _), tanggal, dan isi catatan.
2. Masukkan tiga kunci kata, hanya A–Z/a–z. Contoh demonstrasi: ZEBRAS, LEMON,
   BALLOON. Kunci diproses tanpa membedakan besar/kecil.
3. Klik **Enkripsi & simpan**. Program mengenkripsi, mendekripsi kembali, dan
   membandingkan teks secara persis sebelum menyimpan.
4. **Detail proses algoritma** dapat dilipat untuk melihat hasil tiga tahap.
5. Klik **Buka**, masukkan kembali ketiga kunci, lalu dekripsi.
6. **Tutup** membersihkan hasil dekripsi dari tampilan; **Hapus** meminta konfirmasi.

Simpan ketiga kunci sendiri; program tidak menyimpannya dan tidak menyediakan
pemulihan kunci. Setelah berhasil menyimpan/membuka atau menutup dialog, input
kunci dibersihkan. Penyimpanan gagal mempertahankan formulir agar dapat dicoba ulang.

## Algoritma
Urutan: Substitusi Monoalfabetik → Vigenère → Transposisi Kolom.
Dekripsi membalik urutan tersebut. Seluruh algoritma ditulis sendiri memakai
sintaks JavaScript. Import hanya menghubungkan modul lokal buatan proyek.
Tidak menggunakan library kriptografi, Web Crypto, atau API.

Substitusi membentuk alfabet dari kata kunci unik ditambah alfabet tersisa.
Vigenère menggeser A–Z/a–z; karakter lain tidak menghabiskan posisi kunci.
Transposisi mengurutkan kolom menurut huruf kunci, lalu indeks asal untuk huruf
berulang, tanpa padding. Array.from menjaga karakter Unicode seperti emoji.
Huruf besar/kecil, spasi, tanda baca, angka, Unicode dan baris baru dipulihkan identik.

## Penyimpanan dan batasan
localStorage memakai nama ruangcatat-mini:v1 dengan format:
version, notes; setiap record berisi id, clientCode, sessionDate, createdAt,
ciphertext. Isi catatan dibungkus JSON dengan penanda ruangcatat-mini-note-v1
lalu dienkripsi. Kunci dan salinan plainteks tidak disimpan.

Kode klien, tanggal, ID dan waktu penambahan tetap terbuka. Plainteks muncul di
memori/tampilan saat dibuka, termasuk tahap akhir Detail proses. Pemeriksaan
format bukan autentikasi kriptografis; kombinasi klasik ini tidak layak untuk
catatan konseling asli. Validasi identik membuktikan pemulihan teks saja.

Data hanya ada pada browser dan origin yang sama. Mengubah browser, host
(localhost vs 127.0.0.1), port atau profil dapat menghasilkan daftar berbeda.
Menghapus data browser menghapus catatan. Mode privat dapat membuang data saat
ditutup. Data rusak tidak ditimpa; tombol simpan dinonaktifkan dengan pesan.
Daftar diurutkan menurut waktu penambahan terbaru.

Database lama di data-lama/ hanya arsip, tanpa migrasi. Aplikasi tidak membacanya.

## Struktur
- index.html: antarmuka satu halaman.
- css/input.css: sumber Tailwind dan komponen sederhana.
- css/style.css: CSS lokal siap pakai.
- js/app.js: alur formulir, enkripsi, validasi dan pembukaan.
- js/ui.js: interaksi dan rendering aman menggunakan textContent.
- js/storage.js: validasi format dan akses localStorage.
- js/crypto/: monoalphabetic.js, vigenere.js, columnar.js, pipeline.js.
- tests/: pengujian algoritma dan penyimpanan.
- docs/: draf laporan, hasil uji dan screenshot aplikasi.
- data-lama/: arsip SQLite versi sebelumnya, diabaikan Git.

## Pengembangan opsional
Node.js 20+ dan npm hanya diperlukan untuk pengujian atau membangun ulang CSS.

    npm ci
    npm test
    npm run build:css

CSS hasil build disertakan, sehingga pemakaian biasa tetap offline.
Tailwind hanya dependensi pengembangan; @parcel/watcher dioverride ke 2.6.0
untuk memakai dependensi yang sudah diperbaiki. Lockfile disertakan.
Referensi CLI: https://tailwindcss.com/docs/installation/tailwind-cli

## Penugasan
Tiga algoritma mencakup substitusi monoalfabetik, substitusi polialfabetik,
dan transposisi. Input teks, tiga kunci, enkripsi, dekripsi, dan validasi identik
tersedia. Komentar algoritma dan laporan ada dalam proyek.
Pastikan kombinasi belum dipakai kelompok lain di kelas. Isi nama/NIM,
kontribusi aktual, dan identitas mata kuliah pada docs/LAPORAN_DRAF.md.
Kumpulkan source code dan laporan; node_modules dan arsip database tidak perlu
disertakan. Sesuaikan laporan dengan pengujian kelompok sendiri.

## Hosting Vercel
Konfigurasi tersedia di vercel.json; panduan lengkap: docs/HOSTING_VERCEL.md.
Build hosting memakai npm run build untuk menyalin aset web ke dist/, tanpa
mengubah cara penggunaan Live Server. CSS tetap dibangun terpisah melalui
npm run build:css bila tampilan diubah. Arsip database tidak ikut dipublikasikan.
