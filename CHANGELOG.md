# Changelog - Emoji ID

Semua perubahan penting pada add-on ini didokumentasikan dalam berkas ini. Format mengikuti panduan Keep a Changelog.

## [1.0.0] - 2026-10-14

### Ditambahkan (Added)
- Rilis perdana add-on Emoji ID untuk NVDA 2026.1+.
- Intersepsi dan penerjemahan emoji ke bahasa Indonesia secara konsisten pada semua synthesizer (termasuk Eloquence bahasa Inggris).
- Dukungan lengkap untuk emoji dasar, Zero-Width Joiner (ZWJ) sequence (keluarga, profesi), bendera negara, digit keycap, dan varian warna kulit (Fitzpatrick).
- Integrasi ke speech sequence filter (`speech.extensions.filter_speechSequence`) yang mempertahankan semua SpeechCommand, IndexCommand, dan objek non-string lainnya tanpa modifikasi.
- Penyelesaian perangkap satu karakter (*single-character trap*): pembungkusan `characterProcessing.processSpeechSymbol` dengan try/except yang aman dan pemulihan bersih saat terminasi plugin.
- Panel pengaturan NVDA di dialog preferensi dengan dukungan profil konfigurasi NVDA (*profile-aware*).
- Opsi awalan nama emoji ("emoji") dengan pengaturan awalan sekali per rangkaian emoji berurutan.
- Opsi penggabungan emoji identik yang berurutan ("N kali [nama]").
- Opsi pengaktifan/penonaktifan detail warna kulit.
- Opsi kepatuhan tingkat simbol (*symbol level*).
- Perintah gestur masukan unassigned dengan `@script` untuk beralih aktif/nonaktif seketika dengan pengumuman status.
- Mesin pencocokan berbasis regex terkompilasi berurutan *longest-match first* dengan normalisasi U+FE0F/U+FE0E.
- Skrip build-time pipeline data (`tools/build_emoji_data.py`) dari Unicode CLDR 48.2.0.
- Berkas penimpa (*overrides*) manual (`tools/overrides.tsv`) untuk kosakata bahasa Indonesia yang lebih alami.
- Suite pengujian unit mandiri mencakup semua kasus emoji dan siklus hidup plugin.
- Dokumentasi bilingual (Indonesia dan Inggris) dan pemberitahuan lisensi Unicode v3.
