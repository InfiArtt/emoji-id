# Emoji ID - Pembaca Emoji Bahasa Indonesia untuk NVDA

Emoji ID adalah add-on NVDA yang membacakan semua simbol emoji dalam bahasa Indonesia, terlepas dari synthesizer atau suara TTS yang sedang aktif (misalnya Eloquence suara bahasa Inggris, OneCore, atau Vocalizer).

Add-on ini dirancang khusus bagi pengguna tunanetra agar selalu dapat memahami emoji dengan jelas dalam bahasa Indonesia saat membaca teks, berselancar di web, membaca pesan obrolan, maupun menavigasi karakter demi karakter.

## Fitur Utama

- **Pembacaan Emoji Bahasa Indonesia**: Mengubah ribuan emoji menjadi nama alami dalam bahasa Indonesia berdasarkan data resmi Unicode CLDR.
- **Dukungan Penuh Semua Jenis Emoji**: Mendukung emoji dasar (wajah, gestur, hewan, benda), ZWJ sequence (keluarga, profesi), bendera negara (seperti bendera Indonesia), keycap angka, dan varian warna kulit (Fitzpatrick scale).
- **Mengatasi Perangkap Satu Karakter (Single-Character Trap)**: Emoji tetap dibacakan dalam bahasa Indonesia baik saat membaca kalimat, membaca baris (Say All), navigasi panah karakter per karakter, review cursor, maupun saat mengetik (character echo).
- **Penggabungan Emoji Berulang**: Opsi untuk menggabungkan emoji yang muncul berulang kali secara berurutan, misalnya tiga emoji wajah tersenyum dibacakan sebagai "3 kali wajah gembira".
- **Kata Awalan yang Dapat Diatur**: Opsi untuk menambahkan kata awalan seperti "emoji" sebelum nama emoji, baik pada setiap emoji atau hanya sekali di awal rangkaian emoji berurutan.
- **Opsi Detail Warna Kulit**: Pengguna dapat memilih untuk menyertakan nama warna kulit (misalnya "warna kulit sedang") atau menyederhanakannya menjadi nama dasar emoji saja.
- **Pintasan Cepat**: Tersedia perintah unassigned di NVDA untuk mengaktifkan atau menonaktifkan pembacaan emoji secara instan tanpa perlu membuka dialog pengaturan.
- **Performa Tinggi**: Menggunakan pencarian berbasis regex terkompilasi dengan pengurutan longest-match first, sehingga tidak menyebabkan jeda pada pembacaan teks panjang (diuji hingga 50.000 karakter).

## Pengaturan NVDA

Buka menu NVDA -> Pengaturan -> Pengaturan (NVDA+Control+G), lalu pilih kategori **Emoji ID**:

1. **Aktifkan pembacaan emoji dalam bahasa Indonesia**: Centang untuk mengaktifkan add-on. Jika tidak dicentang, NVDA kembali ke perilaku bawaan.
2. **Tambahkan kata awalan sebelum nama emoji**: Centang untuk menyertakan kata awalan sebelum nama emoji (bawaan: aktif).
3. **Kata awalan**: Teks yang diucapkan sebelum nama emoji (bawaan: "emoji").
4. **Kata awalan hanya sekali untuk emoji berturut-turut**: Jika dicentang, kata awalan hanya diucapkan di depan emoji pertama pada kelompok emoji berturut-turut.
5. **Gabungkan emoji berulang yang sama**: Jika dicentang, emoji identik yang berurutan digabungkan menjadi "N kali [nama emoji]".
6. **Sertakan detail warna kulit**: Jika dicentang, variasi warna kulit diucapkan lengkap. Jika tidak, hanya nama dasar emoji yang dibacakan.
7. **Bersihkan tanda hubung dan tanda kurung pada nama emoji**: Jika dicentang (bawaan: aktif), tanda hubung pada kata ulang (seperti kupu-kupu menjadi kupu kupu) dan tanda kurung dihilangkan saat dikirim ke TTS sehingga synthesizer seperti Eloquence tidak mengeja kata "dash" atau "left paren". Tanda baca pada teks dokumen di luar emoji tidak akan terpengaruh sama sekali.
8. **Ikuti tingkat simbol NVDA**: Jika dicentang, emoji hanya dibaca jika tingkat pengucapan simbol NVDA mencakupnya. Jika tidak dicentang (bawaan), emoji selalu dibacakan.
9. **Tampilkan pengingat donasi berkala**: Jika dicentang (bawaan: aktif), NVDA secara berkala pada jeda waktu acak yang bersahabat akan menampilkan pengingat santai untuk mendukung pengembangan add-on ini.
10. **Dukung Pengembang (Donasi GoPay)**: Membuka dialog informasi donasi GoPay yang dilengkapi tombol salin nomor rekening/HP secara cepat.

Pengaturan ini tersimpan otomatis per profil konfigurasi NVDA.

## Menetapkan Tombol Pintasan

Add-on ini menyediakan perintah tanpa pintasan bawaan (unassigned) untuk beralih aktif/nonaktif:

1. Buka menu NVDA -> Preferensi -> Gestur Masukan.
2. Cari kategori **Emoji ID**.
3. Pilih **Aktifkan atau nonaktifkan pembacaan emoji dalam bahasa Indonesia**.
4. Tekan tombol **Tambah** dan tekan tombol pintasan yang diinginkan (misalnya NVDA+Shift+E).
5. Tekan Enter untuk menyimpan.

Saat ditekan, NVDA akan mengumumkan status baru: "Emoji ID aktif" atau "Emoji ID nonaktif".

## Dukungan dan Donasi

Pengembangan add-on Emoji ID dilakukan secara sukarela agar teman-teman tunanetra pengguna NVDA dapat membaca simbol emoji dalam bahasa Indonesia secara nyaman dan konsisten di segala synthesizer.

Kalau kamu merasa add-on ini bermanfaat dan ingin mendukung pengembangannya agar terus terawat, yuk berikan apresiasi melalui GoPay:
- **Metode**: GoPay
- **Nomor HP / Rekening**: 085128011831
- **Atas Nama**: Rexya Muhamad Rizki

Dukungan sekecil apa pun sangat berarti. Terima kasih banyak!

## Persyaratan Sistem

- NVDA 2026.1 atau yang lebih baru.
- Arsitektur: 64-bit (Python 3.13 bawaan NVDA).
- Bekerja dengan semua synthesizer (Eloquence, Windows OneCore, eSpeak NG, Vocalizer Expressive, SAPI5).

## Lisensi dan Hak Cipta

- Pengembang: Rexya Muhamad <rexya2017@gmail.com>
- Lisensi Add-on: GNU General Public License versi 2 atau yang lebih baru (GPL-2.0-or-later).
- Hak Cipta Kode: (c) 2026 Rexya Muhamad <rexya2017@gmail.com>.

### Pemberitahuan Lisensi Unicode CLDR (Unicode License v3)

Data nama emoji bahasa Indonesia bersumber dari proyek Unicode Common Locale Data Repository (CLDR).

UNICODE LICENSE V3
COPYRIGHT AND PERMISSION NOTICE

Copyright (c) 1991-2026 Unicode, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of data files and any associated documentation (the "Data Files") or software and any associated documentation (the "Software") to deal in the Data Files or Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, and/or sell copies of the Data Files or Software, and to permit persons to whom the Data Files or Software are furnished to do so, provided that either (a) this copyright and permission notice appear with all copies of the Data Files or Software, or (b) this copyright and permission notice appear in associated Documentation.

THE DATA FILES AND SOFTWARE ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT OF THIRD PARTY RIGHTS.

IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS INCLUDED IN THIS NOTICE BE LIABLE FOR ANY CLAIM, OR ANY SPECIAL INDIRECT OR CONSEQUENTIAL DAMAGES, OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THE DATA FILES OR SOFTWARE.
