# Panduan Pengujian Manual Add-on Emoji ID

Panduan ini ditujukan bagi pengguna tunanetra untuk memverifikasi fungsionalitas add-on Emoji ID menggunakan NVDA Speech Viewer (Penampil Ucapan) dan Log NVDA.

## Cara Membuka Speech Viewer
1. Buka menu NVDA (tekan tombol NVDA+N).
2. Pilih submenu Perkakas (Tools).
3. Pilih Penampil Ucapan (Speech Viewer).
4. Kotak dialog Speech Viewer akan menampilkan teks persis seperti yang dikirim ke synthesizer.

## Kasus Uji 1: Membaca Sebaris Teks (Line Reading)
- Tindakan: Buat dokumen Notepad, ketik kalimat: `Hari ini sangat menyenangkan 😀 sekali.` lalu tekan tombol Panah Atas untuk membaca baris tersebut.
- Hasil yang Diharapkan:
  - Jika awalan aktif: `Hari ini sangat menyenangkan emoji wajah gembira sekali.`
  - Jika awalan nonaktif: `Hari ini sangat menyenangkan wajah gembira sekali.`

## Kasus Uji 2: Membaca Terus-Menerus / Say All (NVDA+Panah Bawah)
- Tindakan: Buat teks dua paragraf dengan beberapa emoji (misalnya `Paragraf satu 👍.` lalu enter dan `Paragraf dua 🇮🇩.`). Tekan NVDA+Panah Bawah dari awal dokumen.
- Hasil yang Diharapkan:
  - Say All berjalan lancar tanpa terhenti.
  - Index Command dan pemenggalan kalimat tetap utuh.
  - Terdengar: `Paragraf satu emoji jempol ke atas.` diikuti `Paragraf dua emoji bendera Indonesia.`

## Kasus Uji 3: Navigasi Panah Karakter demi Karakter (Arrow-Key Character Navigation)
- Tindakan: Pada dokumen teks, tempatkan kursor pada karakter emoji `😀` dan gerakkan kursor dengan Panah Kanan/Kiri.
- Catatan Penting: Kasus ini menguji penyelesaian 'Single-Character Trap' (di mana karakter tunggal biasanya diterjemahkan oleh NVDA sebelum speak()).
- Hasil yang Diharapkan:
  - NVDA langsung mengucapkan nama Indonesia: `emoji wajah gembira` (bukan nama bahasa Inggris `grinning face`).

## Kasus Uji 4: Gema Karakter saat Mengetik (Typed-Character Echo)
- Tindakan: Pastikan pengaturan Gema Mengetik (Typing Echo) pada kategori Papan Ketik NVDA aktif untuk karakter. Buka kotak teks dan ketik emoji (misalnya tempel emoji `🔥` atau gunakan Windows+Titik untuk memilih emoji api).
- Hasil yang Diharapkan:
  - Saat karakter diketik/ditempel, terdengar: `emoji api` (bukan `fire`).

## Kasus Uji 5: Kursor Tinjau (Review Cursor Navigation)
- Tindakan: Gunakan kursor tinjau (NumPad 7 untuk baris atas, NumPad 8 untuk baris saat ini, NumPad 9 untuk baris bawah, NumPad 4 dan 6 untuk navigasi karakter tinjau). Arahkan kursor tinjau ke karakter emoji `👍`.
- Hasil yang Diharapkan:
  - Terdengar nama dalam bahasa Indonesia: `emoji jempol ke atas`.

## Kasus Uji 6: Navigasi Kata demi Kata (Control+Panah Kanan / Kiri)
- Tindakan: Navigasi dengan Control+Panah Kanan melintasi kalimat: `Halo 😀 teman`.
- Hasil yang Diharapkan:
  - Kata pertama: `Halo`
  - Kata kedua: `emoji wajah gembira`
  - Kata ketiga: `teman`

## Kasus Uji 7: Fokus Objek dengan Nama Berisi Emoji (Object Focus)
- Tindakan: Buka aplikasi obrolan (WhatsApp, Telegram, atau Discord) di mana nama kontak atau nama grup mengandung emoji (misalnya `Keluarga 👨‍👩‍👧`). Tekan Tab hingga fokus berada pada objek tersebut.
- Hasil yang Diharapkan:
  - Nama objek dibacakan dengan nama Indonesia: `Keluarga emoji keluarga pria, wanita, anak perempuan`.

## Kasus Uji 8: Penggabungan Emoji Berulang (Collapse Repeated)
- Tindakan: Ketik tiga emoji identik berurutan: `😀😀😀`.
- Hasil yang Diharapkan:
  - Jika opsi gabungkan berulang aktif: `3 emoji wajah gembira`.
  - Jika opsi gabungkan nonaktif: `emoji wajah gembira emoji wajah gembira emoji wajah gembira`.

## Kasus Uji 9: Variasi Warna Kulit (Skin Tone Detail)
- Tindakan: Ketik emoji dengan warna kulit: `👍🏽`.
- Hasil yang Diharapkan:
  - Jika opsi detail warna kulit aktif: `emoji jempol ke atas warna kulit sedang`.
  - Jika opsi detail warna kulit nonaktif: `emoji jempol ke atas`.

## Kasus Uji 10: Tombol Pengalih Aktif / Nonaktif (Toggle Script)
- Tindakan: Tetapkan pintasan gestur untuk Emoji ID di Preferensi -> Gestur Masukan (misalnya NVDA+Shift+E). Tekan pintasan tersebut sekali.
- Hasil yang Diharapkan:
  - Terdengar: `Emoji ID nonaktif`.
  - Saat membaca `😀`, terdengar nama bawaan NVDA/Eloquence (`grinning face`).
  - Tekan pintasan sekali lagi: terdengar `Emoji ID aktif`.
  - Membaca `😀` kembali menghasilkan: `emoji wajah gembira`.

## Kasus Uji 11: Pengecekan Log NVDA (NVDA Log Verification)
- Tindakan: Buka menu NVDA -> Perkakas -> Tampilkan Log (NVDA+F1).
- Hasil yang Diharapkan:
  - Tidak ada satupun pesan galat (*ERROR* atau *EXCEPTION*) dari plugin `emojiID`.
  - Terdapat pesan info: `Emoji ID: loaded 3917 emoji entries` dan `Emoji ID: plugin initialized successfully`.

## Kasus uji khusus NVDA 2026.3

Jalankan kasus berikut sebelum mengubah `lastTestedNVDAVersion` atau merilis versi baru.

- Bendera dengan normalisasi Unicode. Aktifkan normalisasi Unicode di pengaturan Ucapan NVDA, lalu baca baris `Bendera 🇮🇩 dan 🇯🇵`. Hasil yang diharapkan: kedua bendera dibacakan dengan nama Indonesia, bukan huruf I D atau J P. NVDA 2026.2 mulai menormalisasi regional indicator menjadi huruf biasa saat opsi ini aktif.
- Navigasi per kata. Pada baris `Halo 👨‍👩‍👧 apa kabar`, tekan Control+Panah Kanan berulang kali. Hasil yang diharapkan: emoji keluarga dibacakan sebagai satu nama, tidak terpecah. NVDA 2026.3 memakai ICU Windows untuk memisahkan kata. Catat aplikasi yang dipakai, karena di beberapa aplikasi (misalnya Notepad Windows 11) pemisahan kata dilakukan oleh aplikasi itu sendiri, bukan oleh NVDA.
- Navigasi per karakter pada bendera. Pada baris `Bendera 🇮🇩 dan 🇯🇵`, letakkan kursor di spasi sebelum bendera Indonesia, lalu tekan Panah Kanan. Hasilnya bergantung pada aplikasi. Di Notepad Windows 11, aplikasi mengirim bendera utuh, jadi hasil yang diharapkan adalah "emoji bendera Indonesia". Di aplikasi yang pemisahan karakternya dilakukan NVDA sendiri, misalnya Notepad++, bendera terpecah menjadi dua huruf, jadi hasil yang diharapkan adalah "huruf regional I", lalu "huruf regional D". Yang penting, NVDA tidak boleh membisu.
- Pembanding tanpa Emoji ID. Jika navigasi per kata terdengar janggal, matikan Emoji ID dengan perintah pengalihnya, lalu ulangi langkah yang sama. Jika pola kata yang dibacakan tetap sama (hanya nama emojinya yang berbeda), penyebabnya ada pada cara aplikasi memotong kata, bukan pada Emoji ID.
- Sambutan saat instalasi. Pasang add-on. Hasil yang diharapkan: dialog Selamat Datang di Emoji ID muncul dan teksnya langsung dibacakan. Pilih Donasi, lalu pastikan informasi GoPay dibacakan dan nomor sudah ada di papan klip. Setelah NVDA dimulai ulang, dialog sambutan tidak muncul lagi.
- Pembaruan dari 1.0.0. Pasang versi baru di atas versi 1.0.0, mulai ulang NVDA, lalu buka pengaturan Emoji ID. Hasil yang diharapkan: tidak ada galat di log NVDA, dan pilihan "Ikuti tingkat simbol NVDA" sudah tidak ada.

## Kasus uji tanda baca dan simbol

- Tanda baca dalam kalimat. Pakai suara bahasa Inggris, misalnya Eloquence, dan atur tingkat simbol NVDA ke "semua". Baca baris `Halo, apa kabar? (baik) 50% #NVDA`. Hasil yang diharapkan: koma, tanda tanya, kurung buka, kurung tutup, persen, dan tanda pagar dibacakan dalam bahasa Indonesia.
- Tingkat simbol. Ubah tingkat simbol ke "sebagian", lalu baca baris yang sama. Hasil yang diharapkan: koma dan tanda tanya tidak dibacakan, sama seperti perilaku NVDA biasa.
- Navigasi per karakter. Gerakkan kursor per karakter pada `a.b,c`. Hasil yang diharapkan: "titik" dan "koma".
- Saklar di pengaturan. Hapus centang "Bacakan tanda baca dan simbol dalam bahasa Indonesia", lalu tekan OK. Hasil yang diharapkan: tanda baca kembali dibacakan dalam bahasa Inggris. Di pengaturan Ucapan NVDA, kamus "Tanda baca dan simbol bahasa Indonesia (Emoji ID)" juga ikut tidak tercentang.
- Mulai ulang NVDA setelah fitur dimatikan. Hasil yang diharapkan: fitur tetap mati.

## Kasus uji dialog Sisipkan Emoji

Tetapkan dulu tombol pintas untuk "Buka dialog sisipkan emoji" di Gestur Masukan, kategori Emoji ID.

- Membuka dialog. Buka Notepad, lalu tekan tombol pintas itu. Hasil yang diharapkan: dialog "Sisipkan Emoji - Emoji ID" terbuka dengan fokus di kolom Cari. Dialog tidak bisa dibuka dari menu NVDA.
- Mencari dan menyisipkan. Ketik "ngakak", lalu tekan Enter. Hasil yang diharapkan: dialog tertutup, 🤣 tertempel di Notepad, dan isi papan klip sebelumnya kembali.
- Personalisasi. Buka dialog, cari "jempol". Hasil yang diharapkan: daftar menyebut "jempol ke atas, dapat dipersonalisasi". Tekan Enter: dialog Personalisasi muncul dengan "Tanpa personalisasi". Tekan Enter lagi: tertempel 👍 tanpa warna kulit. Ulangi, pilih "Personalisasi", atur Warna kulit ke Sedang, lalu tekan Enter: tertempel 👍🏽.
- Dua orang. Cari "jabat", tekan Enter, pilih "Personalisasi", atur Warna kulit orang pertama ke Cerah dan Warna kulit orang kedua ke Gelap, lalu tekan Enter. Hasil yang diharapkan: tertempel jabat tangan dengan dua warna kulit berbeda.
- Jenis kelamin dan arah. Cari "berlari", tekan Enter, pilih "Personalisasi", atur Jenis kelamin ke Wanita dan Arah ke Menghadap kanan. Hasil yang diharapkan: kolom Hasil menyebut "wanita berlari ... menghadap kanan".
- Emoji tanpa personalisasi. Cari "indonesia" dan tekan Enter. Hasil yang diharapkan: bendera langsung tertempel tanpa dialog Personalisasi.
- Kecepatan. Gerakkan panah naik dan turun di kotak Kategori dan Subkategori. Hasil yang diharapkan: tidak terasa berat.
- Rangkaian. Cari "kue ulang tahun", tekan Tambah ke Rangkaian, lalu cari "terima kasih" dan tekan Tambah ke Rangkaian. Tekan Sisipkan. Hasil yang diharapkan: 🎂🙏 tertempel sekaligus.
- Kaomoji. Pilih Jenis Kaomoji, cari "bahu", lalu tekan Enter. Hasil yang diharapkan: `¯\_(ツ)_/¯` tertempel.
- Favorit dan terakhir dipakai. Tekan Tambah ke Favorit pada sebuah emoji, tutup, lalu buka lagi dan pilih kategori Favorit. Hasil yang diharapkan: emoji itu ada di daftar. Kategori Terakhir dipakai berisi emoji yang tadi disisipkan.
- Bahasa Inggris. Ganti bahasa NVDA ke bahasa Inggris dan mulai ulang NVDA. Hasil yang diharapkan: semua label, tombol, kategori, dan subkategori di dialog berbahasa Inggris. Nama emoji dan kaomoji tetap berbahasa Indonesia.

## Kasus uji mode baca ringkas

- Atur "Jumlah emoji berturut-turut yang dibacakan" ke 3, lalu baca baris `Mantap 😀❤️👍🎉🔥😂 ok`. Hasil yang diharapkan: "Mantap wajah gembira hati merah jempol ke atas dan 3 emoji lainnya ok".
