import tkinter as tk

from client.app import OchatApp


def test_ochat_app_does_not_override_tk_register() -> None:
    assert OchatApp._register is tk.Tk._register
