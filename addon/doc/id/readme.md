# Emoji ID - Pembaca Emoji Bahasa Indonesia untuk NVDA

Emoji ID membacakan emoji dalam bahasa Indonesia, apa pun bahasa suara TTS yang sedang dipakai. Misalnya, dengan suara Eloquence bahasa Inggris, 😀 tetap dibacakan "wajah gembira", bukan "grinning face".

Emoji dibacakan dalam bahasa Indonesia saat membaca teks, Say All, navigasi per karakter, kursor tinjauan, dan saat mengetik.

## Bedanya dengan fitur bawaan NVDA

NVDA sendiri sudah punya nama emoji bahasa Indonesia dari data Unicode CLDR. Tapi NVDA memakai nama itu hanya jika bahasa yang dipakai untuk simbol adalah bahasa Indonesia. Kalau suaramu berbahasa Inggris, NVDA membacakan nama emoji dalam bahasa Inggris. Emoji ID menutup celah ini.

Kalau kamu sudah memakai suara bahasa Indonesia dan opsi "Sertakan data Unicode Consortium" di NVDA aktif, kamu mungkin tidak memerlukan add-on ini.

## Tanda baca dan simbol

NVDA 2026.3 tidak punya kamus tanda baca bahasa Indonesia, jadi tanda baca biasanya dibacakan dalam bahasa Inggris, bahkan dengan suara bahasa Indonesia. Emoji ID menambahkan kamus berisi 806 tanda baca dan simbol dalam bahasa Indonesia, termasuk simbol matematika, panah, mata uang, dan pola braille.

- Nama mengikuti EYD Edisi V dan KBBI bila ada, misalnya titik, koma, titik koma, titik dua, tanda pisah, elipsis, tanda pagar, tilde, dan garis bawah.
- Simbol yang tidak punya nama di EYD atau KBBI memakai nama yang lazim, misalnya garis miring terbalik untuk \ dan et untuk @.
- Tanda baca tetap berbahasa Indonesia walaupun suara TTS berbahasa Inggris.
- Tingkat simbol NVDA tetap berlaku. Pada tingkat "sebagian", misalnya, koma tetap tidak dibacakan.

Fitur ini aktif secara bawaan. Fitur ini bisa dimatikan di pengaturan Emoji ID, di daftar kamus simbol pada pengaturan Ucapan NVDA, atau dengan perintahnya di Gestur Masukan. Ketiganya selalu menunjukkan keadaan yang sama.

## Yang didukung

- Emoji dasar seperti wajah, gestur, hewan, dan benda.
- Rangkaian ZWJ, misalnya keluarga dan profesi.
- Bendera negara, misalnya bendera Indonesia.
- Keycap angka, misalnya 1️⃣.
- Warna kulit.

Nama emoji diambil dari Unicode CLDR 48.2, sama dengan versi yang dipakai NVDA 2026.3. Beberapa nama diganti dengan kata yang lebih umum dipakai, misalnya 💩 dibacakan "kotoran".

## Pengaturan

Buka menu NVDA, Preferensi, Pengaturan, lalu pilih kategori Emoji ID. Pilihan yang tersedia:

1. Aktifkan pembacaan emoji dalam bahasa Indonesia. Jika tidak dicentang, NVDA kembali ke perilaku bawaan.
2. Tambahkan kata awalan sebelum nama emoji. Bawaannya aktif.
3. Kata awalan. Kata yang diucapkan sebelum nama emoji. Bawaannya "emoji".
4. Kata awalan hanya sekali untuk emoji berturut-turut. Jika dicentang, kata awalan hanya diucapkan sebelum emoji pertama dalam satu deret emoji.
5. Gabungkan emoji yang sama dan berulang. Jika dicentang, tiga 😀 berturut-turut dibacakan "3 wajah gembira", atau "3 emoji wajah gembira" jika kata awalan aktif.
6. Jumlah emoji berturut-turut yang dibacakan. Bawaannya 0, artinya semua dibacakan. Dengan angka 3, misalnya, deretan delapan emoji dibacakan tiga nama, lalu "dan 5 emoji lainnya". Emoji yang sama dan berulang yang sudah digabung dihitung sebagai satu kelompok.
7. Sertakan detail warna kulit. Jika tidak dicentang, hanya nama dasar emoji yang dibacakan.
8. Bersihkan tanda hubung dan tanda kurung pada nama emoji. Bawaannya aktif. "kupu-kupu" dikirim ke synthesizer sebagai "kupu kupu", dan tanda kurung dihapus, supaya synthesizer seperti Eloquence tidak mengucapkan "dash" atau "left paren". Tanda baca di luar nama emoji tidak diubah.
9. Bacakan tanda baca dan simbol dalam bahasa Indonesia. Bawaannya aktif. Lihat bagian Tanda baca dan simbol.
10. Periksa pembaruan saat NVDA dijalankan. Bawaannya aktif. Lihat bagian Pembaruan.
11. Tombol Periksa Pembaruan Sekarang.
12. Tampilkan pengingat donasi berkala. Bawaannya nonaktif. Jika dicentang, ajakan donasi muncul pertama kali 20 sampai 45 menit setelah NVDA dijalankan, lalu setiap 90 sampai 180 menit.
13. Tombol Dukung Pengembang. Membuka informasi donasi GoPay dengan tombol untuk menyalin nomor.

Pengaturan disimpan per profil konfigurasi NVDA.

## Perintah untuk menyalakan dan mematikan

Emoji ID punya perintah untuk menyalakan atau mematikan pembacaan emoji, tanpa tombol pintasan bawaan. Untuk memasang tombol pintasan:

1. Buka menu NVDA, Preferensi, Gestur Masukan.
2. Buka kategori Emoji ID.
3. Pilih "Aktifkan atau nonaktifkan pembacaan emoji dalam bahasa Indonesia".
4. Tekan tombol Tambah, lalu tekan tombol pintasan yang diinginkan, misalnya NVDA+Shift+E.
5. Tekan Enter untuk menyimpan.

Saat perintah dijalankan, NVDA mengucapkan "Emoji ID aktif" atau "Emoji ID nonaktif".

Dengan cara yang sama, Anda bisa memasang tombol pintasan untuk perintah "Aktifkan atau nonaktifkan pembacaan tanda baca dan simbol dalam bahasa Indonesia". NVDA lalu mengucapkan "Tanda baca bahasa Indonesia aktif" atau "Tanda baca bahasa Indonesia nonaktif".

## Sisipkan emoji

Dialog Sisipkan Emoji dibuat mirip panel emoji Windows 11 (Windows+titik), tetapi semua namanya berbahasa Indonesia dan semua bagiannya bisa dicari. Dialog ini hanya bisa dibuka lewat perintah "Buka dialog sisipkan emoji" di Gestur Masukan, kategori Emoji ID. Perintah ini tidak punya tombol pintas bawaan, jadi tetapkan sendiri tombolnya dengan cara di bagian Perintah untuk menyalakan dan mematikan.

Agar tidak terbuka tanpa sengaja, dialog hanya terbuka di tempat mengetik: kolom teks, dokumen yang bisa diedit seperti Word atau badan email, kolom isian di halaman web, dan terminal. Di tempat lain, misalnya tombol, daftar, desktop, teks hanya baca, atau halaman web dalam mode jelajah di luar kolom isian, NVDA mengucapkan "Bukan tempat mengetik. Tekan dua kali untuk tetap membuka". Kalau sebuah aplikasi punya kolom teks yang tidak dikenali NVDA, tekan tombol pintasnya dua kali cepat untuk tetap membuka dialog.

Dialog ini punya tiga tab: Emoji, Simbol, dan Kaomoji. Isi setiap tab, sesuai urutan tombol Tab:

1. Cari. Hasil langsung diperbarui saat mengetik. Pencarian memakai nama Indonesia dan kata kunci, misalnya "ngakak", "terima kasih", atau "bendera jepang". Pencarian mencakup semua kategori di tab itu.
2. Kategori, mengikuti kategori Windows, ditambah Terakhir dipakai dan Favorit.
3. Subkategori, khusus tab Emoji, misalnya Wajah tersenyum atau Bendera negara. Pilihan ini menyaring daftar Hasil.
4. Hasil. NVDA menyebut posisi item, misalnya "5 dari 140". Mengetik huruf melompat ke nama yang berawalan huruf itu. Di tab Emoji, saat Subkategori diatur ke Semua subkategori dan kolom Cari kosong, panah kanan melompat ke awal subkategori berikutnya dan panah kiri ke awal subkategori sebelumnya. Nama subkategorinya lalu diucapkan.

Di bawah tab ada kolom Rangkaian, yaitu emoji yang dikumpulkan untuk disisipkan sekaligus, lalu tombol-tombol. Setiap tombol menyebut tombol pintasnya, dan tombol pintas itu bisa ditekan dari bagian mana pun di dialog:

- Sisipkan (Enter): sisipkan emoji yang dipilih, atau seluruh rangkaian kalau rangkaian tidak kosong.
- Personalisasi (Shift+Enter): hanya aktif untuk emoji yang dapat dipersonalisasi.
- Tambah ke Rangkaian (Ctrl+Enter).
- Hapus Terakhir (Ctrl+Shift+Backspace): hapus emoji terakhir dari rangkaian.
- Kosongkan Rangkaian (Ctrl+Shift+Delete).
- Salin (Ctrl+Shift+C): salin tanpa menyisipkan.
- Tambah ke Favorit atau Hapus dari Favorit (Ctrl+D).
- Detail (Alt+Enter).
- Pintasan (F1): daftar semua tombol pintas.
- Tutup (Escape).

Tombol pintas lain tanpa tombol: Control+Tab dan Control+Shift+Tab untuk tab berikutnya atau sebelumnya, Control+1, Control+2, dan Control+3 untuk langsung ke tab Emoji, Simbol, atau Kaomoji, Control+F untuk ke kolom Cari, dan Control+R untuk membacakan isi rangkaian.

Enter selalu langsung menyisipkan emoji yang dipilih. Emoji yang punya pilihan warna kulit, jenis kelamin, atau arah hadap diberi keterangan di daftar, misalnya "jempol ke atas, dapat dipersonalisasi, tekan Shift+Enter". Shift+Enter membuka dialog Personalisasi:

- Yang muncul hanya aturan yang berlaku untuk emoji itu: jenis kelamin, arah hadap, warna kulit, dan warna kulit orang kedua untuk emoji dua orang seperti jabat tangan.
- Kolom Hasil menyebut nama emoji jadinya.
- Tekan Enter untuk menyisipkannya, Control+Enter untuk menambahkannya ke rangkaian, atau Control+Shift+C untuk menyalinnya. Tekan Escape untuk batal.

Setelah Sisipkan ditekan, dialog langsung tertutup dan emoji ditempel ke tempat Anda mengetik. Isi papan klip sebelumnya dikembalikan. Kalau sebuah aplikasi tidak menerima tempelan, pakai tombol Salin, lalu tempel sendiri dengan Control+V. Pilihan personalisasi terakhir diingat untuk pemakaian berikutnya.

## Pembaruan

Emoji ID belum ada di Add-on Store NVDA, jadi add-on ini memeriksa sendiri versi terbaru di GitHub saat NVDA dijalankan. Kalau ada versi baru, muncul pesan dengan tiga pilihan: Unduh dan Pasang, Buka Halaman Rilis, atau Nanti. Jika Anda memilih Unduh dan Pasang, NVDA akan meminta konfirmasi pemasangan seperti biasa.

Pemeriksaan juga bisa dilakukan kapan saja dengan tombol Periksa Pembaruan Sekarang di pengaturan Emoji ID. Pemeriksaan otomatis bisa dimatikan dengan menghapus centang "Periksa pembaruan saat NVDA dijalankan".

## Donasi

Emoji ID dikembangkan secara sukarela. Saat instalasi, Emoji ID menampilkan sambutan beserta ajakan donasi. Jika kamu memilih Donasi, nomor GoPay langsung disalin ke papan klip. Kalau kamu ingin mendukung pengembangannya, donasi bisa dikirim lewat GoPay:

- Nomor HP: 085128011831
- Atas nama: Rexya Muhamad Rizki

Terima kasih.

## Persyaratan

- NVDA 2026.1 atau yang lebih baru. Terakhir diuji dengan NVDA 2026.3.
- Bisa dipakai dengan semua synthesizer, termasuk Eloquence, Windows OneCore, eSpeak NG, Vocalizer Expressive, dan SAPI5.

## Lisensi dan hak cipta

- Pengembang: Rexya Muhamad <rexya2017@gmail.com>
- Lisensi add-on: GNU General Public License versi 2 atau yang lebih baru (GPL-2.0-or-later).
- Hak cipta kode: (c) 2026 Rexya Muhamad.
- Kode sumber: https://github.com/InfiArtt/emoji-id

### Pemberitahuan Lisensi Unicode CLDR (Unicode License v3)

Data nama emoji bahasa Indonesia bersumber dari proyek Unicode Common Locale Data Repository (CLDR).

UNICODE LICENSE V3
COPYRIGHT AND PERMISSION NOTICE

Copyright (c) 1991-2026 Unicode, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of data files and any associated documentation (the "Data Files") or software and any associated documentation (the "Software") to deal in the Data Files or Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, and/or sell copies of the Data Files or Software, and to permit persons to whom the Data Files or Software are furnished to do so, provided that either (a) this copyright and permission notice appear with all copies of the Data Files or Software, or (b) this copyright and permission notice appear in associated Documentation.

THE DATA FILES AND SOFTWARE ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT OF THIRD PARTY RIGHTS.

IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS INCLUDED IN THIS NOTICE BE LIABLE FOR ANY CLAIM, OR ANY SPECIAL INDIRECT OR CONSEQUENTIAL DAMAGES, OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THE DATA FILES OR SOFTWARE.
