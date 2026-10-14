# Analisis Fitur dan Role LaundryKu Desktop

## 1. Ringkasan arsitektur

Aplikasi yang tersedia adalah desktop Python + Tkinter. `main.py` mengelola halaman login, session dalam memori, sidebar, dashboard dan placeholder halaman. `app/database/connection.py` membuka koneksi MariaDB dari `.env`; `app/database/dashboard.py` menjalankan query baca dashboard. Autentikasi menggunakan `app/services/authentication.py`, sedangkan aturan akses dipusatkan di `app/services/authorization.py`.

Workspace tidak berisi source Flutter, Kotlin, PHP, atau REST API lama. `database/schema.sql` tersedia tetapi kosong, jadi analisis skema mengacu pada struktur yang diberikan pemilik proyek. Tidak ada skema yang diimpor atau diubah.

## 2. Fitur per role

| Level | Role | Fitur yang direncanakan |
| --- | --- | --- |
| 1 | Pelanggan | Dashboard pesanan pribadi, daftar layanan, pembuatan pesanan, riwayat/timeline, status pembayaran, profil dan logout |
| 2 | Kasir/Admin | Ringkasan transaksi, pelanggan, pembuatan/pengelolaan transaksi, layanan, pembayaran dan pencarian transaksi |
| 3 | Staff Laundry | Antrean cucian, detail pesanan, pembaruan status proses, catatan dan riwayat status |
| 4 | Owner | Dashboard usaha, monitoring transaksi, statistik/pendapatan, laporan, layanan/harga dan pengelolaan akun staff |

## 3. Status implementasi

| Fitur | Status pada project |
| --- | --- |
| Login awal dengan username/password | Diimplementasikan; memakai query parameterized ke tabel `users` |
| Verifikasi password | Diimplementasikan untuk hash PHP bcrypt `$2y$`/`$2a$`/`$2b$`; tidak mengubah hash database |
| Status akun aktif | Diimplementasikan; akun selain `aktif` ditolak setelah password valid |
| Session aplikasi | Diimplementasikan di memori proses; session berakhir saat logout/aplikasi ditutup |
| Logout | Diimplementasikan; menghapus session dan kembali ke login |
| Sidebar per role dan pemeriksaan menu | Diimplementasikan; `show_page` memeriksa izin meskipun menu tidak terlihat |
| Dashboard statistik global | Sudah tersedia untuk level 2 dan 4; query read-only |
| Dashboard pribadi pelanggan | Belum diimplementasikan; landing page tidak menampilkan transaksi global |
| Dashboard antrean staff | Belum diimplementasikan; landing page placeholder |
| CRUD transaksi/pelanggan/layanan/pembayaran/pengguna | Belum diimplementasikan; halaman berupa placeholder |
| Laporan dan riwayat status | Belum diimplementasikan |
| Integrasi API Flutter/PHP lama | Perlu verifikasi jika source lama disediakan; tidak ditemukan di workspace |

## 4. Hak akses menu desktop

Dashboard tidak ditampilkan sebagai item sidebar; brand LaundryKu dapat membawa pengguna kembali ke dashboard. Hak akses saat ini:

| Role | Menu yang dapat dibuka |
| --- | --- |
| Pelanggan | Dashboard, Transaksi, Layanan, Pembayaran |
| Kasir/Admin | Dashboard, Transaksi, Pelanggan, Layanan, Pembayaran, Laporan |
| Staff Laundry | Dashboard, Transaksi |
| Owner | Dashboard, Transaksi, Pelanggan, Layanan, Pembayaran, Laporan, Pengguna |

Halaman menu yang belum dibuat hanya menampilkan placeholder. Menu yang terlihat bukan satu-satunya pemeriksaan otorisasi: query dashboard agregat juga menolak level selain 2 dan 4 di service.

## 5. Relasi fitur dengan tabel

| Fitur | Tabel yang tersedia dalam acuan | Relasi/pemakaian |
| --- | --- | --- |
| Login dan role | `users` | Membaca `id_user`, `nama`, `no_hp`, `username`, `password`, `level`, `status_akun` |
| Katalog layanan | `layanan` | `detail_transaksi.id_layanan` mengacu ke layanan |
| Transaksi pelanggan | `transaksi`, `detail_transaksi`, `users` | `transaksi.id_pelanggan` dan `id_kasir` mengacu ke pengguna; detail mengacu ke transaksi/layanan |
| Pembayaran | `pembayaran`, `transaksi` | Pembayaran mengacu ke transaksi |
| Timeline/status | `riwayat_status`, `transaksi`, `users` | Riwayat mengacu ke transaksi dan pengguna yang mengubah status |
| Token API | `auth_tokens`, `users` | Token mengacu ke pengguna; tidak digunakan oleh session desktop |

Nama kolom dan relasi di atas berasal dari schema acuan dalam permintaan. Tipe data, enum, dan foreign key aktual perlu diverifikasi dari database/server karena file SQL lokal kosong.

## 6. Rencana tahap berikutnya

1. Uji login dengan akun uji yang sudah ada dan hash PHP bcrypt, termasuk akun nonaktif serta tiap level; jangan menambah/mengubah data produksi untuk tes.
2. Verifikasi label level dan status akun dengan sumber aplikasi lama atau dokumentasi database.
3. Implementasikan daftar layanan baca-saja dan dashboard personal pelanggan dengan filter `id_pelanggan` dari session, bukan input UI.
4. Implementasikan antrean staff dan pembaruan status dengan pemeriksaan role di service serta pencatatan `riwayat_status`.
5. Implementasikan alur kasir untuk pelanggan, transaksi, detail dan pembayaran memakai transaksi database serta query parameterized.
6. Implementasikan laporan dan pengelolaan layanan/pengguna owner setelah aturan operasional dikonfirmasi.
7. Uji alur dengan database lokal terkontrol tanpa mengubah data produksi.
