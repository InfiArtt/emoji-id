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
	dialog.searchField.SetValue(query)
	dialog._onFilterChanged(None)
	# Results follow typing after a short delay; run it now.
	dialog._fillResults()


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
	def __init__(self, keyCode: int, isShift: bool) -> None:
		self.keyCode = keyCode
		self.isShift = isShift
		self.isSkipped = False

	def GetKeyCode(self) -> int:
		return self.keyCode

	def ShiftDown(self) -> bool:
		return self.isShift

	def ControlDown(self) -> bool:
		return False

	def AltDown(self) -> bool:
		return False

	def Skip(self) -> None:
		self.isSkipped = True


@pytest.fixture
def choosing(monkeypatch: pytest.MonkeyPatch) -> Iterator[type[_ChoosingPersonalizeDialog]]:
	_ChoosingPersonalizeDialog.opened.clear()
	_ChoosingPersonalizeDialog.answer = None
	_ChoosingPersonalizeDialog.action = picker.ACTION_INSERT
	monkeypatch.setattr(picker, "PersonalizeDialog", _ChoosingPersonalizeDialog)
	yield _ChoosingPersonalizeDialog


def test_rowsMarkCustomizableEmoji(dialog: picker.EmojiPickerDialog) -> None:
	_search(dialog, "jempol ke atas")
	assert dialog.resultsList.items[0] == "jempol ke atas, dapat dipersonalisasi, tekan Shift+Enter"
	_search(dialog, "indonesia")
	assert dialog.resultsList.items[0] == "bendera Indonesia"


def test_enterInsertsWithoutAsking(dialog: picker.EmojiPickerDialog, choosing: type) -> None:
	_search(dialog, "terima kasih")
	assert dialog._rows[0].name == "kedua tangan dikatupkan"
	dialog._onInsert(None)
	assert choosing.opened == []
	assert dialog.result == (chr(0x1F64F), True)
	assert pickerData.decodeText(config.conf["emojiID"]["pickerRecent"][0]) == chr(0x1F64F)


def test_shiftEnterPersonalizesThenInserts(dialog: picker.EmojiPickerDialog, choosing: type) -> None:
	choosing.answer = chr(0x1F64F) + chr(0x1F3FD)
	_search(dialog, "terima kasih")
	wx = nvda_mocks.sys.modules["wx"]
	event = _KeyEvent(wx.WXK_RETURN, isShift=True)
	dialog._onCharHook(event)
	assert not event.isSkipped
	assert choosing.opened == [chr(0x1F64F)]
	assert dialog.result == (chr(0x1F64F) + chr(0x1F3FD), True)
	# Plain Enter goes on to the default button.
	plain = _KeyEvent(wx.WXK_RETURN, isShift=False)
	dialog._onCharHook(plain)
	assert plain.isSkipped


def test_shiftEnterOnPlainEmojiSaysSo(dialog: picker.EmojiPickerDialog, choosing: type) -> None:
	_search(dialog, "indonesia")
	dialog._onPersonalize()
	assert choosing.opened == []
	assert nvda_mocks.spokenMessages[-1] == "Tidak dapat dipersonalisasi"


def test_personalizedEmojiIntoChain(dialog: picker.EmojiPickerDialog, choosing: type) -> None:
	choosing.answer = chr(0x1F44D) + chr(0x1F3FD)
	choosing.action = picker.ACTION_ADD_TO_CHAIN
	_search(dialog, "jempol ke atas")
	dialog._onPersonalize()
	_search(dialog, "indonesia")
	dialog._onAddToChain(None)
	assert nvda_mocks.spokenMessages[-1] == "bendera Indonesia ditambahkan, 2 dalam rangkaian"
	dialog._onCopy(None)
	assert dialog.result == (chr(0x1F44D) + chr(0x1F3FD) + _FLAG_ID, False)


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
	personalize._confirm(picker.ACTION_COPY)
	assert personalize.text == runner.item.resolve("wanita", True, 4)
	assert personalize.action == picker.ACTION_COPY
	assert config.conf["emojiID"]["pickerSkinTone"] == 4
	assert config.conf["emojiID"]["pickerGender"] == "wanita"


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
	dialog.kindChoice.SetSelection(2)
	dialog._onKindChanged(None)
	assert not dialog.subgroupChoice.isEnabled
	_search(dialog, "meja")
	dialog._onToggleFavorite(None)
	assert dialog.favoriteButton.label == "Hapus dari Favorit"
	dialog.searchField.SetValue("")
	dialog.categoryChoice.SetSelection(1)
	dialog._onCategoryChanged(None)
	dialog._fillResults()
	assert [row.name for row in dialog._rows] == ["membalik meja karena kesal"]


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
