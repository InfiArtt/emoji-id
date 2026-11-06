# Emoji ID - Indonesian Emoji Reader for NVDA
# Copyright (C) 2026 Rexya Muhamad <rexya2017@gmail.com>
# This file is covered by the GNU General Public License v2 or later.
# See the file LICENSE for more details.

"""The insert emoji dialog, modelled on the Windows 11 emoji panel.

It is opened only through its command in Input Gestures, which has no default gesture.
The dialog closes after inserting; the text is then pasted into the control that had focus.

Every shortcut of the dialog has a visible button whose label names the shortcut,
except tab and focus moves, which F1 lists.
"""

from collections.abc import Callable

import addonHandler
import api
import controlTypes
import core
import gui
import ui
import wx
from gui import guiHelper
from gui.message import MessageDialog
from keyboardHandler import KeyboardInputGesture
from logHandler import log
from NVDAObjects import NVDAObject
from NVDAObjects.behaviors import EditableText, Terminal

from . import pickerData
from .emojiData import cleanNameSymbols
from .pickerCategories import EMOJI_CATEGORIES, KAOMOJI_CATEGORIES, SKIN_TONES, SUBGROUPS, SYMBOL_CATEGORIES
from .settings import getConfig

addonHandler.initTranslation()

#: How many items "Terakhir dipakai" keeps.
RECENT_LIMIT = 30
#: Delay before pasting, so that focus is back in the application the dialog was opened from.
_PASTE_DELAY_MS = 300
#: Delay before the previous clipboard text is put back.
_RESTORE_CLIPBOARD_DELAY_MS = 800
#: Delay before the results follow a change of search text, category or subcategory.
_REFRESH_DELAY_MS = 250
#: Delay before the subcategory name is spoken after a jump, so that it follows the new item.
_ANNOUNCE_DELAY_MS = 100

_CATEGORIES = {
	pickerData.KIND_EMOJI: EMOJI_CATEGORIES,
	pickerData.KIND_SYMBOL: SYMBOL_CATEGORIES,
	pickerData.KIND_KAOMOJI: KAOMOJI_CATEGORIES,
}
_CATEGORY_RECENT = "recent"
_CATEGORY_FAVORITES = "favorites"

#: What the user does with an emoji, in the insert emoji and personalize dialogs.
ACTION_INSERT = "insert"
ACTION_ADD_TO_CHAIN = "addToChain"
ACTION_COPY = "copy"

_ENTER_KEYS = (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER)

_data: pickerData.PickerData | None = None
_emojiEntries: list[pickerData.Entry] | None = None
_isOpen = False


def _getData() -> pickerData.PickerData:
	global _data
	if _data is None:
		_data = pickerData.loadPickerData()
	return _data


def _getEmojiEntries(
	data: pickerData.PickerData, nameOf: Callable[[str], str | None]
) -> list[pickerData.Entry]:
	"""Rows for all emoji, named once and kept while NVDA runs."""
	global _emojiEntries
	if _emojiEntries is None:
		_emojiEntries = pickerData.emojiEntries(data, nameOf)
	return _emojiEntries


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


def isTypingPlace(obj: NVDAObject | None) -> bool:
	"""Whether text pasted into this focus object would be typed there.

	Editable text, editable documents (Word, email bodies, web text fields) and terminals count.
	Read-only text, buttons, lists, menus and web pages in browse mode outside a text field do not.
	"""
	if obj is None:
		return False
	role = obj.role
	if role == controlTypes.Role.TERMINAL or isinstance(obj, Terminal):
		return True
	states = obj.states
	if controlTypes.State.READONLY in states:
		return False
	return (
		controlTypes.State.EDITABLE in states
		or role == controlTypes.Role.EDITABLETEXT
		or isinstance(obj, EditableText)
	)


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


def _isKey(
	evt: wx.KeyEvent, keys: tuple[int, ...], ctrl: bool = False, shift: bool = False, alt: bool = False
) -> bool:
	return (
		evt.GetKeyCode() in keys
		and evt.ControlDown() == ctrl
		and evt.ShiftDown() == shift
		and evt.AltDown() == alt
	)


class PersonalizeDialog(wx.Dialog):
	"""Choose skin tones, gender and direction for one emoji, opened with Shift+Enter.

	Only the choices this emoji supports are shown.
	"""

	def __init__(
		self,
		parent: wx.Window,
		entry: pickerData.Entry,
		nameOf: Callable[[str], str | None],
	) -> None:
		# Translators: Title of the dialog for choosing skin tone, gender and direction of an emoji.
		super().__init__(parent, title=_("Personalisasi Emoji"))
		assert entry.item is not None
		self._item = entry.item
		self._nameOf = nameOf
		#: The chosen emoji text and action, set when the dialog is confirmed.
		self.text = entry.text
		self.action = ACTION_INSERT
		conf = getConfig()

		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: Introduction of the personalize emoji dialog. {name} is the emoji name.
		sHelper.addItem(wx.StaticText(self, label=_("Emoji: {name}").format(name=entry.name)))

		self.toneChoice = self.secondToneChoice = self.genderChoice = self.directionChoice = None
		genders = self._item.genders()
		self._genders = genders
		if len(genders) > 1:
			labels = {
				# Translators: Gender choice in the personalize emoji dialog.
				pickerData.GENDER_NEUTRAL: _("Netral"),
				# Translators: Gender choice in the personalize emoji dialog.
				pickerData.GENDER_MALE: _("Pria"),
				# Translators: Gender choice in the personalize emoji dialog.
				pickerData.GENDER_FEMALE: _("Wanita"),
			}
			self.genderChoice = sHelper.addLabeledControl(
				# Translators: Label of the gender choice in the personalize emoji dialog.
				_("Jenis kelamin:"),
				wx.Choice,
				choices=[labels[gender] for gender in genders],
			)
			saved = conf["pickerGender"]
			self.genderChoice.SetSelection(genders.index(saved) if saved in genders else 0)
		if self._item.canFaceRight():
			self.directionChoice = sHelper.addLabeledControl(
				# Translators: Label of the direction choice in the personalize emoji dialog.
				_("Arah:"),
				wx.Choice,
				choices=[
					# Translators: Direction choice in the personalize emoji dialog.
					_("Bawaan"),
					# Translators: Direction choice in the personalize emoji dialog.
					_("Menghadap kanan"),
				],
			)
			self.directionChoice.SetSelection(0)
		slots = max(self._item.toneSlots(gender) for gender in genders)
		if slots:
			self.toneChoice = sHelper.addLabeledControl(
				# Translators: Label of the skin tone choice in the personalize emoji dialog.
				_("Warna kulit:")
				if slots == 1
				# Translators: Label of the first person's skin tone choice in two person emoji.
				else _("Warna kulit orang pertama:"),
				wx.Choice,
				choices=list(SKIN_TONES),
			)
			self.toneChoice.SetSelection(conf["pickerSkinTone"])
		if slots == 2:
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
		self.resultField = sHelper.addLabeledControl(
			# Translators: Label of the read-only field naming the personalized emoji.
			_("Hasil:"),
			wx.TextCtrl,
			style=wx.TE_READONLY,
			size=(380, -1),
		)

		buttons = guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: Button that inserts the personalized emoji. Enter is its shortcut.
		self.insertButton = buttons.addButton(self, label=_("Sisipkan (Enter)"))
		# Translators: Button adding the personalized emoji to the collection. Control+Enter is its shortcut.
		self.addToChainButton = buttons.addButton(self, label=_("Tambah ke Rangkaian (Ctrl+Enter)"))
		# Translators: Button that copies the personalized emoji. Control+Shift+C is its shortcut.
		self.copyButton = buttons.addButton(self, label=_("Salin (Ctrl+Shift+C)"))
		# Translators: Button that closes the personalize emoji dialog. Escape is its shortcut.
		buttons.addButton(self, wx.ID_CANCEL, label=_("Batal (Escape)"))
		sHelper.addItem(buttons)
		mainSizer.Add(sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		self.SetSizerAndFit(mainSizer)
		self.insertButton.SetDefault()
		self.SetEscapeId(wx.ID_CANCEL)

		for choice in (self.genderChoice, self.directionChoice, self.toneChoice, self.secondToneChoice):
			if choice is not None:
				choice.Bind(wx.EVT_CHOICE, self._onOptionChanged)
		self.insertButton.Bind(wx.EVT_BUTTON, lambda evt: self._confirm(ACTION_INSERT))
		self.addToChainButton.Bind(wx.EVT_BUTTON, lambda evt: self._confirm(ACTION_ADD_TO_CHAIN))
		self.copyButton.Bind(wx.EVT_BUTTON, lambda evt: self._confirm(ACTION_COPY))
		self.Bind(wx.EVT_CHAR_HOOK, self._onCharHook)
		self._updateResult()
		self.CentreOnScreen()
		first = self.genderChoice or self.directionChoice or self.toneChoice
		if first is not None:
			first.SetFocus()

	def _onCharHook(self, evt: wx.KeyEvent) -> None:
		if _isKey(evt, _ENTER_KEYS, ctrl=True):
			self._confirm(ACTION_ADD_TO_CHAIN)
		elif _isKey(evt, (ord("C"),), ctrl=True, shift=True):
			self._confirm(ACTION_COPY)
		else:
			evt.Skip()

	def _resolve(self) -> str:
		gender = self._genders[self.genderChoice.GetSelection()] if self.genderChoice else ""
		isFacingRight = bool(self.directionChoice and self.directionChoice.GetSelection() == 1)
		tone = self.toneChoice.GetSelection() if self.toneChoice else 0
		secondTone = self.secondToneChoice.GetSelection() if self.secondToneChoice else 0
		return self._item.resolve(gender, isFacingRight, tone, secondTone)

	def _updateResult(self) -> None:
		text = self._resolve()
		self.resultField.SetValue(cleanNameSymbols(self._nameOf(text) or text))

	def _onOptionChanged(self, evt: wx.CommandEvent) -> None:
		self._updateResult()

	def _confirm(self, action: str) -> None:
		self.text = self._resolve()
		self.action = action
		conf = getConfig()
		if self.toneChoice:
			conf["pickerSkinTone"] = self.toneChoice.GetSelection()
		if self.secondToneChoice:
			conf["pickerSecondSkinTone"] = self.secondToneChoice.GetSelection()
		if self.genderChoice:
			conf["pickerGender"] = self._genders[self.genderChoice.GetSelection()]
		self.EndModal(wx.ID_OK)


class ResultsList(wx.ListCtrl):
	"""A one column list view of names.

	Unlike a list box, a list view gives NVDA the position of each item ("5 dari 140"),
	and left and right arrows do not move between items. The list is virtual: names are only
	asked for when shown, so long lists stay fast.
	"""

	def __init__(self, parent: wx.Window) -> None:
		super().__init__(
			parent,
			style=wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_SINGLE_SEL | wx.LC_NO_HEADER,
			size=(420, 220),
		)
		self.InsertColumn(0, "")
		self.SetColumnWidth(0, 400)
		self.names: list[str] = []

	def setNames(self, names: list[str]) -> None:
		self.names = names
		self.SetItemCount(len(names))
		self.Refresh()
		if names:
			self.selectIndex(0)

	def OnGetItemText(self, item: int, column: int) -> str:
		return self.names[item] if 0 <= item < len(self.names) else ""

	def selectedIndex(self) -> int:
		return self.GetFirstSelected()

	def selectIndex(self, index: int) -> None:
		self.Select(index)
		self.Focus(index)
		self.EnsureVisible(index)


class KindPage(wx.Panel):
	"""One tab of the insert emoji dialog: search, category, subcategory and results for one kind."""

	def __init__(self, notebook: wx.Notebook, dialog: "EmojiPickerDialog", kind: str) -> None:
		super().__init__(notebook)
		self._dialog = dialog
		self.kind = kind
		self.rows: list[pickerData.Entry] = []
		self._subgroupKeys: list[str] = [""]
		self._refreshTimer: wx.CallLater | None = None

		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: Label of the search field in the insert emoji dialog.
		self.searchField = sHelper.addLabeledControl(_("Cari:"), wx.TextCtrl)
		# Translators: Label of the category choice in the insert emoji dialog.
		self.categoryChoice = sHelper.addLabeledControl(_("Kategori:"), wx.Choice, choices=[])
		self.subgroupChoice = None
		if kind == pickerData.KIND_EMOJI:
			# Translators: Label of the subcategory choice in the insert emoji dialog.
			self.subgroupChoice = sHelper.addLabeledControl(_("Subkategori:"), wx.Choice, choices=[])
		# Translators: Label of the results list in the insert emoji dialog.
		sHelper.addItem(wx.StaticText(self, label=_("Hasil:")))
		self.resultsList = sHelper.addItem(ResultsList(self))
		self.SetSizer(sHelper.sizer)

		self.searchField.Bind(wx.EVT_TEXT, self._onFilterChanged)
		self.categoryChoice.Bind(wx.EVT_CHOICE, self._onCategoryChanged)
		if self.subgroupChoice is not None:
			self.subgroupChoice.Bind(wx.EVT_CHOICE, self._onFilterChanged)
		self.resultsList.Bind(wx.EVT_LIST_ITEM_SELECTED, self._onSelectionChanged)
		self.resultsList.Bind(wx.EVT_KEY_DOWN, self._onListKeyDown)

		categories = _CATEGORIES[kind]
		self.categoryChoice.SetItems(list(categories.values()))
		# Start at the recent items when there are any, like the Windows emoji panel.
		self.categoryChoice.SetSelection(0 if self._dialog.history(kind, _CATEGORY_RECENT) else 2)
		self._fillSubgroups()
		self.fillResults()

	def _categoryKey(self) -> str:
		return list(_CATEGORIES[self.kind])[self.categoryChoice.GetSelection()]

	def _subgroupKey(self) -> str:
		if self.subgroupChoice is None:
			return ""
		return self._subgroupKeys[self.subgroupChoice.GetSelection()]

	def _fillSubgroups(self) -> None:
		if self.subgroupChoice is None:
			return
		# Translators: First choice of the subcategory list, showing every subcategory.
		choices = [_("Semua subkategori")]
		self._subgroupKeys = [""]
		category = self._categoryKey()
		for item in self._dialog.data.emoji:
			if item.category == category and item.subgroup not in self._subgroupKeys:
				self._subgroupKeys.append(item.subgroup)
				choices.append(SUBGROUPS.get(item.subgroup, item.subgroup))
		self.subgroupChoice.SetItems(choices)
		self.subgroupChoice.SetSelection(0)

	def _allEntries(self) -> list[pickerData.Entry]:
		return self._dialog.entries(self.kind)

	def _isSearching(self) -> bool:
		return bool(self.searchField.GetValue().strip())

	def fillResults(self) -> None:
		if self._isSearching():
			# Like the Windows emoji panel, search looks through every category of this kind.
			rows = pickerData.search(self._allEntries(), self.searchField.GetValue())
		else:
			category = self._categoryKey()
			if category in (_CATEGORY_RECENT, _CATEGORY_FAVORITES):
				rows = self._dialog.history(self.kind, category)
			else:
				subgroup = self._subgroupKey()
				rows = [
					entry
					for entry in self._allEntries()
					if entry.category == category and (not subgroup or entry.subgroup == subgroup)
				]
		self.rows = rows
		# Translators: Shown in the results list when nothing matches.
		self.resultsList.setNames([self._dialog.rowName(row) for row in rows] or [_("Tidak ada hasil")])
		self._dialog.updateButtons()

	def selected(self) -> pickerData.Entry | None:
		index = self.resultsList.selectedIndex()
		return self.rows[index] if 0 <= index < len(self.rows) else None

	def _scheduleRefresh(self) -> None:
		"""Refresh shortly after the last change, so that arrowing through choices stays fast."""
		if self._refreshTimer is not None and self._refreshTimer.IsRunning():
			self._refreshTimer.Restart(_REFRESH_DELAY_MS)
		else:
			self._refreshTimer = wx.CallLater(_REFRESH_DELAY_MS, self.fillResults)

	def _onCategoryChanged(self, evt: wx.CommandEvent) -> None:
		self._fillSubgroups()
		self._scheduleRefresh()

	def _onFilterChanged(self, evt: wx.CommandEvent) -> None:
		self._scheduleRefresh()

	def _onSelectionChanged(self, evt: wx.ListEvent) -> None:
		self._dialog.updateButtons()

	def _onListKeyDown(self, evt: wx.KeyEvent) -> None:
		if _isKey(evt, (wx.WXK_RIGHT,)):
			self.jumpSubgroup(1)
		elif _isKey(evt, (wx.WXK_LEFT,)):
			self.jumpSubgroup(-1)
		else:
			evt.Skip()

	def jumpSubgroup(self, direction: int) -> None:
		"""Move to the first item of the next or previous subcategory, without filtering the list.

		Only emoji listed with every subcategory are grouped by subcategory; elsewhere the keys do nothing.
		"""
		if self.kind != pickerData.KIND_EMOJI or self._isSearching() or self._subgroupKey():
			return
		if self._categoryKey() in (_CATEGORY_RECENT, _CATEGORY_FAVORITES) or not self.rows:
			return
		starts = [
			index
			for index, row in enumerate(self.rows)
			if index == 0 or row.subgroup != self.rows[index - 1].subgroup
		]
		current = max(0, self.resultsList.selectedIndex())
		currentStart = max(start for start in starts if start <= current)
		position = starts.index(currentStart) + direction
		if position < 0:
			# Translators: Announced when the left arrow is pressed in the first subcategory of the list.
			ui.message(_("Subkategori pertama"))
			return
		if position >= len(starts):
			# Translators: Announced when the right arrow is pressed in the last subcategory of the list.
			ui.message(_("Subkategori terakhir"))
			return
		target = starts[position]
		self.resultsList.selectIndex(target)
		name = SUBGROUPS.get(self.rows[target].subgroup, self.rows[target].subgroup)
		# NVDA speaks the newly selected item first; the subcategory follows it.
		wx.CallLater(_ANNOUNCE_DELAY_MS, ui.message, name)


class EmojiPickerDialog(wx.Dialog):
	"""Search, browse and insert emoji, symbols and kaomoji, in three tabs."""

	def __init__(
		self, parent: wx.Window, data: pickerData.PickerData, nameOf: Callable[[str], str | None]
	) -> None:
		# Translators: Title of the insert emoji dialog.
		super().__init__(parent, title=_("Sisipkan Emoji - Emoji ID"))
		self.data = data
		self._nameOf = nameOf
		self._chain: list[pickerData.Entry] = []
		#: (text, shouldPaste) once the user inserts or copies.
		self.result: tuple[str, bool] = ("", False)
		#: False while the tabs are built, before the buttons exist.
		self._isReady = False

		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		self.notebook = wx.Notebook(self)
		self.pages: list[KindPage] = []
		titles = {
			# Translators: Tab of the insert emoji dialog.
			pickerData.KIND_EMOJI: _("Emoji"),
			# Translators: Tab of the insert emoji dialog.
			pickerData.KIND_SYMBOL: _("Simbol"),
			# Translators: Tab of the insert emoji dialog.
			pickerData.KIND_KAOMOJI: _("Kaomoji"),
		}
		for kind in pickerData.KINDS:
			page = KindPage(self.notebook, self, kind)
			self.notebook.AddPage(page, titles[kind])
			self.pages.append(page)
		sHelper.addItem(self.notebook)
		self.chainField = sHelper.addLabeledControl(
			# Translators: Label of the read-only field listing the emoji collected to insert together.
			_("Rangkaian:"),
			wx.TextCtrl,
			style=wx.TE_READONLY | wx.TE_MULTILINE,
			size=(420, 50),
		)

		actions = guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: Button that inserts the chosen emoji and closes the dialog. Enter is its shortcut.
		self.insertButton = actions.addButton(self, label=_("Sisipkan (Enter)"))
		# Translators: Button that opens the personalize dialog. Shift+Enter is its shortcut.
		self.personalizeButton = actions.addButton(self, label=_("Personalisasi (Shift+Enter)"))
		# Translators: Button that adds the selected emoji to the collection. Control+Enter is its shortcut.
		self.addToChainButton = actions.addButton(self, label=_("Tambah ke Rangkaian (Ctrl+Enter)"))
		# Translators: Button that removes the last emoji from the collection.
		self.removeLastButton = actions.addButton(self, label=_("Hapus Terakhir (Ctrl+Shift+Backspace)"))
		# Translators: Button that empties the collection.
		self.clearChainButton = actions.addButton(self, label=_("Kosongkan Rangkaian (Ctrl+Shift+Delete)"))
		sHelper.addItem(actions)
		more = guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: Button that copies the chosen emoji and closes. Control+Shift+C is its shortcut.
		self.copyButton = more.addButton(self, label=_("Salin (Ctrl+Shift+C)"))
		self.favoriteButton = more.addButton(self, label=self._favoriteLabel(False))
		# Translators: Button that reads details about the selected item. Alt+Enter is its shortcut.
		self.detailButton = more.addButton(self, label=_("Detail (Alt+Enter)"))
		# Translators: Button that lists the shortcuts of the insert emoji dialog. F1 is its shortcut.
		self.helpButton = more.addButton(self, label=_("Pintasan (F1)"))
		# Translators: Button that closes the insert emoji dialog. Escape is its shortcut.
		self.closeButton = more.addButton(self, wx.ID_CANCEL, label=_("Tutup (Escape)"))
		sHelper.addItem(more)

		mainSizer.Add(sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		self.SetSizerAndFit(mainSizer)
		self.SetEscapeId(wx.ID_CANCEL)

		self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._onPageChanged)
		self.insertButton.Bind(wx.EVT_BUTTON, lambda evt: self.insert())
		self.personalizeButton.Bind(wx.EVT_BUTTON, lambda evt: self.personalize())
		self.addToChainButton.Bind(wx.EVT_BUTTON, lambda evt: self.addSelectedToChain())
		self.removeLastButton.Bind(wx.EVT_BUTTON, lambda evt: self.removeLast())
		self.clearChainButton.Bind(wx.EVT_BUTTON, lambda evt: self.clearChain())
		self.copyButton.Bind(wx.EVT_BUTTON, lambda evt: self.copy())
		self.favoriteButton.Bind(wx.EVT_BUTTON, lambda evt: self.toggleFavorite())
		self.detailButton.Bind(wx.EVT_BUTTON, lambda evt: self.showDetail())
		self.helpButton.Bind(wx.EVT_BUTTON, lambda evt: self.showHelp())
		self.Bind(wx.EVT_CHAR_HOOK, self._onCharHook)

		self._isReady = True
		self.updateButtons()
		self.CentreOnScreen()
		self.page.searchField.SetFocus()

	# Shared data

	@property
	def page(self) -> KindPage:
		return self.pages[max(0, self.notebook.GetSelection())]

	def entries(self, kind: str) -> list[pickerData.Entry]:
		if kind == pickerData.KIND_EMOJI:
			return _getEmojiEntries(self.data, self._nameOf)
		return self.data.symbols if kind == pickerData.KIND_SYMBOL else self.data.kaomoji

	def history(self, kind: str, category: str) -> list[pickerData.Entry]:
		key = "pickerRecent" if category == _CATEGORY_RECENT else "pickerFavorites"
		allEntries = [*self.entries(pickerData.KIND_EMOJI), *self.data.symbols, *self.data.kaomoji]
		rows = pickerData.entriesFromHistory(getConfig()[key], allEntries, self._nameOf)
		return [row for row in rows if row.kind == kind]

	def rowName(self, entry: pickerData.Entry) -> str:
		if self._canPersonalize(entry):
			# Translators: Added after the name of an emoji that can be personalized.
			return _("{name}, dapat dipersonalisasi, tekan Shift+Enter").format(name=entry.name)
		return entry.name

	@staticmethod
	def _canPersonalize(entry: pickerData.Entry | None) -> bool:
		return (
			entry is not None
			and entry.item is not None
			and entry.item.isCustomizable()
			and entry.text == entry.item.resolve()
		)

	@staticmethod
	def _favoriteLabel(isFavorite: bool) -> str:
		if isFavorite:
			# Translators: Button removing the selected item from the favorites. Control+D is its shortcut.
			return _("Hapus dari Favorit (Ctrl+D)")
		# Translators: Button that adds the selected item to the favorites. Control+D is its shortcut.
		return _("Tambah ke Favorit (Ctrl+D)")

	def updateButtons(self) -> None:
		"""Match the buttons to the selected item."""
		if not self._isReady:
			return
		entry = self.page.selected()
		self.personalizeButton.Enable(self._canPersonalize(entry))
		isFavorite = entry is not None and pickerData.encodeText(entry.text) in getConfig()["pickerFavorites"]
		self.favoriteButton.SetLabel(self._favoriteLabel(isFavorite))

	def _onPageChanged(self, evt: wx.BookCtrlEvent) -> None:
		self.updateButtons()
		evt.Skip()

	def selectTab(self, index: int) -> None:
		self.notebook.SetSelection(index)
		self.updateButtons()
		self.page.searchField.SetFocus()

	# Keyboard

	def _onCharHook(self, evt: wx.KeyEvent) -> None:
		key = evt.GetKeyCode()
		focus = wx.Window.FindFocus()
		if _isKey(evt, _ENTER_KEYS) and not isinstance(focus, wx.Button):
			self.insert()
		elif _isKey(evt, _ENTER_KEYS, shift=True):
			self.personalize()
		elif _isKey(evt, _ENTER_KEYS, ctrl=True):
			self.addSelectedToChain()
		elif _isKey(evt, _ENTER_KEYS, alt=True):
			self.showDetail()
		elif _isKey(evt, (ord("D"),), ctrl=True):
			self.toggleFavorite()
		elif _isKey(evt, (ord("C"),), ctrl=True, shift=True):
			self.copy()
		elif _isKey(evt, (wx.WXK_BACK,), ctrl=True, shift=True):
			self.removeLast()
		elif _isKey(evt, (wx.WXK_DELETE, wx.WXK_NUMPAD_DELETE), ctrl=True, shift=True):
			self.clearChain()
		elif _isKey(evt, (ord("R"),), ctrl=True):
			self.readChain()
		elif _isKey(evt, (ord("F"),), ctrl=True):
			self.page.searchField.SetFocus()
		elif _isKey(evt, (wx.WXK_TAB,), ctrl=True):
			self.selectTab((self.notebook.GetSelection() + 1) % len(self.pages))
		elif _isKey(evt, (wx.WXK_TAB,), ctrl=True, shift=True):
			self.selectTab((self.notebook.GetSelection() - 1) % len(self.pages))
		elif evt.ControlDown() and not evt.ShiftDown() and not evt.AltDown() and ord("1") <= key <= ord("3"):
			self.selectTab(key - ord("1"))
		elif _isKey(evt, (wx.WXK_F1,)):
			self.showHelp()
		else:
			evt.Skip()

	# Actions

	def _selectedOrSay(self) -> pickerData.Entry | None:
		entry = self.page.selected()
		if entry is None:
			# Translators: Announced when nothing is selected in the insert emoji dialog.
			ui.message(_("Tidak ada yang dipilih"))
		return entry

	def _finish(self, entries: list[pickerData.Entry], shouldPaste: bool) -> None:
		conf = getConfig()
		recent = list(conf["pickerRecent"])
		for entry in reversed(entries):
			recent = pickerData.addToHistory(recent, entry.text, RECENT_LIMIT)
		conf["pickerRecent"] = recent
		self.result = ("".join(entry.text for entry in entries), shouldPaste)
		self.EndModal(wx.ID_OK)

	def _useSelectionOrChain(self, shouldPaste: bool) -> None:
		if self._chain:
			self._finish(list(self._chain), shouldPaste)
			return
		entry = self._selectedOrSay()
		if entry is not None:
			self._finish([entry], shouldPaste)

	def insert(self) -> None:
		self._useSelectionOrChain(shouldPaste=True)

	def copy(self) -> None:
		self._useSelectionOrChain(shouldPaste=False)

	def personalize(self) -> None:
		"""Open the personalize dialog for the selected emoji, then do what the user chose there."""
		entry = self.page.selected()
		if not self._canPersonalize(entry):
			# Translators: Announced when Shift+Enter is pressed on an item that cannot be personalized.
			ui.message(_("Tidak dapat dipersonalisasi"))
			return
		dialog = PersonalizeDialog(self, entry, self._nameOf)
		try:
			if dialog.ShowModal() != wx.ID_OK:
				return
			text, action = dialog.text, dialog.action
		finally:
			dialog.Destroy()
		chosen = pickerData.Entry(
			text,
			cleanNameSymbols(self._nameOf(text) or entry.name),
			entry.kind,
			entry.category,
			entry.subgroup,
			entry.keywords,
			entry.item,
		)
		if action == ACTION_ADD_TO_CHAIN:
			self._addToChain(chosen)
		else:
			self._finish([*self._chain, chosen], shouldPaste=action == ACTION_INSERT)

	def _updateChainField(self) -> None:
		self.chainField.SetValue(", ".join(entry.name for entry in self._chain))

	def addSelectedToChain(self) -> None:
		entry = self._selectedOrSay()
		if entry is not None:
			self._addToChain(entry)

	def _addToChain(self, chosen: pickerData.Entry) -> None:
		self._chain.append(chosen)
		self._updateChainField()
		# Translators: Announced when an item is added to the collection. {name} is its name,
		# {count} the number of items now in the collection.
		ui.message(
			_("{name} ditambahkan, {count} dalam rangkaian").format(name=chosen.name, count=len(self._chain))
		)

	def removeLast(self) -> None:
		if not self._chain:
			# Translators: Announced when the collection is already empty.
			ui.message(_("Rangkaian kosong"))
			return
		entry = self._chain.pop()
		self._updateChainField()
		# Translators: Announced when the last item is removed from the collection. {name} is its name.
		ui.message(_("{name} dihapus dari rangkaian").format(name=entry.name))

	def clearChain(self) -> None:
		self._chain.clear()
		self._updateChainField()
		# Translators: Announced when the collection is emptied.
		ui.message(_("Rangkaian dikosongkan"))

	def readChain(self) -> None:
		if not self._chain:
			# Translators: Announced when the collection is already empty.
			ui.message(_("Rangkaian kosong"))
			return
		names = ", ".join(entry.name for entry in self._chain)
		# Translators: Reads the collection. {count} is the number of items, {names} lists them.
		ui.message(_("{count} dalam rangkaian: {names}").format(count=len(self._chain), names=names))

	def toggleFavorite(self) -> None:
		entry = self._selectedOrSay()
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
		self.updateButtons()
		ui.message(message)

	def showDetail(self) -> None:
		entry = self._selectedOrSay()
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
		if self._canPersonalize(entry):
			# Translators: Line of the details of an emoji whose skin tone, gender or direction can be chosen.
			lines.append(_("Dapat dipersonalisasi"))
		if entry.keywords:
			# Translators: Line of the details of an item. {keywords} lists its search keywords.
			lines.append(_("Kata kunci: {keywords}").format(keywords=", ".join(entry.keywords)))
		# Translators: Title of the dialog with the details of an item.
		MessageDialog.alert("\n".join(lines), _("Detail"), parent=self)

	def showHelp(self) -> None:
		MessageDialog.alert(
			_(
				# Translators: List of the shortcuts of the insert emoji dialog.
				"Enter: sisipkan emoji yang dipilih, atau seluruh rangkaian.\n"
				"Shift+Enter: personalisasi warna kulit, jenis kelamin, atau arah.\n"
				"Ctrl+Enter: tambah ke rangkaian.\n"
				"Ctrl+Shift+Backspace: hapus emoji terakhir dari rangkaian.\n"
				"Ctrl+Shift+Delete: kosongkan rangkaian.\n"
				"Ctrl+R: bacakan isi rangkaian.\n"
				"Ctrl+Shift+C: salin tanpa menyisipkan.\n"
				"Ctrl+D: tambah ke favorit atau hapus dari favorit.\n"
				"Alt+Enter: detail emoji.\n"
				"Ctrl+Tab dan Ctrl+Shift+Tab: tab berikutnya atau sebelumnya.\n"
				"Ctrl+1, Ctrl+2, Ctrl+3: tab Emoji, Simbol, atau Kaomoji.\n"
				"Ctrl+F: pindah ke kolom Cari.\n"
				"Panah kanan dan kiri di daftar Hasil: lompat ke subkategori berikutnya atau sebelumnya, "
				"saat Subkategori diatur ke Semua subkategori.\n"
				"Escape: tutup."
			),
			# Translators: Title of the list of shortcuts of the insert emoji dialog.
			_("Pintasan Sisipkan Emoji"),
			parent=self,
		)
