# -*- coding: UTF-8 -*-
"""Mocks for NVDA core modules to enable headless unit testing."""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Any, Callable

# 1. Mock logging if not present
if "logging" not in sys.modules:
    mock_logging = ModuleType("logging")
    class DummyLogger:
        def debug(self, msg: str, *args: Any, **kwargs: Any) -> None: pass
        def info(self, msg: str, *args: Any, **kwargs: Any) -> None: pass
        def warning(self, msg: str, *args: Any, **kwargs: Any) -> None: pass
        def error(self, msg: str, *args: Any, **kwargs: Any) -> None: pass
        def exception(self, msg: str, *args: Any, **kwargs: Any) -> None: pass

    mock_logging.getLogger = lambda name=None: DummyLogger()
    mock_logging.DEBUG = 10
    mock_logging.INFO = 20
    mock_logging.WARNING = 30
    mock_logging.ERROR = 40
    sys.modules["logging"] = mock_logging

# 2. Mock speech
mock_speech = ModuleType("speech")
mock_speech_ext = ModuleType("speech.extensions")
mock_speech_types = ModuleType("speech.types")

class Filter:
    def __init__(self):
        self.handlers = []

    def register(self, handler: Callable):
        self.handlers.append(handler)

    def unregister(self, handler: Callable):
        if handler in self.handlers:
            self.handlers.remove(handler)

    def apply(self, value, *args, **kwargs):
        for h in self.handlers:
            value = h(value, *args, **kwargs)
        return value

mock_speech_ext.filter_speechSequence = Filter()
mock_speech.extensions = mock_speech_ext
mock_speech_types.SpeechSequence = list
mock_speech.types = mock_speech_types

sys.modules["speech"] = mock_speech
sys.modules["speech.extensions"] = mock_speech_ext
sys.modules["speech.types"] = mock_speech_types

# 3. Mock characterProcessing
mock_cp = ModuleType("characterProcessing")
def default_processSpeechSymbol(locale: str, symbol: str) -> str:
    # Default English names for testing
    defaults = {
        "😀": "grinning face",
        "😃": "grinning face with big eyes",
        "👍": "thumbs up",
    }
    return defaults.get(symbol, symbol)

mock_cp.processSpeechSymbol = default_processSpeechSymbol
sys.modules["characterProcessing"] = mock_cp

# 4. Mock config
mock_config = ModuleType("config")
class MockConf:
    def __init__(self):
        self.spec = {}
        self.data = {
            "emojiID": {
                "enabled": True,
                "prefix": True,
                "prefixText": "emoji",
                "prefixOnce": False,
                "collapseRepeated": True,
                "skinToneDetail": True,
                "cleanSymbols": True,
                "respectSymbolLevel": False,
                "periodicDonationReminder": True,
                "firstRun": True,
            }
        }

    def __getitem__(self, key: str):
        return self.data[key]

    def __setitem__(self, key: str, value: Any):
        self.data[key] = value

    def get(self, key: str, default: Any = None):
        return self.data.get(key, default)

mock_config.conf = MockConf()
mock_config.AggregatedSection = dict
sys.modules["config"] = mock_config

# 5. Mock ui
mock_ui = ModuleType("ui")
last_messages = []
def ui_message(msg: str):
    last_messages.append(msg)
mock_ui.message = ui_message
mock_ui.last_messages = last_messages
sys.modules["ui"] = mock_ui

# 6. Mock scriptHandler
mock_sh = ModuleType("scriptHandler")
def script(**kwargs):
    def decorator(fn):
        fn._script_meta = kwargs
        return fn
    return decorator
mock_sh.script = script
sys.modules["scriptHandler"] = mock_sh

# 7. Mock globalPluginHandler
mock_gph = ModuleType("globalPluginHandler")
class BaseGlobalPlugin:
    def __init__(self, *args, **kwargs): pass
    def terminate(self): pass
mock_gph.GlobalPlugin = BaseGlobalPlugin
sys.modules["globalPluginHandler"] = mock_gph

# 8. Mock gui and settingsDialogs
mock_gui = ModuleType("gui")
mock_gui_sd = ModuleType("gui.settingsDialogs")
mock_gui_helper = ModuleType("gui.guiHelper")
class SettingsPanel:
    title = ""
    def __init__(self, *args, **kwargs): pass
class NVDASettingsDialog:
    categoryClasses = []
mock_gui_sd.SettingsPanel = SettingsPanel
mock_gui_sd.NVDASettingsDialog = NVDASettingsDialog
class BoxSizerHelper:
    def __init__(self, *args, **kwargs): pass
    def addItem(self, item): return item
mock_gui_helper.BoxSizerHelper = BoxSizerHelper

mock_gui.settingsDialogs = mock_gui_sd
mock_gui.guiHelper = mock_gui_helper

class DummyMainFrame:
    def prePopup(self): pass
    def postPopup(self): pass

mock_gui.mainFrame = DummyMainFrame()

sys.modules["gui"] = mock_gui
sys.modules["gui.settingsDialogs"] = mock_gui_sd
sys.modules["gui.guiHelper"] = mock_gui_helper

# 9. Mock wx
mock_wx = ModuleType("wx")
class DummyWx:
    def __init__(self, *args, **kwargs):
        self.value = kwargs.get("value", "")
        if not self.value and len(args) > 1 and isinstance(args[1], str):
            self.value = args[1]
        self.label = kwargs.get("label", "")
        self.enabled = True
    def SetValue(self, val): self.value = val
    def GetValue(self): return self.value
    def Enable(self, state=True): self.enabled = state
    def Bind(self, *args): pass
    def Add(self, *args, **kwargs): pass
    def CentreOnParent(self): pass
    def Fit(self): pass
    def SetMinSize(self, *args): pass
    def GetSize(self): return (400, 300)
    def SetFocus(self): pass
    def EndModal(self, code): return code
    def ShowModal(self): return 1001
    def Destroy(self): pass
    def SetSizer(self, sizer): pass

mock_wx.Panel = DummyWx
mock_wx.Dialog = DummyWx
mock_wx.Button = DummyWx
mock_wx.CheckBox = DummyWx
mock_wx.TextCtrl = DummyWx
mock_wx.StaticText = DummyWx
mock_wx.BoxSizer = DummyWx
mock_wx.HORIZONTAL = 0
mock_wx.VERTICAL = 1
mock_wx.ALIGN_CENTER_VERTICAL = 0
mock_wx.ALIGN_RIGHT = 0
mock_wx.RIGHT = 0
mock_wx.ALL = 0
mock_wx.EXPAND = 0
mock_wx.DEFAULT_DIALOG_STYLE = 0
mock_wx.RESIZE_BORDER = 0
mock_wx.TE_MULTILINE = 0
mock_wx.TE_READONLY = 0
mock_wx.ID_CLOSE = 1001
mock_wx.ID_CANCEL = 1002
mock_wx.EVT_CHECKBOX = 0
mock_wx.EVT_BUTTON = 1

mock_wx.CallAfter = lambda fn, *args, **kwargs: fn(*args, **kwargs)
mock_wx.CallLater = lambda ms, fn, *args, **kwargs: fn(*args, **kwargs)

class DummyClipboard:
    def __init__(self):
        self.data = None
    def Open(self): return True
    def Close(self): pass
    def SetData(self, data):
        self.data = data

mock_wx.TheClipboard = DummyClipboard()
mock_wx.TextDataObject = lambda txt: txt

sys.modules["wx"] = mock_wx
