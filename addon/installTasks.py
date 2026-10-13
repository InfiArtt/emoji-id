# -*- coding: UTF-8 -*-
# Emoji ID - Indonesian Emoji Reader for NVDA
# Copyright (C) 2026 Rexya Muhamad <rexya2017@gmail.com>
# This file is covered by the GNU General Public License v2 or later.
# See the file LICENSE for more details.

"""Installation tasks for Emoji ID add-on.

NVDA invokes functions in this module during installation:
- onInstall(): Called when installing the add-on. Displays a welcome message
  and an invitation to support development through GoPay donations.
"""

from __future__ import annotations

import logging
import os
import sys

log = logging.getLogger(__name__)


def onInstall() -> None:
    """Execute installation tasks and display the welcome & donation dialog."""
    # Ensure addon/globalPlugins is on sys.path so emojiID package can be loaded
    addon_dir = os.path.dirname(os.path.abspath(__file__))
    gp_dir = os.path.join(addon_dir, "globalPlugins")
    if gp_dir not in sys.path:
        sys.path.insert(0, gp_dir)

    try:
        from emojiID.donation import show_install_dialog

        show_install_dialog()
    except Exception:
        log.warning("Emoji ID: gagal menampilkan dialog selamat datang saat instalasi", exc_info=True)
