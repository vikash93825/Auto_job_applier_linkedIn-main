'''
Load PyAutoGUI when an X11/Wayland display is available; otherwise use stubs so
imports and headless/SSH runs do not crash with DisplayConnectionError.
'''
from __future__ import annotations

import sys
from typing import Any, Sequence

try:
    import pyautogui as _pyautogui  # type: ignore
except Exception:
    _pyautogui = None  # type: ignore


def _print_gui_fallback(kind: str, title: str, text: str, buttons: Sequence[str] | None = None) -> None:
    lines = [f"\n[{kind} — no GUI display; PyAutoGUI stub]", f"Title: {title}", text]
    if buttons:
        lines.append(f"Buttons: {list(buttons)}")
    print("\n".join(lines), file=sys.stderr)


def _stub_alert(text: str = "", title: str = "", button: str = "OK") -> str:
    _print_gui_fallback("alert", title, str(text))
    return button


def _stub_confirm(
    text: str = "",
    title: str | list[str] | tuple[str, ...] = "",
    buttons: list[str] | tuple[str, ...] | None = None,
) -> str:
    # PyAutoGUI allows confirm(msg, [btn1, btn2]) — second positional is buttons, not title.
    if buttons is None and isinstance(title, (list, tuple)):
        buttons = title
        title = ""
    if not buttons:
        buttons = ("OK",)
    else:
        buttons = tuple(buttons)
    title_str = title if isinstance(title, str) else ""
    _print_gui_fallback("confirm", title_str, str(text), buttons)
    # Sensible defaults when nobody can click (matches common “continue” paths).
    if len(buttons) == 2:
        if "Look's good, Continue" in buttons:
            return "Look's good, Continue"
        if "Yes" in buttons and "No" in buttons:
            return "No"
        return buttons[-1]
    if len(buttons) == 3 and "Disable Pause" in buttons:
        return "Disable Pause"
    return buttons[0]


def _stub_press(_key: str) -> None:
    pass


if _pyautogui is not None:
    pyautogui = _pyautogui
    alert = _pyautogui.alert
    confirm = _pyautogui.confirm
    press = _pyautogui.press
else:

    class _PyAutoStub:
        FAILSAFE = False

        alert = staticmethod(_stub_alert)
        confirm = staticmethod(_stub_confirm)
        press = staticmethod(_stub_press)

    pyautogui = _PyAutoStub()
    alert = pyautogui.alert
    confirm = pyautogui.confirm
    press = pyautogui.press
