# -*- coding: UTF-8 -*-
# Emoji ID - Indonesian Emoji Reader for NVDA
# Copyright (C) 2026 Rexya Muhamad <rexya2017@gmail.com>
# This file is covered by the GNU General Public License v2 or later.
# See the file LICENSE for more details.

"""Emoji data loading and matching engine.

Loads a pre-built JSON file of emoji -> Indonesian name mappings and provides
a high-performance matcher that handles:
- Multi-codepoint sequences (ZWJ, skin tones, flags, keycaps)
- U+FE0F normalization (variation selector stripping)
- Longest-match-first semantics via compiled regex
- Thread-safe cached lookups
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

log = logging.getLogger(__name__)

# Variation selectors to strip when normalizing emoji for lookup
_VS_PATTERN = re.compile("[\uFE0E\uFE0F]")

# Skin tone modifier codepoints (Fitzpatrick scale)
SKIN_TONE_MODIFIERS = {
    "\U0001F3FB": "kulit putih",
    "\U0001F3FC": "kulit putih-sawo matang",
    "\U0001F3FD": "kulit sawo matang",
    "\U0001F3FE": "kulit cokelat",
    "\U0001F3FF": "kulit gelap",
}

# Range of emoji codepoints for quick pre-check
# This helps skip the regex for strings that cannot contain emoji
_EMOJI_QUICK_CHECK = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # Emoticons
    "\U0001F300-\U0001F5FF"  # Misc Symbols and Pictographs
    "\U0001F680-\U0001F6FF"  # Transport and Map
    "\U0001F700-\U0001F77F"  # Alchemical Symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "\U0000FE00-\U0000FE0F"  # Variation Selectors
    "\U0000200D"             # ZWJ
    "\U000020E3"             # Combining Enclosing Keycap
    "\U00002600-\U000026FF"  # Misc symbols
    "\U00002300-\U000023FF"  # Misc Technical
    "\U0000231A-\U0000231B"  # Watch, Hourglass
    "\U00002934-\U00002935"  # Arrows
    "\U000025AA-\U000025AB"  # Squares
    "\U000025B6\U000025C0"   # Play buttons
    "\U000025FB-\U000025FE"  # Squares
    "\U00002B05-\U00002B07"  # Arrows
    "\U00002B1B-\U00002B1C"  # Squares
    "\U00002B50\U00002B55"   # Star, Circle
    "\U00003030\U0000303D"   # Wavy dash, part alternation mark
    "\U00003297\U00003299"   # Circled Ideograph
    "\U0001F1E0-\U0001F1FF"  # Regional indicators (flags)
    "\U000000A9\U000000AE"   # Copyright, Registered
    "\U0000203C\U00002049"   # Exclamation marks
    "#*0-9"                  # Keycap bases
    "]"
)


class EmojiMatcher:
    """High-performance emoji matcher using compiled regex.

    Loads emoji data from a JSON file and builds a regex pattern that matches
    emoji sequences in text, longest-first. The regex approach ensures O(n)
    matching across the input text.
    """

    def __init__(self) -> None:
        self._data: dict[str, str] = {}
        self._pattern: re.Pattern | None = None
        self._loaded = False

    @property
    def loaded(self) -> bool:
        """Whether emoji data has been loaded successfully."""
        return self._loaded

    @property
    def count(self) -> int:
        """Number of emoji entries loaded."""
        return len(self._data)

    def load(self, data_path: str | os.PathLike | None = None) -> bool:
        """Load emoji data from JSON file.

        Args:
            data_path: Path to emoji_id.json. If None, uses the default
                       location in the data/ subdirectory.

        Returns:
            True if data was loaded successfully, False otherwise.
        """
        if data_path is None:
            data_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "data",
                "emoji_id.json",
            )

        try:
            with open(data_path, encoding="utf-8-sig") as f:
                raw = json.load(f)

            emoji_map = raw.get("data", {})
            if not emoji_map:
                log.error("Emoji data file is empty or has no 'data' key: %s", data_path)
                return False

            self._data = emoji_map
            self._build_pattern()
            self._loaded = True
            log.info(
                "Emoji ID: loaded %d emoji entries from %s (CLDR %s)",
                len(self._data),
                data_path,
                raw.get("version", "unknown"),
            )
            return True

        except FileNotFoundError:
            log.error("Emoji data file not found: %s", data_path)
        except json.JSONDecodeError as e:
            log.error("Emoji data file is not valid JSON: %s (%s)", data_path, e)
        except Exception:
            log.error("Failed to load emoji data from %s", data_path, exc_info=True)

        return False

    def _build_pattern(self) -> None:
        """Build compiled regex pattern from loaded data.

        Keys are sorted by length descending to ensure longest-match-first
        semantics. Each key is escaped for regex safety.
        """
        if not self._data:
            self._pattern = None
            return

        # Sort by length descending, then lexicographically for determinism
        sorted_keys = sorted(self._data.keys(), key=lambda k: (-len(k), k))

        # Escape each emoji string for regex and join with alternation.
        # We also need to match the emoji with optional FE0F between components,
        # since text may contain FE0F even though our keys don't.
        alternatives = []
        for key in sorted_keys:
            # Build a pattern that optionally matches FE0F after each character
            # This handles the case where input text has FE0F but our keys don't
            chars = list(key)
            pattern_parts = []
            for i, ch in enumerate(chars):
                pattern_parts.append(re.escape(ch))
                # Allow optional FE0F/FE0E after each character except the last
                # (variation selectors can appear after any base character)
                if i < len(chars) - 1:
                    pattern_parts.append("[\uFE0E\uFE0F]?")
            # Also allow trailing FE0F
            pattern_parts.append("[\uFE0E\uFE0F]?")
            alternatives.append("".join(pattern_parts))

        pattern_str = "|".join(alternatives)
        self._pattern = re.compile(pattern_str)

    def lookup(self, emoji: str) -> str | None:
        """Look up the Indonesian name for a single emoji.

        Args:
            emoji: The emoji character or sequence to look up.

        Returns:
            The Indonesian name, or None if not found.
        """
        if not self._loaded:
            return None

        # Normalize: strip variation selectors for lookup
        normalized = _VS_PATTERN.sub("", emoji)
        name = self._data.get(normalized)

        if name is None and normalized != emoji:
            # Try the original (with VS) just in case
            name = self._data.get(emoji)

        return name

    @staticmethod
    def clean_name_symbols(name: str) -> str:
        """Sanitize symbols (hyphens, parentheses, etc.) in emoji names for speech.

        - Converts word-connecting hyphens to spaces (e.g. 'kupu-kupu' -> 'kupu kupu')
        - Removes parentheses cleanly (e.g. 'menunjuk ke atas (dibalik)' -> 'menunjuk ke atas dibalik')
        - Removes double quotes (e.g. 'tombol "rahasia"' -> 'tombol rahasia')
        - Replaces '&' with 'dan' (e.g. '& Kep.' -> 'dan Kep.')
        - Collapses consecutive whitespace
        """
        if not name:
            return name

        s = re.sub(r"(\w+)-(\w+)", r"\1 \2", name)
        s = s.replace("-", " ")
        s = s.replace("(", " ").replace(")", " ")
        s = s.replace('"', "")
        s = s.replace("&", " dan ")
        return re.sub(r"\s+", " ", s).strip()

    def lookup_single_char(self, char: str, clean_symbols: bool = True) -> str | None:
        """Look up a single character, optimized for the character navigation path.

        Args:
            char: A single character (may be a surrogate pair in terms of
                  Python string, but len() == 1).
            clean_symbols: If True, remove hyphens and parentheses for clean speech.

        Returns:
            The Indonesian name, or None if not found.
        """
        if not self._loaded or not char:
            return None

        normalized = _VS_PATTERN.sub("", char)
        name = self._data.get(normalized)
        if name and clean_symbols:
            name = self.clean_name_symbols(name)
        return name

    def replace_in_text(
        self,
        text: str,
        *,
        prefix: str = "",
        prefix_once: bool = False,
        collapse_repeated: bool = False,
        skin_tone_detail: bool = True,
        clean_symbols: bool = True,
    ) -> str:
        """Replace all emoji in text with their Indonesian names.

        Args:
            text: Input text that may contain emoji.
            prefix: Prefix word to add before emoji names (e.g. "emoji").
            prefix_once: If True, only add prefix before the first emoji
                        in a consecutive run.
            collapse_repeated: If True, collapse consecutive identical emoji
                              into "N kali <name>".
            skin_tone_detail: If True, include skin tone descriptions.
            clean_symbols: If True, remove hyphens and parentheses from emoji
                          names for smooth speech.

        Returns:
            Text with emoji replaced by Indonesian names.
        """
        if not self._loaded or not self._pattern:
            return text

        # Quick pre-check: if no emoji-like characters, skip regex
        if not _EMOJI_QUICK_CHECK.search(text):
            return text

        result_parts: list[str] = []
        last_end = 0
        current_name: str | None = None
        current_count = 0
        in_emoji_run = False

        def flush_emoji(name: str | None, count: int) -> None:
            nonlocal in_emoji_run
            if not name or count <= 0:
                return

            # Determine prefix for this output
            use_prefix = bool(prefix)
            if prefix and prefix_once and in_emoji_run:
                use_prefix = False

            if collapse_repeated and count > 1:
                item_text = f"{count} kali {name}"
            else:
                item_text = " ".join([name] * count)

            if use_prefix:
                formatted = f"{prefix} {item_text}"
            else:
                formatted = item_text

            # Ensure separation from adjacent text or emojis
            if result_parts and not result_parts[-1].endswith((" ", "\t", "\n")):
                result_parts.append(" ")
            result_parts.append(formatted)
            in_emoji_run = True

        for match in self._pattern.finditer(text):
            start, end = match.span()
            matched = match.group()
            normalized = _VS_PATTERN.sub("", matched)
            name = self._data.get(normalized)

            if name is None:
                name = self._build_fallback_name(normalized, skin_tone_detail)

            if name is None:
                # Unrecognized emoji: flush current, append raw text, break emoji run
                if current_name is not None:
                    flush_emoji(current_name, current_count)
                    current_name = None
                    current_count = 0
                if start > last_end:
                    result_parts.append(text[last_end:start])
                result_parts.append(matched)
                in_emoji_run = False
                last_end = end
                continue

            if not skin_tone_detail:
                name = self._strip_skin_tone(name)

            if clean_symbols:
                name = self.clean_name_symbols(name)

            between_text = text[last_end:start] if start > last_end else ""
            has_words = bool(re.search(r"\w", between_text)) if between_text else False

            if has_words:
                # Real words between emojis: flush current and break run
                if current_name is not None:
                    flush_emoji(current_name, current_count)
                    current_name = None
                    current_count = 0
                result_parts.append(between_text)
                in_emoji_run = False
                current_name = name
                current_count = 1
            elif collapse_repeated and name == current_name:
                # Same emoji separated only by whitespace or separator punctuation: collapse
                current_count += 1
            else:
                # Different emoji or collapse off: flush previous
                if current_name is not None:
                    flush_emoji(current_name, current_count)
                if between_text:
                    result_parts.append(between_text)
                    # Note: in_emoji_run remains True because has_words is False!
                current_name = name
                current_count = 1

            last_end = end

        if current_name is not None:
            flush_emoji(current_name, current_count)

        if last_end < len(text):
            result_parts.append(text[last_end:])

        return "".join(result_parts)

    def _build_fallback_name(self, emoji: str, skin_tone_detail: bool) -> str | None:
        """Try to build a name from emoji components.

        For example, for an emoji with a skin tone modifier, try looking up
        the base emoji and appending the skin tone name.

        Args:
            emoji: Normalized emoji string (no VS).
            skin_tone_detail: Whether to include skin tone in the name.

        Returns:
            A constructed Indonesian name, or None if we can't build one.
        """
        if len(emoji) < 2:
            return None

        # Check for skin tone modifier
        for modifier, tone_name in SKIN_TONE_MODIFIERS.items():
            if modifier in emoji:
                base = emoji.replace(modifier, "")
                base_name = self._data.get(base)
                if base_name:
                    if skin_tone_detail:
                        return f"{base_name}: {tone_name}"
                    return base_name

        # Check for ZWJ sequences: try splitting on ZWJ
        if "\u200D" in emoji:
            parts = emoji.split("\u200D")
            part_names = []
            for part in parts:
                part_name = self._data.get(part)
                if part_name:
                    part_names.append(part_name)
            if part_names:
                return ", ".join(part_names)

        return None

    def _strip_skin_tone(self, name: str) -> str:
        """Remove skin tone suffix from an emoji name."""
        for pattern in (": warna kulit ", " warna kulit ", ": kulit ", " kulit "):
            if pattern in name:
                return name.split(pattern)[0]
        return name

    def is_emoji(self, char: str) -> bool:
        """Quick check if a character could be an emoji.

        This is a fast pre-filter, not a definitive check.
        """
        if not char:
            return False
        cp = ord(char[0])
        return (
            0x1F600 <= cp <= 0x1F64F  # Emoticons
            or 0x1F300 <= cp <= 0x1F5FF  # Misc Symbols
            or 0x1F680 <= cp <= 0x1F6FF  # Transport
            or 0x1F900 <= cp <= 0x1F9FF  # Supplemental Symbols
            or 0x1FA70 <= cp <= 0x1FAFF  # Extended-A
            or 0x2600 <= cp <= 0x27BF  # Misc symbols + Dingbats
            or 0x1F1E0 <= cp <= 0x1F1FF  # Regional indicators
            or 0xFE00 <= cp <= 0xFE0F  # Variation selectors
            or 0x200D == cp  # ZWJ
            or 0x20E3 == cp  # Keycap
            or cp in (0xA9, 0xAE, 0x203C, 0x2049)  # Special symbols
        )
