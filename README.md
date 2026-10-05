# RuangCatat — Web Lokal

Aplikasi catatan konseling fiktif untuk tugas Kriptografi IF21A05. Antarmuka **HTML/CSS/JavaScript**, backend **Python**, database **SQLite**. Seluruh algoritma ditulis sendiri; tidak ada paket kriptografi siap pakai, framework web, npm, atau pip yang diperlukan untuk menjalankan aplikasi.

## Menjalankan versi web

Klik dua kali **Jalankan-Web.bat** (atau **Jalankan.bat**). Server dimulai dan browser terbuka di **http://127.0.0.1:8765**. Biarkan terminal peluncur tetap terbuka selama penggunaan. Tekan **Ctrl+C** di terminal untuk berhenti.

Alternatif dari folder proyek:

```console
python run.py
```

Butuh Python 3.10+ dan browser modern. Tkinter hanya diperlukan jika memakai versi desktop. Peluncur Windows memeriksa Python sistem dan menyediakan fallback runtime bawaan Codex pada perangkat ini.

Jika port digunakan aplikasi lain:

```console
python run_web.py --port 8767
```

Opsi `--no-browser` tidak membuka browser otomatis. Opsi `--db lokasi.sqlite3` menggunakan database lain. Tanpa opsi, kedua versi memakai `data/ruangcatat.sqlite3`; data sebelumnya tetap terbaca. **Jangan membuka index.html langsung** karena aplikasi memerlukan server API. Server hanya mendengarkan `127.0.0.1`, tidak dipublikasikan ke internet, dan tidak memiliki login/multi-user.

## Alur penggunaan

1. Pilih **Klien & catatan**, tambahkan kode samaran seperti `K-001`, kemudian pilih klien.
2. Klik **+ Catatan sesi**. Isi tanggal, topik, isi catatan, tindak lanjut, dan jadwal berikutnya (opsional).
3. Isi tiga kata kunci huruf Latin, misalnya `ZEBRAS`, `LEMON`, `BALLOON`, lalu **Simpan tersandi**. Aplikasi memverifikasi dekripsi identik sebelum menyimpan.
4. Klik **Buka** pada riwayat, masukkan kunci, lalu **Buka dengan kunci**. Kunci salah membuat catatan tetap terkunci.
5. Sesudah membuka, edit isi dan simpan. Mengubah tiga input kunci mengenkripsi ulang dengan kunci baru; server tetap memverifikasi kunci lama sebelum memperbarui.
6. Klik **Selesai** atau **Batalkan** untuk mengubah status tanpa membuka isi. Dashboard menampilkan semua tindak lanjut belum selesai.
7. Klik **Ekspor** untuk mengunduh satu paket JSON tersandi. **Impor catatan** memverifikasi paket dan kunci sebelum menyimpan sebagai sesi baru; impor berulang membuat salinan sesi.
8. Input catatan atau demo bisa dimuat dari `.txt` UTF-8, maksimal 1 MiB. Muatan API dibatasi 2 MiB; masukan yang terlalu besar ditolak tanpa disimpan.
9. **Demo kriptografi** menampilkan tiga tahap. Pilih **Enkripsi**, lalu **Dekripsi & validasi**. Cipherteks bisa dimuat/disimpan sebagai `.txt`. Untuk cipherteks dari luar, isi plainteks pembanding jika ingin memvalidasi kesamaan.

Kunci dan teks terbuka berada dalam memori browser/server selama proses, tidak disimpan ke localStorage, database, atau paket ekspor. Tutup dialog untuk membersihkan formulir. Tombol **Bersihkan** membersihkan demo. Kode klien, tanggal, jadwal, dan status adalah metadata terbuka. Tidak ada pemulihan kunci yang hilang.

## Algoritma

**Substitusi Monoalfabetik → Vigenère → Transposisi Kolom**. Dekripsi berjalan dengan urutan terbalik.

- Substitusi: huruf berulang kata kunci dihapus, sisa alfabet ditambahkan; dekripsi memakai pemetaan invers.
- Vigenère: tambah/kurangi pergeseran modulo 26; hanya A-Z/a-z memakai posisi kunci.
- Kolom: urutan alfabet kunci dengan indeks asal sebagai pembeda huruf berulang. Panjang kolom dihitung dari panjang teks, tanpa padding.
- Kunci `[A-Za-z]+`, tanpa spasi/angka. Huruf besar/kecil, Unicode, tanda baca, dan baris baru dipertahankan. Frontend mempertahankan isi asli file CRLF di memori sampai pengguna mengeditnya; editor browser memakai LF setelah edit.
- Pelestarian Unicode bukan enkripsi substitusi alfabet non-Latin: karakter tersebut hanya ikut transposisi.

## Struktur modular

```text
run.py / run_web.py           entrypoint web
ruangcatat/web/server.py      HTTP lokal, validasi request, API
ruangcatat/web/static/        HTML/CSS dan JavaScript ES modules
  api.js                     akses API dan token sesi
  ui.js                      komponen tabel, file, formulir kunci
  notes.js                   editor, buka/edit, impor/ekspor
  demo.js                    demonstrasi enkripsi/dekripsi
  app.js                     navigasi, dashboard, daftar klien
ruangcatat/crypto/            3 algoritma dan pipeline
ruangcatat/services.py        aturan catatan, validasi, paket impor/ekspor
ruangcatat/storage.py         SQLite dan transaksi
ruangcatat/app.py, ui/        versi desktop alternatif
run_desktop.py               entrypoint desktop
tests/                      pengujian Python
docs/                       laporan, hasil uji, screenshot web
```

Antarmuka algoritma: `encrypt(text, key)` dan `decrypt(text, key)`. Pipeline menerima `Keys(mono,vigenere,columnar)` dan menghasilkan `Result(text,stages)`. Service digunakan bersama oleh web dan desktop; Repository tidak menerima kunci.

API lokal:

| Endpoint | Fungsi |
|---|---|
| GET `/api/bootstrap` | Token sesi server untuk frontend |
| GET `/api/dashboard` | Statistik dan tindak lanjut |
| GET `/api/clients?search=...` | Pencarian klien |
| GET `/api/sessions?client_id=...` | Metadata riwayat, tanpa plaintext |
| POST `/api/clients` | Tambah klien |
| POST `/api/sessions/save` | Validasi dan simpan tersandi |
| POST `/api/sessions/open` | Dekripsi dengan kunci |
| POST `/api/sessions/status` | Ubah tindak lanjut |
| POST `/api/sessions/export` | Paket JSON tersandi |
| POST `/api/sessions/import` | Verifikasi dan impor paket |
| POST `/api/demo` | Hasil algoritma dan tiga tahap |

Selain bootstrap, API memerlukan `X-RuangCatat-Token`; POST berformat JSON. Host/origin dibatasi server lokal, respons tidak dicache, dan request tidak dicatat ke log. Ini tidak mengubah batas keamanan algoritma klasik.

## Pengujian

```console
python -m unittest discover -s tests -v
```

**27 tes lulus**: algoritma, layanan/database, GUI desktop, dan API web. Tes GUI desktop dilewati jika Tk/display tidak tersedia. Tes memakai database sementara.

Alur web juga sudah diuji dengan Edge otomatis: tambah/buka/edit catatan, kunci salah, penggantian kunci, status, ekspor/impor, demo Unicode/CRLF, bersihkan formulir, dan viewport mobile. Screenshot aktual ada di `docs/screenshots/`. Browser automation hanya alat verifikasi pengembangan, bukan dependensi aplikasi.

## Kesesuaian penugasan

| Ketentuan | Implementasi |
|---|---|
| Minimal 3 algoritma substitusi + transposisi | Monoalfabetik, Vigenère, Kolom berlapis |
| Input plainteks dan kunci | Formulir web dan input file teks |
| Enkripsi dan dekripsi | Modul mandiri serta pipeline |
| Dekripsi identik | Validasi sebelum simpan dan demo |
| Komentar logika algoritma | Pemetaan, modulo, urutan/panjang kolom |
| Tanpa paket kriptografi siap pakai | Algoritma buatan sendiri |
| Antarmuka grafis | Web responsif; desktop tetap tersedia |
| Baca/tulis cipherteks | Ekspor/impor JSON dan `.txt` demo |
| Source dan laporan | Proyek ini serta `docs/LAPORAN_DRAF.md` |

Gunakan data fiktif. Kriptografi klasik tidak cocok untuk catatan konseling asli; validasi JSON bukan autentikasi kriptografis. Konfirmasi kombinasi belum dipakai kelompok lain. Laporan masih memerlukan identitas anggota (maksimal 5) dan pembagian kontribusi yang sebenarnya. Kriptanalisis dan enkripsi substitusi alfabet non-Latin tidak diimplementasikan.

Versi desktop tetap bisa dijalankan dengan `python run_desktop.py` atau `Jalankan-Desktop.bat`.
