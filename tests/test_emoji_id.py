"""Unit tests for Emoji ID. Run with ``python -m pytest``."""

import re
from collections.abc import Iterator
from pathlib import Path

import characterProcessing
import config
import core
import nvda_mocks
import pytest
import speech.extensions
from emojiID import GlobalPlugin
from emojiID.emojiData import EmojiMatcher

_ROOT = Path(__file__).resolve().parent.parent
_FORBIDDEN_WORD = re.compile(r"\banda\b", re.IGNORECASE)


@pytest.fixture(scope="module")
def matcher() -> EmojiMatcher:
	emojiMatcher = EmojiMatcher()
	assert emojiMatcher.load()
	return emojiMatcher


@pytest.fixture
def plugin() -> Iterator[GlobalPlugin]:
	config.conf["emojiID"] = dict(nvda_mocks.DEFAULT_CONFIG)
	nvda_mocks.FakeCallLater.instances.clear()
	nvda_mocks.calledAfter.clear()
	instance = GlobalPlugin()
	yield instance
	instance.terminate()
	characterProcessing.processSpeechSymbol = nvda_mocks.originalProcessSpeechSymbol


def test_dataLoaded(matcher: EmojiMatcher) -> None:
	assert matcher.count > 3000


def test_variationSelector(matcher: EmojiMatcher) -> None:
	assert matcher.replaceInText("❤️") == "hati merah"
	assert matcher.replaceInText("❤") == "hati merah"


def test_zwjFlagKeycap(matcher: EmojiMatcher) -> None:
	assert "keluarga" in matcher.replaceInText("👨‍👩‍👧").lower()
	assert "indonesia" in matcher.replaceInText("🇮🇩").lower()
	keycap = matcher.replaceInText("1️⃣").lower()
	assert any(word in keycap for word in ("1", "angka", "tombol"))


def test_plainDigitsUntouched(matcher: EmojiMatcher) -> None:
	assert matcher.replaceInText("Nomor 123 #4 *5") == "Nomor 123 #4 *5"


def test_skinTone(matcher: EmojiMatcher) -> None:
	assert "kulit" in matcher.replaceInText("👍🏽", hasSkinToneDetail=True).lower()
	withoutTone = matcher.replaceInText("👍🏽", hasSkinToneDetail=False).lower()
	assert "kulit" not in withoutTone
	assert "jempol" in withoutTone


def test_textWithoutEmoji(matcher: EmojiMatcher) -> None:
	assert matcher.replaceInText("") == ""
	assert matcher.replaceInText("Halo dunia!") == "Halo dunia!"


def test_mixedText(matcher: EmojiMatcher) -> None:
	result = matcher.replaceInText("Halo 😀 apa kabar?")
	assert result == "Halo wajah gembira apa kabar?"


def test_collapseRepeated(matcher: EmojiMatcher) -> None:
	assert matcher.replaceInText("😀😀😀", shouldCollapseRepeated=True) == "3 kali wajah gembira"
	assert (
		matcher.replaceInText("😀😀😀", shouldCollapseRepeated=False)
		== "wajah gembira wajah gembira wajah gembira"
	)


@pytest.mark.parametrize(
	("text", "isPrefixOnce", "shouldCollapse", "expected"),
	[
		("😀", False, False, "emoji wajah gembira"),
		("😀👍", True, False, "emoji wajah gembira jempol ke atas"),
		(
			"😂, 👋, 👨‍🦯",
			True,
			False,
			"emoji wajah gembira berurai air mata, tangan melambai, pria dengan tongkat",
		),
		(
			"😂 👋 👨‍🦯",
			True,
			False,
			"emoji wajah gembira berurai air mata tangan melambai pria dengan tongkat",
		),
		("😂 😂 😂", True, True, "emoji 3 kali wajah gembira berurai air mata"),
		("😂, 😂, 😂", True, True, "emoji 3 kali wajah gembira berurai air mata"),
	],
)
def test_prefix(
	matcher: EmojiMatcher,
	text: str,
	isPrefixOnce: bool,
	shouldCollapse: bool,
	expected: str,
) -> None:
	result = matcher.replaceInText(
		text,
		prefix="emoji",
		isPrefixOnce=isPrefixOnce,
		shouldCollapseRepeated=shouldCollapse,
	)
	assert result == expected


@pytest.mark.parametrize(
	("emoji", "expected"),
	[("🤥", "bohong"), ("💩", "kotoran"), ("🤧", "bersin"), ("💨", "berlari")],
)
def test_overrides(matcher: EmojiMatcher, emoji: str, expected: str) -> None:
	assert matcher.replaceInText(emoji) == expected


def test_cleanSymbols(matcher: EmojiMatcher) -> None:
	assert matcher.replaceInText("🦋", shouldCleanSymbols=True) == "kupu kupu"
	assert matcher.replaceInText("🦋", shouldCleanSymbols=False) == "kupu-kupu"
	assert matcher.replaceInText("👆", shouldCleanSymbols=True) == "menunjuk ke atas dibalik"
	assert matcher.replaceInText("👆", shouldCleanSymbols=False) == "menunjuk ke atas (dibalik)"
	assert (
		matcher.replaceInText("Pasal 1-2 (a) 🦋 hal 3-4", shouldCleanSymbols=True)
		== "Pasal 1-2 (a) kupu kupu hal 3-4"
	)


def test_singleCharacter(plugin: GlobalPlugin) -> None:
	assert characterProcessing.processSpeechSymbol("en", "😀") == "emoji wajah gembira"
	assert characterProcessing.processSpeechSymbol("en", "a") == "a"


def test_speechSequenceKeepsCommands(plugin: GlobalPlugin) -> None:
	firstCommand = object()
	secondCommand = object()
	sequence = ["Lihat ", firstCommand, "😀 dan 👍", secondCommand, " selesai."]
	result = speech.extensions.filter_speechSequence.apply(sequence)
	assert len(result) == 5
	assert result[0] == "Lihat "
	assert result[1] is firstCommand
	assert "emoji wajah gembira" in result[2]
	assert result[3] is secondCommand
	assert result[4] == " selesai."


def test_disabledUsesNvdaDefaults(plugin: GlobalPlugin) -> None:
	config.conf["emojiID"]["enabled"] = False
	assert characterProcessing.processSpeechSymbol("en", "😀") == "grinning face"
	assert speech.extensions.filter_speechSequence.apply(["Halo 😀"]) == ["Halo 😀"]


def test_toggleScript(plugin: GlobalPlugin) -> None:
	plugin.script_toggleEmojiID(None)
	assert config.conf["emojiID"]["enabled"] is False
	assert nvda_mocks.spokenMessages[-1] == "Emoji ID nonaktif"
	plugin.script_toggleEmojiID(None)
	assert nvda_mocks.spokenMessages[-1] == "Emoji ID aktif"


def test_terminateRestoresOriginal(plugin: GlobalPlugin) -> None:
	plugin.terminate()
	assert characterProcessing.processSpeechSymbol is nvda_mocks.originalProcessSpeechSymbol
	assert speech.extensions.filter_speechSequence.handlers == []


def test_terminateKeepsOtherWrappers(plugin: GlobalPlugin) -> None:
	ourWrapper = characterProcessing.processSpeechSymbol

	def otherAddonWrapper(locale: str, symbol: str) -> str:
		return ourWrapper(locale, symbol)

	characterProcessing.processSpeechSymbol = otherAddonWrapper
	plugin.terminate()
	assert characterProcessing.processSpeechSymbol is otherAddonWrapper
	# Our wrapper is still in the chain but now passes everything through.
	assert characterProcessing.processSpeechSymbol("en", "😀") == "grinning face"


def test_welcomeShownOnceOnFirstRun(plugin: GlobalPlugin) -> None:
	config.conf["emojiID"]["firstRun"] = True
	core.postNvdaStartup.notify()
	assert config.conf["emojiID"]["firstRun"] is False
	assert len(nvda_mocks.calledAfter) == 1
	core.postNvdaStartup.notify()
	assert len(nvda_mocks.calledAfter) == 1


def test_reminderOffByDefault(plugin: GlobalPlugin) -> None:
	core.postNvdaStartup.notify()
	assert nvda_mocks.FakeCallLater.instances == []


def test_reminderScheduledAndStopped(plugin: GlobalPlugin) -> None:
	config.conf["emojiID"]["periodicDonationReminder"] = True
	core.postNvdaStartup.notify()
	timer = nvda_mocks.FakeCallLater.instances[-1]
	assert 20 * 60_000 <= timer.delayMs <= 45 * 60_000
	timer.fire()
	nextTimer = nvda_mocks.FakeCallLater.instances[-1]
	assert nextTimer is not timer
	assert 90 * 60_000 <= nextTimer.delayMs <= 180 * 60_000
	plugin.terminate()
	assert nextTimer.isStopped


def test_donationDialogs() -> None:
	from emojiID.donation import GOPAY_NAME, GOPAY_NUMBER, DonationDetailsDialog, showWelcomeDialog

	dialog = DonationDetailsDialog(None)
	assert GOPAY_NUMBER in dialog.detailsText.value
	assert GOPAY_NAME in dialog.detailsText.value
	assert not _FORBIDDEN_WORD.search(dialog.detailsText.value)
	dialog._onCopy(None)
	assert nvda_mocks.clipboard[-1] == GOPAY_NUMBER
	showWelcomeDialog()
	assert nvda_mocks.sys.modules["gui"].mainFrame.popupCount == 0


def test_settingsPanelSave() -> None:
	from emojiID.settings import EmojiIDSettingsPanel

	config.conf["emojiID"] = dict(nvda_mocks.DEFAULT_CONFIG)
	panel = EmojiIDSettingsPanel()
	panel.makeSettings(None)
	panel.prefixCheckbox.SetValue(False)
	panel._updateControlStates()
	assert not panel.prefixTextCtrl.isEnabled
	panel.periodicReminderCheckbox.SetValue(True)
	panel.onSave()
	assert config.conf["emojiID"]["prefix"] is False
	assert config.conf["emojiID"]["periodicDonationReminder"] is True


@pytest.fixture
def installTasks() -> Iterator[object]:
	import installTasks as module

	config.conf["emojiID"] = dict(nvda_mocks.DEFAULT_CONFIG, firstRun=True)
	nvda_mocks.FakeMessageDialog.shown.clear()
	yield module
	nvda_mocks.FakeMessageDialog.confirmAnswer = nvda_mocks.ReturnCode.CANCEL


def test_installWelcomeNotNow(installTasks: object) -> None:
	installTasks.onInstall()
	assert len(nvda_mocks.FakeMessageDialog.shown) == 1
	assert "Selamat datang di Emoji ID" in nvda_mocks.FakeMessageDialog.shown[0]
	assert config.conf["emojiID"]["firstRun"] is False
	assert nvda_mocks.sys.modules["gui"].mainFrame.popupCount == 0


def test_installWelcomeDonate(installTasks: object) -> None:
	from emojiID.donation import GOPAY_NAME, GOPAY_NUMBER

	nvda_mocks.FakeMessageDialog.confirmAnswer = nvda_mocks.ReturnCode.OK
	installTasks.onInstall()
	details = nvda_mocks.FakeMessageDialog.shown[-1]
	assert GOPAY_NUMBER in details and GOPAY_NAME in details
	assert nvda_mocks.clipboard[-1] == GOPAY_NUMBER
	assert not _FORBIDDEN_WORD.search(details)
	# installTasks keeps its own copy of the donation details.
	assert (installTasks.GOPAY_NUMBER, installTasks.GOPAY_NAME) == (GOPAY_NUMBER, GOPAY_NAME)


_FLAG_I = chr(0x1F1EE)
_FLAG_D = chr(0x1F1E9)
_FLAG_J = chr(0x1F1EF)
_FLAG_P = chr(0x1F1F5)


def test_wholeFlagsInText(matcher: EmojiMatcher) -> None:
	text = f"Bendera {_FLAG_I}{_FLAG_D} dan {_FLAG_J}{_FLAG_P}"
	assert matcher.replaceInText(text) == "Bendera bendera Indonesia dan bendera Jepang"


@pytest.mark.parametrize(
	("text", "expected"),
	[
		# Half a flag left over when an application cuts a word in the middle of a flag.
		(f"Bendera {_FLAG_I}", "Bendera huruf regional I"),
		(f"{_FLAG_D} dan", "huruf regional D dan"),
		(f"dan{_FLAG_J}", "dan huruf regional J"),
		(_FLAG_P, "huruf regional P"),
	],
)
def test_loneRegionalIndicatorInText(matcher: EmojiMatcher, text: str, expected: str) -> None:
	assert matcher.replaceInText(text, prefix="emoji") == expected


def test_loneRegionalIndicatorCharacter(plugin: GlobalPlugin) -> None:
	# Character navigation moves through a flag one regional indicator at a time.
	assert characterProcessing.processSpeechSymbol("en", _FLAG_I) == "huruf regional I"
	assert characterProcessing.processSpeechSymbol("en", _FLAG_D) == "huruf regional D"


def test_noAcceleratorKeys() -> None:
	# Accelerator letters were removed on purpose: several labels shared the same letter.
	sources = [
		_ROOT / "addon" / "globalPlugins" / "emojiID" / "settings.py",
		_ROOT / "addon" / "globalPlugins" / "emojiID" / "donation.py",
		_ROOT / "addon" / "installTasks.py",
	]
	for source in sources:
		labels = re.findall(r'_\("([^"]*)"\)', source.read_text(encoding="utf-8"))
		assert labels
		assert not [label for label in labels if "&" in label], source.name


def test_noDuplicateNames(matcher: EmojiMatcher) -> None:
	# Two emoji with the same name cannot be told apart by ear.
	names = list(matcher._data.values())
	duplicates = {name for name in names if names.count(name) > 1}
	assert not duplicates


@pytest.mark.parametrize(
	"codepoint",
	# Emoji below U+1F300 that an earlier data build left out.
	[0x1F004, 0x1F0CF, 0x1F170, 0x1F197, 0x1F198, 0x1F201, 0x1F251, 0x2196],
)
def test_emojiBelowPictographBlocks(matcher: EmojiMatcher, codepoint: int) -> None:
	assert matcher.lookup(chr(codepoint))


def test_ordinarySymbolsAreNotEmoji(matcher: EmojiMatcher) -> None:
	# A plain arrow is a symbol, not an emoji: NVDA names it itself.
	assert matcher.lookup(chr(0x2192)) is None


@pytest.mark.parametrize(
	("codepoint", "expected"),
	[(0x266A, "not seperdelapan"), (0x266D, "nada mol"), (0x266F, "nada kres")],
)
def test_musicSignsKeepIndonesianNames(matcher: EmojiMatcher, codepoint: int, expected: str) -> None:
	# Not emoji, but Indonesian has names for them, so they stay in the data.
	assert matcher.lookup(chr(codepoint)) == expected
