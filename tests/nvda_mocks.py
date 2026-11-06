"""Minimal stand-ins for NVDA modules so the add-on can be tested without NVDA.

Importing this module registers the fakes in ``sys.modules``.
"""

import builtins
import sys
from collections.abc import Callable
from types import ModuleType
from typing import Any

builtins._ = lambda text: text  # type: ignore[attr-defined]


def _module(name: str, **attributes: Any) -> ModuleType:
	module = ModuleType(name)
	module.__dict__.update(attributes)
	sys.modules[name] = module
	return module


class _Log:
	def __getattr__(self, name: str) -> Callable[..., None]:
		return lambda *args, **kwargs: None


class HandlerRegistry:
	"""Fake for NVDA extension points (Action and Filter)."""

	def __init__(self) -> None:
		self.handlers: list[Callable[..., Any]] = []

	def register(self, handler: Callable[..., Any]) -> None:
		self.handlers.append(handler)

	def unregister(self, handler: Callable[..., Any]) -> None:
		if handler in self.handlers:
			self.handlers.remove(handler)

	def apply(self, value: Any) -> Any:
		for handler in self.handlers:
			value = handler(value)
		return value

	def notify(self) -> None:
		for handler in list(self.handlers):
			handler()


ENGLISH_NAMES = {"😀": "grinning face", "👍": "thumbs up"}


def originalProcessSpeechSymbol(locale: str, symbol: str) -> str:
	return ENGLISH_NAMES.get(symbol, symbol)


DEFAULT_CONFIG: dict[str, Any] = {
	"enabled": True,
	"prefix": True,
	"prefixText": "emoji",
	"prefixOnce": False,
	"collapseRepeated": True,
	"skinToneDetail": True,
	"cleanSymbols": True,
	"periodicDonationReminder": False,
	"firstRun": False,
	"symbolsEnabledOnce": False,
	"checkUpdateAtStartup": False,
	"maxEmojiInRun": 0,
	"pickerRecent": [],
	"pickerFavorites": [],
	"pickerSkinTone": 0,
	"pickerSecondSkinTone": 0,
	"pickerGender": "",
}


class _Conf(dict[str, Any]):
	def __init__(self) -> None:
		super().__init__(emojiID=dict(DEFAULT_CONFIG), speech={"symbolDictionaries": ["cldr"]})
		self.spec: dict[str, Any] = {}
		self.saveCount = 0

	def save(self) -> None:
		self.saveCount += 1


_module("logHandler", log=_Log())


class _CodeAddon:
	version = "1.3.0"


_module("addonHandler", initTranslation=lambda: None, getCodeAddon=_CodeAddon)
_module("config", conf=_Conf(), AggregatedSection=dict)
symbolCalls: list[tuple[str, str]] = []
symbolCacheClears: list[bool] = []


def originalProcessSpeechSymbols(locale: str, text: str, level: int) -> str:
	symbolCalls.append((locale, text))
	return text


_module(
	"characterProcessing",
	processSpeechSymbol=originalProcessSpeechSymbol,
	processSpeechSymbols=originalProcessSpeechSymbols,
	clearSpeechSymbols=lambda: symbolCacheClears.append(True),
)
speechTypes = _module("speech.types", SpeechSequence=list)
speechExtensions = _module("speech.extensions", filter_speechSequence=HandlerRegistry())
_module("speech", extensions=speechExtensions, types=speechTypes)
calledLater: list[tuple[Any, ...]] = []
_module("core", postNvdaStartup=HandlerRegistry(), callLater=lambda *args: calledLater.append(args))
_module("inputCore", InputGesture=object)
spokenMessages: list[str] = []
_module("ui", message=spokenMessages.append)
clipboard: list[str] = []
_module(
	"api",
	copyToClip=lambda text, notify=False: clipboard.append(text) or True,
	getClipData=lambda: clipboard[-1] if clipboard else "",
)
sentGestures: list[str] = []


class _KeyboardInputGesture:
	def __init__(self, name: str) -> None:
		self.name = name

	@classmethod
	def fromName(cls, name: str) -> "_KeyboardInputGesture":
		return cls(name)

	def send(self) -> None:
		sentGestures.append(self.name)


_module("keyboardHandler", KeyboardInputGesture=_KeyboardInputGesture)


def _script(**kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
	def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
		func.__doc__ = kwargs.get("description")
		return func

	return decorator


_module("scriptHandler", script=_script)


class _GlobalPlugin:
	def __init__(self) -> None:
		pass

	def terminate(self) -> None:
		pass


_module("globalPluginHandler", GlobalPlugin=_GlobalPlugin)


class FakeWindow:
	"""Stands in for every wx window and sizer class."""

	def __init__(self, *args: Any, **kwargs: Any) -> None:
		self.value: Any = kwargs.get("value", "")
		self.label: str = kwargs.get("label", "")
		self.isEnabled = True
		self.items: list[str] = list(kwargs.get("choices", []))
		self.selection = -1
		self.endModalCode: int | None = None

	def SetItems(self, items: list[str]) -> None:
		self.items = list(items)
		self.selection = -1

	def GetCount(self) -> int:
		return len(self.items)

	def GetSelection(self) -> int:
		return self.selection

	def SetSelection(self, index: int) -> None:
		self.selection = index

	def SetLabel(self, label: str) -> None:
		self.label = label

	def EndModal(self, code: int) -> None:
		self.endModalCode = code

	def SetValue(self, value: Any) -> None:
		self.value = value

	def GetValue(self) -> Any:
		return self.value

	def Enable(self, isEnabled: bool = True) -> None:
		self.isEnabled = isEnabled

	def ShowModal(self) -> int:
		return 0

	def __getattr__(self, name: str) -> Callable[..., None]:
		return lambda *args, **kwargs: None


class FakeCallLater:
	"""Records the delay instead of starting a timer. Call ``fire`` to run it."""

	instances: list["FakeCallLater"] = []

	def __init__(self, delayMs: int, func: Callable[..., None], *args: Any) -> None:
		self.delayMs = delayMs
		self.func = func
		self.args = args
		self.isStopped = False
		FakeCallLater.instances.append(self)

	def Stop(self) -> None:
		self.isStopped = True

	def IsRunning(self) -> bool:
		return not self.isStopped

	def Restart(self, delayMs: int) -> None:
		self.delayMs = delayMs

	def fire(self) -> None:
		self.func(*self.args)


calledAfter: list[tuple[Any, ...]] = []
_module(
	"wx",
	Window=FakeWindow,
	Dialog=FakeWindow,
	Button=FakeWindow,
	CheckBox=FakeWindow,
	TextCtrl=FakeWindow,
	StaticText=FakeWindow,
	BoxSizer=FakeWindow,
	Choice=FakeWindow,
	ListBox=FakeWindow,
	SpinCtrl=FakeWindow,
	CommandEvent=object,
	KeyEvent=object,
	WXK_RETURN=13,
	WXK_NUMPAD_ENTER=370,
	CallLater=FakeCallLater,
	CallAfter=lambda *args: calledAfter.append(args),
	**{
		name: 0
		for name in (
			"HORIZONTAL",
			"VERTICAL",
			"ALIGN_RIGHT",
			"ALIGN_CENTER_VERTICAL",
			"RIGHT",
			"ALL",
			"EXPAND",
			"TE_MULTILINE",
			"TE_READONLY",
			"ID_CANCEL",
			"ID_OK",
			"EVT_CHECKBOX",
			"EVT_BUTTON",
			"EVT_TEXT",
			"EVT_CHOICE",
			"EVT_LISTBOX",
			"EVT_LISTBOX_DCLICK",
			"EVT_CHAR_HOOK",
		)
	},
)


class _BoxSizerHelper:
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		self.sizer = FakeWindow()

	def addItem(self, item: Any) -> Any:
		return item

	def addLabeledControl(self, label: str, controlClass: type, **kwargs: Any) -> Any:
		return controlClass(label=label, choices=kwargs.get("choices", []))


class _ButtonHelper:
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		pass

	def addButton(self, parent: Any, id: int = 0, label: str = "") -> FakeWindow:
		return FakeWindow(label=label)


class _SettingsPanel(FakeWindow):
	pass


class _NVDASettingsDialog:
	categoryClasses: list[type] = []


class _MainFrame:
	def __init__(self) -> None:
		self.popupCount = 0

	def prePopup(self) -> None:
		self.popupCount += 1

	def postPopup(self) -> None:
		self.popupCount -= 1


class ReturnCode:
	OK = 1
	CANCEL = 2
	YES = 3
	NO = 4


class FakeMessageDialog:
	"""Answers ``confirm`` and ``ask`` with preset answers and records every message shown."""

	confirmAnswer = ReturnCode.CANCEL
	askAnswer = ReturnCode.CANCEL
	shown: list[str] = []

	@classmethod
	def confirm(cls, message: str, caption: str, **kwargs: Any) -> int:
		cls.shown.append(message)
		return cls.confirmAnswer

	@classmethod
	def ask(cls, message: str, caption: str, **kwargs: Any) -> int:
		cls.shown.append(message)
		return cls.askAnswer

	@classmethod
	def alert(cls, message: str, caption: str, **kwargs: Any) -> None:
		cls.shown.append(message)


guiHelper = _module(
	"gui.guiHelper",
	BoxSizerHelper=_BoxSizerHelper,
	ButtonHelper=_ButtonHelper,
	BORDER_FOR_DIALOGS=10,
	wxCallOnMain=lambda function: function(),
)
guiMessage = _module("gui.message", MessageDialog=FakeMessageDialog, ReturnCode=ReturnCode)
settingsDialogs = _module(
	"gui.settingsDialogs",
	SettingsPanel=_SettingsPanel,
	NVDASettingsDialog=_NVDASettingsDialog,
)
_module(
	"gui",
	mainFrame=_MainFrame(),
	guiHelper=guiHelper,
	settingsDialogs=settingsDialogs,
	message=guiMessage,
)
