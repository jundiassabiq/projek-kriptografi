# Hasil pengujian RuangCatat File
Tanggal: 6 Oktober 2026. Windows, Python pustaka standar, browser Edge headless.

## Pengujian Python
Perintah: python -m unittest discover -s tests -v
**26 tes lulus, 0 gagal**:
- 11 tes algoritma/frekuensi: vektor Monoalfabetik, Vigenère dan Kolom;
  posisi kunci non-Latin; kunci berulang/tidak valid; format/Unicode;
  urutan invers; 200 variasi panjang; frekuensi diketahui dan tanpa huruf.
- 9 tes catatan/file: round-trip UTF-8/Unicode/CRLF; file tanpa plaintext atau
  kunci; salah tiap kunci; data rusak tanpa mutasi; format invalid; penanda wajib;
  validasi input; ukuran besar; batas tepat file 1 MB.
- 6 tes HTTP: round-trip API, status kesalahan, JSON rusak, content type,
  batas request, allowlist file statis (source/arsip tidak dapat diakses).

## Pengujian browser
Aplikasi dijalankan pada http://127.0.0.1:8000.
- Isi Unicode → enkripsi → unduh K-111.json → unggah → dekripsi identik.
- Aksara Arab, Mandarin, Yunani, Rusia, emoji dan baris baru dipulihkan.
- File hanya mempunyai format dan ciphertext; tidak memuat teks asli,
  kode klien, atau tiga kunci contoh.
- Salah kunci: pesan, hasil tetap tersembunyi. Berkas asli tidak berubah.
- File JSON rusak, versi lama, dan melebihi 1 MB: ditolak dengan pesan.
- Analisis memuat 26 baris, jumlah dan persentase.
- Bersihkan mengosongkan input, kunci, file pilihan, hasil dan tabel frekuensi.
- Tombol/input dinonaktifkan selama permintaan berlangsung.
- Kegagalan jaringan disimulasikan: pesan jalankan server, input dipertahankan,
  tombol kembali tersedia.
- Teks seperti <img ...> dirender sebagai teks, bukan elemen aktif.
- Desktop 1440×1100 dan mobile 390×844 diperiksa melalui screenshot.
  Tidak ditemukan overflow halaman horizontal di mobile.
- Tidak ada pageerror JavaScript atau permintaan resource eksternal.
- Tidak ada operasi localStorage di kode aplikasi; penyimpanan lewat unduhan.

Screenshot aktual: file-enkripsi.png, file-dekripsi.png, file-mobile.png.

## Build dan kompatibilitas
CSS lokal dibangun dengan npm run build:css. Hasil disertakan agar tidak
memerlukan npm/internet saat penggunaan.
Algoritma/storage JavaScript, tes versi lama, dan konfigurasi Vercel dihapus
sesudah pengganti lulus. Arsip data-lama tidak diubah dan tidak dibaca aplikasi.
File versi lama tidak dimigrasikan; storage browser lama tidak dihapus.
Server hanya menyediakan localhost. Server/kunci/catatan tidak diarsipkan di disk.

Validasi identik memeriksa pemulihan; pemeriksaan format bukan autentikasi
kriptografis. Analisis frekuensi bukan pemecahan seluruh rangkaian.
Isi hasil pengujian kelompok sendiri sebelum laporan final dikumpulkan.
