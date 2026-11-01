# Emoji ID - Indonesian Emoji Reader for NVDA
# Copyright (C) 2026 Rexya Muhamad <rexya2017@gmail.com>
# This file is covered by the GNU General Public License v2 or later.
# See the file LICENSE for more details.

"""Shows the welcome and donation message while Emoji ID is being installed.

Only NVDA's documented message dialogs are used, run on the GUI thread through ``wxCallOnMain``,
so the installation waits for the user without blocking NVDA.
"""

import addonHandler
import api
import config
import gui
from gui.guiHelper import wxCallOnMain
from gui.message import MessageDialog, ReturnCode
from logHandler import log

addonHandler.initTranslation()

# Keep in sync with globalPlugins/emojiID/donation.py.
# installTasks cannot import the plugin package, because it is not installed yet.
GOPAY_NUMBER = "085128011831"
GOPAY_NAME = "Rexya Muhamad Rizki"
_CONFIG_SECTION = "emojiID"


def _showWelcome() -> None:
	"""Ask the user to donate and, if they agree, copy the GoPay number. Runs on the GUI thread."""
	gui.mainFrame.prePopup()
	try:
		answer = MessageDialog.confirm(
			_(
				# Translators: Message of the welcome dialog shown while Emoji ID is being installed.
				"Selamat datang di Emoji ID!\n\n"
				"Add-on ini membacakan emoji dalam bahasa Indonesia, apa pun suara TTS yang kamu pakai.\n\n"
				"Kalau add-on ini bermanfaat, kamu bisa mendukung pengembangnya lewat donasi sukarela "
				"melalui GoPay. Pilih Donasi untuk melihat nomornya, atau Tidak Sekarang untuk "
				"melanjutkan instalasi."
			),
			# Translators: Title of the welcome dialog shown while Emoji ID is being installed.
			_("Selamat Datang di Emoji ID"),
			# Translators: Button in the installation welcome dialog that shows the donation details.
			okLabel=_("Donasi"),
			# Translators: Button in the installation welcome dialog that continues the installation.
			cancelLabel=_("Tidak Sekarang"),
		)
		if answer != ReturnCode.OK:
			return
		isCopied = api.copyToClip(GOPAY_NUMBER)
		details = _(
			# Translators: Donation details. {number} is the GoPay phone number, {name} is the account holder.
			"Metode: GoPay\nNomor HP: {number}\nAtas nama: {name}\n\n"
			"Donasi berapa pun membantu add-on ini terus diperbarui. Terima kasih!"
		).format(number=GOPAY_NUMBER, name=GOPAY_NAME)
		if isCopied:
			# Translators: Added to the donation details after the GoPay number was copied.
			details += "\n\n" + _("Nomor GoPay sudah disalin ke papan klip.")
		MessageDialog.alert(
			details,
			# Translators: Title of the dialog that shows the GoPay donation details.
			_("Informasi Donasi GoPay - Emoji ID"),
		)
	finally:
		gui.mainFrame.postPopup()


def _markWelcomeShown() -> None:
	"""Stop the plugin from showing the welcome dialog again after NVDA restarts."""
	spec = config.conf.spec.setdefault(_CONFIG_SECTION, {})
	spec.setdefault("firstRun", "boolean(default=True)")
	config.conf[_CONFIG_SECTION]["firstRun"] = False
	config.conf.save()


def onInstall() -> None:
	try:
		wxCallOnMain(_showWelcome)
	except Exception:
		# A failed dialog must never fail the installation.
		# The plugin then shows its welcome dialog after NVDA restarts instead.
		log.error("Emoji ID: could not show the installation welcome dialog", exc_info=True)
		return
	try:
		wxCallOnMain(_markWelcomeShown)
	except Exception:
		log.error("Emoji ID: could not save that the welcome dialog was shown", exc_info=True)
