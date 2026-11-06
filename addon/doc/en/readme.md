# Emoji ID - Indonesian Emoji Reader for NVDA

Emoji ID reads emoji in Indonesian, whatever language your speech synthesizer uses. With an English Eloquence voice, for example, 😀 is read as "wajah gembira" instead of "grinning face".

Emoji are read in Indonesian during normal reading, Say All, character navigation, the review cursor, and typed character echo.

The add-on interface (settings, dialogs, and messages) follows the NVDA language: it is in English when NVDA is set to English, and in Indonesian otherwise. Emoji names are always Indonesian.

## How this differs from NVDA's built-in emoji names

NVDA already includes Indonesian emoji names from Unicode CLDR. It uses them only when the language used for symbols is Indonesian. With an English voice, NVDA reads emoji names in English. Emoji ID fills that gap.

If you already use an Indonesian voice and NVDA's "Include Unicode Consortium data" option is on, you may not need this add-on.

## Punctuation and symbols

NVDA 2026.3 has no Indonesian punctuation dictionary, so punctuation is normally read in English, even with an Indonesian voice. Emoji ID adds a dictionary of 806 punctuation marks and symbols in Indonesian, including mathematical symbols, arrows, currencies, and braille patterns.

- Names follow EYD Edisi V and KBBI where they name the symbol, for example titik, koma, titik koma, titik dua, tanda pisah, elipsis, tanda pagar, tilde, and garis bawah.
- Symbols that EYD and KBBI do not name use common Indonesian names, for example garis miring terbalik for \ and et for @.
- Punctuation stays Indonesian even when the voice is English.
- NVDA's symbol levels still apply. At the "some" level, for example, commas are still not read.

The feature is on by default. You can turn it off in the Emoji ID settings, in the symbol dictionary list in NVDA's speech settings, or with its command in Input Gestures. All three always show the same state.

## Supported emoji

- Basic emoji such as faces, gestures, animals, and objects.
- ZWJ sequences, such as families and professions.
- Country flags, such as the Indonesian flag.
- Number keycaps, such as 1️⃣.
- Skin tones.

Names come from Unicode CLDR 48.2, the same version NVDA 2026.3 uses. A few names are replaced with more common words. For example, 💩 is read as "kotoran".

## Settings

Open the NVDA menu, Preferences, Settings, and choose the Emoji ID category. The options are:

1. Enable Indonesian emoji reading. When unchecked, NVDA behaves as it does without the add-on.
2. Add a prefix word before emoji names. On by default.
3. Prefix word. The word spoken before each emoji name. "emoji" by default.
4. Prefix only once for consecutive emoji. When checked, the prefix is spoken only before the first emoji in a run.
5. Collapse repeated identical emoji. When checked, three 😀 in a row are read as "3 wajah gembira", or "3 emoji wajah gembira" with the prefix word.
6. Number of emoji in a row to read. 0 by default, which reads all. With 3, for example, a run of eight emoji is read as three names, then "dan 5 emoji lainnya". Repeated identical emoji that are already collapsed count as one group.
7. Include skin tone details. When unchecked, only the base emoji name is read.
8. Remove hyphens and parentheses from emoji names. On by default. "kupu-kupu" is sent to the synthesizer as "kupu kupu" and parentheses are removed, so synthesizers such as Eloquence do not say "dash" or "left paren". Punctuation outside emoji names is not changed.
9. Read punctuation and symbols in Indonesian. On by default. See the Punctuation and symbols section.
10. Check for updates when NVDA starts. On by default. See the Updates section.
11. Check for Updates Now button.
12. Show periodic donation reminder. Off by default. When checked, a donation invitation appears 20 to 45 minutes after NVDA starts, then every 90 to 180 minutes.
13. Support the Developer (GoPay Donation) button. Opens the GoPay donation details with a button that copies the number.

Settings are saved per NVDA configuration profile.

## Toggle command

Emoji ID has a command that turns Indonesian emoji reading on or off. It has no default gesture. To assign one:

1. Open the NVDA menu, Preferences, Input Gestures.
2. Expand the Emoji ID category.
3. Select "Turns Indonesian emoji reading on or off".
4. Press Add, then press the gesture you want, for example NVDA+Shift+E.
5. Press Enter to save.

When you use the command, NVDA says "Emoji ID on" or "Emoji ID off".

In the same way, you can assign a gesture to "Turns Indonesian punctuation and symbol reading on or off". NVDA then says "Indonesian punctuation on" or "Indonesian punctuation off".

## Insert emoji

The Insert Emoji dialog is modelled on the Windows 11 emoji panel (Windows+period), but every name is Indonesian and every part can be searched. It opens only through the "Opens the insert emoji dialog" command in Input Gestures, Emoji ID category. The command has no default gesture, so assign one as described in the Toggle command section.

The dialog contains, in Tab order:

1. Kind: Emoji, Symbols or Kaomoji.
2. Search. Results update as you type. Search uses Indonesian names and keywords, for example "ngakak", "terima kasih" or "bendera jepang", across every category of the chosen kind.
3. Category, following the Windows categories, plus Most recently used and Favorites.
4. Subcategory, for emoji only, such as Smiling faces or Country flags.
5. Results. Press Enter to insert the selected emoji.
6. Skin tone, for people and hand emoji.
7. Second person's skin tone, for two person emoji such as handshake and couples.
8. Gender: neutral, man or woman, for emoji that exist in all three.
9. Direction: default or facing right, for emoji such as a person running or a person with a white cane.
10. Collection: emoji gathered with Add to Collection, to insert together.
11. Buttons Insert, Add to Collection, Remove Last, Clear Collection, Copy, Add to Favorites or Remove from Favorites, Details, and Close.

After Insert, the dialog closes and the emoji is pasted where you were typing. The previous clipboard text is put back. If an application does not accept pasting, use Copy and paste with Control+V yourself. The last skin tone and gender are remembered.

## Updates

Emoji ID is not in the NVDA Add-on Store yet, so it checks GitHub for a newer version when NVDA starts. If one exists, a message offers three choices: Download and Install, Open Release Page, or Later. If you choose Download and Install, NVDA asks you to confirm the installation as usual.

You can also check at any time with the Check for Updates Now button in the Emoji ID settings. To turn off the automatic check, uncheck "Check for updates when NVDA starts".

## Donations

Emoji ID is developed on a volunteer basis. During installation, Emoji ID shows a welcome message with a donation invitation. If you choose Donate, the GoPay number is copied to the clipboard. Donations can be sent through GoPay:

- Phone number: 085128011831
- Account name: Rexya Muhamad Rizki

Thank you.

## Requirements

- NVDA 2026.1 or later. Last tested with NVDA 2026.3.
- Works with any synthesizer, including Eloquence, Windows OneCore, eSpeak NG, Vocalizer Expressive, and SAPI5.

## License and copyright

- Author: Rexya Muhamad <rexya2017@gmail.com>
- Add-on license: GNU General Public License version 2 or later (GPL-2.0-or-later).
- Code copyright: (c) 2026 Rexya Muhamad.
- Source code: https://github.com/InfiArtt/emoji-id

### Unicode CLDR License Notice (Unicode License v3)

Indonesian emoji annotation data is sourced from the Unicode Common Locale Data Repository (CLDR) project.

UNICODE LICENSE V3
COPYRIGHT AND PERMISSION NOTICE

Copyright (c) 1991-2026 Unicode, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of data files and any associated documentation (the "Data Files") or software and any associated documentation (the "Software") to deal in the Data Files or Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, and/or sell copies of the Data Files or Software, and to permit persons to whom the Data Files or Software are furnished to do so, provided that either (a) this copyright and permission notice appear with all copies of the Data Files or Software, or (b) this copyright and permission notice appear in associated Documentation.

THE DATA FILES AND SOFTWARE ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT OF THIRD PARTY RIGHTS.

IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS INCLUDED IN THIS NOTICE BE LIABLE FOR ANY CLAIM, OR ANY SPECIAL INDIRECT OR CONSEQUENTIAL DAMAGES, OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THE DATA FILES OR SOFTWARE.
