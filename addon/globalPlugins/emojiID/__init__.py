# -*- coding: UTF-8 -*-
# Emoji ID - Indonesian Emoji Reader for NVDA
# Copyright (C) 2024 Emoji ID Contributors
# This file is covered by the GNU General Public License v2 or later.
# See the file LICENSE for more details.

"""Emoji ID Global Plugin for NVDA.

Reads emoji in Indonesian regardless of the active TTS voice.
Works by:
1. Filtering speech sequences via speech.extensions.filter_speechSequence
   to replace emoji in text items with Indonesian names.
2. Wrapping characterProcessing.processSpeechSymbol to intercept
   single-character emoji before they reach the speech filter
   (the "single-character trap": character navigation, typed-character echo,
   and review cursor call processSpeechSymbol before speak()).
"""

from __future__ import annotations

import logging
from typing import Any

try:
    _ = _  # type: ignore[name-defined]
except NameError:
    try:
        import addonHandler
        addonHandler.initTranslation()
    except Exception:
        _ = lambda x: x

import characterProcessing
import config
import globalPluginHandler
import speech.extensions
import ui
from scriptHandler import script
from speech.types import SpeechSequence

from .emoji_data import EmojiMatcher
from .settings import (
    EmojiIDSettingsPanel,
    is_enabled,
    register_config,
    unregister_config,
)

log = logging.getLogger(__name__)

# Keep a module-level reference to the original function so we can
# always restore it, even if our wrapper is replaced by another add-on.
_original_processSpeechSymbol = None


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    """NVDA global plugin that reads emoji in Indonesian."""

    # Script category for Input Gestures dialog
    scriptCategory = "Emoji ID"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # Register configuration
        register_config()

        # Initialize the emoji matcher
        self._matcher = EmojiMatcher()
        if not self._matcher.load():
            log.error("Emoji ID: failed to load emoji data. Plugin will be limited.")

        # Register the speech sequence filter
        speech.extensions.filter_speechSequence.register(self._filterSpeechSequence)
        log.debug("Emoji ID: registered filter_speechSequence handler")

        # Wrap characterProcessing.processSpeechSymbol to handle
        # single-character emoji (the "single-character trap").
        self._patchApplied = False
        self._applyProcessSpeechSymbolPatch()

        # Register settings panel
        from gui.settingsDialogs import NVDASettingsDialog

        NVDASettingsDialog.categoryClasses.append(EmojiIDSettingsPanel)
        log.info("Emoji ID: plugin initialized successfully")

    def terminate(self) -> None:
        """Clean up on plugin termination."""
        # Unregister speech filter
        try:
            speech.extensions.filter_speechSequence.unregister(self._filterSpeechSequence)
            log.debug("Emoji ID: unregistered filter_speechSequence handler")
        except Exception:
            log.warning("Emoji ID: failed to unregister speech filter", exc_info=True)

        # Restore original processSpeechSymbol
        self._removeProcessSpeechSymbolPatch()

        # Unregister settings panel
        try:
            from gui.settingsDialogs import NVDASettingsDialog

            NVDASettingsDialog.categoryClasses.remove(EmojiIDSettingsPanel)
        except ValueError:
            pass
        except Exception:
            log.warning("Emoji ID: failed to remove settings panel", exc_info=True)

        # Unregister config
        unregister_config()

        log.info("Emoji ID: plugin terminated")
        super().terminate()

    # ------------------------------------------------------------------ #
    # Speech sequence filter (handles multi-character emoji in text)
    # ------------------------------------------------------------------ #

    def _filterSpeechSequence(self, speechSequence: SpeechSequence) -> SpeechSequence:
        """Filter speech sequences to replace emoji with Indonesian names.

        This handler is called by speech.extensions.filter_speechSequence
        before speech dictionaries and processSpeechSymbols are applied.

        It iterates over the sequence items:
        - str items: scanned for emoji and replaced with Indonesian names
        - Non-str items (SpeechCommand, callbacks, etc.): passed through unchanged

        Args:
            speechSequence: The speech sequence to filter.

        Returns:
            The filtered speech sequence.
        """
        if not is_enabled() or not self._matcher.loaded:
            return speechSequence

        conf = config.conf["emojiID"]
        prefix = conf["prefixText"] if conf["prefix"] else ""
        prefix_once = conf["prefixOnce"]
        collapse_repeated = conf["collapseRepeated"]
        skin_tone_detail = conf["skinToneDetail"]
        clean_symbols = conf.get("cleanSymbols", True)

        new_sequence: SpeechSequence = []
        for item in speechSequence:
            if isinstance(item, str):
                # Replace emoji in text
                replaced = self._matcher.replace_in_text(
                    item,
                    prefix=prefix,
                    prefix_once=prefix_once,
                    collapse_repeated=collapse_repeated,
                    skin_tone_detail=skin_tone_detail,
                    clean_symbols=clean_symbols,
                )
                if replaced:
                    new_sequence.append(replaced)
            else:
                # Pass through all non-string items unchanged
                # (SpeechCommand, IndexCommand, CallbackCommand,
                #  CharacterModeCommand, etc.)
                new_sequence.append(item)

        return new_sequence

    # ------------------------------------------------------------------ #
    # Single-character patch (handles the "single-character trap")
    # ------------------------------------------------------------------ #

    def _applyProcessSpeechSymbolPatch(self) -> None:
        """Wrap characterProcessing.processSpeechSymbol.

        This is needed because character navigation, typed-character echo,
        and review cursor call processSpeechSymbol(locale, char) BEFORE
        speak() is called. The English name is already in the speech
        sequence when our filter sees it, so the filter alone cannot
        catch single-character emoji.

        The wrapper checks if the symbol is a single emoji and returns
        the Indonesian name directly. For everything else, it delegates
        to the original function.
        """
        global _original_processSpeechSymbol

        try:
            _original_processSpeechSymbol = characterProcessing.processSpeechSymbol

            def wrappedProcessSpeechSymbol(locale: str, symbol: str) -> str:
                """Wrapper that returns Indonesian emoji names for single emoji."""
                if is_enabled() and self._matcher.loaded:
                    conf = config.conf["emojiID"]
                    clean_symbols = conf.get("cleanSymbols", True)
                    name = self._matcher.lookup_single_char(symbol, clean_symbols=clean_symbols)
                    if name is not None:
                        if not conf["skinToneDetail"]:
                            name = self._matcher._strip_skin_tone(name)
                        if conf["prefix"] and conf["prefixText"]:
                            name = f"{conf['prefixText']} {name}"
                        return name

                # Delegate to original for non-emoji or when disabled
                return _original_processSpeechSymbol(locale, symbol)

            characterProcessing.processSpeechSymbol = wrappedProcessSpeechSymbol
            self._patchApplied = True
            log.debug("Emoji ID: patched characterProcessing.processSpeechSymbol")

        except Exception:
            log.warning(
                "Emoji ID: failed to patch processSpeechSymbol. "
                "Single-character emoji in character navigation will use "
                "NVDA's default (English) names.",
                exc_info=True,
            )
            self._patchApplied = False

    def _removeProcessSpeechSymbolPatch(self) -> None:
        """Restore the original processSpeechSymbol function."""
        global _original_processSpeechSymbol

        if self._patchApplied and _original_processSpeechSymbol is not None:
            try:
                characterProcessing.processSpeechSymbol = _original_processSpeechSymbol
                log.debug("Emoji ID: restored original processSpeechSymbol")
            except Exception:
                log.warning(
                    "Emoji ID: failed to restore processSpeechSymbol",
                    exc_info=True,
                )
            finally:
                _original_processSpeechSymbol = None
                self._patchApplied = False

    # ------------------------------------------------------------------ #
    # Toggle script
    # ------------------------------------------------------------------ #

    @script(
        # Translators: Description of the toggle script shown in Input Gestures
        description=_("Aktifkan atau nonaktifkan pembacaan emoji dalam bahasa Indonesia"),
        category="Emoji ID",
    )
    def script_toggleEmojiID(self, gesture: Any) -> None:
        """Toggle Emoji ID on or off and announce the new state."""
        conf = config.conf["emojiID"]
        new_state = not conf["enabled"]
        conf["enabled"] = new_state

        if new_state:
            # Translators: Announced when the user enables Emoji ID
            message = _("Emoji ID aktif")
        else:
            # Translators: Announced when the user disables Emoji ID
            message = _("Emoji ID nonaktif")

        ui.message(message)
