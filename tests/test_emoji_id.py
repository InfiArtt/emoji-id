# -*- coding: UTF-8 -*-
"""Unit tests for Emoji ID add-on.

Self-contained runner that does not depend on optional standard library modules like unittest.
Tests:
1. U+FE0F variation selector handling (with and without FE0F)
2. ZWJ sequences (family, profession, couples)
3. Skin tone modifiers and skin_tone_detail option
4. Country and regional flags
5. Combining enclosing keycaps
6. Empty input and text without emoji
7. Mixed text with multiple emojis
8. Consecutive repeated emoji collapsing
9. Prefix configuration (on/off, custom text, prefix once)
10. SpeechSequence filtering (preservation of non-str items and order)
11. Single-character processSpeechSymbol patch and fallback
12. Enabling/disabling toggle behavior
13. Clean termination and unpatching
"""

import os
import sys

# Ensure UTF-8 stdout on Windows console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import re

# Ensure paths
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
addon_root = os.path.join(repo_root, "addon")
addon_path = os.path.join(repo_root, "addon", "globalPlugins")
tests_path = os.path.join(repo_root, "tests")

if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if addon_root not in sys.path:
    sys.path.insert(0, addon_root)
if tests_path not in sys.path:
    sys.path.insert(0, tests_path)
if addon_path not in sys.path:
    sys.path.insert(0, addon_path)

import nvda_mocks  # noqa: F401
import characterProcessing  # noqa: F401
import config  # noqa: F401
import speech.extensions  # noqa: F401
from emojiID.emoji_data import EmojiMatcher
from emojiID import GlobalPlugin


def run_tests():
    passed = 0
    failed = 0

    def assert_eq(actual, expected, msg=""):
        if actual != expected:
            raise AssertionError(f"{msg}: expected {expected!r}, got {actual!r}")

    def assert_true(cond, msg=""):
        if not cond:
            raise AssertionError(f"{msg}: expected True")

    def assert_in(member, container, msg=""):
        if member not in container:
            raise AssertionError(f"{msg}: expected {member!r} in {container!r}")

    def test(name, func):
        nonlocal passed, failed
        try:
            func()
            print(f"  [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            failed += 1

    print("=" * 60)
    print("RUNNING EMOJI ID UNIT TESTS")
    print("=" * 60)

    # 1. Matcher tests
    matcher = EmojiMatcher()
    assert_true(matcher.load(), "Load data")

    test("Data loaded and count > 3000", lambda: assert_true(matcher.count > 3000))

    test(
        "FE0F handling (heart with and without FE0F)",
        lambda: [
            assert_eq(matcher.replace_in_text("\u2764\uFE0F"), "hati merah"),
            assert_eq(matcher.replace_in_text("\u2764"), "hati merah"),
        ],
    )

    test(
        "ZWJ sequence (family 👨‍👩‍👧)",
        lambda: assert_in("keluarga", matcher.replace_in_text("👨‍👩‍👧").lower()),
    )

    test(
        "Flags (Indonesia 🇮🇩)",
        lambda: assert_in("indonesia", matcher.replace_in_text("🇮🇩").lower()),
    )

    test(
        "Keycaps (1️⃣)",
        lambda: assert_true(
            any(k in matcher.replace_in_text("1\uFE0F\u20E3").lower() for k in ("1", "angka", "tombol"))
        ),
    )

    test(
        "Skin tone detail True vs False",
        lambda: [
            assert_in("kulit", matcher.replace_in_text("👍🏽", skin_tone_detail=True).lower()),
            assert_true("kulit" not in matcher.replace_in_text("👍🏽", skin_tone_detail=False).lower()),
            assert_in("jempol", matcher.replace_in_text("👍🏽", skin_tone_detail=False).lower()),
        ],
    )

    test(
        "Empty and plain text without emoji",
        lambda: [
            assert_eq(matcher.replace_in_text(""), ""),
            assert_eq(matcher.replace_in_text("Halo dunia!"), "Halo dunia!"),
        ],
    )

    test(
        "Mixed text with emojis",
        lambda: [
            assert_in("wajah gembira", matcher.replace_in_text("Halo 😀 apa kabar?")),
            assert_true(matcher.replace_in_text("Halo 😀 apa kabar?").startswith("Halo ")),
            assert_true(matcher.replace_in_text("Halo 😀 apa kabar?").endswith(" apa kabar?")),
        ],
    )

    test(
        "Collapse repeated identical emoji",
        lambda: [
            assert_eq(matcher.replace_in_text("😀😀😀", collapse_repeated=True), "3 kali wajah gembira"),
            assert_eq(
                matcher.replace_in_text("😀😀😀", collapse_repeated=False),
                "wajah gembira wajah gembira wajah gembira",
            ),
        ],
    )

    test(
        "Prefix configuration and prefix once with spaces/commas",
        lambda: [
            assert_eq(matcher.replace_in_text("😀", prefix="emoji"), "emoji wajah gembira"),
            assert_eq(
                matcher.replace_in_text("😀👍", prefix="emoji", prefix_once=True),
                "emoji wajah gembira jempol ke atas",
            ),
            assert_eq(
                matcher.replace_in_text("😂, 👋, 👨‍🦯", prefix="emoji", prefix_once=True),
                "emoji wajah gembira berurai air mata, tangan melambai, pria dengan tongkat",
            ),
            assert_eq(
                matcher.replace_in_text("😂 👋 👨‍🦯", prefix="emoji", prefix_once=True),
                "emoji wajah gembira berurai air mata tangan melambai pria dengan tongkat",
            ),
            assert_eq(
                matcher.replace_in_text("😂 😂 😂", prefix="emoji", prefix_once=True, collapse_repeated=True),
                "emoji 3 kali wajah gembira berurai air mata",
            ),
            assert_eq(
                matcher.replace_in_text("😂, 😂, 😂", prefix="emoji", prefix_once=True, collapse_repeated=True),
                "emoji 3 kali wajah gembira berurai air mata",
            ),
        ],
    )

    test(
        "Hand-maintained overrides",
        lambda: [
            assert_eq(matcher.replace_in_text("🤥"), "bohong"),
            assert_eq(matcher.replace_in_text("💩"), "kotoran"),
            assert_eq(matcher.replace_in_text("🤧"), "bersin"),
            assert_eq(matcher.replace_in_text("💨"), "berlari"),
        ],
    )

    test(
        "Clean symbols (hyphens and parentheses in emoji names vs text outside)",
        lambda: [
            assert_eq(matcher.replace_in_text("🦋", clean_symbols=True), "kupu kupu"),
            assert_eq(matcher.replace_in_text("🦋", clean_symbols=False), "kupu-kupu"),
            assert_eq(matcher.replace_in_text("👆", clean_symbols=True), "menunjuk ke atas dibalik"),
            assert_eq(matcher.replace_in_text("👆", clean_symbols=False), "menunjuk ke atas (dibalik)"),
            assert_eq(
                matcher.replace_in_text("Pasal 1-2 (a) 🦋 hal 3-4", clean_symbols=True),
                "Pasal 1-2 (a) kupu kupu hal 3-4",
            ),
        ],
    )

    # 2. GlobalPlugin Integration tests
    config.conf["emojiID"]["enabled"] = True
    config.conf["emojiID"]["prefix"] = True
    config.conf["emojiID"]["prefixText"] = "emoji"
    config.conf["emojiID"]["prefixOnce"] = False
    config.conf["emojiID"]["collapseRepeated"] = True
    config.conf["emojiID"]["skinToneDetail"] = True

    plugin = GlobalPlugin()

    test(
        "Single-character trap intercepted via processSpeechSymbol",
        lambda: assert_eq(characterProcessing.processSpeechSymbol("en", "😀"), "emoji wajah gembira"),
    )

    class MockCommand:
        def __init__(self, tag):
            self.tag = tag

        def __repr__(self):
            return f"MockCmd({self.tag})"

    cmd1 = MockCommand("index_1")
    cmd2 = MockCommand("callback_break")
    seq = ["Lihat ", cmd1, "😀 dan 👍", cmd2, " selesai."]

    test(
        "SpeechSequence filter preserves non-str items and order",
        lambda: [
            assert_eq(len(speech.extensions.filter_speechSequence.apply(seq)), 5),
            assert_eq(speech.extensions.filter_speechSequence.apply(seq)[0], "Lihat "),
            assert_true(speech.extensions.filter_speechSequence.apply(seq)[1] is cmd1),
            assert_in("emoji wajah gembira", speech.extensions.filter_speechSequence.apply(seq)[2]),
            assert_true(speech.extensions.filter_speechSequence.apply(seq)[3] is cmd2),
            assert_eq(speech.extensions.filter_speechSequence.apply(seq)[4], " selesai."),
        ],
    )

    test(
        "Disabled state restores NVDA defaults",
        lambda: [
            config.conf["emojiID"].__setitem__("enabled", False),
            assert_eq(characterProcessing.processSpeechSymbol("en", "😀"), "grinning face"),
            assert_eq(speech.extensions.filter_speechSequence.apply(["Halo 😀"]), ["Halo 😀"]),
            config.conf["emojiID"].__setitem__("enabled", True),
        ],
    )

    test(
        "Plugin termination restores original functions cleanly",
        lambda: [
            plugin.terminate(),
            assert_eq(characterProcessing.processSpeechSymbol("en", "😀"), "grinning face"),
        ],
    )

    from emojiID.donation import (
        GOPAY_NAME,
        GOPAY_NUMBER,
        DonationDetailsDialog,
        InstallWelcomeDialog,
        ReminderDialog,
        copy_to_clipboard,
    )
    from emojiID.settings import EmojiIDSettingsPanel

    test(
        "GoPay donation details and clipboard copy",
        lambda: [
            assert_eq(GOPAY_NUMBER, "085128011831"),
            assert_eq(GOPAY_NAME, "Rexya Muhamad Rizki"),
            assert_true(copy_to_clipboard("085128011831")),
            assert_eq(nvda_mocks.mock_wx.TheClipboard.data, "085128011831"),
        ],
    )

    test(
        "Donation dialogs initialization and absence of forbidden word 'anda'",
        lambda: [
            # Check details dialog
            (details_dlg := DonationDetailsDialog()),
            assert_in("085128011831", details_dlg.text_ctrl.value),
            assert_in("Rexya Muhamad Rizki", details_dlg.text_ctrl.value),
            assert_true(
                not bool(re.search(r"\banda\b", details_dlg.text_ctrl.value, re.IGNORECASE)),
                "Kata 'anda' ditemukan di dialog detail donasi",
            ),
            # Check welcome dialog
            (welcome_dlg := InstallWelcomeDialog()),
            assert_in("Selamat datang di Emoji ID", welcome_dlg.text_ctrl.value),
            assert_true(
                not bool(re.search(r"\banda\b", welcome_dlg.text_ctrl.value, re.IGNORECASE)),
                "Kata 'anda' ditemukan di dialog instalasi",
            ),
            # Check reminder dialog
            (reminder_dlg := ReminderDialog()),
            assert_in("Hai!", reminder_dlg.text_ctrl.value),
            assert_true(
                not bool(re.search(r"\banda\b", reminder_dlg.text_ctrl.value, re.IGNORECASE)),
                "Kata 'anda' ditemukan di dialog pengingat",
            ),
        ],
    )

    test(
        "First-run welcome dialog triggers and updates firstRun config",
        lambda: [
            config.conf["emojiID"].__setitem__("firstRun", True),
            (p_first := GlobalPlugin()),
            p_first.terminate(),
            assert_true(not config.conf["emojiID"]["firstRun"], "firstRun should be marked False after display"),
        ],
    )

    test(
        "Periodic donation timer lifecycle in GlobalPlugin",
        lambda: [
            (p2 := GlobalPlugin()),
            assert_true(p2._donationTimer is not None, "Donation timer should be scheduled"),
            p2.terminate(),
            assert_true(p2._donationTimer is None, "Donation timer should be canceled"),
        ],
    )

    test(
        "Settings panel donation controls and save",
        lambda: [
            (panel := EmojiIDSettingsPanel()),
            panel.makeSettings(nvda_mocks.mock_wx.BoxSizer()),
            assert_true(hasattr(panel, "donateButton"), "Missing donate button"),
            assert_true(hasattr(panel, "periodicReminderCheckbox"), "Missing reminder checkbox"),
            panel.onSave(),
            assert_true(config.conf["emojiID"]["periodicDonationReminder"]),
        ],
    )

    print("=" * 60)
    print(f"TEST RESULTS: {passed} PASSED, {failed} FAILED")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
