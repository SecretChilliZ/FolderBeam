from pathlib import Path
from folderbeam.config import Config


def test_roundtrip(tmp_path):
    p = tmp_path / "config.json"
    c = Config(
        root_dir=str(tmp_path / "share"),
        dav_port=8080,
        ui_port=8081,
        username="alice",
        password="secret",
        enable_wan=False,
    )
    c.save(p)
    loaded = Config.load(p)
    assert loaded == c


def test_load_missing_returns_defaults(tmp_path):
    loaded = Config.load(tmp_path / "nope.json")
    assert loaded.dav_port == 8080
    assert loaded.ui_port == 8081
    assert loaded.enable_wan is False
