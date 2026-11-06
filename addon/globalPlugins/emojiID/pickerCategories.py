# Emoji ID - Indonesian Emoji Reader for NVDA
# Copyright (C) 2026 Rexya Muhamad <rexya2017@gmail.com>
# This file is covered by the GNU General Public License v2 or later.
# See the file LICENSE for more details.

"""Names of the categories in the insert emoji dialog.

The main categories follow the Windows 11 emoji panel. Emoji subcategories are the Unicode emoji subgroups.
"""

import addonHandler

addonHandler.initTranslation()

#: Main categories for each kind, in the order shown.
EMOJI_CATEGORIES: dict[str, str] = {
	# Translators: Emoji category in the insert emoji dialog.
	"recent": _("Terakhir dipakai"),
	# Translators: Emoji category in the insert emoji dialog.
	"favorites": _("Favorit"),
	# Translators: Emoji category in the insert emoji dialog.
	"faces": _("Wajah dan hewan"),
	# Translators: Emoji category in the insert emoji dialog.
	"people": _("Orang"),
	# Translators: Emoji category in the insert emoji dialog.
	"objects": _("Perayaan dan benda"),
	# Translators: Emoji category in the insert emoji dialog.
	"food": _("Makanan dan tumbuhan"),
	# Translators: Emoji category in the insert emoji dialog.
	"travel": _("Transportasi dan tempat"),
	# Translators: Emoji category in the insert emoji dialog.
	"symbols": _("Simbol"),
	# Translators: Emoji category in the insert emoji dialog.
	"flags": _("Bendera"),
}

SYMBOL_CATEGORIES: dict[str, str] = {
	# Translators: Symbol category in the insert emoji dialog.
	"recent": _("Terakhir dipakai"),
	# Translators: Symbol category in the insert emoji dialog.
	"favorites": _("Favorit"),
	# Translators: Symbol category in the insert emoji dialog.
	"punctuation": _("Tanda baca umum"),
	# Translators: Symbol category in the insert emoji dialog.
	"currency": _("Simbol mata uang"),
	# Translators: Symbol category in the insert emoji dialog.
	"latin": _("Simbol huruf Latin"),
	# Translators: Symbol category in the insert emoji dialog.
	"geometric": _("Simbol geometri"),
	# Translators: Symbol category in the insert emoji dialog.
	"math": _("Simbol matematika"),
	# Translators: Symbol category in the insert emoji dialog.
	"supplemental": _("Simbol tambahan"),
	# Translators: Symbol category in the insert emoji dialog.
	"language": _("Simbol bahasa"),
}

KAOMOJI_CATEGORIES: dict[str, str] = {
	# Translators: Kaomoji category in the insert emoji dialog.
	"recent": _("Terakhir dipakai"),
	# Translators: Kaomoji category in the insert emoji dialog.
	"favorites": _("Favorit"),
	# Translators: Kaomoji category in the insert emoji dialog.
	"classic": _("Emotikon ASCII klasik"),
	# Translators: Kaomoji category in the insert emoji dialog.
	"happy": _("Senang"),
	# Translators: Kaomoji category in the insert emoji dialog.
	"greeting": _("Menyapa"),
	# Translators: Kaomoji category in the insert emoji dialog.
	"cute": _("Bertingkah imut"),
	# Translators: Kaomoji category in the insert emoji dialog.
	"angry": _("Marah"),
	# Translators: Kaomoji category in the insert emoji dialog.
	"sad": _("Sedih"),
	# Translators: Kaomoji category in the insert emoji dialog.
	"surprised": _("Terkejut dan terdiam"),
}

#: Unicode emoji subgroups.
SUBGROUPS: dict[str, str] = {
	# Translators: Emoji subcategory in the insert emoji dialog.
	"face-smiling": _("Wajah tersenyum"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"face-affection": _("Wajah penuh kasih sayang"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"face-tongue": _("Wajah menjulurkan lidah"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"face-hand": _("Wajah dengan tangan"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"face-neutral-skeptical": _("Wajah datar dan ragu"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"face-sleepy": _("Wajah mengantuk"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"face-unwell": _("Wajah sakit"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"face-hat": _("Wajah bertopi"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"face-glasses": _("Wajah berkacamata"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"face-concerned": _("Wajah cemas"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"face-negative": _("Wajah marah"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"face-costume": _("Wajah kostum"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"cat-face": _("Wajah kucing"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"monkey-face": _("Wajah monyet"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"heart": _("Hati"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"emotion": _("Simbol emosi"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"hand-fingers-open": _("Tangan dengan jari terbuka"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"hand-fingers-partial": _("Tangan dengan sebagian jari"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"hand-single-finger": _("Tangan dengan satu jari"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"hand-fingers-closed": _("Tangan terkepal"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"hands": _("Kedua tangan"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"hand-prop": _("Tangan memegang benda"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"body-parts": _("Bagian tubuh"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"person": _("Orang"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"person-gesture": _("Orang dengan gerak isyarat"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"person-role": _("Profesi dan peran"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"person-fantasy": _("Tokoh khayalan"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"person-activity": _("Orang berkegiatan"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"person-sport": _("Orang berolahraga"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"person-resting": _("Orang beristirahat"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"family": _("Keluarga dan pasangan"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"person-symbol": _("Simbol orang"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"animal-mammal": _("Mamalia"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"animal-bird": _("Burung"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"animal-amphibian": _("Amfibi"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"animal-reptile": _("Reptil"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"animal-marine": _("Hewan laut"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"animal-bug": _("Serangga"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"plant-flower": _("Bunga"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"plant-other": _("Tumbuhan lain"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"food-fruit": _("Buah"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"food-vegetable": _("Sayuran"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"food-prepared": _("Makanan olahan"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"food-asian": _("Makanan Asia"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"food-sweet": _("Makanan manis"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"drink": _("Minuman"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"dishware": _("Peralatan makan"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"place-map": _("Peta"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"place-geographic": _("Tempat alam"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"place-building": _("Bangunan"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"place-religious": _("Tempat ibadah"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"place-other": _("Tempat lain"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"transport-ground": _("Transportasi darat"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"transport-water": _("Transportasi air"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"transport-air": _("Transportasi udara"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"hotel": _("Hotel"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"time": _("Waktu"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"sky & weather": _("Langit dan cuaca"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"event": _("Acara"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"award-medal": _("Penghargaan dan medali"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"sport": _("Olahraga"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"game": _("Permainan"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"arts & crafts": _("Seni dan kerajinan"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"clothing": _("Pakaian"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"sound": _("Suara"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"music": _("Musik"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"musical-instrument": _("Alat musik"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"phone": _("Telepon"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"computer": _("Komputer"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"light & video": _("Lampu dan video"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"book-paper": _("Buku dan kertas"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"money": _("Uang"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"mail": _("Surat"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"writing": _("Alat tulis"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"office": _("Kantor"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"lock": _("Kunci"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"tool": _("Perkakas"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"science": _("Sains"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"medical": _("Medis"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"household": _("Rumah tangga"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"other-object": _("Benda lain"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"transport-sign": _("Rambu transportasi"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"warning": _("Peringatan"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"arrow": _("Panah"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"religion": _("Agama"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"zodiac": _("Zodiak"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"av-symbol": _("Simbol audio dan video"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"gender": _("Gender"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"math": _("Matematika"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"punctuation": _("Tanda baca"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"currency": _("Mata uang"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"other-symbol": _("Simbol lain"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"keycap": _("Tombol angka"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"alphanum": _("Huruf dan angka"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"geometric": _("Bentuk geometri"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"flag": _("Bendera umum"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"country-flag": _("Bendera negara"),
	# Translators: Emoji subcategory in the insert emoji dialog.
	"subdivision-flag": _("Bendera wilayah"),
}

#: Skin tone choices, from no tone to the five Fitzpatrick tones.
SKIN_TONES: tuple[str, ...] = (
	# Translators: Skin tone choice in the insert emoji dialog.
	_("Tanpa warna kulit"),
	# Translators: Skin tone choice in the insert emoji dialog.
	_("Cerah"),
	# Translators: Skin tone choice in the insert emoji dialog.
	_("Cerah sedang"),
	# Translators: Skin tone choice in the insert emoji dialog.
	_("Sedang"),
	# Translators: Skin tone choice in the insert emoji dialog.
	_("Gelap sedang"),
	# Translators: Skin tone choice in the insert emoji dialog.
	_("Gelap"),
)
