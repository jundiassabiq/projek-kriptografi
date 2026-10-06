# RuangCatat File
Web lokal satu halaman untuk catatan konseling fiktif. Semua algoritma ditulis
sendiri dalam Python. HTML, JavaScript vanilla, dan CSS Tailwind lokal hanya
menangani tampilan. Tidak memakai database, localStorage, framework backend,
atau library kriptografi.

## Menjalankan
Pasang Python 3.10 atau lebih baru, lalu buka terminal di folder proyek:

    cd C:\Users\Junid\Documents\project-kriptografi
    python server.py

Buka http://127.0.0.1:8000 di browser. Biarkan terminal menyala selama memakai
aplikasi. Ctrl+C menghentikan server. Jika Windows memakai Python Launcher,
gunakan py server.py. Jika port 8000 dipakai, hentikan server sebelumnya dahulu.

Tidak perlu pip install, npm, Live Server, atau internet untuk memakai aplikasi.
Jangan membuka index.html lewat file://. Versi lokal memakai server Python; deployment opsional Vercel juga disiapkan.

## Mengenkripsi
1. Isi kode samaran (1–32 huruf/angka, - atau _) dan isi catatan fiktif.
2. Isi kunci Monoalfabetik, Vigenère, dan Kolom dengan kata A–Z/a–z.
   Contoh untuk demonstrasi: ZEBRAS, LEMON, BALLOON.
3. Klik Enkripsi & unduh.
4. Server mendekripsi balik dan membandingkan isi secara persis.
5. Jika berhasil, browser mulai mengunduh file KODE.json.
   Browser mungkin meminta lokasi atau izin unduhan; periksa folder Downloads.

Kunci tidak ada pada file. Catat/ingat ketiganya sendiri. Kunci tetap di formulir
supaya dapat digunakan untuk mencoba dekripsi. Bersihkan menghapus semua input.

## Membuka file
1. Klik Bersihkan bila perlu, pilih file .json tersandi (maksimal 1 MB).
2. Masukkan ketiga kunci yang sama pada formulir.
3. Klik Dekripsi. Kode klien dan teks muncul di Hasil dekripsi.
Kode klien/isi formulir tidak diperlukan untuk proses dekripsi.
File asli tidak diubah. Salah kunci/data rusak tidak membuka hasil.
File browser versi Mini sebelumnya tidak kompatibel dan tidak dimigrasikan.

Analisis frekuensi dapat dilipat. Tabel memuat 26 huruf, jumlah, persentase,
diurutkan paling sering kemudian alfabet. Persentase hanya memakai total A–Z;
angka dan karakter lain diabaikan. Ini analisis pola, bukan pemecahan tiga lapis.

## Alur yang dapat dijelaskan
1. Bungkus kode dan catatan sebagai JSON dengan penanda format.
2. Encode JSON menjadi UTF-8, lalu hex huruf besar. Contoh: A → 41.
   Encoding adalah representasi data, bukan algoritma enkripsi keempat.
3. Enkripsi: Monoalfabetik → Vigenère → Transposisi Kolom.
4. Dekripsi: balik Kolom → balik Vigenère → balik Monoalfabetik.
5. Decode hex → UTF-8 → JSON, lalu periksa format catatan.

Konversi UTF-8 membuat teks Arab, Mandarin, Yunani, Rusia, aksara lain dan emoji
dapat dipulihkan identik. Algoritma klasik tetap bekerja pada representasi Latin/
angka, bukan memakai tabel alfabet setiap bahasa. Monoalfabetik/Vigenère hanya
mengubah A–Z/a–z. Kolom mengubah posisi seluruh karakter tanpa padding.

Monoalfabetik memakai huruf unik kata kunci diikuti alfabet yang belum muncul.
Vigenère memakai (P+K) mod 26 dan (C-K) mod 26. Non-Latin tidak menghabiskan kunci
pada modul dasar. Kolom diurutkan menurut huruf kunci dan posisi asal untuk huruf
berulang. Dekripsi menghitung panjang kolom termasuk baris tidak penuh.
Komentar tiap modul menjelaskan logikanya.

## Struktur modular
    server.py             HTTP lokal dan penyajian file web
    notes.py              Validasi, format file, encoding dan round-trip
    crypto/
      keys.py             Validasi kunci
      monoalphabetic.py   Substitusi
      vigenere.py         Pergeseran berulang
      columnar.py         Pengacakan kolom
      pipeline.py         Rangkaian/invers tiga algoritma
      frequency.py        Analisis frekuensi
    index.html            Satu halaman
    js/app.js             Formulir, fetch, unggah/unduh, hasil
    css/input.css         Sumber Tailwind
    css/style.css         CSS lokal siap pakai
    tests/                unittest Python
    docs/                 Laporan, hasil uji dan screenshot
    data-lama/            Arsip SQLite lama; tidak digunakan

Setiap modul algoritma menyediakan encrypt(text, key) dan decrypt(text, key).
Import algoritma hanya ke modul buatan proyek. Pustaka standar json, re,
http.server dan pathlib dipakai untuk aplikasi, bukan implementasi kriptografi.

## Format dan endpoint
File unduhan hanya:
    {"format":"ruangcatat-file-v2","ciphertext":"..."}

POST /api/encrypt:
    {"code":"K-001","text":"Catatan fiktif","keys":{"mono":"ZEBRAS","vigenere":"LEMON","columnar":"BALLOON"}}
Mengembalikan package, filename, validated dan frequency.

POST /api/decrypt:
    {"package":{...},"keys":{...}}
Mengembalikan code, text dan frequency.

Keduanya application/json. Gagal: status 400 + error; permintaan terlalu besar:
413. Batas request HTTP 2 MB, file cipherteks 1 MB. Isi panjang dapat ditolak
karena hex membuat representasi sekitar dua kali panjang byte UTF-8.
Server hanya menyajikan HTML/CSS/JS aplikasi; source Python dan arsip tidak
tersedia melalui HTTP. Tidak menulis plaintext atau kunci ke disk/log.
Browser dan server tetap memegang data dalam memori saat pemrosesan.

## Empat nilai tambahan
| Fitur | Implementasi |
|---|---|
| GUI | Web responsif satu halaman |
| Kriptanalisis sederhana | Analisis frekuensi huruf cipherteks |
| Multibahasa | Encoding UTF-8 dan pemulihan Unicode identik |
| Baca/tulis cipherteks ke file | Pilih file JSON dan unduh hasil |

Tetap pastikan interpretasi nilai tambahan serta keunikan kombinasi pada dosen.
Kombinasi klasik untuk pembelajaran, bukan catatan konseling asli. Validasi
identik dan penanda format tidak memberikan autentikasi atau keamanan modern.
Unduhan, arsip dan kunci dikelola pengguna. Tidak ada pemulihan kunci/sinkronisasi.
Data browser lama tidak dihapus otomatis; data-lama tetap dipertahankan.

## Tes dan perubahan CSS
    python -m unittest discover -s tests -v

Hasil: 26 tes Python dan pengujian browser lulus. Rincian di
docs/HASIL_PENGUJIAN.md. npm hanya untuk developer yang ingin mengubah Tailwind:

    npm ci
    npm run build:css

CSS hasil build sudah disertakan. Tidak ada paket Python tambahan.
Draf laporan ada di docs/LAPORAN_DRAF.md; isi identitas dan kontribusi anggota
sebenarnya. Kumpulkan source dan laporan; abaikan node_modules, cache Python,
dan database arsip. Referensi Tailwind: https://tailwindcss.com/docs/installation/tailwind-cli

## Hosting dan berbagi
Panduan: docs/HOSTING_VERCEL.md. Vercel memakai api/encrypt.py dan api/decrypt.py.
npm run build menyiapkan aset public/; algoritma tetap Python. Deploy lewat npx vercel --prod.

