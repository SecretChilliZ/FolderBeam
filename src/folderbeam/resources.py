from __future__ import annotations

import sys
from pathlib import Path


def _root() -> Path:
    """Directory holding the bundled .ico files.

    - Frozen (PyInstaller): bundle root via --add-data (sys._MEIPASS for
      onefile, or next to the exe).
    - Source / editable (uv run): the project root (src/folderbeam/
      resources.py -> parents[2]).
    """
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parents[2]


def icon_path() -> Path:
    """App / window / taskbar icon (the chilli)."""
    return _root() / "folderbeam.ico"


def status_icon_path(running: bool) -> Path:
    """Tray icon reflecting server state: green when running, red when stopped."""
    return _root() / ("green.ico" if running else "red.ico")
