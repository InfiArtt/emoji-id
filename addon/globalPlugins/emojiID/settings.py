# -*- coding: UTF-8 -*-
# Emoji ID - Indonesian Emoji Reader for NVDA
# Copyright (C) 2024 Emoji ID Contributors
# This file is covered by the GNU General Public License v2 or later.
# See the file LICENSE for more details.

"""Settings panel for Emoji ID add-on.

Provides an NVDA settings panel with controls for:
- Feature on/off toggle
- Emoji prefix configuration
- Collapse repeated emoji
- Skin tone detail
- Symbol level respect
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import config
import wx
from gui import guiHelper
from gui.settingsDialogs import SettingsPanel

if TYPE_CHECKING:
    pass

log = logging.getLogger(__name__)

# Configuration specification for configobj validation.
# These settings are profile-aware by default.
CONFSPEC = {
    "enabled": "boolean(default=True)",
    "prefix": "boolean(default=True)",
    "prefixText": 'string(default="emoji")',
    "prefixOnce": "boolean(default=False)",
    "collapseRepeated": "boolean(default=True)",
    "skinToneDetail": "boolean(default=True)",
    "respectSymbolLevel": "boolean(default=False)",
}

# Translatable strings
# Using a function to allow gettext to extract them
_ = lambda x: x


def get_config() -> config.AggregatedSection:
    """Get the Emoji ID configuration section."""
    return config.conf["emojiID"]


def is_enabled() -> bool:
    """Check if Emoji ID is enabled in current profile."""
    try:
        return config.conf["emojiID"]["enabled"]
    except KeyError:
        return True


def register_config() -> None:
    """Register the Emoji ID config spec with NVDA."""
    config.conf.spec["emojiID"] = CONFSPEC


def unregister_config() -> None:
    """Unregister the Emoji ID config spec."""
    try:
        del config.conf.spec["emojiID"]
    except KeyError:
        pass


class EmojiIDSettingsPanel(SettingsPanel):
    """NVDA settings panel for Emoji ID configuration."""

    # Panel title shown in NVDA settings categories
    title = "Emoji ID"

    def makeSettings(self, settingsSizer: wx.BoxSizer) -> None:
        """Build the settings panel UI controls."""
        sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
        conf = get_config()

        # Enable/disable checkbox
        self.enabledCheckbox = sHelper.addItem(
            wx.CheckBox(self, label=_("&Aktifkan pembacaan emoji dalam bahasa Indonesia"))
        )
        self.enabledCheckbox.SetValue(conf["enabled"])

        # Prefix section
        self.prefixCheckbox = sHelper.addItem(
            wx.CheckBox(self, label=_("Tambahkan kata &awalan sebelum nama emoji"))
        )
        self.prefixCheckbox.SetValue(conf["prefix"])

        # Prefix text
        prefixTextLabel = wx.StaticText(self, label=_("&Kata awalan:"))
        self.prefixTextCtrl = wx.TextCtrl(self)
        self.prefixTextCtrl.SetValue(conf["prefixText"])
        prefixSizer = wx.BoxSizer(wx.HORIZONTAL)
        prefixSizer.Add(prefixTextLabel, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
        prefixSizer.Add(self.prefixTextCtrl, proportion=1)
        sHelper.addItem(prefixSizer)

        # Prefix once per run
        self.prefixOnceCheckbox = sHelper.addItem(
            wx.CheckBox(
                self,
                label=_("Kata awalan hanya &sekali untuk emoji berturut-turut"),
            )
        )
        self.prefixOnceCheckbox.SetValue(conf["prefixOnce"])

        # Collapse repeated emoji
        self.collapseRepeatedCheckbox = sHelper.addItem(
            wx.CheckBox(
                self,
                label=_("&Gabungkan emoji berulang yang sama (misalnya '3 kali wajah gembira')"),
            )
        )
        self.collapseRepeatedCheckbox.SetValue(conf["collapseRepeated"])

        # Skin tone detail
        self.skinToneDetailCheckbox = sHelper.addItem(
            wx.CheckBox(
                self,
                label=_("Sertakan detail &warna kulit"),
            )
        )
        self.skinToneDetailCheckbox.SetValue(conf["skinToneDetail"])

        # Respect symbol level
        self.respectSymbolLevelCheckbox = sHelper.addItem(
            wx.CheckBox(
                self,
                label=_("Ikuti tingkat &simbol NVDA (jika nonaktif, selalu bacakan emoji)"),
            )
        )
        self.respectSymbolLevelCheckbox.SetValue(conf["respectSymbolLevel"])

        # Bind enable checkbox to update control states
        self.enabledCheckbox.Bind(wx.EVT_CHECKBOX, self._onEnabledToggle)
        self._updateControlStates()

    def _onEnabledToggle(self, evt: wx.CommandEvent) -> None:
        """Handle enable checkbox toggle to update dependent control states."""
        self._updateControlStates()

    def _updateControlStates(self) -> None:
        """Enable or disable controls based on the enabled state."""
        enabled = self.enabledCheckbox.GetValue()
        self.prefixCheckbox.Enable(enabled)
        self.prefixTextCtrl.Enable(enabled and self.prefixCheckbox.GetValue())
        self.prefixOnceCheckbox.Enable(enabled)
        self.collapseRepeatedCheckbox.Enable(enabled)
        self.skinToneDetailCheckbox.Enable(enabled)
        self.respectSymbolLevelCheckbox.Enable(enabled)

    def isValid(self) -> bool:
        """Validate settings before saving."""
        if self.prefixCheckbox.GetValue():
            prefix_text = self.prefixTextCtrl.GetValue().strip()
            if not prefix_text:
                # Empty prefix text with prefix enabled - warn but allow
                log.warning("Emoji ID: prefix is enabled but prefix text is empty")
        return True

    def onSave(self) -> None:
        """Save settings to NVDA configuration."""
        conf = get_config()
        conf["enabled"] = self.enabledCheckbox.GetValue()
        conf["prefix"] = self.prefixCheckbox.GetValue()
        conf["prefixText"] = self.prefixTextCtrl.GetValue().strip()
        conf["prefixOnce"] = self.prefixOnceCheckbox.GetValue()
        conf["collapseRepeated"] = self.collapseRepeatedCheckbox.GetValue()
        conf["skinToneDetail"] = self.skinToneDetailCheckbox.GetValue()
        conf["respectSymbolLevel"] = self.respectSymbolLevelCheckbox.GetValue()
