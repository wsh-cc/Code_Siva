import tkinter as tk

from client.app import EMOJI_CATEGORIES, OchatApp


def test_ochat_app_does_not_override_tk_register() -> None:
    assert OchatApp._register is tk.Tk._register


def test_emoji_catalog_has_expanded_choices() -> None:
    emojis = [emoji for _category, values in EMOJI_CATEGORIES for emoji in values]

    assert len(emojis) >= 70
    assert len(emojis) == len(set(emojis))
    assert all(emoji.strip() for emoji in emojis)
