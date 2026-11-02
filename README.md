# Emoji ID

Add-on NVDA yang membacakan emoji dalam bahasa Indonesia, apa pun bahasa suara TTS yang dipakai. Panduan pengguna ada di `addon/doc/id/readme.md` (bahasa Indonesia) dan `addon/doc/en/readme.md` (bahasa Inggris).

## Versi NVDA

- Versi minimum: NVDA 2026.1.
- Terakhir diuji: NVDA 2026.3.

## Struktur berkas

- `addon/globalPlugins/emojiID/`: kode plugin dan data emoji (`data/emoji_id.json`).
- `addon/doc/`: panduan pengguna dalam bahasa Indonesia dan Inggris.
- `tools/build_emoji_data.py`: membangun ulang data emoji dari Unicode CLDR, ditambah penggantian nama dari `tools/overrides.tsv`.
- `tests/`: tes unit yang berjalan tanpa NVDA.
- `buildVars.py`: informasi add-on dan konfigurasi build, mengikuti NVDA AddonTemplate.
- `sconstruct` dan `site_scons/`: skrip build SCons dari AddonTemplate.

## Membangun add-on

Butuh Python 3.13, SCons, Markdown, dan gettext (`msgfmt`, `xgettext`).

```bash
scons
```

Hasilnya `emojiID-<versi>.nvda-addon` di folder utama.

## Terjemahan

Teks sumber antarmuka berbahasa Indonesia. Terjemahan bahasa Inggris ada di `addon/locale/en/LC_MESSAGES/nvda.po`. Nama emoji tidak diterjemahkan, karena berasal dari data CLDR, bukan dari berkas terjemahan.

Setelah mengubah teks antarmuka, perbarui berkas terjemahan:

```bash
scons pot
```

```bash
msgmerge --update --no-location addon/locale/en/LC_MESSAGES/nvda.po emojiID.pot
```

## Tes dan pemeriksaan kode

```bash
python -m pytest
```

```bash
python -m ruff check .
```

Kode mengikuti standar penulisan kode NVDA: indentasi tab, nama lowerCamelCase, dan komentar `Translators:` untuk setiap string yang diterjemahkan.

## GitHub Actions dan rilis

Setiap push dan pull request ke `main` menjalankan Ruff, tes, pemeriksaan versi, build, dan pemeriksaan terjemahan. Paket hasil build bisa diunduh dari halaman Actions.

Rilis dibuat otomatis saat push ke `main`, jika:

- versi di `buildVars.py` belum punya tag rilis, dan
- `CHANGELOG.md` punya bagian versi itu dengan tanggal, misalnya `## [1.1.0] - 2026-11-15`.

Bagian yang masih bertulisan "belum dirilis" hanya dibangun, tidak dirilis. Rilis berisi paket `.nvda-addon`, berkas `.pot`, catatan dari `CHANGELOG.md`, dan checksum SHA256 untuk memeriksa keaslian paket.

## Membangun ulang data emoji

```bash
python tools/build_emoji_data.py --cldr-version 48.2.0
```

## Lisensi

- Kode: GPL-2.0-or-later, (c) 2026 Rexya Muhamad <rexya2017@gmail.com>.
- Data nama emoji: Unicode CLDR, Unicode License v3.
