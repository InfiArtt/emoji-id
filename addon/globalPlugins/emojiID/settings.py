# Emoji ID - Indonesian Emoji Reader for NVDA
# Copyright (C) 2026 Rexya Muhamad <rexya2017@gmail.com>
# This file is covered by the GNU General Public License v2 or later.
# See the file LICENSE for more details.

"""Configuration and the NVDA settings panel for Emoji ID."""

import addonHandler
import config
import wx
from gui import guiHelper
from gui.settingsDialogs import SettingsPanel

from .symbols import isIndonesianSymbolsEnabled, setIndonesianSymbolsEnabled

addonHandler.initTranslation()

CONFIG_SECTION = "emojiID"

#: Configuration specification. All settings are profile-aware.
CONF_SPEC: dict[str, str] = {
	"enabled": "boolean(default=True)",
	"prefix": "boolean(default=True)",
	"prefixText": 'string(default="emoji")',
	"prefixOnce": "boolean(default=False)",
	"collapseRepeated": "boolean(default=True)",
	"skinToneDetail": "boolean(default=True)",
	"cleanSymbols": "boolean(default=True)",
	"periodicDonationReminder": "boolean(default=False)",
	"firstRun": "boolean(default=True)",
	"symbolsEnabledOnce": "boolean(default=False)",
}


def getConfig() -> config.AggregatedSection:
	"""Return the Emoji ID configuration section."""
	return config.conf[CONFIG_SECTION]


def isEnabled() -> bool:
	"""Whether Emoji ID is enabled in the current configuration profile."""
	return bool(getConfig()["enabled"])


def registerConfig() -> None:
	"""Register the Emoji ID configuration specification with NVDA."""
	config.conf.spec[CONFIG_SECTION] = CONF_SPEC


class EmojiIDSettingsPanel(SettingsPanel):
	"""Settings panel shown in the NVDA settings dialog."""

	# Translators: Title of the Emoji ID category in the NVDA settings dialog.
	title = _("Emoji ID")

	def makeSettings(self, settingsSizer: wx.BoxSizer) -> None:
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		conf = getConfig()

		self.enabledCheckbox = sHelper.addItem(
			# Translators: Checkbox in the Emoji ID settings panel.
			wx.CheckBox(self, label=_("Aktifkan pembacaan emoji dalam bahasa Indonesia")),
		)
		self.enabledCheckbox.SetValue(conf["enabled"])
		self.enabledCheckbox.Bind(wx.EVT_CHECKBOX, self._onDependencyToggle)

		self.prefixCheckbox = sHelper.addItem(
			# Translators: Checkbox in the Emoji ID settings panel.
			wx.CheckBox(self, label=_("Tambahkan kata awalan sebelum nama emoji")),
		)
		self.prefixCheckbox.SetValue(conf["prefix"])
		self.prefixCheckbox.Bind(wx.EVT_CHECKBOX, self._onDependencyToggle)

		self.prefixTextCtrl = sHelper.addLabeledControl(
			# Translators: Label of the edit field for the prefix word in the Emoji ID settings panel.
			_("Kata awalan:"),
			wx.TextCtrl,
		)
		self.prefixTextCtrl.SetValue(conf["prefixText"])

		self.prefixOnceCheckbox = sHelper.addItem(
			# Translators: Checkbox in the Emoji ID settings panel.
			wx.CheckBox(self, label=_("Kata awalan hanya sekali untuk emoji berturut-turut")),
		)
		self.prefixOnceCheckbox.SetValue(conf["prefixOnce"])

		self.collapseRepeatedCheckbox = sHelper.addItem(
			wx.CheckBox(
				self,
				# Translators: Checkbox in the Emoji ID settings panel.
				label=_("Gabungkan emoji yang sama dan berulang (misalnya '3 kali wajah gembira')"),
			),
		)
		self.collapseRepeatedCheckbox.SetValue(conf["collapseRepeated"])

		self.skinToneDetailCheckbox = sHelper.addItem(
			# Translators: Checkbox in the Emoji ID settings panel.
			wx.CheckBox(self, label=_("Sertakan detail warna kulit")),
		)
		self.skinToneDetailCheckbox.SetValue(conf["skinToneDetail"])

		self.cleanSymbolsCheckbox = sHelper.addItem(
			# Translators: Checkbox in the Emoji ID settings panel.
			wx.CheckBox(self, label=_("Bersihkan tanda hubung dan tanda kurung pada nama emoji")),
		)
		self.cleanSymbolsCheckbox.SetValue(conf["cleanSymbols"])

		self.indonesianSymbolsCheckbox = sHelper.addItem(
			# Translators: Checkbox in the Emoji ID settings panel.
			wx.CheckBox(self, label=_("Bacakan tanda baca dan simbol dalam bahasa Indonesia")),
		)
		self.indonesianSymbolsCheckbox.SetValue(isIndonesianSymbolsEnabled())

		self.periodicReminderCheckbox = sHelper.addItem(
			# Translators: Checkbox in the Emoji ID settings panel.
			wx.CheckBox(self, label=_("Tampilkan pengingat donasi berkala")),
		)
		self.periodicReminderCheckbox.SetValue(conf["periodicDonationReminder"])

		self.donateButton = sHelper.addItem(
			# Translators: Button in the Emoji ID settings panel that opens the donation details.
			wx.Button(self, label=_("Dukung Pengembang (Donasi GoPay)...")),
		)
		self.donateButton.Bind(wx.EVT_BUTTON, self._onDonateClicked)

		self._updateControlStates()

	def _onDonateClicked(self, evt: wx.CommandEvent) -> None:
		from .donation import showDonationDetailsDialog

		showDonationDetailsDialog(self)

	def _onDependencyToggle(self, evt: wx.CommandEvent) -> None:
		self._updateControlStates()

	def _updateControlStates(self) -> None:
		"""Disable options that have no effect with the current choices."""
		isOn = self.enabledCheckbox.GetValue()
		hasPrefix = isOn and self.prefixCheckbox.GetValue()
		self.prefixCheckbox.Enable(isOn)
		self.prefixTextCtrl.Enable(hasPrefix)
		self.prefixOnceCheckbox.Enable(hasPrefix)
		self.collapseRepeatedCheckbox.Enable(isOn)
		self.skinToneDetailCheckbox.Enable(isOn)
		self.cleanSymbolsCheckbox.Enable(isOn)

	def onSave(self) -> None:
		conf = getConfig()
		conf["enabled"] = self.enabledCheckbox.GetValue()
		conf["prefix"] = self.prefixCheckbox.GetValue()
		conf["prefixText"] = self.prefixTextCtrl.GetValue().strip()
		conf["prefixOnce"] = self.prefixOnceCheckbox.GetValue()
		conf["collapseRepeated"] = self.collapseRepeatedCheckbox.GetValue()
		conf["skinToneDetail"] = self.skinToneDetailCheckbox.GetValue()
		conf["cleanSymbols"] = self.cleanSymbolsCheckbox.GetValue()
		conf["periodicDonationReminder"] = self.periodicReminderCheckbox.GetValue()
		setIndonesianSymbolsEnabled(self.indonesianSymbolsCheckbox.GetValue())
