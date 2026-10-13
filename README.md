# Emoji ID - Pembaca Emoji Bahasa Indonesia untuk NVDA

Add-on resmi NVDA untuk membacakan emoji dalam bahasa Indonesia di segala suara synthesizer (TTS).

## Target NVDA
- Minimum NVDA Version: 2026.1
- Last Tested NVDA Version: 2026.1
- Arsitektur: Python 3.13, 64-bit

## Struktur Berkas
- `addon/`: Kode sumber add-on dan dokumentasi.
  - `globalPlugins/emojiID/`: Plugin global utama dan data emoji.
  - `doc/`: Dokumentasi bahasa Indonesia (`id/`) dan Inggris (`en/`).
  - `manifest.ini`: Manifest add-on NVDA.
- `tools/`: Skrip build data CLDR dan berkas overrides manual.
- `tests/`: Suite pengujian unit mandiri.
- `buildVars.py`: Konfigurasi build AddonTemplate.
- `SConstruct`: Skrip packaging SCons.
- `LICENSE`: Lisensi GPL v2+.

## Menjalankan Pengujian
Jalankan pengujian unit mandiri:
```bash
python tests/test_emoji_id.py
```

## Membangun Paket Add-on (.nvda-addon)
Paket add-on dibangun dengan SCons atau dikemas langsung sebagai arsip zip berekstensi `.nvda-addon`.

## Pengembang dan Hak Cipta
- Pengembang: Rexya Muhamad <rexya2017@gmail.com>
- Lisensi: GPL-2.0-or-later
- Hak Cipta: (c) 2026 Rexya Muhamad <rexya2017@gmail.com>
- Dukungan Donasi: GoPay 085128011831 (a.n. Rexya Muhamad Rizki)
