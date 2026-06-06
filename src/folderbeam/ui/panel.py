from __future__ import annotations

import webbrowser
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QPushButton, QLabel, QFileDialog,
    QSystemTrayIcon, QMenu, QApplication,
)

from ..config import Config
from ..netutil import lan_ip, client_urls
from ..resources import icon_path, status_icon_path
from ..server.manager import ServerManager
from .qr import qr_pixmap

GREEN = "#2a8a2a"
GREY = "#777777"


class ControlPanel(QMainWindow):
    def __init__(self, cfg: Config, config_path: Path | None = None,
                 manager_factory=ServerManager):
        super().__init__()
        self.cfg = cfg
        self.config_path = config_path
        self.manager = manager_factory(cfg)
        self.setWindowTitle("FolderBeam")
        self.setWindowIcon(QIcon(str(icon_path())))
        self.resize(560, 520)
        self._quitting = False
        self.tray = None
        self._build()
        self._build_tray()
        self._refresh_status()

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        form = QFormLayout()
        self.root_edit = QLineEdit(self.cfg.root_dir)
        browse = QPushButton("Browse...")
        browse.clicked.connect(self._pick_folder)
        rrow = QHBoxLayout()
        rrow.addWidget(self.root_edit, 1)
        rrow.addWidget(browse)
        rwrap = QWidget(); rwrap.setLayout(rrow)
        form.addRow("Shared folder", rwrap)

        self.dav_port = QSpinBox(); self.dav_port.setRange(1, 65535)
        self.dav_port.setValue(self.cfg.dav_port)
        self.ui_port = QSpinBox(); self.ui_port.setRange(1, 65535)
        self.ui_port.setValue(self.cfg.ui_port)
        form.addRow("WebDAV port", self.dav_port)
        form.addRow("Browser port", self.ui_port)

        self.user_edit = QLineEdit(self.cfg.username)
        self.pass_edit = QLineEdit(self.cfg.password)
        form.addRow("Username", self.user_edit)
        form.addRow("Password", self.pass_edit)
        root.addLayout(form)

        self.status_dot = QLabel("● Stopped")
        self.status_dot.setStyleSheet(f"color:{GREY}; font-size:15px;")
        root.addWidget(self.status_dot)

        self.toggle_btn = QPushButton("Start")
        self.toggle_btn.clicked.connect(self._on_toggle)
        root.addWidget(self.toggle_btn)

        self.dav_url = QLabel(""); self.dav_url.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.ui_url = QLabel(""); self.ui_url.setTextInteractionFlags(Qt.TextSelectableByMouse)
        root.addWidget(self.dav_url)
        root.addWidget(self.ui_url)

        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        root.addWidget(self.qr_label, 1)

        hint = QLabel("Allow these ports through Windows Firewall (Private + Public). "
                      "On each VPN, enable 'allow local network'.")
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color:{GREY};")
        root.addWidget(hint)

    def _pick_folder(self):
        d = QFileDialog.getExistingDirectory(self, "Choose shared folder", self.root_edit.text())
        if d:
            self.root_edit.setText(d)

    def _sync_cfg_from_form(self):
        self.cfg.root_dir = self.root_edit.text().strip()
        self.cfg.dav_port = self.dav_port.value()
        self.cfg.ui_port = self.ui_port.value()
        self.cfg.username = self.user_edit.text()
        self.cfg.password = self.pass_edit.text()
        if self.config_path:
            self.cfg.save(self.config_path)

    def _on_toggle(self):
        if self.manager.is_running():
            self.manager.stop()
        else:
            self._sync_cfg_from_form()
            Path(self.cfg.root_dir).mkdir(parents=True, exist_ok=True)
            self.manager = type(self.manager)(self.cfg)
            self.manager.start()
        self._refresh_status()

    def _refresh_status(self):
        running = self.manager.is_running()
        if running:
            self.status_dot.setText("● Running")
            self.status_dot.setStyleSheet(f"color:{GREEN}; font-size:15px;")
            self.toggle_btn.setText("Stop")
            ip = lan_ip()
            urls = client_urls(ip, self.cfg.dav_port, self.cfg.ui_port)
            self.dav_url.setText(f"WebDAV (MiXplorer / map drive):  {urls['webdav']}")
            self.ui_url.setText(f"Browser file manager:  {urls['browser']}")
            self.qr_label.setPixmap(
                qr_pixmap(urls["browser"]).scaledToWidth(220, Qt.SmoothTransformation)
            )
        else:
            self.status_dot.setText("● Stopped")
            self.status_dot.setStyleSheet(f"color:{GREY}; font-size:15px;")
            self.toggle_btn.setText("Start")
            self.dav_url.setText("")
            self.ui_url.setText("")
            self.qr_label.setPixmap(QPixmap())
        if self.tray:
            self.tray.setIcon(self._status_icon(running))
            self.tray.setToolTip(f"FolderBeam — {'Running' if running else 'Stopped'}")
            self.tray_toggle.setText("Stop" if running else "Start")

    def _status_icon(self, running: bool) -> QIcon:
        return QIcon(str(status_icon_path(running)))

    def _build_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray = QSystemTrayIcon(self._status_icon(False), self)
        menu = QMenu()
        self._tray_menu = menu  # keep a ref so it is not garbage collected
        self.tray_toggle = menu.addAction("Start")
        self.tray_toggle.triggered.connect(self._on_toggle)
        menu.addAction("Show / hide window").triggered.connect(self._toggle_window)
        menu.addAction("Open in browser").triggered.connect(self._open_browser)
        menu.addSeparator()
        menu.addAction("Quit").triggered.connect(self._quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.setToolTip("FolderBeam — Stopped")
        self.tray.show()

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # left click
            self._toggle_window()

    def _toggle_window(self):
        if self.isVisible():
            self.hide()
        else:
            self.showNormal()
            self.raise_()
            self.activateWindow()

    def _open_browser(self):
        if not self.manager.is_running():
            return
        url = client_urls(lan_ip(), self.cfg.dav_port, self.cfg.ui_port)["browser"]
        webbrowser.open(url)

    def _quit(self):
        self._quitting = True
        self.close()

    def closeEvent(self, event):
        # With a tray, closing the window hides to tray. Without a tray, or
        # when quitting explicitly, actually shut down.
        if self.tray and not self._quitting:
            event.ignore()
            self.hide()
            self.tray.showMessage("FolderBeam", "Still running in the tray.",
                                  QSystemTrayIcon.Information, 2000)
            return
        if self.manager.is_running():
            self.manager.stop()
        if self.tray:
            self.tray.hide()
        super().closeEvent(event)
        QApplication.quit()
