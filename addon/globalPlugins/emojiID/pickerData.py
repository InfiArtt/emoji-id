# Emoji ID - Indonesian Emoji Reader for NVDA
# Copyright (C) 2026 Rexya Muhamad <rexya2017@gmail.com>
# This file is covered by the GNU General Public License v2 or later.
# See the file LICENSE for more details.

"""Data and search for the insert emoji dialog, without any user interface.

``data/picker.json`` is built by ``tools/build_picker_data.py``.
"""

import json
import os
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field

from .emojiData import cleanNameSymbols

KIND_EMOJI = "emoji"
KIND_SYMBOL = "symbols"
KIND_KAOMOJI = "kaomoji"
KINDS = (KIND_EMOJI, KIND_SYMBOL, KIND_KAOMOJI)

GENDER_NEUTRAL = ""
GENDER_MALE = "pria"
GENDER_FEMALE = "wanita"
GENDERS = (GENDER_NEUTRAL, GENDER_MALE, GENDER_FEMALE)
_FACING_RIGHT = "kanan"

#: Number of skin tones: 0 means no tone, 1 to 5 are light to dark.
TONE_COUNT = 6
_VS16 = chr(0xFE0F)


@dataclass
class EmojiItem:
	"""One emoji as listed in the dialog, with all its official variants."""

	variants: dict[str, dict]
	category: str
	subgroup: str
	keywords: list[str]

	@property
	def base(self) -> str:
		return next(iter(self.variants.values()))["s"]

	def genders(self) -> list[str]:
		"""The genders this emoji exists in, neutral first."""
		found = {key.split("|")[0] if key.split("|")[0] != _FACING_RIGHT else "" for key in self.variants}
		return [gender for gender in GENDERS if gender in found]

	def canFaceRight(self) -> bool:
		return any(_FACING_RIGHT in key.split("|") for key in self.variants)

	def _variant(self, gender: str, isFacingRight: bool) -> dict:
		key = "|".join(part for part in (gender, _FACING_RIGHT if isFacingRight else "") if part)
		if key in self.variants:
			return self.variants[key]
		without = gender if gender in self.variants else ""
		return self.variants.get(without, next(iter(self.variants.values())))

	def toneSlots(self, gender: str = GENDER_NEUTRAL, isFacingRight: bool = False) -> int:
		"""How many people in this emoji can get their own skin tone: 0, 1 or 2."""
		tones = self._variant(gender, isFacingRight).get("t", {})
		if not tones:
			return 0
		return 2 if any("," in key for key in tones) else 1

	def resolve(
		self,
		gender: str = GENDER_NEUTRAL,
		isFacingRight: bool = False,
		tone: int = 0,
		secondTone: int = 0,
	) -> str:
		"""Return the emoji text for the chosen gender, direction and skin tones.

		:param tone: Skin tone of the (first) person, 0 for none.
		:param secondTone: Skin tone of the second person, 0 for the same as the first.
		"""
		variant = self._variant(gender, isFacingRight)
		tones = variant.get("t", {})
		if not tone or not tones:
			return variant["s"]
		second = secondTone or tone
		pair = f"{tone},{second}"
		if pair in tones:
			return tones[pair]
		# One person, or two people with the same tone written as a single tone (such as 🤝🏽).
		hasPairs = any("," in key for key in tones)
		if str(tone) in tones and (second == tone or not hasPairs):
			return tones[str(tone)]
		return variant["s"]


@dataclass
class Entry:
	"""A row in the results list: the text to insert, its spoken name, and its emoji item if any."""

	text: str
	name: str
	kind: str
	category: str = ""
	subgroup: str = ""
	keywords: list[str] = field(default_factory=list)
	item: EmojiItem | None = None


@dataclass
class PickerData:
	emoji: list[EmojiItem]
	symbols: list[Entry]
	kaomoji: list[Entry]


def loadPickerData(path: str | None = None) -> PickerData:
	"""Read ``data/picker.json``."""
	if path is None:
		path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "picker.json")
	with open(path, encoding="utf-8") as file:
		raw = json.load(file)
	emoji = [
		EmojiItem(variants=item["v"], category=item["c"], subgroup=item["sg"], keywords=item["k"])
		for item in raw["emoji"]
	]
	symbols = [Entry(entry["c"], entry["n"], KIND_SYMBOL, entry["cat"]) for entry in raw["symbols"]]
	kaomoji = [Entry(entry["c"], entry["n"], KIND_KAOMOJI, entry["cat"]) for entry in raw["kaomoji"]]
	return PickerData(emoji=emoji, symbols=symbols, kaomoji=kaomoji)


def encodeText(text: str) -> str:
	"""Encode text as code points, such as "1F44D-1F3FD", so that it can be stored in NVDA's settings."""
	return "-".join(f"{ord(ch):X}" for ch in text)


def decodeText(encoded: str) -> str:
	try:
		return "".join(chr(int(part, 16)) for part in encoded.split("-") if part)
	except ValueError:
		return ""


def addToHistory(history: list[str], text: str, limit: int | None = None) -> list[str]:
	"""Return ``history`` with ``text`` moved to the front, keeping at most ``limit`` items."""
	encoded = encodeText(text)
	updated = [encoded] + [item for item in history if item != encoded]
	return updated[:limit] if limit else updated


def normalizeForSearch(text: str) -> str:
	return " ".join(text.lower().replace("-", " ").split())


def search(entries: Iterable[Entry], query: str) -> list[Entry]:
	"""Find entries whose name or keywords contain every word of ``query``.

	Names that start with the query come first, then names that contain it, then keyword matches.
	"""
	wanted = normalizeForSearch(query)
	if not wanted:
		return list(entries)
	words = wanted.split()
	ranked: list[tuple[int, int, Entry]] = []
	for index, entry in enumerate(entries):
		name = normalizeForSearch(entry.name)
		keywords = normalizeForSearch(" ".join(entry.keywords))
		if name.startswith(wanted):
			rank = 0
		elif wanted in name:
			rank = 1
		elif all(word in name or word in keywords for word in words):
			rank = 2
		else:
			continue
		ranked.append((rank, index, entry))
	return [entry for _rank, _index, entry in sorted(ranked, key=lambda row: (row[0], row[1]))]


def emojiEntries(
	data: PickerData,
	nameOf: Callable[[str], str | None],
	gender: str = GENDER_NEUTRAL,
	isFacingRight: bool = False,
	tone: int = 0,
	secondTone: int = 0,
) -> list[Entry]:
	"""Make list rows for all emoji, resolved for the chosen gender, direction and skin tones."""
	entries = []
	for item in data.emoji:
		text = item.resolve(gender, isFacingRight, tone, secondTone)
		name = nameOf(text) or nameOf(item.base) or text
		entries.append(
			Entry(
				text=text,
				name=cleanNameSymbols(name),
				kind=KIND_EMOJI,
				category=item.category,
				subgroup=item.subgroup,
				keywords=item.keywords,
				item=item,
			)
		)
	return entries


def entriesFromHistory(
	history: Iterable[str], allEntries: Iterable[Entry], nameOf: Callable[[str], str | None]
) -> list[Entry]:
	"""Rows for stored recent or favorite texts, in stored order."""
	byText = {entry.text.replace(_VS16, ""): entry for entry in allEntries}
	rows = []
	for encoded in history:
		text = decodeText(encoded)
		if not text:
			continue
		known = byText.get(text.replace(_VS16, ""))
		if known is not None:
			rows.append(
				Entry(
					text, known.name, known.kind, known.category, known.subgroup, known.keywords, known.item
				)
			)
		else:
			rows.append(Entry(text, cleanNameSymbols(nameOf(text) or text), KIND_EMOJI))
	return rows
