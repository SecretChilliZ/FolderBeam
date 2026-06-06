import os
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def test_panel_constructs_and_toggles(qapp, tmp_path):
    from folderbeam.config import Config
    from folderbeam.ui.panel import ControlPanel

    class FakeManager:
        def __init__(self, cfg): self.cfg = cfg; self._on = False
        def is_running(self): return self._on
        def start(self): self._on = True
        def stop(self): self._on = False

    cfg = Config(root_dir=str(tmp_path / "share"))
    panel = ControlPanel(cfg, manager_factory=FakeManager)
    assert panel.manager.is_running() is False

    panel._on_toggle()
    assert panel.manager.is_running() is True
    assert "Stop" in panel.toggle_btn.text()

    panel._on_toggle()
    assert panel.manager.is_running() is False
    assert "Start" in panel.toggle_btn.text()


def test_status_icon_renders(qapp, tmp_path):
    from folderbeam.config import Config
    from folderbeam.ui.panel import ControlPanel

    class FakeManager:
        def __init__(self, cfg): self._on = False
        def is_running(self): return self._on
        def start(self): self._on = True
        def stop(self): self._on = False

    cfg = Config(root_dir=str(tmp_path / "share"))
    panel = ControlPanel(cfg, manager_factory=FakeManager)
    assert not panel._status_icon(True).isNull()   # green.ico
    assert not panel._status_icon(False).isNull()  # red.ico
