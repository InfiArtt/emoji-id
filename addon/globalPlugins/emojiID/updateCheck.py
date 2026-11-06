# Emoji ID - Indonesian Emoji Reader for NVDA
# Copyright (C) 2026 Rexya Muhamad <rexya2017@gmail.com>
# This file is covered by the GNU General Public License v2 or later.
# See the file LICENSE for more details.

"""Checks GitHub for a newer Emoji ID release.

This is temporary: Emoji ID is not in the NVDA Add-on Store yet, so users would not hear about new versions.
Remove this module once the add-on is published in the store, which then handles updates.
"""

import json
import os
import tempfile
import threading
import urllib.request
from dataclasses import dataclass

import addonHandler
import gui
import ui
import wx
from gui.message import MessageDialog, ReturnCode
from logHandler import log

addonHandler.initTranslation()

RELEASES_API_URL = "https://api.github.com/repos/InfiArtt/emoji-id/releases/latest"
_TIMEOUT_SECONDS = 15
_ADDON_EXTENSION = ".nvda-addon"

#: Only one check runs at a time.
_checkLock = threading.Lock()


@dataclass(frozen=True)
class Release:
	"""The latest published Emoji ID release."""

	version: str
	pageUrl: str
	downloadUrl: str | None


def parseVersion(version: str) -> tuple[int, ...]:
	"""Turn "v1.2.3" or "1.2.3" into (1, 2, 3). Parts that are not numbers count as 0."""
	parts = version.strip().lstrip("vV").split("-")[0].split(".")
	return tuple(int(part) if part.isdigit() else 0 for part in parts)


def isNewer(latest: str, current: str) -> bool:
	"""Whether version ``latest`` is newer than version ``current``."""
	return parseVersion(latest) > parseVersion(current)


def getInstalledVersion() -> str:
	"""Return the version of the running Emoji ID add-on."""
	return addonHandler.getCodeAddon().version


def fetchLatestRelease() -> Release:
	"""Ask GitHub for the latest release.

	:raises OSError: When GitHub cannot be reached.
	:raises ValueError: When the answer is not a release.
	"""
	request = urllib.request.Request(
		RELEASES_API_URL,
		headers={"Accept": "application/vnd.github+json", "User-Agent": "Emoji-ID-NVDA-add-on"},
	)
	with urllib.request.urlopen(request, timeout=_TIMEOUT_SECONDS) as response:
		data = json.loads(response.read().decode("utf-8"))
	try:
		downloadUrl = next(
			(
				asset["browser_download_url"]
				for asset in data.get("assets", [])
				if asset["name"].endswith(_ADDON_EXTENSION)
			),
			None,
		)
		return Release(
			version=data["tag_name"].lstrip("vV"), pageUrl=data["html_url"], downloadUrl=downloadUrl
		)
	except (KeyError, TypeError, AttributeError) as error:
		raise ValueError(f"Unexpected release data: {error}") from error


def checkForUpdate(isManual: bool) -> None:
	"""Check for a newer release in the background and tell the user on the GUI thread.

	:param isManual: The user asked for the check. Then "no update" and errors are reported too;
		the automatic check at startup stays silent unless there is an update.
	"""
	if not _checkLock.acquire(blocking=False):
		return
	if isManual:
		# Translators: Announced when the user starts an update check.
		ui.message(_("Memeriksa pembaruan Emoji ID..."))
	threading.Thread(target=_check, args=(isManual,), name="EmojiIDUpdateCheck", daemon=True).start()


def _check(isManual: bool) -> None:
	try:
		try:
			release = fetchLatestRelease()
		except (OSError, ValueError):
			log.debugWarning("Emoji ID: update check failed", exc_info=True)
			if isManual:
				wx.CallAfter(_showCheckFailed)
			return
		installed = getInstalledVersion()
		if isNewer(release.version, installed):
			wx.CallAfter(_offerUpdate, release, installed)
		elif isManual:
			wx.CallAfter(_showUpToDate, installed)
	finally:
		_checkLock.release()


def _showCheckFailed() -> None:
	MessageDialog.alert(
		# Translators: Shown when the update check could not reach GitHub.
		_("Gagal memeriksa pembaruan. Periksa koneksi internet, lalu coba lagi."),
		# Translators: Title of the update check dialogs.
		_("Pembaruan Emoji ID"),
	)


def _showUpToDate(installed: str) -> None:
	MessageDialog.alert(
		# Translators: Shown when no newer version exists. {version} is the installed version.
		_("Emoji ID versi {version} sudah yang terbaru.").format(version=installed),
		# Translators: Title of the update check dialogs.
		_("Pembaruan Emoji ID"),
	)


def _offerUpdate(release: Release, installed: str) -> None:
	gui.mainFrame.prePopup()
	try:
		answer = MessageDialog.ask(
			_(
				# Translators: Shown when a newer version exists. {new} and {installed} are version numbers.
				"Emoji ID versi {new} sudah tersedia. Versi yang terpasang sekarang {installed}.\n\n"
				"Pilih Unduh dan Pasang untuk memasangnya, Buka Halaman Rilis untuk membaca perubahannya, "
				"atau Nanti untuk menutup pesan ini."
			).format(new=release.version, installed=installed),
			# Translators: Title of the update check dialogs.
			_("Pembaruan Emoji ID"),
			# Translators: Button that downloads and installs the new version.
			yesLabel=_("Unduh dan Pasang"),
			# Translators: Button that opens the release page in the web browser.
			noLabel=_("Buka Halaman Rilis"),
			# Translators: Button that closes the update message.
			cancelLabel=_("Nanti"),
		)
	finally:
		gui.mainFrame.postPopup()
	if answer == ReturnCode.YES and release.downloadUrl:
		# Translators: Announced while the new version is being downloaded.
		ui.message(_("Mengunduh pembaruan Emoji ID..."))
		threading.Thread(target=_download, args=(release,), name="EmojiIDUpdateDownload", daemon=True).start()
	elif answer in (ReturnCode.YES, ReturnCode.NO):
		os.startfile(release.pageUrl)


def _download(release: Release) -> None:
	path = os.path.join(tempfile.gettempdir(), f"emojiID-{release.version}{_ADDON_EXTENSION}")
	try:
		request = urllib.request.Request(release.downloadUrl, headers={"User-Agent": "Emoji-ID-NVDA-add-on"})
		with urllib.request.urlopen(request, timeout=_TIMEOUT_SECONDS) as response, open(path, "wb") as file:
			file.write(response.read())
	except OSError:
		log.error("Emoji ID: could not download the update", exc_info=True)
		wx.CallAfter(_showDownloadFailed, release)
		return
	# Opening the package hands it to NVDA, which asks the user to confirm the installation.
	wx.CallAfter(os.startfile, path)


def _showDownloadFailed(release: Release) -> None:
	MessageDialog.alert(
		# Translators: Shown when the new version could not be downloaded. {url} is the release page.
		_("Gagal mengunduh pembaruan. Kamu bisa mengunduhnya sendiri dari {url}").format(url=release.pageUrl),
		# Translators: Title of the update check dialogs.
		_("Pembaruan Emoji ID"),
	)
