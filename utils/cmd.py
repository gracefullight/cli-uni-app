"""CLI helper utilities."""

import os


def clear_screen() -> None:
    """Clear terminal screen in a cross-platform manner."""
    os.system("cls" if os.name == "nt" else "clear")


def pause(msg: str = "Press Enter to continue...") -> None:
    """Pause execution awaiting user to press Enter."""
    input(msg)
