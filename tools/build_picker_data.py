#!/usr/bin/env python3
"""Build the data for the insert emoji dialog.

Writes addon/globalPlugins/emojiID/data/picker.json with:

- emoji: one item per emoji as the Windows emoji panel shows it, with its gender, direction and
  skin tone variants, its category and Unicode subgroup, and its Indonesian CLDR keywords;
- symbols: the non-emoji symbols of the Indonesian symbol dictionary, plus accented Latin letters
  and Greek letters, sorted into the Windows emoji panel symbol categories;
- kaomoji: tools/kaomoji.tsv.

Usage:
    python tools/build_picker_data.py
"""

import argparse
import json
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EMOJI_TEST_URL = "https://www.unicode.org/Public/{version}/emoji/emoji-test.txt"
CLDR_ANNOTATIONS_URL = (
	"https://cdn.jsdelivr.net/npm/cldr-annotations-full@{version}/annotations/id/annotations.json"
)
SYMBOL_DICTIONARY = ROOT / "addon" / "locale" / "id" / "symbols-simbolIndonesia.dic"
KAOMOJI = ROOT / "tools" / "kaomoji.tsv"
OUTPUT = ROOT / "addon" / "globalPlugins" / "emojiID" / "data" / "picker.json"

ZWJ = chr(0x200D)
VS16 = chr(0xFE0F)
TONES = {chr(0x1F3FB + index): str(index + 1) for index in range(5)}
MALE = ZWJ + chr(0x2642) + VS16
FEMALE = ZWJ + chr(0x2640) + VS16
FACING_RIGHT = ZWJ + chr(0x27A1) + VS16
PERSON = chr(0x1F9D1)
MAN = chr(0x1F468)
WOMAN = chr(0x1F469)

#: Single emoji that are the male or female form of a gender neutral emoji.
GENDER_PAIRS = {
	MAN: (PERSON, "pria"),
	WOMAN: (PERSON, "wanita"),
	chr(0x1F466): (chr(0x1F9D2), "pria"),  # boy, child
	chr(0x1F467): (chr(0x1F9D2), "wanita"),  # girl, child
	chr(0x1F474): (chr(0x1F9D3), "pria"),  # old man, older person
	chr(0x1F475): (chr(0x1F9D3), "wanita"),  # old woman, older person
	chr(0x1F934): (chr(0x1FAC5), "pria"),  # prince, person with crown
	chr(0x1F478): (chr(0x1FAC5), "wanita"),  # princess, person with crown
	chr(0x1F385): (PERSON + ZWJ + chr(0x1F384), "pria"),  # Santa Claus, Mx Claus
	chr(0x1F936): (PERSON + ZWJ + chr(0x1F384), "wanita"),  # Mrs. Claus, Mx Claus
	chr(0x1FAC3): (chr(0x1FAC4), "pria"),  # pregnant man, pregnant person
	chr(0x1F930): (chr(0x1FAC4), "wanita"),  # pregnant woman, pregnant person
}

#: Two person emoji whose mixed skin tones are written as a different sequence.
MIXED_TONE_FORMS = {
	chr(0x1F91D): chr(0x1FAF1) + ZWJ + chr(0x1FAF2),  # handshake
	chr(0x1F48F): PERSON + ZWJ + chr(0x2764) + VS16 + ZWJ + chr(0x1F48B) + ZWJ + PERSON,  # kiss
	chr(0x1F491): PERSON + ZWJ + chr(0x2764) + VS16 + ZWJ + PERSON,  # couple with heart
	chr(0x1F46D): WOMAN + ZWJ + chr(0x1F91D) + ZWJ + WOMAN,  # women holding hands
	chr(0x1F46B): WOMAN + ZWJ + chr(0x1F91D) + ZWJ + MAN,  # woman and man holding hands
	chr(0x1F46C): MAN + ZWJ + chr(0x1F91D) + ZWJ + MAN,  # men holding hands
}


def categoryFor(group: str, subgroup: str) -> str:
	"""Map a Unicode emoji group to a Windows emoji panel category."""
	if group == "Smileys & Emotion":
		return "symbols" if subgroup in ("heart", "emotion") else "faces"
	if group == "Animals & Nature":
		return "food" if subgroup.startswith("plant-") else "faces"
	return {
		"People & Body": "people",
		"Food & Drink": "food",
		"Travel & Places": "travel",
		"Activities": "objects",
		"Objects": "objects",
		"Symbols": "symbols",
		"Flags": "flags",
	}[group]


def fetch(url: str) -> str:
	request = urllib.request.Request(url, headers={"User-Agent": "Emoji-ID-BuildTool/1.0"})
	with urllib.request.urlopen(request, timeout=60) as response:
		return response.read().decode("utf-8")


def parseEmojiTest(text: str) -> list[tuple[str, str, str]]:
	"""Return (sequence, group, subgroup) for every fully-qualified emoji, in Unicode order."""
	result = []
	group = subgroup = ""
	for line in text.splitlines():
		if line.startswith("# group:"):
			group = line.split(":", 1)[1].strip()
		elif line.startswith("# subgroup:"):
			subgroup = line.split(":", 1)[1].strip()
		elif "; fully-qualified" in line and group != "Component":
			codepoints = line.split(";", 1)[0].split()
			result.append(("".join(chr(int(cp, 16)) for cp in codepoints), group, subgroup))
	return result


def splitTones(sequence: str) -> tuple[str, str]:
	"""Split a sequence into its toneless form and its tone key, such as "3" or "1,5"."""
	tones = [TONES[ch] for ch in sequence if ch in TONES]
	return "".join(ch for ch in sequence if ch not in TONES), ",".join(tones)


def variantOf(toneless: str, allToneless: set[str]) -> tuple[str, str]:
	"""Return (group key, variant key) for a toneless emoji, for example ("🏃", "wanita|kanan")."""
	rest = toneless
	isFacingRight = rest.endswith(FACING_RIGHT)
	if isFacingRight:
		rest = rest[: -len(FACING_RIGHT)]
	gender = ""
	if rest.endswith(MALE) and rest[: -len(MALE)] in allToneless:
		gender, rest = "pria", rest[: -len(MALE)]
	elif rest.endswith(FEMALE) and rest[: -len(FEMALE)] in allToneless:
		gender, rest = "wanita", rest[: -len(FEMALE)]
	elif rest[:2] in (MAN + ZWJ, WOMAN + ZWJ) and PERSON + rest[1:] in allToneless:
		gender, rest = ("pria" if rest[0] == MAN else "wanita"), PERSON + rest[1:]
	elif rest in GENDER_PAIRS:
		rest, gender = GENDER_PAIRS[rest]
	return rest, "|".join(part for part in (gender, "kanan" if isFacingRight else "") if part)


def buildEmoji(entries: list[tuple[str, str, str]], keywords: dict[str, list[str]]) -> list[dict]:
	allToneless = {splitTones(sequence)[0] for sequence, _group, _subgroup in entries}
	tonesByToneless: dict[str, dict[str, str]] = {}
	for sequence, _group, _subgroup in entries:
		toneless, toneKey = splitTones(sequence)
		if toneKey:
			tonesByToneless.setdefault(toneless, {})[toneKey] = sequence
	items: dict[str, dict] = {}
	for sequence, group, subgroup in entries:
		toneless, toneKey = splitTones(sequence)
		if toneKey:
			continue
		groupKey, variant = variantOf(toneless, allToneless)
		item = items.setdefault(
			groupKey,
			{"c": categoryFor(group, subgroup), "sg": subgroup, "k": [], "v": {}},
		)
		tones = dict(tonesByToneless.get(toneless, {}))
		mixed = MIXED_TONE_FORMS.get(toneless)
		if mixed:
			tones.update(tonesByToneless.get(mixed, {}))
		item["v"][variant] = {"s": sequence, **({"t": tones} if tones else {})}
		for word in keywords.get(toneless.replace(VS16, ""), []):
			if word not in item["k"]:
				item["k"].append(word)
	result = []
	for item in items.values():
		# The neutral form comes first; it is what the list shows when no gender is chosen.
		variants = item["v"]
		item["v"] = dict(sorted(variants.items(), key=lambda pair: (pair[0] != "", pair[0])))
		result.append(item)
	return result


ACCENTS = {
	"GRAVE": "aksen rendah",
	"ACUTE": "aksen tirus",
	"DOUBLE ACUTE": "aksen tirus ganda",
	"CIRCUMFLEX": "sirkumfleks",
	"TILDE": "tilde",
	"DIAERESIS": "trema",
	"RING ABOVE": "cincin di atas",
	"CEDILLA": "sedila",
	"STROKE": "coretan",
	"MACRON": "makron",
	"BREVE": "lengkung",
	"OGONEK": "ogonek",
	"DOT ABOVE": "titik di atas",
	"CARON": "karon",
	"MIDDLE DOT": "titik tengah",
}
SPECIAL_LATIN = {
	"SHARP S": "eszet",
	"AE": "AE ligatur",
	"ETH": "eth",
	"THORN": "thorn",
	"DOTLESS I": "i tanpa titik",
	"ENG": "eng",
	"KRA": "kra",
	"LONG S": "s panjang",
}
GREEK = {
	"ALPHA": "alfa",
	"BETA": "beta",
	"GAMMA": "gama",
	"DELTA": "delta",
	"EPSILON": "epsilon",
	"ZETA": "zeta",
	"ETA": "eta",
	"THETA": "teta",
	"IOTA": "iota",
	"KAPPA": "kapa",
	"LAMDA": "lambda",
	"MU": "mu",
	"NU": "nu",
	"XI": "ksi",
	"OMICRON": "omikron",
	"PI": "pi",
	"RHO": "rho",
	"SIGMA": "sigma",
	"FINAL SIGMA": "sigma akhir",
	"TAU": "tau",
	"UPSILON": "upsilon",
	"PHI": "fi",
	"CHI": "khi",
	"PSI": "psi",
	"OMEGA": "omega",
}


def latinName(char: str) -> str | None:
	name = unicodedata.name(char, "")
	for prefix, case in (("LATIN CAPITAL LETTER ", "kapital"), ("LATIN SMALL LETTER ", "kecil")):
		if not name.startswith(prefix):
			continue
		rest = name[len(prefix) :]
		if rest in SPECIAL_LATIN:
			return f"{SPECIAL_LATIN[rest]} {case}"
		if rest.startswith("LIGATURE OE"):
			return f"OE ligatur {case}"
		letter, _, accent = rest.partition(" WITH ")
		if len(letter) == 1 and accent in ACCENTS:
			return f"{letter.lower() if case == 'kecil' else letter} {case} dengan {ACCENTS[accent]}"
	return None


def greekName(char: str) -> str | None:
	name = unicodedata.name(char, "")
	for prefix, case in (("GREEK CAPITAL LETTER ", "kapital"), ("GREEK SMALL LETTER ", "kecil")):
		if name.startswith(prefix) and name[len(prefix) :] in GREEK:
			return f"huruf Yunani {GREEK[name[len(prefix) :]]} {case}"
	return None


def symbolCategory(char: str) -> str:
	codepoint = ord(char)
	category = unicodedata.category(char)
	if category == "Sc" or char == "¤":
		return "currency"
	if (
		category == "Sm"
		or 0x2200 <= codepoint <= 0x22FF
		or 0x2A00 <= codepoint <= 0x2AFF
		or 0x2070 <= codepoint <= 0x209F
		or char in "¹²³¼½¾"
		or 0x2150 <= codepoint <= 0x215F
		or 0x2100 <= codepoint <= 0x214F
		or 0x1D400 <= codepoint <= 0x1D7FF
	):
		return "math"
	if (
		0x2190 <= codepoint <= 0x21FF
		or 0x25A0 <= codepoint <= 0x25FF
		or 0x27F0 <= codepoint <= 0x27FF
		or 0x2900 <= codepoint <= 0x297F
		or 0x2B00 <= codepoint <= 0x2BFF
		or 0x1F800 <= codepoint <= 0x1F8FF
	):
		return "geometric"
	if category.startswith("P"):
		return "punctuation"
	return "supplemental"


def readSymbolDictionary(emojiSequences: set[str]) -> list[dict]:
	symbols = []
	for line in SYMBOL_DICTIONARY.read_text(encoding="utf-8-sig").splitlines():
		if not line or line.startswith("#") or "\t" not in line:
			continue
		identifier, name = line.split("\t")[:2]
		if identifier.startswith("\\"):
			continue  # Escaped identifiers are control characters, spaces or # and \.
		if len(identifier) != 1 or identifier in emojiSequences:
			continue
		category = unicodedata.category(identifier)
		if category[0] in "CZ" or 0x2800 <= ord(identifier) <= 0x28FF:
			continue  # Invisible characters and braille cells are not offered for insertion.
		symbols.append({"c": identifier, "n": name, "cat": symbolCategory(identifier)})
	for char in ("#", "\\"):
		symbols.append(
			{"c": char, "n": "tanda pagar" if char == "#" else "garis miring terbalik", "cat": "punctuation"}
		)
	for codepoint in list(range(0x00C0, 0x0180)):
		char = chr(codepoint)
		name = latinName(char)
		if name:
			symbols.append({"c": char, "n": name, "cat": "latin"})
	for codepoint in range(0x0391, 0x03CA):
		char = chr(codepoint)
		name = greekName(char)
		if name:
			symbols.append({"c": char, "n": name, "cat": "language"})
	return symbols


def readKaomoji() -> list[dict]:
	result = []
	for line in KAOMOJI.read_text(encoding="utf-8").splitlines():
		if not line.strip() or line.startswith("# "):
			continue
		category, kaomoji, name = line.split("\t")
		result.append({"c": kaomoji, "n": name, "cat": category})
	return result


def main() -> None:
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	parser.add_argument("--emoji-version", default="17.0.0")
	parser.add_argument("--cldr-version", default="48.2.0")
	args = parser.parse_args()
	entries = parseEmojiTest(fetch(EMOJI_TEST_URL.format(version=args.emoji_version)))
	annotations = json.loads(fetch(CLDR_ANNOTATIONS_URL.format(version=args.cldr_version)))
	keywords = {
		emoji.replace(VS16, ""): info.get("default", [])
		for emoji, info in annotations["annotations"]["annotations"].items()
	}
	emoji = buildEmoji(entries, keywords)
	emojiSequences = {sequence.replace(VS16, "") for sequence, _group, _subgroup in entries}
	data = {
		"version": {"emoji": args.emoji_version, "cldr": args.cldr_version},
		"emoji": emoji,
		"symbols": readSymbolDictionary(emojiSequences),
		"kaomoji": readKaomoji(),
	}
	OUTPUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
	print(
		f"Wrote {OUTPUT} with {len(emoji)} emoji, {len(data['symbols'])} symbols "
		f"and {len(data['kaomoji'])} kaomoji ({OUTPUT.stat().st_size:,} bytes)."
	)


if __name__ == "__main__":
	main()
