# Hosting RuangCatat Mini ke Vercel

Konfigurasi sudah tersedia di vercel.json. Hosting hanya mengambil aset dari
dist/ yang dibentuk scripts/build-site.js. CSS lokal telah disertakan.
Tidak diperlukan backend, variabel lingkungan, atau database cloud.

## Cara lewat terminal VS Code
Pastikan Node.js/npm tersedia dan buat/login akun di https://vercel.com.
Buka terminal PowerShell di VS Code, jalankan:

    cd C:\Users\Junid\Documents\project-kriptografi
    npx vercel login
    npx vercel --prod

Jika npx meminta izin mengunduh CLI Vercel, jawab y. Ikuti tautan login pada
terminal, masuk dengan akun sendiri, lalu kembali ke terminal.

Saat deployment:
- Set up and deploy: Y.
- Scope/team: pilih akun pribadi yang sesuai.
- Link to existing project: N untuk proyek baru.
- Project name: ruangcatat-mini (atau nama tersedia lainnya).
- Directory containing code: ./.
- Bila ditanya mengubah settings, tidak perlu; gunakan vercel.json.
- Bila framework diminta, pilih Other.

Tunggu status berhasil lalu buka URL Production yang ditampilkan terminal.
Uji simpan, refresh, Buka, salah kunci dan Hapus pada domain tersebut.
Perubahan berikutnya: jalankan npx vercel --prod lagi dari folder yang sama.
Sesudah mengubah kelas/tampilan Tailwind, jalankan npm run build:css dahulu.

## Alternatif GitHub
Unggah source proyek ke repository GitHub (sertakan CSS hasil build).
Jangan unggah node_modules, data-lama, dist, atau .vercel.
Di Vercel pilih Add New → Project, import repository, pilih Framework Other.
Root Directory adalah folder berisi index.html dan vercel.json.
Konfigurasi build/output sudah ditentukan vercel.json; lalu Deploy.

## Hal penting
Catatan localhost tidak otomatis muncul pada domain Vercel karena localStorage
dipisahkan berdasarkan origin. Hosting membuat web dapat diakses online, tetapi
catatan tetap pada browser pengguna dan tidak disinkronkan antar perangkat.
Gunakan domain Production yang sama untuk membuka catatan berikutnya.
Gunakan data fiktif, karena algoritma klasik ini merupakan prototipe akademik.

Referensi:
https://vercel.com/docs/cli/deploying-from-cli
https://vercel.com/docs/project-configuration/vercel-json
