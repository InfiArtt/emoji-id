# Emoji ID - Indonesian Emoji Reader for NVDA
# Copyright (C) 2026 Rexya Muhamad <rexya2017@gmail.com>
# This file is covered by the GNU General Public License v2 or later.
# See the file LICENSE for more details.

"""Reads emoji in Indonesian regardless of the active synthesizer language.

Two hooks are used:

1. ``speech.extensions.filter_speechSequence`` replaces emoji inside text that is about to be spoken.
2. ``characterProcessing.processSpeechSymbol`` is wrapped, because character navigation,
	typed character echo and the review cursor turn a single character into its name
	before the speech sequence is built, so the filter would only see the English name.
"""

import random
from collections.abc import Callable

import addonHandler
import characterProcessing
import config
import core
import globalPluginHandler
import inputCore
import speech.extensions
import ui
import wx
from gui.settingsDialogs import NVDASettingsDialog
from logHandler import log
from scriptHandler import script
from speech.types import SpeechSequence

from .emojiData import EmojiMatcher
from .settings import EmojiIDSettingsPanel, getConfig, isEnabled, registerConfig

addonHandler.initTranslation()

_MS_PER_MINUTE = 60 * 1000
#: Delay range of the first donation reminder after NVDA starts.
FIRST_REMINDER_DELAY_MINUTES = (20, 45)
#: Delay range between later donation reminders.
NEXT_REMINDER_DELAY_MINUTES = (90, 180)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Replaces emoji in speech with Indonesian names."""

	# Translators: Category of Emoji ID commands in the Input Gestures dialog.
	scriptCategory = _("Emoji ID")

	def __init__(self) -> None:
		super().__init__()
		self._isTerminated = False
		self._reminderTimer: wx.CallLater | None = None

		registerConfig()
		self._matcher = EmojiMatcher()
		if not self._matcher.load():
			log.error("Emoji ID: emoji data could not be loaded, emoji will not be replaced")

		speech.extensions.filter_speechSequence.register(self._filterSpeechSequence)
		self._originalProcessSpeechSymbol: Callable[[str, str], str] = characterProcessing.processSpeechSymbol
		characterProcessing.processSpeechSymbol = self._processSpeechSymbol

		NVDASettingsDialog.categoryClasses.append(EmojiIDSettingsPanel)
		core.postNvdaStartup.register(self._onNvdaStartupComplete)

	def terminate(self) -> None:
		self._isTerminated = True
		self._cancelReminder()
		core.postNvdaStartup.unregister(self._onNvdaStartupComplete)
		speech.extensions.filter_speechSequence.unregister(self._filterSpeechSequence)
		# Restore the original only if no other add-on wrapped our wrapper in the meantime.
		# Otherwise the wrapper stays in the chain and passes everything through.
		if characterProcessing.processSpeechSymbol == self._processSpeechSymbol:
			characterProcessing.processSpeechSymbol = self._originalProcessSpeechSymbol
		try:
			NVDASettingsDialog.categoryClasses.remove(EmojiIDSettingsPanel)
		except ValueError:
			pass
		super().terminate()

	def _filterSpeechSequence(self, speechSequence: SpeechSequence) -> SpeechSequence:
		"""Replace emoji in the text items of a speech sequence. Commands pass through unchanged."""
		if not isEnabled() or not self._matcher.isLoaded:
			return speechSequence

		conf = getConfig()
		prefix = conf["prefixText"] if conf["prefix"] else ""
		newSequence: SpeechSequence = []
		for item in speechSequence:
			if isinstance(item, str):
				item = self._matcher.replaceInText(
					item,
					prefix=prefix,
					isPrefixOnce=conf["prefixOnce"],
					shouldCollapseRepeated=conf["collapseRepeated"],
					hasSkinToneDetail=conf["skinToneDetail"],
					shouldCleanSymbols=conf["cleanSymbols"],
				)
				if not item:
					continue
			newSequence.append(item)
		return newSequence

	def _processSpeechSymbol(self, locale: str, symbol: str) -> str:
		"""Return the Indonesian name of a single emoji, otherwise defer to NVDA."""
		if not self._isTerminated and isEnabled():
			conf = getConfig()
			name = self._matcher.lookupSingleChar(symbol, shouldCleanSymbols=conf["cleanSymbols"])
			if name is not None:
				if conf["prefix"] and conf["prefixText"]:
					return f"{conf['prefixText']} {name}"
				return name
		return self._originalProcessSpeechSymbol(locale, symbol)

	@script(
		# Translators: Description of the command that turns Emoji ID on or off, shown in Input Gestures.
		description=_("Aktifkan atau nonaktifkan pembacaan emoji dalam bahasa Indonesia"),
	)
	def script_toggleEmojiID(self, gesture: inputCore.InputGesture) -> None:
		conf = getConfig()
		conf["enabled"] = not conf["enabled"]
		if conf["enabled"]:
			# Translators: Announced when Emoji ID is turned on.
			ui.message(_("Emoji ID aktif"))
		else:
			# Translators: Announced when Emoji ID is turned off.
			ui.message(_("Emoji ID nonaktif"))

	def _onNvdaStartupComplete(self) -> None:
		"""Show the welcome dialog once after installation and start the donation reminder."""
		conf = getConfig()
		if conf["firstRun"]:
			conf["firstRun"] = False
			try:
				config.conf.save()
			except Exception:
				log.error("Emoji ID: could not save configuration", exc_info=True)
			from .donation import showWelcomeDialog

			wx.CallAfter(showWelcomeDialog)
		self._scheduleReminder(*FIRST_REMINDER_DELAY_MINUTES)

	def _isReminderEnabled(self) -> bool:
		return not self._isTerminated and bool(getConfig()["periodicDonationReminder"])

	def _scheduleReminder(self, minMinutes: int, maxMinutes: int) -> None:
		if not self._isReminderEnabled():
			return
		delayMs = random.randint(minMinutes * _MS_PER_MINUTE, maxMinutes * _MS_PER_MINUTE)
		self._reminderTimer = wx.CallLater(delayMs, self._onReminderDue)

	def _cancelReminder(self) -> None:
		if self._reminderTimer is not None:
			self._reminderTimer.Stop()
			self._reminderTimer = None

	def _onReminderDue(self) -> None:
		self._reminderTimer = None
		if not self._isReminderEnabled():
			return
		from .donation import showReminderDialog

		showReminderDialog()
		self._scheduleReminder(*NEXT_REMINDER_DELAY_MINUTES)
