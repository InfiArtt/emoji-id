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

So that it does not open by accident, the dialog only opens where you can type: text fields, editable documents such as Word or an email body, form fields on web pages, and terminals. Elsewhere, for example on a button, a list, the desktop, read-only text, or a web page in browse mode outside a form field, NVDA says "Not a place to type. Press twice to open anyway". If an application has a text field NVDA does not recognize, press the gesture twice quickly to open the dialog anyway.

The dialog has three tabs: Emoji, Symbols and Kaomoji. Each tab contains, in Tab order:

1. Search. Results update as you type. Search uses Indonesian names and keywords, for example "ngakak", "terima kasih" or "bendera jepang", across every category of the tab.
2. Category, following the Windows categories, plus Most recently used and Favorites.
3. Subcategory, on the Emoji tab only, such as Smiling faces or Country flags. It filters the Results list.
4. Results. NVDA reports the position of each item, for example "5 of 140". Typing a letter jumps to a name starting with it. On the Emoji tab, when Subcategory is set to All subcategories and Search is empty, the right arrow jumps to the start of the next subcategory and the left arrow to the start of the previous one. The subcategory name is then spoken.

Below the tabs are the Collection field, listing emoji gathered to insert together, and the buttons. Every button names its shortcut, and the shortcuts work from anywhere in the dialog:

- Insert (Enter): inserts the selected emoji, or the whole collection when it is not empty.
- Personalize (Shift+Enter): enabled only for emoji that can be personalized.
- Add to Collection (Ctrl+Enter).
- Remove Last (Ctrl+Shift+Backspace): removes the last emoji from the collection.
- Clear Collection (Ctrl+Shift+Delete).
- Copy (Ctrl+Shift+C): copies without inserting.
- Add to Favorites or Remove from Favorites (Ctrl+D).
- Details (Alt+Enter).
- Shortcuts (F1): lists every shortcut.
- Close (Escape).

Other shortcuts without a button: Control+Tab and Control+Shift+Tab for the next or previous tab, Control+1, Control+2 and Control+3 to go straight to the Emoji, Symbols or Kaomoji tab, Control+F to move to Search, and Control+R to read the collection.

Enter always inserts the selected emoji right away. Emoji with a skin tone, gender or direction to choose are marked in the list, for example "jempol ke atas, can be personalized, press Shift+Enter". Shift+Enter opens the Personalize dialog:

- Only the options that apply to that emoji appear: gender, direction, skin tone, and the second person's skin tone for two person emoji such as handshake.
- The Result field names the emoji you will get.
- Press Enter to insert it, Control+Enter to add it to the collection, or Control+Shift+C to copy it. Press Escape to cancel.

After Insert, the dialog closes and the emoji is pasted where you were typing. The previous clipboard text is put back. If an application does not accept pasting, use Copy and paste with Control+V yourself. The last personalization choices are remembered.

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
