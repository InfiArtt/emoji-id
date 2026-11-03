# Emoji ID - Indonesian Emoji Reader for NVDA
# Copyright (C) 2026 Rexya Muhamad <rexya2017@gmail.com>
# This file is covered by the GNU General Public License v2 or later.
# See the file LICENSE for more details.

"""Indonesian names for punctuation and symbols.

The add-on ships an NVDA symbol dictionary, ``locale/id/symbols-simbolIndonesia.dic``,
declared in the manifest. NVDA itself has no Indonesian punctuation dictionary,
so without it punctuation is spoken in English even with an Indonesian voice.

The dictionary is switched on and off through NVDA's own list of enabled symbol dictionaries,
so the add-on setting and NVDA's speech settings always agree.
While it is on, symbol processing uses the Indonesian locale whatever the voice language is,
so that NVDA keeps applying its symbol levels to the Indonesian names.
"""

import characterProcessing
import config

#: Name of the symbol dictionary in the manifest and in NVDA's configuration.
SYMBOL_DICTIONARY = "simbolIndonesia"
#: Locale whose symbol data holds the Indonesian names.
INDONESIAN_LOCALE = "id"


def isIndonesianSymbolsEnabled() -> bool:
	"""Whether punctuation and symbols are spoken with Indonesian names."""
	return SYMBOL_DICTIONARY in config.conf["speech"]["symbolDictionaries"]


def setIndonesianSymbolsEnabled(isOn: bool) -> None:
	"""Turn the Indonesian symbol dictionary on or off.

	:param isOn: Whether the dictionary should be used.
	"""
	dictionaries = list(config.conf["speech"]["symbolDictionaries"])
	if isOn == (SYMBOL_DICTIONARY in dictionaries):
		return
	if isOn:
		dictionaries.append(SYMBOL_DICTIONARY)
	else:
		dictionaries.remove(SYMBOL_DICTIONARY)
	config.conf["speech"]["symbolDictionaries"] = dictionaries
	# NVDA caches symbol data per locale, built from the dictionaries enabled at that time.
	characterProcessing.clearSpeechSymbols()


def getSymbolLocale(locale: str) -> str:
	"""Return the locale to use for symbol processing.

	:param locale: The locale NVDA asked for, usually the voice language.
	:return: The Indonesian locale while Indonesian symbols are on, otherwise ``locale`` unchanged.
	"""
	return INDONESIAN_LOCALE if isIndonesianSymbolsEnabled() else locale
