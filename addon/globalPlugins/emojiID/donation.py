# Emoji ID - Indonesian Emoji Reader for NVDA
# Copyright (C) 2026 Rexya Muhamad <rexya2017@gmail.com>
# This file is covered by the GNU General Public License v2 or later.
# See the file LICENSE for more details.

"""Welcome, donation reminder and donation details dialogs."""

import addonHandler
import api
import gui
import ui
import wx
from logHandler import log

addonHandler.initTranslation()

GOPAY_NUMBER = "085128011831"
GOPAY_NAME = "Rexya Muhamad Rizki"


def _showModal(dialog: wx.Dialog) -> int:
	"""Show a modal dialog with NVDA's pre and post popup handling, then destroy it."""
	gui.mainFrame.prePopup()
	try:
		return dialog.ShowModal()
	finally:
		dialog.Destroy()
		gui.mainFrame.postPopup()


class DonationDetailsDialog(wx.Dialog):
	"""Shows the GoPay account details with a button to copy the number."""

	def __init__(self, parent: wx.Window | None) -> None:
		# Translators: Title of the dialog that shows the GoPay donation details.
		super().__init__(parent, title=_("Informasi Donasi GoPay - Emoji ID"))
		sizer = wx.BoxSizer(wx.VERTICAL)

		detailsText = _(
			# Translators: Donation details. {number} is the GoPay phone number, {name} is the account holder.
			"Dukungan Pengembang Emoji ID\n\n"
			"Metode: GoPay\n"
			"Nomor HP: {number}\n"
			"Atas nama: {name}\n\n"
			"Donasi berapa pun membantu add-on ini terus diperbarui. Terima kasih!"
		).format(number=GOPAY_NUMBER, name=GOPAY_NAME)
		self.detailsText = wx.TextCtrl(
			self,
			value=detailsText,
			style=wx.TE_MULTILINE | wx.TE_READONLY,
			size=(480, 200),
		)
		sizer.Add(self.detailsText, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

		buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
		# Translators: Button that copies the GoPay number to the clipboard.
		copyButton = wx.Button(self, label=_("Salin Nomor"))
		copyButton.Bind(wx.EVT_BUTTON, self._onCopy)
		buttonSizer.Add(copyButton, flag=wx.RIGHT, border=10)
		# Translators: Button that closes the donation details dialog.
		closeButton = wx.Button(self, wx.ID_CANCEL, label=_("Tutup"))
		buttonSizer.Add(closeButton)
		sizer.Add(buttonSizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

		self.SetSizerAndFit(sizer)
		self.CentreOnScreen()
		self.detailsText.SetFocus()
		self.detailsText.SetInsertionPoint(0)

	def _onCopy(self, evt: wx.CommandEvent) -> None:
		if api.copyToClip(GOPAY_NUMBER):
			# Translators: Announced after the GoPay number is copied. {number} is the number.
			ui.message(_("Nomor GoPay {number} disalin ke papan klip.").format(number=GOPAY_NUMBER))
		else:
			# Translators: Announced when the GoPay number could not be copied.
			ui.message(_("Gagal menyalin nomor ke papan klip."))


class DonationInviteDialog(wx.Dialog):
	"""Short message inviting the user to donate, with "Donasi" and "Tidak Sekarang" buttons."""

	def __init__(self, parent: wx.Window | None, title: str, message: str) -> None:
		super().__init__(parent, title=title)
		sizer = wx.BoxSizer(wx.VERTICAL)

		self.messageText = wx.StaticText(self, label=message)
		self.messageText.Wrap(500)
		sizer.Add(self.messageText, flag=wx.ALL | wx.EXPAND, border=15)

		buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
		# Translators: Button that opens the donation details.
		donateButton = wx.Button(self, label=_("Donasi"))
		donateButton.Bind(wx.EVT_BUTTON, self._onDonate)
		buttonSizer.Add(donateButton, flag=wx.RIGHT, border=10)
		# Translators: Button that closes the donation invitation.
		notNowButton = wx.Button(self, wx.ID_CANCEL, label=_("Tidak Sekarang"))
		notNowButton.SetDefault()
		buttonSizer.Add(notNowButton)
		sizer.Add(buttonSizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=15)

		self.SetSizerAndFit(sizer)
		self.CentreOnScreen()

	def _onDonate(self, evt: wx.CommandEvent) -> None:
		showDonationDetailsDialog(self)


def showDonationDetailsDialog(parent: wx.Window | None = None) -> None:
	"""Open the GoPay donation details dialog. Must be called on the GUI thread."""
	try:
		_showModal(DonationDetailsDialog(parent or gui.mainFrame))
	except Exception:
		log.error("Emoji ID: could not show the donation details dialog", exc_info=True)


def _showInviteDialog(title: str, message: str) -> None:
	try:
		_showModal(DonationInviteDialog(gui.mainFrame, title, message))
	except Exception:
		log.error("Emoji ID: could not show the donation invitation", exc_info=True)


def showWelcomeDialog() -> None:
	"""Open the welcome dialog shown once after installation. Must be called on the GUI thread."""
	_showInviteDialog(
		# Translators: Title of the welcome dialog shown the first time NVDA starts with Emoji ID.
		_("Selamat Datang di Emoji ID"),
		_(
			# Translators: Message of the welcome dialog shown the first time NVDA starts with Emoji ID.
			"Selamat datang di Emoji ID!\n\n"
			"Add-on ini membacakan emoji dalam bahasa Indonesia, apa pun suara TTS yang kamu pakai.\n\n"
			"Kalau add-on ini bermanfaat, kamu bisa mendukung pengembangnya lewat donasi sukarela "
			"melalui GoPay. Pilih Donasi untuk melihat nomornya, atau Tidak Sekarang untuk menutup pesan ini."
		),
	)


def showReminderDialog() -> None:
	"""Open the periodic donation reminder. Must be called on the GUI thread."""
	_showInviteDialog(
		# Translators: Title of the periodic donation reminder.
		_("Dukungan Pengembang - Emoji ID"),
		_(
			# Translators: Message of the periodic donation reminder.
			"Semoga Emoji ID membantu aktivitasmu sehari-hari.\n\n"
			"Kalau kamu ingin add-on ini terus diperbarui, kamu bisa mendukung pengembangnya "
			"lewat donasi sukarela melalui GoPay. Pengingat ini bisa dimatikan di pengaturan Emoji ID."
		),
	)
