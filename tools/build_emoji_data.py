#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Build emoji data for Emoji ID NVDA add-on.

Downloads Unicode CLDR Indonesian emoji annotations (or extracts from NVDA's cldr.dic)
and merges with hand-maintained overrides to produce a compact JSON lookup file.

Usage:
    python tools/build_emoji_data.py
    python tools/build_emoji_data.py --cldr-version 48.2.0 --emoji-version 16.0
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

CLDR_ANNOTATIONS_URL = (
	"https://cdn.jsdelivr.net/npm/cldr-annotations-full@{version}/annotations/id/annotations.json"
)
CLDR_DERIVED_URL = (
	"https://cdn.jsdelivr.net/npm/cldr-annotations-derived-full@{version}/"
	"annotationsDerived/id/annotations.json"
)
EMOJI_TEST_URL = "https://unicode.org/Public/emoji/{version}/emoji-test.txt"

VS_PATTERN = re.compile(r"[\uFE0E\uFE0F]")

UNICODE_LICENSE = (
	"UNICODE LICENSE V3 - Copyright (c) 1991-2026 Unicode, Inc. "
	"Data from CLDR. See https://www.unicode.org/license for full license text."
)


def normalize_emoji(emoji: str) -> str:
	"""Strip variation selectors from emoji string for CLDR key normalization."""
	return VS_PATTERN.sub("", emoji)


def fetch_url(url: str) -> str:
	"""Download text from URL using standard library urllib."""
	req = urllib.request.Request(url, headers={"User-Agent": "Emoji-ID-BuildTool/1.0"})
	with urllib.request.urlopen(req, timeout=30) as resp:
		return resp.read().decode("utf-8")


def parse_annotations(data: dict) -> dict[str, str]:
	"""Extract emoji -> tts name mapping from CLDR annotation data."""
	result = {}
	root_key = "annotations" if "annotations" in data else "annotationsDerived"
	annotations = data.get(root_key, {}).get("annotations", {})
	for emoji, info in annotations.items():
		if "tts" in info and info["tts"]:
			name = info["tts"][0]
			normalized = normalize_emoji(emoji)
			result[normalized] = name
	return result


def load_overrides(path: Path) -> dict[str, str]:
	"""Load hand-maintained overrides from TSV file."""
	result = {}
	if not path.exists():
		print(f"Warning: overrides file not found: {path}")
		return result
	with open(path, encoding="utf-8") as f:
		for line_num, line in enumerate(f, 1):
			line = line.strip()
			if not line or line.startswith("#"):
				continue
			parts = line.split("\t")
			if len(parts) < 2:
				print(f"Warning: skipping malformed line {line_num}: {line!r}")
				continue
			emoji = normalize_emoji(parts[0].strip())
			name = parts[1].strip()
			if emoji and name:
				result[emoji] = name
	return result


def parse_cldr_dic(path: Path) -> dict[str, str]:
	"""Extract emoji definitions from NVDA's cldr.dic file if available."""
	result = {}
	if not path.exists():
		return result

	def is_emoji_str(s: str) -> bool:
		if "\u200d" in s or "\u20e3" in s:
			return True
		for ch in s:
			cp = ord(ch)
			if (
				0x1F1E6 <= cp <= 0x1F1FF
				or 0x1F300 <= cp <= 0x1FAFF
				or 0x2600 <= cp <= 0x27BF
				or cp in (0x00A9, 0x00AE, 0x203C, 0x2049, 0x2122, 0x2139, 0x231A, 0x231B, 0x2B50, 0x2B55)
			):
				return True
		return False

	with open(path, encoding="utf-8") as f:
		for line in f:
			if line.startswith("#") or line.strip() in ("symbols:", "complexSymbols:"):
				continue
			parts = line.split("\t")
			if len(parts) >= 2:
				sym = parts[0]
				rep = parts[1]
				if is_emoji_str(sym):
					norm = normalize_emoji(sym)
					if norm and rep:
						result[norm] = rep
	return result


def build_data(
	cldr_version: str,
	emoji_version: str,
	overrides_path: Path,
	output_path: Path,
	cldr_dic_path: Path | None = None,
) -> None:
	"""Main build pipeline."""
	merged = {}

	# Try downloading CLDR annotations online
	try:
		base_url = CLDR_ANNOTATIONS_URL.format(version=cldr_version)
		derived_url = CLDR_DERIVED_URL.format(version=cldr_version)
		print(f"Fetching base annotations from {base_url}...")
		base_data = json.loads(fetch_url(base_url))
		print(f"Fetching derived annotations from {derived_url}...")
		derived_data = json.loads(fetch_url(derived_url))

		base_names = parse_annotations(base_data)
		derived_names = parse_annotations(derived_data)
		merged.update(base_names)
		merged.update(derived_names)
		print(f"Loaded {len(base_names)} base and {len(derived_names)} derived annotations from CDN.")
	except Exception as e:
		print(f"Network download failed: {e}")
		if cldr_dic_path and cldr_dic_path.exists():
			print(f"Falling back to local NVDA cldr.dic at {cldr_dic_path}...")
			merged = parse_cldr_dic(cldr_dic_path)
			print(f"Loaded {len(merged)} emoji entries from cldr.dic.")
		else:
			print("Error: No data source available.")
			sys.exit(1)

	# Apply overrides
	overrides = load_overrides(overrides_path)
	override_count = 0
	for emoji, name in overrides.items():
		merged[emoji] = name
		override_count += 1
	print(f"Applied {override_count} overrides.")

	# Sort by key length descending, then by codepoint for determinism
	sorted_data = dict(sorted(merged.items(), key=lambda x: (-len(x[0]), x[0])))

	output = {
		"version": cldr_version,
		"emoji_version": emoji_version,
		"count": len(sorted_data),
		"license": UNICODE_LICENSE,
		"data": sorted_data,
	}

	output_path.parent.mkdir(parents=True, exist_ok=True)
	with open(output_path, "w", encoding="utf-8") as f:
		json.dump(output, f, ensure_ascii=False, separators=(",", ":"))

	print(
		f"Successfully generated {output_path} with {len(sorted_data)} entries "
		f"({output_path.stat().st_size:,} bytes)."
	)


def main():
	parser = argparse.ArgumentParser(description="Build emoji data for Emoji ID NVDA add-on")
	parser.add_argument("--cldr-version", default="48.2.0", help="CLDR version tag")
	parser.add_argument("--emoji-version", default="16.0", help="Unicode emoji version")
	parser.add_argument(
		"--output",
		type=Path,
		default=Path(__file__).resolve().parent.parent
		/ "addon"
		/ "globalPlugins"
		/ "emojiID"
		/ "data"
		/ "emoji_id.json",
	)
	parser.add_argument(
		"--overrides",
		type=Path,
		default=Path(__file__).resolve().parent / "overrides.tsv",
	)
	parser.add_argument(
		"--cldr-dic",
		type=Path,
		default=Path(r"C:\Program Files\NVDA\locale\id\cldr.dic"),
		help="Path to local NVDA cldr.dic as fallback",
	)
	args = parser.parse_args()
	build_data(args.cldr_version, args.emoji_version, args.overrides, args.output, args.cldr_dic)


if __name__ == "__main__":
	main()
