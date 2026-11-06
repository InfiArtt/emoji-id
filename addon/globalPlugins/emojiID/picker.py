# Emoji ID - Indonesian Emoji Reader for NVDA
# Copyright (C) 2026 Rexya Muhamad <rexya2017@gmail.com>
# This file is covered by the GNU General Public License v2 or later.
# See the file LICENSE for more details.

"""The insert emoji dialog, modelled on the Windows 11 emoji panel.

It is opened only through its command in Input Gestures, which has no default gesture.
The dialog closes after inserting; the text is then pasted into the control that had focus.
"""

from collections.abc import Callable

import addonHandler
import api
import core
import gui
import ui
import wx
from gui import guiHelper
from gui.message import MessageDialog
from keyboardHandler import KeyboardInputGesture
from logHandler import log

from . import pickerData
from .pickerCategories import EMOJI_CATEGORIES, KAOMOJI_CATEGORIES, SKIN_TONES, SUBGROUPS, SYMBOL_CATEGORIES
from .settings import getConfig

addonHandler.initTranslation()

#: How many items "Terakhir dipakai" keeps.
RECENT_LIMIT = 30
#: Delay before pasting, so that focus is back in the application the dialog was opened from.
_PASTE_DELAY_MS = 300
#: Delay before the previous clipboard text is put back.
_RESTORE_CLIPBOARD_DELAY_MS = 800

_CATEGORIES = {
	pickerData.KIND_EMOJI: EMOJI_CATEGORIES,
	pickerData.KIND_SYMBOL: SYMBOL_CATEGORIES,
	pickerData.KIND_KAOMOJI: KAOMOJI_CATEGORIES,
}
_CATEGORY_RECENT = "recent"
_CATEGORY_FAVORITES = "favorites"

_data: pickerData.PickerData | None = None
_isOpen = False


def _getData() -> pickerData.PickerData:
	global _data
	if _data is None:
		_data = pickerData.loadPickerData()
	return _data


def openPicker(nameOf: Callable[[str], str | None]) -> None:
	"""Show the insert emoji dialog. Must be called on the GUI thread."""
	global _isOpen
	if _isOpen:
		return
	_isOpen = True
	try:
		dialog = EmojiPickerDialog(gui.mainFrame, _getData(), nameOf)
	except Exception:
		_isOpen = False
		log.error("Emoji ID: could not open the insert emoji dialog", exc_info=True)
		return
	gui.mainFrame.prePopup()
	try:
		dialog.ShowModal()
		text, shouldPaste = dialog.result
	finally:
		dialog.Destroy()
		gui.mainFrame.postPopup()
		_isOpen = False
	if text:
		wx.CallLater(_PASTE_DELAY_MS, insertText if shouldPaste else copyText, text)


def copyText(text: str) -> None:
	if api.copyToClip(text):
		# Translators: Announced after the chosen emoji were copied from the insert emoji dialog.
		ui.message(_("Disalin ke papan klip"))


def insertText(text: str) -> None:
	"""Paste text into the focused control, then put the previous clipboard text back."""
	try:
		previous = api.getClipData()
	except Exception:
		previous = None
	if not api.copyToClip(text):
		# Translators: Announced when the chosen emoji could not be inserted.
		ui.message(_("Gagal menyisipkan emoji"))
		return
	KeyboardInputGesture.fromName("control+v").send()
	if previous:
		core.callLater(_RESTORE_CLIPBOARD_DELAY_MS, api.copyToClip, previous)


class EmojiPickerDialog(wx.Dialog):
	"""Search, browse and insert emoji, symbols and kaomoji."""

	def __init__(
		self, parent: wx.Window, data: pickerData.PickerData, nameOf: Callable[[str], str | None]
	) -> None:
		# Translators: Title of the insert emoji dialog.
		super().__init__(parent, title=_("Sisipkan Emoji - Emoji ID"))
		self._data = data
		self._nameOf = nameOf
		self._chain: list[pickerData.Entry] = []
		self._rows: list[pickerData.Entry] = []
		self._emojiCacheKey: tuple | None = None
		self._emojiCache: list[pickerData.Entry] = []
		#: (text, shouldPaste) once the user inserts or copies.
		self.result: tuple[str, bool] = ("", False)
		conf = getConfig()

		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		self.kindChoice = sHelper.addLabeledControl(
			# Translators: Label of the choice between emoji, symbols and kaomoji in the insert emoji dialog.
			_("Jenis:"),
			wx.Choice,
			choices=[
				# Translators: Kind of items in the insert emoji dialog.
				_("Emoji"),
				# Translators: Kind of items in the insert emoji dialog.
				_("Simbol"),
				# Translators: Kind of items in the insert emoji dialog.
				_("Kaomoji"),
			],
		)
		self.kindChoice.SetSelection(0)
		# Translators: Label of the search field in the insert emoji dialog.
		self.searchField = sHelper.addLabeledControl(_("Cari:"), wx.TextCtrl)
		# Translators: Label of the category choice in the insert emoji dialog.
		self.categoryChoice = sHelper.addLabeledControl(_("Kategori:"), wx.Choice, choices=[])
		# Translators: Label of the subcategory choice in the insert emoji dialog.
		self.subgroupChoice = sHelper.addLabeledControl(_("Subkategori:"), wx.Choice, choices=[])
		self.resultsList = sHelper.addLabeledControl(
			# Translators: Label of the results list in the insert emoji dialog.
			_("Hasil:"),
			wx.ListBox,
			size=(420, 220),
		)
		self.toneChoice = sHelper.addLabeledControl(
			# Translators: Label of the skin tone choice in the insert emoji dialog.
			_("Warna kulit:"),
			wx.Choice,
			choices=list(SKIN_TONES),
		)
		self.toneChoice.SetSelection(conf["pickerSkinTone"])
		self.secondToneChoice = sHelper.addLabeledControl(
			# Translators: Label of the skin tone choice for the second person in two person emoji.
			_("Warna kulit orang kedua:"),
			wx.Choice,
			choices=[
				# Translators: Choice that gives the second person the same skin tone as the first.
				_("Sama dengan orang pertama"),
				*SKIN_TONES[1:],
			],
		)
		self.secondToneChoice.SetSelection(conf["pickerSecondSkinTone"])
		self.genderChoice = sHelper.addLabeledControl(
			# Translators: Label of the gender choice in the insert emoji dialog.
			_("Jenis kelamin:"),
			wx.Choice,
			choices=[
				# Translators: Gender choice in the insert emoji dialog.
				_("Netral"),
				# Translators: Gender choice in the insert emoji dialog.
				_("Pria"),
				# Translators: Gender choice in the insert emoji dialog.
				_("Wanita"),
			],
		)
		self.genderChoice.SetSelection(pickerData.GENDERS.index(conf["pickerGender"]))
		self.directionChoice = sHelper.addLabeledControl(
			# Translators: Label of the direction choice in the insert emoji dialog.
			_("Arah:"),
			wx.Choice,
			choices=[
				# Translators: Direction choice in the insert emoji dialog.
				_("Bawaan"),
				# Translators: Direction choice in the insert emoji dialog.
				_("Menghadap kanan"),
			],
		)
		self.directionChoice.SetSelection(0)
		self.chainField = sHelper.addLabeledControl(
			# Translators: Label of the read-only field listing the emoji collected to insert together.
			_("Rangkaian:"),
			wx.TextCtrl,
			style=wx.TE_READONLY | wx.TE_MULTILINE,
			size=(420, 50),
		)

		actions = guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: Button that inserts the chosen emoji and closes the dialog.
		self.insertButton = actions.addButton(self, label=_("Sisipkan"))
		# Translators: Button that adds the selected emoji to the collection.
		self.addToChainButton = actions.addButton(self, label=_("Tambah ke Rangkaian"))
		# Translators: Button that removes the last emoji from the collection.
		self.removeLastButton = actions.addButton(self, label=_("Hapus Terakhir"))
		# Translators: Button that empties the collection.
		self.clearChainButton = actions.addButton(self, label=_("Kosongkan Rangkaian"))
		sHelper.addItem(actions)
		more = guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: Button that copies the chosen emoji to the clipboard and closes the dialog.
		self.copyButton = more.addButton(self, label=_("Salin"))
		# Translators: Button that adds the selected item to the favorites.
		self.favoriteButton = more.addButton(self, label=_("Tambah ke Favorit"))
		# Translators: Button that reads details about the selected item.
		self.detailButton = more.addButton(self, label=_("Detail"))
		# Translators: Button that closes the insert emoji dialog.
		self.closeButton = more.addButton(self, wx.ID_CANCEL, label=_("Tutup"))
		sHelper.addItem(more)

		mainSizer.Add(sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		self.SetSizerAndFit(mainSizer)
		self.insertButton.SetDefault()
		self.SetEscapeId(wx.ID_CANCEL)

		self.kindChoice.Bind(wx.EVT_CHOICE, self._onKindChanged)
		self.searchField.Bind(wx.EVT_TEXT, self._onFilterChanged)
		self.categoryChoice.Bind(wx.EVT_CHOICE, self._onCategoryChanged)
		self.subgroupChoice.Bind(wx.EVT_CHOICE, self._onFilterChanged)
		for choice in (self.toneChoice, self.secondToneChoice, self.genderChoice, self.directionChoice):
			choice.Bind(wx.EVT_CHOICE, self._onVariantChanged)
		self.resultsList.Bind(wx.EVT_LISTBOX, self._onSelectionChanged)
		self.resultsList.Bind(wx.EVT_LISTBOX_DCLICK, self._onInsert)
		self.insertButton.Bind(wx.EVT_BUTTON, self._onInsert)
		self.copyButton.Bind(wx.EVT_BUTTON, self._onCopy)
		self.addToChainButton.Bind(wx.EVT_BUTTON, self._onAddToChain)
		self.removeLastButton.Bind(wx.EVT_BUTTON, self._onRemoveLast)
		self.clearChainButton.Bind(wx.EVT_BUTTON, self._onClearChain)
		self.favoriteButton.Bind(wx.EVT_BUTTON, self._onToggleFavorite)
		self.detailButton.Bind(wx.EVT_BUTTON, self._onDetail)

		self._fillCategories()
		self.CentreOnScreen()
		self.searchField.SetFocus()

	# Filling the controls

	@property
	def _kind(self) -> str:
		return pickerData.KINDS[self.kindChoice.GetSelection()]

	def _categoryKeys(self) -> list[str]:
		return list(_CATEGORIES[self._kind])

	def _fillCategories(self) -> None:
		categories = _CATEGORIES[self._kind]
		self.categoryChoice.SetItems(list(categories.values()))
		recent = self._history(_CATEGORY_RECENT)
		# Start at the recent items when there are any, like the Windows emoji panel.
		self.categoryChoice.SetSelection(0 if recent else 2)
		isEmoji = self._kind == pickerData.KIND_EMOJI
		for control in (
			self.subgroupChoice,
			self.toneChoice,
			self.secondToneChoice,
			self.genderChoice,
			self.directionChoice,
		):
			control.Enable(isEmoji)
		self._fillSubgroups()

	def _fillSubgroups(self) -> None:
		# Translators: First choice of the subcategory list, showing every subcategory.
		choices = [_("Semua subkategori")]
		self._subgroupKeys: list[str] = [""]
		category = self._categoryKeys()[self.categoryChoice.GetSelection()]
		if self._kind == pickerData.KIND_EMOJI:
			for item in self._data.emoji:
				if item.category == category and item.subgroup not in self._subgroupKeys:
					self._subgroupKeys.append(item.subgroup)
					choices.append(SUBGROUPS.get(item.subgroup, item.subgroup))
		self.subgroupChoice.SetItems(choices)
		self.subgroupChoice.SetSelection(0)
		self._fillResults()

	def _variantChoices(self) -> tuple[str, bool, int, int]:
		return (
			pickerData.GENDERS[self.genderChoice.GetSelection()],
			self.directionChoice.GetSelection() == 1,
			self.toneChoice.GetSelection(),
			self.secondToneChoice.GetSelection(),
		)

	def _emojiEntries(self) -> list[pickerData.Entry]:
		key = self._variantChoices()
		if key != self._emojiCacheKey:
			self._emojiCache = pickerData.emojiEntries(self._data, self._nameOf, *key)
			self._emojiCacheKey = key
		return self._emojiCache

	def _allEntries(self) -> list[pickerData.Entry]:
		if self._kind == pickerData.KIND_EMOJI:
			return self._emojiEntries()
		return self._data.symbols if self._kind == pickerData.KIND_SYMBOL else self._data.kaomoji

	def _history(self, category: str) -> list[pickerData.Entry]:
		key = "pickerRecent" if category == _CATEGORY_RECENT else "pickerFavorites"
		rows = pickerData.entriesFromHistory(getConfig()[key], self._allKindsEntries(), self._nameOf)
		return [row for row in rows if row.kind == self._kind]

	def _allKindsEntries(self) -> list[pickerData.Entry]:
		return [*self._emojiEntries(), *self._data.symbols, *self._data.kaomoji]

	def _fillResults(self) -> None:
		query = self.searchField.GetValue()
		if query.strip():
			# Like the Windows emoji panel, search looks through every category of the current kind.
			rows = pickerData.search(self._allEntries(), query)
		else:
			category = self._categoryKeys()[self.categoryChoice.GetSelection()]
			if category in (_CATEGORY_RECENT, _CATEGORY_FAVORITES):
				rows = self._history(category)
			else:
				subgroup = self._subgroupKeys[self.subgroupChoice.GetSelection()]
				rows = [
					entry
					for entry in self._allEntries()
					if entry.category == category and (not subgroup or entry.subgroup == subgroup)
				]
		self._rows = rows
		# Translators: Shown in the results list when nothing matches.
		names = [row.name for row in rows] or [_("Tidak ada hasil")]
		self.resultsList.SetItems(names)
		self.resultsList.SetSelection(0)
		self._updateFavoriteButton()

	# Events

	def _onKindChanged(self, evt: wx.CommandEvent) -> None:
		self._fillCategories()

	def _onCategoryChanged(self, evt: wx.CommandEvent) -> None:
		self._fillSubgroups()

	def _onFilterChanged(self, evt: wx.CommandEvent) -> None:
		self._fillResults()

	def _onVariantChanged(self, evt: wx.CommandEvent) -> None:
		selection = self.resultsList.GetSelection()
		self._fillResults()
		if 0 <= selection < self.resultsList.GetCount():
			self.resultsList.SetSelection(selection)
		self._updateFavoriteButton()

	def _onSelectionChanged(self, evt: wx.CommandEvent) -> None:
		self._updateFavoriteButton()

	def _selected(self) -> pickerData.Entry | None:
		index = self.resultsList.GetSelection()
		return self._rows[index] if 0 <= index < len(self._rows) else None

	def _updateFavoriteButton(self) -> None:
		entry = self._selected()
		isFavorite = entry is not None and pickerData.encodeText(entry.text) in getConfig()["pickerFavorites"]
		self.favoriteButton.SetLabel(
			# Translators: Button that removes the selected item from the favorites.
			_("Hapus dari Favorit")
			if isFavorite
			# Translators: Button that adds the selected item to the favorites.
			else _("Tambah ke Favorit"),
		)

	def _chosenEntries(self) -> list[pickerData.Entry]:
		if self._chain:
			return list(self._chain)
		entry = self._selected()
		return [entry] if entry else []

	def _finish(self, shouldPaste: bool) -> None:
		entries = self._chosenEntries()
		if not entries:
			# Translators: Announced when nothing is selected in the insert emoji dialog.
			ui.message(_("Tidak ada yang dipilih"))
			return
		conf = getConfig()
		recent = list(conf["pickerRecent"])
		for entry in reversed(entries):
			recent = pickerData.addToHistory(recent, entry.text, RECENT_LIMIT)
		conf["pickerRecent"] = recent
		conf["pickerSkinTone"] = self.toneChoice.GetSelection()
		conf["pickerSecondSkinTone"] = self.secondToneChoice.GetSelection()
		conf["pickerGender"] = pickerData.GENDERS[self.genderChoice.GetSelection()]
		self.result = ("".join(entry.text for entry in entries), shouldPaste)
		self.EndModal(wx.ID_OK)

	def _onInsert(self, evt: wx.CommandEvent) -> None:
		self._finish(shouldPaste=True)

	def _onCopy(self, evt: wx.CommandEvent) -> None:
		self._finish(shouldPaste=False)

	def _updateChainField(self) -> None:
		self.chainField.SetValue(", ".join(entry.name for entry in self._chain))

	def _onAddToChain(self, evt: wx.CommandEvent) -> None:
		entry = self._selected()
		if entry is None:
			return
		self._chain.append(entry)
		self._updateChainField()
		# Translators: Announced when an item is added to the collection. {name} is its name,
		# {count} the number of items now in the collection.
		ui.message(
			_("{name} ditambahkan, {count} dalam rangkaian").format(name=entry.name, count=len(self._chain))
		)

	def _onRemoveLast(self, evt: wx.CommandEvent) -> None:
		if not self._chain:
			# Translators: Announced when the collection is already empty.
			ui.message(_("Rangkaian kosong"))
			return
		entry = self._chain.pop()
		self._updateChainField()
		# Translators: Announced when the last item is removed from the collection. {name} is its name.
		ui.message(_("{name} dihapus dari rangkaian").format(name=entry.name))

	def _onClearChain(self, evt: wx.CommandEvent) -> None:
		self._chain.clear()
		self._updateChainField()
		# Translators: Announced when the collection is emptied.
		ui.message(_("Rangkaian dikosongkan"))

	def _onToggleFavorite(self, evt: wx.CommandEvent) -> None:
		entry = self._selected()
		if entry is None:
			return
		conf = getConfig()
		favorites = list(conf["pickerFavorites"])
		encoded = pickerData.encodeText(entry.text)
		if encoded in favorites:
			favorites.remove(encoded)
			# Translators: Announced when an item is removed from the favorites. {name} is its name.
			message = _("{name} dihapus dari favorit").format(name=entry.name)
		else:
			favorites = pickerData.addToHistory(favorites, entry.text)
			# Translators: Announced when an item is added to the favorites. {name} is its name.
			message = _("{name} ditambahkan ke favorit").format(name=entry.name)
		conf["pickerFavorites"] = favorites
		self._updateFavoriteButton()
		ui.message(message)

	def _onDetail(self, evt: wx.CommandEvent) -> None:
		entry = self._selected()
		if entry is None:
			return
		categories = _CATEGORIES[entry.kind]
		lines = [
			# Translators: Line of the details of an item. {name} is its name.
			_("Nama: {name}").format(name=entry.name),
			# Translators: Line of the details of an item. {code} is its Unicode code points.
			_("Kode Unicode: {code}").format(code=" ".join(f"U+{ord(ch):04X}" for ch in entry.text)),
		]
		if entry.category in categories:
			# Translators: Line of the details of an item. {category} is its category.
			lines.append(_("Kategori: {category}").format(category=categories[entry.category]))
		if entry.subgroup in SUBGROUPS:
			# Translators: Line of the details of an item. {subgroup} is its subcategory.
			lines.append(_("Subkategori: {subgroup}").format(subgroup=SUBGROUPS[entry.subgroup]))
		if entry.keywords:
			# Translators: Line of the details of an item. {keywords} lists its search keywords.
			lines.append(_("Kata kunci: {keywords}").format(keywords=", ".join(entry.keywords)))
		# Translators: Title of the dialog with the details of an item.
		MessageDialog.alert("\n".join(lines), _("Detail"), parent=self)
