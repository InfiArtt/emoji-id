# Riwayat perubahan Emoji ID

Format mengikuti Keep a Changelog.

## [Belum dirilis]

### Ditambahkan

- Dialog Sisipkan Emoji, dibuat mirip panel emoji Windows 11:
  - Ada tiga jenis: Emoji, Simbol, dan Kaomoji. Kategorinya mengikuti Windows, ditambah 100 subkategori emoji resmi Unicode yang namanya ditulis dalam bahasa Indonesia.
  - Pencarian memakai nama Indonesia dan kata kunci CLDR bahasa Indonesia, misalnya "ngakak" atau "terima kasih". Berbeda dari Windows, simbol dan kaomoji juga bisa dicari.
  - Enter langsung menyisipkan emoji. Emoji yang punya pilihan warna kulit, jenis kelamin, atau arah hadap diberi keterangan "dapat dipersonalisasi, tekan Shift+Enter" di daftar. Shift+Enter membuka dialog Personalisasi yang hanya menampilkan aturan yang berlaku untuk emoji itu, termasuk warna kulit per orang untuk emoji dua orang seperti jabat tangan. Dari dialog itu emoji bisa disisipkan, ditambahkan ke rangkaian, atau disalin.
  - Daftar terakhir dipakai, favorit, rangkaian beberapa emoji yang disisipkan sekaligus, tombol Salin, dan tombol Detail.
  - Berisi 82 kaomoji bernama Indonesia dalam kategori Windows, serta simbol huruf Latin dan huruf Yunani bernama Indonesia.
  - Dialog langsung tertutup setelah menyisipkan, lalu teksnya ditempel ke tempat mengetik. Isi papan klip sebelumnya dikembalikan.
  - Dialog hanya dibuka lewat perintahnya di Gestur Masukan, yang tidak punya tombol pintas bawaan.
- Mode baca ringkas: pengaturan "Jumlah emoji berturut-turut yang dibacakan". Misalnya dengan angka 3, deretan delapan emoji dibacakan tiga nama, lalu "dan 5 emoji lainnya". Bawaannya 0, artinya semua dibacakan.

### Diubah

- Emoji yang sama dan berulang sekarang dibacakan tanpa kata "kali". Tiga 🇮🇩 berturut-turut dibacakan "3 emoji bendera Indonesia", bukan lagi "emoji 3 kali bendera Indonesia".
- Pesan pemeriksa pembaruan saat tidak ada versi baru sekarang berbunyi "Emoji ID versi ... sudah versi terbaru".

### Untuk pengembang

- Data dialog Sisipkan Emoji dibuat dengan `tools/build_picker_data.py` menjadi `data/picker.json`. Daftar kaomoji ada di `tools/kaomoji.tsv`.

## [1.3.0] - 2026-11-07

### Ditambahkan

- Tanda baca dan simbol sekarang dibacakan dalam bahasa Indonesia, walaupun suara TTS berbahasa Inggris. NVDA 2026.3 tidak punya kamus tanda baca bahasa Indonesia, sehingga sebelumnya titik, koma, dan simbol lain selalu dibacakan dalam bahasa Inggris.
- Kamus ini mencakup 806 tanda baca dan simbol yang dikenal NVDA, termasuk simbol matematika, panah, mata uang, dan pola braille. Nama mengikuti EYD Edisi V dan KBBI bila ada, misalnya "titik koma", "tanda pisah", "elipsis", "tilde", dan "tanda pagar". Simbol lain memakai nama yang lazim, misalnya "garis miring terbalik" dan "et".
- Tingkat simbol NVDA tetap berlaku. Misalnya, pada tingkat "sebagian", koma tetap tidak dibacakan.
- Fitur ini aktif secara bawaan dan bisa dimatikan di pengaturan Emoji ID, di daftar kamus simbol pada pengaturan Ucapan NVDA, atau dengan perintah baru tanpa tombol pintas di Gestur Masukan.
- Pemeriksa pembaruan. Saat NVDA dijalankan, Emoji ID memeriksa rilis terbaru di GitHub dan menawarkan untuk mengunduh dan memasangnya. Pemeriksaan juga bisa dilakukan kapan saja dengan tombol "Periksa Pembaruan Sekarang" di pengaturan Emoji ID, dan pemeriksaan otomatis bisa dimatikan. Fitur ini sementara dan akan dihapus setelah Emoji ID masuk Add-on Store NVDA.

### Untuk pengembang

- Kamus ada di `addon/locale/id/symbols-simbolIndonesia.dic` dan didaftarkan lewat `symbolDictionaries` di `buildVars.py`.
- Pemeriksa pembaruan ada di `addon/globalPlugins/emojiID/updateCheck.py`. Hapus modul ini, pengaturannya, dan tombolnya saat add-on dikirim ke Add-on Store.
- `sconstruct` melewati folder bahasa yang tidak punya berkas terjemahan, misalnya `locale/id` yang hanya berisi kamus simbol.

## [1.2.0] - 2026-11-03

### Diubah

- Nama 38 emoji wajah ditulis ulang supaya lebih alami dan sesuai maknanya. Semua emoji wajah sekarang diawali kata "wajah", dan "memberikan ciuman" disingkat menjadi "mencium". Contohnya 🤑 "wajah mata duitan", 🤬 "wajah mengumpat", 🤥 "wajah berbohong", dan 🙈 "monyet tutup mata". Daftar lengkapnya ada di `tools/overrides.tsv`.
- Nama sekitar 250 emoji lain juga ditinjau ulang supaya sesuai makna dan isinya, dan varian warna kulitnya ikut berubah. Contohnya:
  - 🙏 "kedua tangan dikatupkan". Sebelumnya "melipat tangan", yang berarti bersedekap.
  - 🐞 "kepik". Sebelumnya "kumbang betina".
  - 🍗 "paha ayam". Sebelumnya "kaki ayam".
  - 🧑‍🦯 "orang dengan tongkat putih". Sebelumnya hanya "orang dengan tongkat".
  - 🙍 "orang cemberut". Sebelumnya "orang marah".
  - Tombol angka dibacakan "tombol 1", bukan "keycap 1".
  - Bendera 🇨🇮 dibacakan "bendera Pantai Gading".
- Nama warna kulit cadangan di kode sekarang sama dengan CLDR, misalnya "warna kulit cerah" dan "warna kulit sedang".

### Diperbaiki

- 36 emoji yang sebelumnya tidak dikenali sekarang dibacakan dalam bahasa Indonesia, misalnya 🆗 "tombol OK", 🆘 "tombol SOS", 🀄 "naga merah mahyong", 🃏 "joker", tombol huruf Jepang, dan empat panah diagonal.
- Tombol pagar #️⃣, tombol bintang *️⃣, dan 🔟 sekarang dibacakan dalam bahasa Indonesia.
- 🤭 sekarang dibacakan "wajah dengan tangan menutup mulut". Sebelumnya namanya sama dengan 😳 "wajah tersipu".

### Untuk pengembang

- `tools/build_emoji_data.py` hanya menyimpan urutan yang tercantum di daftar emoji Unicode 17.0 (`emoji-test.txt`).
- Not musik ♪, ♭, dan ♯ bukan emoji, tetapi tetap disimpan lewat `tools/overrides.tsv` karena punya nama dalam bahasa Indonesia.

## [1.1.0] - 2026-11-02

### Diubah

- Diperbarui untuk NVDA 2026.3. Data emoji tetap Unicode CLDR 48.2, sama dengan versi di NVDA 2026.3.
- Pengingat donasi berkala sekarang nonaktif secara bawaan. Pengingat bisa diaktifkan di pengaturan Emoji ID.
- Dialog sambutan saat instalasi sekarang memakai dialog pesan bawaan NVDA. Memilih Donasi langsung menyalin nomor GoPay ke papan klip. Jika dialog gagal tampil, sambutan muncul sekali setelah NVDA dimulai ulang.
- Kata awalan hanya sekali sekarang ikut dinonaktifkan di pengaturan saat kata awalan dimatikan.
- Panduan pengguna menjelaskan beda Emoji ID dengan nama emoji bawaan NVDA.
- Antarmuka add-on (pengaturan, dialog, dan pesan) sekarang tersedia dalam bahasa Inggris dan mengikuti bahasa NVDA. Nama emoji tetap berbahasa Indonesia.

### Diperbaiki

- Terjemahan add-on sekarang dimuat. Sebelumnya teks antarmuka tidak bisa diterjemahkan.
- Angka, tanda pagar, dan tanda bintang biasa tidak lagi diperiksa dengan pencarian emoji yang berat, sehingga teks berisi angka dibaca lebih cepat.
- Saat add-on dimatikan, Emoji ID tidak lagi memutus add-on lain yang juga membungkus pembacaan simbol NVDA.
- Navigasi per karakter pada bendera tidak lagi membisu. NVDA memecah bendera menjadi dua huruf regional, dan setiap huruf sekarang dibacakan, misalnya "huruf regional I" lalu "huruf regional D" untuk bendera Indonesia. Potongan bendera yang tersisa saat navigasi per kata juga dibacakan dengan cara yang sama.

### Dihapus

- Pengaturan "Ikuti tingkat simbol NVDA". Pengaturan ini belum pernah berfungsi.
- Kode yang mengubah data internal NVDA saat instalasi.

### Untuk pengembang

- Build memakai SCons dan `site_scons` dari NVDA AddonTemplate. `buildVars.py` memakai `AddonInfo` dan menambahkan changelog, URL kode sumber, dan lisensi ke manifest.
- Kode mengikuti standar NVDA: indentasi tab, nama lowerCamelCase, `logHandler.log`, dan komentar `Translators:`.
- Tes ditulis ulang untuk pytest.

## [1.0.0] - 2026-10-14

Rilis pertama.

- Membacakan emoji dalam bahasa Indonesia di semua synthesizer, termasuk Eloquence bahasa Inggris.
- Mendukung emoji dasar, rangkaian ZWJ, bendera, keycap, dan warna kulit.
- Emoji tetap dibacakan dalam bahasa Indonesia saat navigasi per karakter, kursor tinjauan, dan saat mengetik.
- Pengaturan kata awalan, penggabungan emoji berulang, detail warna kulit, dan pembersihan tanda hubung serta tanda kurung pada nama emoji.
- Perintah tanpa tombol pintasan bawaan untuk menyalakan dan mematikan Emoji ID.
- Data dari Unicode CLDR 48.2, ditambah penggantian nama di `tools/overrides.tsv`.
- Panduan dalam bahasa Indonesia dan Inggris.
- Dialog sambutan, informasi donasi GoPay, dan pengingat donasi berkala.
