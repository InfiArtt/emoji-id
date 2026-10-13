# -*- coding: UTF-8 -*-
# Emoji ID - Indonesian Emoji Reader for NVDA
# Copyright (C) 2026 Rexya Muhamad <rexya2017@gmail.com>
# This file is covered by the GNU General Public License v2 or later.
# See the file LICENSE for more details.

"""Installation tasks for Emoji ID add-on.

Displays a screen-reader friendly welcome and GoPay donation dialog
during add-on installation, safely dispatched to the main GUI thread
with defensive NVDA import tracker scrubbing for Python 3.13 compatibility.
"""

from __future__ import annotations

import os
import threading

import addonHandler
import gui
import wx
from logHandler import log

try:
    addonHandler.initTranslation()
except Exception:
    pass

try:
    _ = _  # type: ignore[name-defined]
except NameError:
    _ = lambda x: x

_ADDON_DIR = os.path.dirname(__file__)
GOPAY_NUMBER = "085128011831"
GOPAY_NAME = "Rexya Muhamad Rizki"


def _copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard via wx.TheClipboard."""
    try:
        if wx.TheClipboard.Open():
            data = wx.TextDataObject(text)
            wx.TheClipboard.SetData(data)
            wx.TheClipboard.Close()
            return True
    except Exception:
        log.warning("Emoji ID installTasks: gagal menyalin ke papan klip", exc_info=True)
    return False


class DonationDetailsDialog(wx.Dialog):
    """Dialog displaying GoPay donation details and copy button."""

    def __init__(self, parent: wx.Window | None = None) -> None:
        super().__init__(
            parent,
            title=_("Informasi Donasi GoPay - Emoji ID"),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self._init_ui()
        self.CentreOnParent()

    def _init_ui(self) -> None:
        sizer = wx.BoxSizer(wx.VERTICAL)

        info_text = (
            "Dukungan Pengembang Emoji ID\n\n"
            "Metode: GoPay\n"
            f"Nomor HP / Rekening: {GOPAY_NUMBER}\n"
            f"Atas Nama: {GOPAY_NAME}\n\n"
            "Dukungan sekecil apa pun dari kamu sangat berarti untuk kelanjutan pengembangan "
            "dan pembaruan add-on ini. Terima kasih banyak atas apresiasi dan kebaikanmu!"
        )

        self.text_ctrl = wx.TextCtrl(
            self,
            value=info_text,
            style=wx.TE_MULTILINE | wx.TE_READONLY,
            size=(480, 200),
        )
        sizer.Add(self.text_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.copy_btn = wx.Button(self, label=_("Salin Nomor"))
        self.copy_btn.Bind(wx.EVT_BUTTON, self._on_copy)
        btn_sizer.Add(self.copy_btn, flag=wx.RIGHT, border=10)

        self.close_btn = wx.Button(self, wx.ID_CLOSE, label=_("Tutup"))
        self.close_btn.Bind(wx.EVT_BUTTON, self._on_close)
        btn_sizer.Add(self.close_btn)

        sizer.Add(btn_sizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

        self.SetSizer(sizer)
        self.Fit()
        self.SetMinSize(self.GetSize())
        self.copy_btn.SetFocus()
        self.Bind(wx.EVT_CLOSE, self._on_close)

    def _on_copy(self, evt: wx.CommandEvent) -> None:
        if _copy_to_clipboard(GOPAY_NUMBER):
            msg = _("Nomor GoPay 085128011831 telah disalin ke papan klip.")
        else:
            msg = _("Gagal menyalin nomor ke papan klip.")
        try:
            import ui

            ui.message(msg)
        except Exception:
            pass

    def _on_close(self, evt: wx.Event) -> None:
        self.EndModal(wx.ID_CLOSE)


class InstallWelcomeDialog(wx.Dialog):
    """Welcome dialog displayed during add-on installation."""

    def __init__(self, parent: wx.Window | None = None) -> None:
        super().__init__(
            parent,
            title=_("Selamat Datang di Emoji ID"),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self._init_ui()
        self.CentreOnParent()

    def _init_ui(self) -> None:
        sizer = wx.BoxSizer(wx.VERTICAL)

        welcome_text = (
            "Selamat datang di Emoji ID!\n\n"
            "Add-on ini membantu membacakan ribuan simbol emoji dalam bahasa Indonesia "
            "di segala synthesizer dan suara TTS NVDA.\n\n"
            "Kalau kamu merasa add-on ini bermanfaat dan ingin menyemangati pengembang "
            "agar terus terawat dan berkembang, yuk dukung lewat donasi sukarela melalui GoPay.\n\n"
            "Pilih 'Donasi' untuk melihat informasi akun GoPay, atau 'Tidak Sekarang' untuk "
            "langsung melanjutkan proses instalasi."
        )

        self.text_ctrl = wx.TextCtrl(
            self,
            value=welcome_text,
            style=wx.TE_MULTILINE | wx.TE_READONLY,
            size=(500, 210),
        )
        sizer.Add(self.text_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.donate_btn = wx.Button(self, label=_("Donasi"))
        self.donate_btn.Bind(wx.EVT_BUTTON, self._on_donate)
        btn_sizer.Add(self.donate_btn, flag=wx.RIGHT, border=10)

        self.continue_btn = wx.Button(self, wx.ID_OK, label=_("Tidak Sekarang"))
        self.continue_btn.Bind(wx.EVT_BUTTON, self._on_continue)
        self.continue_btn.SetDefault()
        btn_sizer.Add(self.continue_btn)

        sizer.Add(btn_sizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

        self.SetSizer(sizer)
        self.Fit()
        self.SetMinSize(self.GetSize())
        self.donate_btn.SetFocus()
        self.Bind(wx.EVT_CLOSE, self._on_close)

    def _on_donate(self, evt: wx.CommandEvent) -> None:
        dlg = DonationDetailsDialog(self)
        try:
            dlg.ShowModal()
        finally:
            dlg.Destroy()

    def _on_continue(self, evt: wx.CommandEvent) -> None:
        self.EndModal(wx.ID_OK)

    def _on_close(self, evt: wx.Event) -> None:
        self.EndModal(wx.ID_OK)


def _defensive_cleanup_nvda_import_tracker(addon_name: str) -> None:
    """Forcefully detach any built-in/compiled module without __file__ attribute.

    Protects NVDA's _cleanupAddonImports from crashing in Python 3.13 when
    inspecting built-in modules lacking file paths.
    """
    if not hasattr(addonHandler, "_addonImportTrackers"):
        return

    tracker_set = getattr(addonHandler, "_addonImportTrackers", {}).get(addon_name)
    if not tracker_set:
        return

    to_remove = []
    for mod in tracker_set:
        if not hasattr(mod, "__file__"):
            to_remove.append(mod)
            continue

        spec = getattr(mod, "__spec__", None)
        if spec and getattr(spec, "origin", None) == "built-in":
            to_remove.append(mod)
            continue

        try:
            file_path = getattr(mod, "__file__", "")
            if not file_path or not str(file_path).startswith(_ADDON_DIR):
                to_remove.append(mod)
        except Exception:
            to_remove.append(mod)

    for invalid_mod in to_remove:
        try:
            tracker_set.remove(invalid_mod)
            log.debug(
                f"Emoji ID installTasks: Scrubber removed '{getattr(invalid_mod, '__name__', 'unknown')}' from tracker"
            )
        except KeyError:
            pass


def onInstall() -> None:
    """Execute installation tasks and display the welcome & donation dialog safely on the main GUI thread."""
    addon = addonHandler.getCodeAddon() if hasattr(addonHandler, "getCodeAddon") else None
    addon_name = addon.manifest.get("summary") or addon.manifest.get("name") if addon else "Emoji ID"

    done_event = threading.Event()

    def _show_dialog() -> None:
        prePopup = getattr(gui.mainFrame, "prePopup", lambda: None)
        postPopup = getattr(gui.mainFrame, "postPopup", lambda: None)
        prePopup()
        dialog = None
        try:
            dialog = InstallWelcomeDialog(gui.mainFrame)
            dialog.ShowModal()
        except Exception:
            log.error("Emoji ID installTasks: failed to show install dialog", exc_info=True)
        finally:
            try:
                if dialog:
                    dialog.Destroy()
                postPopup()
            finally:
                # Release the waiting installation thread
                done_event.set()

    wx.CallAfter(_show_dialog)
    # Wait for the user to close the dialog before proceeding with installation
    done_event.wait()

    # Clean up import tracker safely for Python 3.13
    try:
        _defensive_cleanup_nvda_import_tracker(str(addon_name))
    except Exception as e:
        log.error(f"Emoji ID installTasks: defensive cleanup scrubber failed: {e}", exc_info=True)
