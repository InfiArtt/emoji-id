# -*- coding: UTF-8 -*-

# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

_ = lambda x: x

addon_info = {
    "addon_name": "emojiID",
    "addon_summary": _("Emoji ID - Pembaca Emoji Bahasa Indonesia"),
    "addon_description": _("""Membacakan emoji dalam bahasa Indonesia, terlepas dari suara TTS yang digunakan. Mendukung emoji dasar, ZWJ sequence, bendera, keycap, dan skin tone."""),
    "addon_version": "1.0.0",
    "addon_author": "Emoji ID Contributors",
    "addon_url": "https://github.com/emoji-id/emoji-id-nvda",
    "addon_docFileName": "readme.html",
    "addon_minimumNVDAVersion": "2026.1",
    "addon_lastTestedNVDAVersion": "2026.1",
    "addon_updateChannel": None,
}

import os

pythonSources = [
    os.path.join("addon", "globalPlugins", "emojiID", "*.py"),
]

i18nSources = pythonSources + ["buildVars.py"]

excludedFiles = []
