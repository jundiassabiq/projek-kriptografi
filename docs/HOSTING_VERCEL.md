# Hosting ke Vercel dan membagikan web
Konfigurasi hosting sudah tersedia. Dua file api/encrypt.py dan api/decrypt.py
memakai handler aplikasi Python yang sama. Algoritma tetap Python buatan sendiri.

## Deploy tanpa GitHub
1. Buka folder proyek di VS Code dan terminal PowerShell.
2. Pastikan Node.js/npm tersedia, lalu jalankan:

    cd C:\Users\Junid\Documents\project-kriptografi
    npx vercel login
    npx vercel --prod

3. Jawab y jika npx meminta mengunduh CLI.
4. Login melalui tautan terminal menggunakan akun Vercel.
5. Set up and deploy: Y; pilih akun pribadi.
6. Link to existing project: N untuk proyek baru.
7. Nama: ruangcatat-file; folder: ./.
8. Framework jika ditanya: Other. Gunakan settings dari vercel.json.
9. Tunggu Ready lalu buka URL Production dan uji enkripsi/dekripsi file.
10. Bagikan URL Production itu ke teman. Mereka tidak perlu Python atau Node.

Konfigurasi: build node scripts/build-site.js, output public, install command
kosong. CSS sudah lokal/terkompilasi. Python Functions disiapkan otomatis dari
folder api. Tidak perlu variabel lingkungan atau database cloud.
Bila CLI meminta mengubah pengaturan, biarkan konfigurasi tersebut.

## Jika teman diminta login Vercel
Bagikan URL/domain Production, bukan link dashboard Vercel atau preview.
Bila domain Production masih dilindungi, periksa Settings → Deployment Protection
dan sesuaikan proteksi Production agar demo dapat diakses teman tanpa login.

## Update
Setelah perubahan, jalankan npx vercel --prod lagi dari folder yang sama.
Jika mengubah tampilan Tailwind, jalankan npm run build:css lebih dahulu.
Versi lokal tetap bisa dijalankan dengan python server.py.

## Data dan batas pengujian
File catatan tetap diunduh/disimpan oleh masing-masing pengguna. Tidak ada
penyimpanan bersama/sinkronisasi. Pada versi online, teks dan kunci dikirim melalui
HTTPS ke fungsi Python Vercel untuk diproses. Gunakan data fiktif.
Arsip database dan dokumen tidak disertakan unggahan maupun output publik.

Build aset dan handler diperiksa lokal. Deployment akun Vercel belum dilakukan;
verifikasi di domain sesudah deploy untuk memastikan bundling Python berjalan.

Referensi:
https://vercel.com/docs/functions/runtimes/python/api-directory
https://vercel.com/docs/cli/deploying-from-cli
