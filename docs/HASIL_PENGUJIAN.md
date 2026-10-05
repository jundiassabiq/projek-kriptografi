# Hasil Pengujian RuangCatat

Tanggal: 5 Oktober 2026 (Asia/Jakarta). Lingkungan: Windows, Python bawaan Codex, Tk 8.6.

Perintah: `python -B -m unittest discover -s tests -v` memakai executable runtime bawaan Codex.

Hasil: **20 pengujian lulus, 0 gagal, 0 dilewati**.

- 7 pengujian algoritma: vektor diketahui, validasi kunci, urutan invers, edge cases dan 180 panjang teks acak deterministik.
- 9 pengujian service/database: CRUD catatan, persistensi, kode unik/pencarian, salah kunci, privasi, impor/ekspor dan data tidak valid.
- 4 pengujian GUI Tk nyata: demo, teks kosong, editor simpan/buka/edit/status, dan editor tetap terkunci saat kunci salah. Dialog informasi dimock supaya tes tidak menunggu interaksi.

Tes memakai database sementara. Tidak ada catatan asli yang dimasukkan. Pengujian GUI dilakukan secara otomatis dengan jendela disembunyikan; screenshot dan pemeriksaan visual manual belum termasuk hasil ini.

Temuan lingkungan: `py -3` melaporkan tidak ada instalasi Python. Peluncur Windows menyediakan fallback runtime bawaan Codex yang mempunyai Tkinter dan SQLite.

Pemeriksaan peluncur `Jalankan.bat --check` berhasil. Python yang ditemukan lewat perintah `python` adalah Python 3.13 di AppData; 4 tes GUI tambahan juga lulus dengan interpreter tersebut. Jadi aplikasi dapat memakai Python sistem pada perangkat ini, sementara fallback Codex tetap tersedia.

## Pembaruan versi web

- Seluruh **27 tes Python lulus**, termasuk 7 tes baru API web: static/bootstrap, kontrol akses, create/open/status/dashboard, edit dengan verifikasi kunci lama dan penggantian kunci, impor/ekspor, demo format/Unicode, serta request salah.
- Uji browser Edge headless lulus: tambah klien, simpan/buka/edit sesi, kunci salah tetap terkunci, enkripsi ulang dengan kunci baru, status, ekspor/impor, pemulihan file Unicode dan CRLF, validasi gagal untuk cipherteks rusak, bersihkan demo, dan viewport mobile 390px tanpa overflow halaman.
- Tidak ada JavaScript page errors selama uji browser. Screenshot aktual disimpan dalam `screenshots/` dan diperiksa secara visual.
- Database browser-test terpisah dari database aplikasi; seluruh isi merupakan data fiktif.
