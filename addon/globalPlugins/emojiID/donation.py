# -*- coding: UTF-8 -*-
# Emoji ID - Indonesian Emoji Reader for NVDA
# Copyright (C) 2026 Rexya Muhamad <rexya2017@gmail.com>
# This file is covered by the GNU General Public License v2 or later.
# See the file LICENSE for more details.

"""Donation and welcome dialogs for Emoji ID add-on.

Provides screen-reader friendly modal dialogs for:
- Welcome message during installation with donation invitation
- Donation details (GoPay) with quick clipboard copy
- Friendly periodic donation reminders during runtime
"""

from __future__ import annotations

import logging
from typing import Any

import wx

try:
    _ = _  # type: ignore[name-defined]
except NameError:
    try:
        import addonHandler

        addonHandler.initTranslation()
    except Exception:
        _ = lambda x: x

log = logging.getLogger(__name__)

GOPAY_NUMBER = "085128011831"
GOPAY_NAME = "Rexya Muhamad Rizki"


def copy_to_clipboard(text: str) -> bool:
    """Copy text to system clipboard via wx.TheClipboard."""
    try:
        if wx.TheClipboard.Open():
            data = wx.TextDataObject(text)
            wx.TheClipboard.SetData(data)
            wx.TheClipboard.Close()
            return True
    except Exception:
        log.warning("Emoji ID: gagal menyalin ke papan klip", exc_info=True)
    return False


def _safe_popup(dlg: wx.Dialog) -> int:
    """Safely show a modal dialog respecting NVDA mainFrame focus hooks."""
    try:
        import gui

        mainFrame = getattr(gui, "mainFrame", None)
        prePopup = getattr(mainFrame, "prePopup", lambda: None)
        postPopup = getattr(mainFrame, "postPopup", lambda: None)
    except Exception:
        prePopup = lambda: None
        postPopup = lambda: None

    prePopup()
    try:
        return dlg.ShowModal()
    finally:
        postPopup()
        dlg.Destroy()


class DonationDetailsDialog(wx.Dialog):
    """Dialog displaying GoPay donation information and copy button."""

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

    def _on_copy(self, evt: wx.CommandEvent) -> None:
        if copy_to_clipboard(GOPAY_NUMBER):
            msg = _("Nomor GoPay 085128011831 telah disalin ke papan klip.")
        else:
            msg = _("Gagal menyalin nomor ke papan klip.")
        try:
            import ui

            ui.message(msg)
        except Exception:
            pass

    def _on_close(self, evt: wx.CommandEvent) -> None:
        self.EndModal(wx.ID_CLOSE)


class WelcomeDialog(wx.Dialog):
    """Welcome dialog displayed on first run after add-on installation."""

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
            "Pilih 'Donasi' untuk melihat informasi GoPay, atau 'Tidak Sekarang' untuk "
            "langsung menikmati add-on."
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

        self.not_now_btn = wx.Button(self, wx.ID_CANCEL, label=_("Tidak Sekarang"))
        self.not_now_btn.Bind(wx.EVT_BUTTON, self._on_not_now)
        btn_sizer.Add(self.not_now_btn)

        sizer.Add(btn_sizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

        self.SetSizer(sizer)
        self.Fit()
        self.SetMinSize(self.GetSize())
        self.donate_btn.SetFocus()

    def _on_donate(self, evt: wx.CommandEvent) -> None:
        show_donation_details_dialog(self)

    def _on_not_now(self, evt: wx.CommandEvent) -> None:
        self.EndModal(wx.ID_CANCEL)


# Alias for compatibility
InstallWelcomeDialog = WelcomeDialog


class ReminderDialog(wx.Dialog):
    """Periodic reminder dialog to invite user donation."""

    def __init__(self, parent: wx.Window | None = None) -> None:
        super().__init__(
            parent,
            title=_("Dukungan Pengembang - Emoji ID"),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self._init_ui()
        self.CentreOnParent()

    def _init_ui(self) -> None:
        sizer = wx.BoxSizer(wx.VERTICAL)

        reminder_text = (
            "Hai! Semoga Emoji ID membantu kelancaran aktivitasmu sehari-hari.\n\n"
            "Jika kamu merasa terbantu dan ingin menyemangati pengembang agar add-on ini terus diperbarui, "
            "yuk dukung lewat donasi sukarela via GoPay.\n\n"
            "Pilih 'Donasi' untuk melihat informasi GoPay, atau 'Tidak Sekarang' untuk "
            "melanjutkan aktivitas."
        )

        self.text_ctrl = wx.TextCtrl(
            self,
            value=reminder_text,
            style=wx.TE_MULTILINE | wx.TE_READONLY,
            size=(480, 190),
        )
        sizer.Add(self.text_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.donate_btn = wx.Button(self, label=_("Donasi"))
        self.donate_btn.Bind(wx.EVT_BUTTON, self._on_donate)
        btn_sizer.Add(self.donate_btn, flag=wx.RIGHT, border=10)

        self.not_now_btn = wx.Button(self, wx.ID_CANCEL, label=_("Tidak Sekarang"))
        self.not_now_btn.Bind(wx.EVT_BUTTON, self._on_not_now)
        btn_sizer.Add(self.not_now_btn)

        sizer.Add(btn_sizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

        self.SetSizer(sizer)
        self.Fit()
        self.SetMinSize(self.GetSize())
        self.donate_btn.SetFocus()

    def _on_donate(self, evt: wx.CommandEvent) -> None:
        show_donation_details_dialog(self)

    def _on_not_now(self, evt: wx.CommandEvent) -> None:
        self.EndModal(wx.ID_CANCEL)


def show_donation_details_dialog(parent: wx.Window | None = None) -> None:
    """Open the GoPay donation details dialog."""
    try:
        import gui

        if parent is None:
            parent = getattr(gui, "mainFrame", None)
        dlg = DonationDetailsDialog(parent)
        _safe_popup(dlg)
    except Exception:
        log.warning("Emoji ID: gagal menampilkan dialog detail donasi", exc_info=True)


def show_welcome_dialog(parent: wx.Window | None = None) -> None:
    """Open the welcome and donation dialog on first run."""
    try:
        import gui

        if parent is None:
            parent = getattr(gui, "mainFrame", None)
        dlg = WelcomeDialog(parent)
        _safe_popup(dlg)
    except Exception:
        log.warning("Emoji ID: gagal menampilkan dialog selamat datang", exc_info=True)


# Alias for compatibility
show_install_dialog = show_welcome_dialog


def show_reminder_dialog(parent: wx.Window | None = None) -> None:
    """Open the periodic donation reminder dialog."""
    try:
        import gui

        if parent is None:
            parent = getattr(gui, "mainFrame", None)
        dlg = ReminderDialog(parent)
        _safe_popup(dlg)
    except Exception:
        log.warning("Emoji ID: gagal menampilkan dialog pengingat donasi", exc_info=True)
