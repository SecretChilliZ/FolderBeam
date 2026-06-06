from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from .config import Config
from .resources import icon_path
from .ui.panel import ControlPanel

CONFIG_PATH = Path.home() / ".folderbeam" / "config.json"


def main():
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    cfg = Config.load(CONFIG_PATH)

    if sys.platform == "win32":
        # Detach taskbar identity from python.exe so our icon shows there.
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("folderbeam.app")
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(icon_path())))
    app.setQuitOnLastWindowClosed(False)  # keep running in the tray
    # Native Windows 11 style follows the OS light/dark setting for free.
    # Uncomment to force dark regardless of OS (PySide6 6.8+):
    # from PySide6.QtCore import Qt
    # app.styleHints().setColorScheme(Qt.ColorScheme.Dark)

    panel = ControlPanel(cfg, config_path=CONFIG_PATH)
    panel.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
