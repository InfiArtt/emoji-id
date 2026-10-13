# Emoji ID - Indonesian Emoji Reader for NVDA

Emoji ID is an NVDA add-on that reads all emoji symbols in Indonesian, regardless of the active speech synthesizer or TTS voice in use (such as an English Eloquence voice, OneCore, or Vocalizer).

This add-on is designed for blind and visually impaired users who want consistent Indonesian emoji announcements when reading documents, browsing the web, reading chat messages, or navigating character by character.

## Key Features

- **Indonesian Emoji Announcements**: Replaces thousands of emoji with natural Indonesian descriptions based on official Unicode CLDR data.
- **Comprehensive Emoji Support**: Supports standard emoji (faces, gestures, animals, objects), ZWJ sequences (families, professions), national flags (such as the Indonesian flag), digit keycaps, and skin tone modifiers (Fitzpatrick scale).
- **Single-Character Trap Solved**: Emoji are announced in Indonesian during continuous reading, Say All, arrow key navigation (by character), review cursor review, and typed character echo.
- **Repeated Emoji Collapsing**: Option to collapse consecutive identical emoji, e.g. three grinning faces are announced as "3 kali wajah gembira".
- **Customizable Prefix Word**: Option to announce a prefix such as "emoji" before the emoji description, either before every emoji or only once before consecutive runs.
- **Skin Tone Detail Toggle**: Users can choose whether to include skin tone descriptions or announce only the base emoji description.
- **Quick Toggle Command**: An unassigned NVDA script allows toggling the add-on on or off instantly without opening settings dialogs.
- **High Performance**: Compiled regex engine sorted longest-match first ensures zero noticeable latency on long text (benchmarked on 50,000 characters).

## Settings Panel

Open NVDA Menu -> Preferences -> Settings (NVDA+Control+G), then select the **Emoji ID** category:

1. **Enable Indonesian emoji reading**: Check to enable the add-on. When unchecked, NVDA reverts to default behavior.
2. **Add prefix word before emoji name**: Check to prepend a prefix word (default: enabled).
3. **Prefix word**: The prefix text spoken before emoji names (default: "emoji").
4. **Prefix word only once for consecutive emojis**: If checked, the prefix is spoken only before the first emoji in a run of consecutive emojis.
5. **Collapse repeated identical emojis**: If checked, identical consecutive emojis are collapsed into "N kali [emoji name]".
6. **Include skin tone details**: If checked, skin tone variations are announced. If unchecked, only base names are announced.
7. **Respect NVDA symbol level**: If checked, emoji are subject to NVDA's symbol level setting. If unchecked (default), emoji are always announced.

Settings are saved automatically per NVDA configuration profile.

## Assigning a Shortcut Key

This add-on provides an unassigned command to toggle the feature on and off:

1. Open NVDA Menu -> Preferences -> Input Gestures.
2. Expand the **Emoji ID** category.
3. Select **Aktifkan atau nonaktifkan pembacaan emoji dalam bahasa Indonesia**.
4. Press **Add** and press your desired shortcut key (for example NVDA+Shift+E).
5. Press Enter to save.

When pressed, NVDA announces the new status: "Emoji ID aktif" or "Emoji ID nonaktif".

## System Requirements

- NVDA 2026.1 or later.
- Architecture: 64-bit (NVDA Python 3.13 runtime).
- Works with any speech synthesizer (Eloquence, Windows OneCore, eSpeak NG, Vocalizer Expressive, SAPI5).

## License and Copyright

- Add-on License: GNU General Public License version 2 or later (GPL-2.0-or-later).
- Code Copyright: (c) 2024-2026 Emoji ID Contributors.

### Unicode CLDR License Notice (Unicode License v3)

Indonesian emoji annotation data is sourced from the Unicode Common Locale Data Repository (CLDR) project.

UNICODE LICENSE V3
COPYRIGHT AND PERMISSION NOTICE

Copyright (c) 1991-2026 Unicode, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of data files and any associated documentation (the "Data Files") or software and any associated documentation (the "Software") to deal in the Data Files or Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, and/or sell copies of the Data Files or Software, and to permit persons to whom the Data Files or Software are furnished to do so, provided that either (a) this copyright and permission notice appear with all copies of the Data Files or Software, or (b) this copyright and permission notice appear in associated Documentation.

THE DATA FILES AND SOFTWARE ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT OF THIRD PARTY RIGHTS.

IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS INCLUDED IN THIS NOTICE BE LIABLE FOR ANY CLAIM, OR ANY SPECIAL INDIRECT OR CONSEQUENTIAL DAMAGES, OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THE DATA FILES OR SOFTWARE.
