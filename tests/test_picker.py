"""Tests for the insert emoji dialog and the brief reading mode. Run with ``python -m pytest``."""

from collections.abc import Iterator

import config
import nvda_mocks
import pytest
from emojiID import picker, pickerData
from emojiID.emojiData import EmojiMatcher

_HANDSHAKE = chr(0x1F91D)
_RUNNER = chr(0x1F3C3)
_FLAG_ID = chr(0x1F1EE) + chr(0x1F1E9)


@pytest.fixture(scope="module")
def matcher() -> EmojiMatcher:
	emojiMatcher = EmojiMatcher()
	assert emojiMatcher.load()
	return emojiMatcher


@pytest.fixture(scope="module")
def data() -> pickerData.PickerData:
	return pickerData.loadPickerData()


@pytest.fixture
def dialog(matcher: EmojiMatcher, data: pickerData.PickerData) -> Iterator[picker.EmojiPickerDialog]:
	config.conf["emojiID"] = dict(nvda_mocks.DEFAULT_CONFIG)
	yield picker.EmojiPickerDialog(None, data, matcher.lookup)


def _item(data: pickerData.PickerData, base: str) -> pickerData.EmojiItem:
	return next(item for item in data.emoji if item.base == base)


def test_pickerDataCounts(data: pickerData.PickerData) -> None:
	assert len(data.emoji) > 1700
	assert len(data.kaomoji) == 82
	assert {entry.category for entry in data.symbols} == {
		"punctuation",
		"currency",
		"latin",
		"geometric",
		"math",
		"supplemental",
		"language",
	}


def test_emojiCategoriesFollowWindows(data: pickerData.PickerData) -> None:
	assert {item.category for item in data.emoji} == {
		"faces",
		"people",
		"objects",
		"food",
		"travel",
		"symbols",
		"flags",
	}
	# Every subgroup shown in the dialog has an Indonesian name.
	from emojiID.pickerCategories import SUBGROUPS

	assert not {item.subgroup for item in data.emoji} - set(SUBGROUPS)


def test_resolveGenderDirectionAndTone(data: pickerData.PickerData, matcher: EmojiMatcher) -> None:
	runner = _item(data, _RUNNER)
	assert runner.genders() == ["", "pria", "wanita"]
	assert runner.canFaceRight()
	text = runner.resolve("wanita", True, 4)
	assert matcher.lookup(text).startswith("wanita berlari warna kulit gelap")


def test_resolveTwoPersonTones(data: pickerData.PickerData) -> None:
	handshake = _item(data, _HANDSHAKE)
	assert handshake.toneSlots() == 2
	# The same tone for both people is a single toned handshake.
	assert handshake.resolve(tone=3) == _HANDSHAKE + chr(0x1F3FD)
	# Different tones use the two hands sequence.
	mixed = handshake.resolve(tone=1, secondTone=5)
	assert mixed == chr(0x1FAF1) + chr(0x1F3FB) + chr(0x200D) + chr(0x1FAF2) + chr(0x1F3FF)


def test_searchRanksNamesBeforeKeywords(data: pickerData.PickerData, matcher: EmojiMatcher) -> None:
	entries = pickerData.emojiEntries(data, matcher.lookup)
	assert pickerData.search(entries, "indonesia")[0].text == _FLAG_ID
	# "ngakak" is only a CLDR keyword.
	assert [entry.name for entry in pickerData.search(entries, "ngakak")][:2] == [
		"tertawa terbahak bahak",
		"wajah gembira berurai air mata",
	]
	assert pickerData.search(data.kaomoji, "bahu")[0].text == "¯\\_(ツ)_/¯"
	assert pickerData.search(data.symbols, "aksen tirus")[0].name.endswith("dengan aksen tirus")


def test_historyEncodingKeepsKaomojiSafe() -> None:
	text = "(●'◡'●)"
	history = pickerData.addToHistory([], text)
	history = pickerData.addToHistory(history, "x")
	history = pickerData.addToHistory(history, text, limit=2)
	assert [pickerData.decodeText(item) for item in history] == [text, "x"]
	# Only hexadecimal code points are stored, never quotes or commas.
	assert all(set(item) <= set("0123456789ABCDEF-") for item in history)


def _search(dialog: picker.EmojiPickerDialog, query: str) -> None:
	page = dialog.page
	page.searchField.SetValue(query)
	page._onFilterChanged(None)
	# Results follow typing after a short delay; run it now.
	page.fillResults()


class _ChoosingPersonalizeDialog:
	"""Stands in for the personalize dialog and confirms a preset choice."""

	answer: str | None = None
	action = picker.ACTION_INSERT
	opened: list[str] = []

	def __init__(self, parent: object, entry: pickerData.Entry, nameOf: object) -> None:
		self.text = _ChoosingPersonalizeDialog.answer or entry.text
		self.action = _ChoosingPersonalizeDialog.action
		_ChoosingPersonalizeDialog.opened.append(entry.text)

	def ShowModal(self) -> int:
		return nvda_mocks.sys.modules["wx"].ID_OK

	def Destroy(self) -> None:
		pass


class _KeyEvent:
	def __init__(
		self, keyCode: int | str, ctrl: bool = False, shift: bool = False, alt: bool = False
	) -> None:
		self.keyCode = ord(keyCode) if isinstance(keyCode, str) else keyCode
		self.ctrl = ctrl
		self.shift = shift
		self.alt = alt
		self.isSkipped = False

	def GetKeyCode(self) -> int:
		return self.keyCode

	def ShiftDown(self) -> bool:
		return self.shift

	def ControlDown(self) -> bool:
		return self.ctrl

	def AltDown(self) -> bool:
		return self.alt

	def Skip(self) -> None:
		self.isSkipped = True


def _wx() -> object:
	return nvda_mocks.sys.modules["wx"]


@pytest.fixture
def choosing(monkeypatch: pytest.MonkeyPatch) -> Iterator[type[_ChoosingPersonalizeDialog]]:
	_ChoosingPersonalizeDialog.opened.clear()
	_ChoosingPersonalizeDialog.answer = None
	_ChoosingPersonalizeDialog.action = picker.ACTION_INSERT
	monkeypatch.setattr(picker, "PersonalizeDialog", _ChoosingPersonalizeDialog)
	yield _ChoosingPersonalizeDialog


def test_tabsAndListView(dialog: picker.EmojiPickerDialog) -> None:
	assert [title for _page, title in dialog.notebook.pages] == ["Emoji", "Simbol", "Kaomoji"]
	emojiPage, symbolPage, kaomojiPage = dialog.pages
	assert emojiPage.subgroupChoice is not None
	assert symbolPage.subgroupChoice is None and kaomojiPage.subgroupChoice is None
	# Without recent items every tab starts at its first real category, with the first item selected.
	assert emojiPage.resultsList.names[0] == emojiPage.rows[0].name
	assert emojiPage.resultsList.selectedIndex() == 0


def test_rowsMarkCustomizableEmoji(dialog: picker.EmojiPickerDialog) -> None:
	_search(dialog, "jempol ke atas")
	assert dialog.page.resultsList.names[0] == "jempol ke atas, dapat dipersonalisasi, tekan Shift+Enter"
	assert dialog.personalizeButton.isEnabled
	_search(dialog, "indonesia")
	assert dialog.page.resultsList.names[0] == "bendera Indonesia"
	assert not dialog.personalizeButton.isEnabled
	_search(dialog, "tidak ada yang cocok sama sekali")
	assert dialog.page.resultsList.names == ["Tidak ada hasil"]
	assert dialog.page.selected() is None


def test_enterInsertsWithoutAsking(dialog: picker.EmojiPickerDialog, choosing: type) -> None:
	_search(dialog, "terima kasih")
	assert dialog.page.rows[0].name == "kedua tangan dikatupkan"
	event = _KeyEvent(_wx().WXK_RETURN)
	dialog._onCharHook(event)
	assert not event.isSkipped
	assert choosing.opened == []
	assert dialog.result == (chr(0x1F64F), True)
	assert pickerData.decodeText(config.conf["emojiID"]["pickerRecent"][0]) == chr(0x1F64F)


def test_enterOnButtonPressesTheButton(
	dialog: picker.EmojiPickerDialog, monkeypatch: pytest.MonkeyPatch
) -> None:
	wx = _wx()
	monkeypatch.setattr(wx.Window, "FindFocus", staticmethod(lambda: dialog.closeButton))
	event = _KeyEvent(wx.WXK_RETURN)
	dialog._onCharHook(event)
	assert event.isSkipped
	assert dialog.result == ("", False)


def test_shiftEnterPersonalizesThenInserts(dialog: picker.EmojiPickerDialog, choosing: type) -> None:
	choosing.answer = chr(0x1F64F) + chr(0x1F3FD)
	_search(dialog, "terima kasih")
	event = _KeyEvent(_wx().WXK_RETURN, shift=True)
	dialog._onCharHook(event)
	assert not event.isSkipped
	assert choosing.opened == [chr(0x1F64F)]
	assert dialog.result == (chr(0x1F64F) + chr(0x1F3FD), True)


def test_shiftEnterOnPlainEmojiSaysSo(dialog: picker.EmojiPickerDialog, choosing: type) -> None:
	_search(dialog, "indonesia")
	dialog.personalize()
	assert choosing.opened == []
	assert nvda_mocks.spokenMessages[-1] == "Tidak dapat dipersonalisasi"


def test_chainShortcuts(dialog: picker.EmojiPickerDialog, choosing: type) -> None:
	wx = _wx()
	choosing.answer = chr(0x1F44D) + chr(0x1F3FD)
	choosing.action = picker.ACTION_ADD_TO_CHAIN
	_search(dialog, "jempol ke atas")
	dialog.personalize()
	_search(dialog, "indonesia")
	dialog._onCharHook(_KeyEvent(wx.WXK_RETURN, ctrl=True))
	assert nvda_mocks.spokenMessages[-1] == "bendera Indonesia ditambahkan, 2 dalam rangkaian"
	dialog._onCharHook(_KeyEvent("R", ctrl=True))
	assert nvda_mocks.spokenMessages[-1].startswith("2 dalam rangkaian: ")
	dialog._onCharHook(_KeyEvent(wx.WXK_BACK, ctrl=True, shift=True))
	assert nvda_mocks.spokenMessages[-1] == "bendera Indonesia dihapus dari rangkaian"
	dialog.addSelectedToChain()
	dialog._onCharHook(_KeyEvent("C", ctrl=True, shift=True))
	assert dialog.result == (chr(0x1F44D) + chr(0x1F3FD) + _FLAG_ID, False)


def test_clearChain(dialog: picker.EmojiPickerDialog) -> None:
	_search(dialog, "indonesia")
	dialog.addSelectedToChain()
	dialog._onCharHook(_KeyEvent(_wx().WXK_DELETE, ctrl=True, shift=True))
	assert dialog.chainField.value == ""
	dialog.readChain()
	assert nvda_mocks.spokenMessages[-1] == "Rangkaian kosong"


def test_tabShortcuts(dialog: picker.EmojiPickerDialog) -> None:
	wx = _wx()
	dialog._onCharHook(_KeyEvent(wx.WXK_TAB, ctrl=True))
	assert dialog.notebook.GetSelection() == 1
	dialog._onCharHook(_KeyEvent(wx.WXK_TAB, ctrl=True, shift=True))
	dialog._onCharHook(_KeyEvent(wx.WXK_TAB, ctrl=True, shift=True))
	assert dialog.notebook.GetSelection() == 2
	dialog._onCharHook(_KeyEvent("1", ctrl=True))
	assert dialog.notebook.GetSelection() == 0
	# Other keys go on to the focused control.
	event = _KeyEvent("A")
	dialog._onCharHook(event)
	assert event.isSkipped


def test_helpListsShortcuts(dialog: picker.EmojiPickerDialog) -> None:
	dialog._onCharHook(_KeyEvent(_wx().WXK_F1))
	assert "Ctrl+Tab" in nvda_mocks.FakeMessageDialog.shown[-1]


def test_arrowsJumpBetweenSubgroups(dialog: picker.EmojiPickerDialog) -> None:
	wx = _wx()
	page = dialog.page
	nvda_mocks.FakeCallLater.instances.clear()
	firstSubgroup = page.rows[0].subgroup
	page._onListKeyDown(_KeyEvent(wx.WXK_RIGHT))
	index = page.resultsList.selectedIndex()
	assert page.rows[index].subgroup != firstSubgroup
	assert page.rows[index - 1].subgroup == firstSubgroup
	announce = nvda_mocks.FakeCallLater.instances[-1]
	announce.fire()
	assert nvda_mocks.spokenMessages[-1] == picker.SUBGROUPS[page.rows[index].subgroup]
	# From the middle of a subcategory, left goes to the start of the previous one.
	page.resultsList.selectIndex(index + 1)
	page._onListKeyDown(_KeyEvent(wx.WXK_LEFT))
	assert page.resultsList.selectedIndex() == 0
	page._onListKeyDown(_KeyEvent(wx.WXK_LEFT))
	assert nvda_mocks.spokenMessages[-1] == "Subkategori pertama"
	# Other keys are left to the list.
	other = _KeyEvent(wx.WXK_RETURN)
	page._onListKeyDown(other)
	assert other.isSkipped


def test_arrowsDoNothingWhileFiltered(dialog: picker.EmojiPickerDialog) -> None:
	wx = _wx()
	page = dialog.page
	_search(dialog, "wajah")
	spoken = len(nvda_mocks.spokenMessages)
	page._onListKeyDown(_KeyEvent(wx.WXK_RIGHT))
	assert page.resultsList.selectedIndex() == 0
	assert len(nvda_mocks.spokenMessages) == spoken


def test_personalizeDialog(data: pickerData.PickerData, matcher: EmojiMatcher) -> None:
	config.conf["emojiID"] = dict(nvda_mocks.DEFAULT_CONFIG)
	runner = next(entry for entry in pickerData.emojiEntries(data, matcher.lookup) if entry.text == _RUNNER)
	personalize = picker.PersonalizeDialog(None, runner, matcher.lookup)
	# A runner is one person, so there is no second skin tone choice.
	assert personalize.secondToneChoice is None
	personalize.genderChoice.SetSelection(2)
	personalize.directionChoice.SetSelection(1)
	personalize.toneChoice.SetSelection(4)
	personalize._onOptionChanged(None)
	assert personalize.resultField.value.startswith("wanita berlari warna kulit gelap")
	personalize._onCharHook(_KeyEvent("C", ctrl=True, shift=True))
	assert personalize.text == runner.item.resolve("wanita", True, 4)
	assert personalize.action == picker.ACTION_COPY
	assert config.conf["emojiID"]["pickerSkinTone"] == 4
	assert config.conf["emojiID"]["pickerGender"] == "wanita"
	personalize._onCharHook(_KeyEvent(_wx().WXK_RETURN, ctrl=True))
	assert personalize.action == picker.ACTION_ADD_TO_CHAIN


def test_personalizeTwoPeople(data: pickerData.PickerData, matcher: EmojiMatcher) -> None:
	config.conf["emojiID"] = dict(nvda_mocks.DEFAULT_CONFIG)
	handshake = next(
		entry for entry in pickerData.emojiEntries(data, matcher.lookup) if entry.text == _HANDSHAKE
	)
	personalize = picker.PersonalizeDialog(None, handshake, matcher.lookup)
	assert personalize.genderChoice is None
	assert personalize.directionChoice is None
	personalize.toneChoice.SetSelection(1)
	personalize.secondToneChoice.SetSelection(5)
	personalize._confirm(picker.ACTION_INSERT)
	assert personalize.text == handshake.item.resolve(tone=1, secondTone=5)


def test_dialogKaomojiAndFavorites(dialog: picker.EmojiPickerDialog) -> None:
	dialog.selectTab(2)
	_search(dialog, "meja")
	dialog._onCharHook(_KeyEvent("D", ctrl=True))
	assert dialog.favoriteButton.label == "Hapus dari Favorit (Ctrl+D)"
	page = dialog.page
	page.searchField.SetValue("")
	page.categoryChoice.SetSelection(1)
	page._onCategoryChanged(None)
	page.fillResults()
	assert [row.name for row in page.rows] == ["membalik meja karena kesal"]


def test_insertPastesAndRestoresClipboard() -> None:
	nvda_mocks.clipboard[:] = ["teks lama"]
	nvda_mocks.calledLater.clear()
	picker.insertText(chr(0x1F600))
	assert nvda_mocks.clipboard[-1] == chr(0x1F600)
	assert nvda_mocks.sentGestures[-1] == "control+v"
	_delay, restore, *args = nvda_mocks.calledLater[-1]
	restore(*args)
	assert nvda_mocks.clipboard[-1] == "teks lama"


@pytest.mark.parametrize(
	("text", "maxInRun", "expected"),
	[
		("😀❤️👍🎉🔥 ok", 3, "wajah gembira hati merah jempol ke atas dan 2 emoji lainnya ok"),
		("😀, ❤️, 👍, 🎉", 2, "wajah gembira, hati merah dan 2 emoji lainnya"),
		("😀 halo 😀", 1, "wajah gembira halo wajah gembira"),
		("😀❤️👍", 0, "wajah gembira hati merah jempol ke atas"),
	],
)
def test_briefReadingMode(matcher: EmojiMatcher, text: str, maxInRun: int, expected: str) -> None:
	assert matcher.replaceInText(text, maxInRun=maxInRun) == expected
