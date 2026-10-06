# Hasil pengujian RuangCatat Mini
Tanggal: 6 Oktober 2026. Platform: Windows, Node.js, Edge headless.
Gunakan data fiktif. Hasil ini tidak membuktikan kekuatan keamanan kriptografi.

## Otomatis
Perintah npm test: **21 tes lulus, 0 gagal**.
- 9 tes crypto: vektor yang diketahui untuk tiap algoritma; invers urutan;
  Unicode, CRLF, campuran besar/kecil, karakter nonhuruf; kosong/satu karakter/
  teks panjang; kunci berulang; panjang kolom tidak penuh; 200 variasi teks;
  kunci kosong atau non-Latin ditolak.
- 12 tes storage: kosong, simpan/baca ulang dan urutan terbaru termasuk waktu sama,
  hapus, duplikasi/missing ID, schema dan tanggal, JSON rusak tanpa penimpaan,
  ID duplikat, akses ditolak, quota gagal tanpa mengubah data, cipherteks
  tersimpan tanpa plainteks/kunci serta dapat didekripsi.

## Browser
Aplikasi dilayani oleh server statis sementara di http://127.0.0.1:5501,
dengan file yang sama seperti Live Server. Server pengujian bukan bagian produk.
- Simpan → refresh → Buka dengan kunci benar: lulus.
- Pesan validasi hanya setelah penyimpanan berhasil: lulus.
- Salah kunci: pesan kesalahan, hasil tidak dibuka: lulus.
- Tombol tampilkan/sembunyikan dan pembersihan kunci sesudah dialog/Escape: lulus.
- Hapus dibatalkan: data tetap; konfirmasi Hapus: data hilang.
- Quota disimulasikan gagal: tidak ada record baru, formulir dipertahankan.
- JSON localStorage rusak: pesan, simpan nonaktif, data rusak tetap tidak ditimpa.
- Akses storage diblokir: pesan dan simpan nonaktif.
- Isi seperti <img ...> muncul sebagai teks, tidak membentuk elemen HTML.
- localStorage tidak berisi teks awal atau tiga kunci contoh.
- Tidak ada error JavaScript browser maupun permintaan resource eksternal/API.
  CSS berasal dari file lokal; tidak ada resource yang membutuhkan internet.
- Tampilan desktop 1440 px dan mobile 390 px diperiksa melalui screenshot.
  Tidak ada overflow halaman horizontal pada viewport mobile.

Screenshot aktual: screenshots/mini-halaman.png, mini-dekripsi.png, mini-mobile.png.
Ekstensi Live Server sendiri tidak diuji otomatis; pengujian menggunakan server
statis localhost dengan perilaku penyajian file yang sama.

## Pemeriksaan proyek
- npm run build:css berhasil; CSS hasil build disertakan.
- npm audit: 0 kerentanan setelah override @parcel/watcher ke 2.6.0.
- Database lama diarsipkan, hash SHA-256 sebelum/sesudah identik:
  1E50E7AAB6B4D96032E4D39D5D0E199ECD763B7BDE4501D224DECD6F7A66FF55
- Python, peluncur lama dan tes Python dihapus setelah pengganti lulus.

Pemeriksaan format catatan bukan autentikasi kriptografis. Catatan browser
dibatasi origin dan profil; metadata tetap terbuka. Tambahkan pengujian kelompok
dan screenshot sendiri sebelum laporan final dikumpulkan.

## Perbaikan dialog dan kesiapan hosting
Dialog kini dipusatkan eksplisit dengan inset:0 dan margin:auto setelah reset
Tailwind, dengan batas tinggi viewport dan scroll internal.
Uji browser hasil dist/ lulus di 1440×900, 1920×1080, 390×844 dan 390×460.
Build aset hosting berhasil. Deployment Vercel belum dijalankan pada akun pengguna.
