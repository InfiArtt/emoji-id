# Riwayat perubahan Emoji ID

Format mengikuti Keep a Changelog.

## [Belum dirilis]

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
