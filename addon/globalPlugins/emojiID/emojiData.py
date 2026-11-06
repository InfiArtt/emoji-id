# Emoji ID - Indonesian Emoji Reader for NVDA
# Copyright (C) 2026 Rexya Muhamad <rexya2017@gmail.com>
# This file is covered by the GNU General Public License v2 or later.
# See the file LICENSE for more details.

"""Emoji data loading and matching.

Loads a pre-built JSON file that maps emoji to Indonesian names, and replaces emoji in text.
Handles multi-codepoint sequences (ZWJ, skin tones, flags, keycaps) and ignores variation selectors.
Longer sequences always win over their components.
"""

import json
import os
import re

from logHandler import log

#: Variation selectors are ignored when looking up emoji.
_VARIATION_SELECTORS = f"[{chr(0xFE0E)}{chr(0xFE0F)}]"
_VS_PATTERN = re.compile(_VARIATION_SELECTORS)
_OPTIONAL_VS = _VARIATION_SELECTORS + "?"

ZWJ = chr(0x200D)
KEYCAP = chr(0x20E3)

#: Regional indicators are the letters that flags are made of: I plus D is the flag of Indonesia.
REGIONAL_INDICATOR_A = 0x1F1E6
REGIONAL_INDICATOR_Z = 0x1F1FF

#: Skin tone modifier codepoints (Fitzpatrick scale) and their Indonesian CLDR names.
SKIN_TONE_MODIFIERS: dict[str, str] = {
	chr(0x1F3FB): "warna kulit cerah",
	chr(0x1F3FC): "warna kulit cerah-sedang",
	chr(0x1F3FD): "warna kulit sedang",
	chr(0x1F3FE): "warna kulit gelap-sedang",
	chr(0x1F3FF): "warna kulit gelap",
}

#: Name suffixes that describe a skin tone, removed when skin tone detail is off.
_SKIN_TONE_SEPARATORS = (": warna kulit ", " warna kulit ", ": kulit ", " kulit ")

#: Codepoint ranges that can start or belong to an emoji.
#: Keycap sequences always contain U+20E3, so plain digits, "#" and "*" are not listed.
_EMOJI_RANGES: tuple[tuple[int, int], ...] = (
	(0x1F000, 0x1FAFF),  # Emoji and pictograph blocks, regional indicators, skin tones
	(0x2190, 0x21FF),  # Arrows
	(0x2300, 0x23FF),  # Misc Technical
	(0x2460, 0x24FF),  # Enclosed Alphanumerics
	(0x25A0, 0x27BF),  # Geometric shapes, misc symbols, dingbats
	(0x2900, 0x297F),  # Supplemental Arrows-B
	(0x2B00, 0x2BFF),  # Misc Symbols and Arrows
)
_EMOJI_SINGLES: tuple[int, ...] = (
	0x3030, 0x303D, 0x3297, 0x3299,  # Wavy dash, part alternation mark, circled ideographs
	0x00A9, 0x00AE, 0x203C, 0x2049, 0x2122, 0x2139,  # Copyright, registered, exclamation marks, TM, info
	0x200D, 0x20E3, 0xFE0F,  # ZWJ, keycap, emoji presentation selector
)  # fmt: skip

#: Cheap pre-check so that text without any emoji-like character skips the large regex.
_EMOJI_QUICK_CHECK = re.compile(
	"["
	+ "".join(f"{re.escape(chr(first))}-{re.escape(chr(last))}" for first, last in _EMOJI_RANGES)
	+ "".join(re.escape(chr(codepoint)) for codepoint in _EMOJI_SINGLES)
	+ "]"
)


def isRegionalIndicator(char: str) -> bool:
	"""Whether the character is a single regional indicator letter."""
	return len(char) == 1 and REGIONAL_INDICATOR_A <= ord(char) <= REGIONAL_INDICATOR_Z


def getRegionalIndicatorName(char: str) -> str:
	"""Name a single regional indicator by its letter, for example "huruf regional I".

	Character navigation splits a flag into its two regional indicators.
	Neither NVDA nor CLDR has a name for a lone regional indicator, so without this
	the synthesizer receives a character it cannot speak and stays silent.
	"""
	letter = chr(ord("A") + ord(char) - REGIONAL_INDICATOR_A)
	return f"huruf regional {letter}"


def _joinWithSpace(match: re.Match[str]) -> str:
	return f"{match.group(1)} {match.group(2)}"


def cleanNameSymbols(name: str) -> str:
	"""Remove punctuation from an emoji name so that synthesizers do not speak it.

	Hyphens become spaces ("kupu-kupu" becomes "kupu kupu"), parentheses and double quotes are removed,
	and "&" becomes "dan".

	:param name: The emoji name.
	:return: The cleaned name.
	"""
	if not name:
		return name
	cleaned = re.sub(r"(\w+)-(\w+)", _joinWithSpace, name)
	cleaned = cleaned.replace("-", " ").replace("(", " ").replace(")", " ")
	cleaned = cleaned.replace('"', "").replace("&", " dan ")
	return re.sub(r"\s+", " ", cleaned).strip()


def stripSkinTone(name: str) -> str:
	"""Remove the skin tone description from an emoji name.

	:param name: The emoji name, possibly ending with a skin tone description.
	:return: The name without the skin tone description.
	"""
	for separator in _SKIN_TONE_SEPARATORS:
		if separator in name:
			return name.split(separator)[0]
	return name


class EmojiMatcher:
	"""Finds emoji in text and replaces them with Indonesian names."""

	def __init__(self) -> None:
		self._data: dict[str, str] = {}
		self._pattern: re.Pattern[str] | None = None

	@property
	def isLoaded(self) -> bool:
		"""Whether emoji data has been loaded."""
		return self._pattern is not None

	@property
	def count(self) -> int:
		"""Number of loaded emoji entries."""
		return len(self._data)

	def load(self, dataPath: str | None = None) -> bool:
		"""Load emoji data from a JSON file.

		:param dataPath: Path to the JSON file. Defaults to ``data/emoji_id.json`` next to this module.
		:return: ``True`` if the data was loaded.
		"""
		if dataPath is None:
			dataPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "emoji_id.json")
		try:
			with open(dataPath, encoding="utf-8-sig") as dataFile:
				raw = json.load(dataFile)
		except (OSError, ValueError):
			log.error(f"Emoji ID: could not read emoji data from {dataPath}", exc_info=True)
			return False

		emojiMap: dict[str, str] = raw.get("data", {})
		if not emojiMap:
			log.error(f"Emoji ID: emoji data file has no entries: {dataPath}")
			return False

		self._data = emojiMap
		self._pattern = self._buildPattern(emojiMap)
		log.info(
			f"Emoji ID: loaded {len(emojiMap)} emoji entries (CLDR {raw.get('version', 'unknown')})",
		)
		return True

	@staticmethod
	def _buildPattern(emojiMap: dict[str, str]) -> re.Pattern[str]:
		"""Build one regex that matches every known emoji, longest sequences first.

		Data keys have no variation selectors, but text often does,
		so an optional selector is allowed after every character.
		"""
		sortedKeys = sorted(emojiMap, key=lambda k: (-len(k), k))
		alternatives = [_OPTIONAL_VS.join(re.escape(ch) for ch in key) + _OPTIONAL_VS for key in sortedKeys]
		# Lone regional indicators come last, so that complete flags always match first.
		alternatives.append(f"[{chr(REGIONAL_INDICATOR_A)}-{chr(REGIONAL_INDICATOR_Z)}]")
		return re.compile("|".join(alternatives))

	def lookup(self, emoji: str) -> str | None:
		"""Look up the Indonesian name of one emoji or emoji sequence.

		:param emoji: The emoji, with or without variation selectors.
		:return: The Indonesian name, or ``None`` if unknown.
		"""
		name = self._data.get(_VS_PATTERN.sub("", emoji))
		if name is None:
			name = self._data.get(emoji)
		return name

	def lookupSingleChar(self, char: str, shouldCleanSymbols: bool = True) -> str | None:
		"""Look up a single character, as used by character navigation and typed character echo.

		:param char: The character.
		:param shouldCleanSymbols: Whether to remove punctuation from the name.
		:return: The Indonesian name, or ``None`` if the character is not a known emoji.
		"""
		if not self._data or not char:
			return None
		if isRegionalIndicator(char):
			return getRegionalIndicatorName(char)
		name = self._data.get(_VS_PATTERN.sub("", char))
		if name and shouldCleanSymbols:
			name = cleanNameSymbols(name)
		return name

	def replaceInText(
		self,
		text: str,
		*,
		prefix: str = "",
		isPrefixOnce: bool = False,
		shouldCollapseRepeated: bool = False,
		hasSkinToneDetail: bool = True,
		shouldCleanSymbols: bool = True,
	) -> str:
		"""Replace all emoji in text with their Indonesian names.

		:param text: Text that may contain emoji.
		:param prefix: Word spoken before each emoji name, such as "emoji". Empty for none.
		:param isPrefixOnce: Speak the prefix only before the first emoji of a run of emoji.
		:param shouldCollapseRepeated: Speak repeated identical emoji as a count and one name.
		:param hasSkinToneDetail: Include skin tone descriptions.
		:param shouldCleanSymbols: Remove punctuation from emoji names.
		:return: The text with emoji replaced.
		"""
		if self._pattern is None or not _EMOJI_QUICK_CHECK.search(text):
			return text

		resultParts: list[str] = []
		lastEnd = 0
		currentName: str | None = None
		currentCount = 0
		isInEmojiRun = False

		def flushEmoji() -> None:
			nonlocal isInEmojiRun
			if currentName is None or currentCount <= 0:
				return
			isCollapsed = shouldCollapseRepeated and currentCount > 1
			itemText = currentName if isCollapsed else " ".join([currentName] * currentCount)
			if prefix and not (isPrefixOnce and isInEmojiRun):
				itemText = f"{prefix} {itemText}"
			if isCollapsed:
				# The count comes first, as in "3 emoji bendera Indonesia".
				itemText = f"{currentCount} {itemText}"
			# Keep the name apart from adjacent text or emoji.
			if resultParts and not resultParts[-1].endswith((" ", "\t", "\n")):
				resultParts.append(" ")
			resultParts.append(itemText)
			isInEmojiRun = True

		for match in self._pattern.finditer(text):
			start, end = match.span()
			matched = match.group()
			normalized = _VS_PATTERN.sub("", matched)
			name = self._data.get(normalized)
			if name is None:
				name = self._buildFallbackName(normalized, hasSkinToneDetail)

			if name is None:
				# Unknown emoji, or half of a flag that was cut off by word or character navigation.
				# A lone regional indicator is spoken as its letter, without the emoji prefix.
				flushEmoji()
				currentName = None
				currentCount = 0
				before = text[lastEnd:start]
				if isRegionalIndicator(normalized):
					matched = getRegionalIndicatorName(normalized)
					previous = before or (resultParts[-1] if resultParts else "")
					if previous and not previous[-1].isspace():
						matched = " " + matched
					if end < len(text) and not text[end].isspace():
						matched += " "
				resultParts.append(before + matched)
				isInEmojiRun = False
				lastEnd = end
				continue

			if not hasSkinToneDetail:
				name = stripSkinTone(name)
			if shouldCleanSymbols:
				name = cleanNameSymbols(name)

			betweenText = text[lastEnd:start]
			if re.search(r"\w", betweenText):
				# Words between emoji end the run.
				flushEmoji()
				resultParts.append(betweenText)
				isInEmojiRun = False
				currentName = name
				currentCount = 1
			elif shouldCollapseRepeated and name == currentName:
				# Same emoji separated only by spaces or punctuation.
				currentCount += 1
			else:
				flushEmoji()
				# Spaces and punctuation between emoji keep the run going.
				if betweenText:
					resultParts.append(betweenText)
				currentName = name
				currentCount = 1
			lastEnd = end

		flushEmoji()
		if lastEnd < len(text):
			resultParts.append(text[lastEnd:])
		return "".join(resultParts)

	def _buildFallbackName(self, emoji: str, hasSkinToneDetail: bool) -> str | None:
		"""Build a name for an unknown sequence from its known parts.

		:param emoji: The sequence without variation selectors.
		:param hasSkinToneDetail: Whether to include the skin tone name.
		:return: The constructed name, or ``None`` if no part is known.
		"""
		if len(emoji) < 2:
			return None

		for modifier, toneName in SKIN_TONE_MODIFIERS.items():
			if modifier in emoji:
				baseName = self._data.get(emoji.replace(modifier, ""))
				if baseName:
					return f"{baseName} {toneName}" if hasSkinToneDetail else baseName

		if ZWJ in emoji:
			partNames = [name for part in emoji.split(ZWJ) if (name := self._data.get(part))]
			if partNames:
				return ", ".join(partNames)

		return None
