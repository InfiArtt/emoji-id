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
}


class _Conf(dict[str, Any]):
	def __init__(self) -> None:
		super().__init__(emojiID=dict(DEFAULT_CONFIG))
		self.spec: dict[str, Any] = {}
		self.saveCount = 0

	def save(self) -> None:
		self.saveCount += 1


_module("logHandler", log=_Log())
_module("addonHandler", initTranslation=lambda: None)
_module("config", conf=_Conf(), AggregatedSection=dict)
_module("characterProcessing", processSpeechSymbol=originalProcessSpeechSymbol)
speechTypes = _module("speech.types", SpeechSequence=list)
speechExtensions = _module("speech.extensions", filter_speechSequence=HandlerRegistry())
_module("speech", extensions=speechExtensions, types=speechTypes)
_module("core", postNvdaStartup=HandlerRegistry())
_module("inputCore", InputGesture=object)
spokenMessages: list[str] = []
_module("ui", message=spokenMessages.append)
clipboard: list[str] = []
_module("api", copyToClip=lambda text: clipboard.append(text) or True)


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

	def __init__(self, delayMs: int, func: Callable[[], None]) -> None:
		self.delayMs = delayMs
		self.func = func
		self.isStopped = False
		FakeCallLater.instances.append(self)

	def Stop(self) -> None:
		self.isStopped = True

	def fire(self) -> None:
		self.func()


calledAfter: list[Callable[[], None]] = []
_module(
	"wx",
	Window=FakeWindow,
	Dialog=FakeWindow,
	Button=FakeWindow,
	CheckBox=FakeWindow,
	TextCtrl=FakeWindow,
	StaticText=FakeWindow,
	BoxSizer=FakeWindow,
	CommandEvent=object,
	CallLater=FakeCallLater,
	CallAfter=calledAfter.append,
	**{
		name: 0
		for name in (
			"HORIZONTAL",
			"VERTICAL",
			"ALIGN_RIGHT",
			"RIGHT",
			"ALL",
			"EXPAND",
			"TE_MULTILINE",
			"TE_READONLY",
			"ID_CANCEL",
			"EVT_CHECKBOX",
			"EVT_BUTTON",
		)
	},
)


class _BoxSizerHelper:
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		pass

	def addItem(self, item: Any) -> Any:
		return item

	def addLabeledControl(self, label: str, controlClass: type, **kwargs: Any) -> Any:
		return controlClass(label=label)


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


guiHelper = _module("gui.guiHelper", BoxSizerHelper=_BoxSizerHelper)
settingsDialogs = _module(
	"gui.settingsDialogs",
	SettingsPanel=_SettingsPanel,
	NVDASettingsDialog=_NVDASettingsDialog,
)
_module("gui", mainFrame=_MainFrame(), guiHelper=guiHelper, settingsDialogs=settingsDialogs)
