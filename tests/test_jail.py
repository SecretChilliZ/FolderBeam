from pathlib import Path
import pytest
from folderbeam.server.jail import safe_resolve


def test_resolves_inside(tmp_path):
    root = tmp_path / "share"
    root.mkdir()
    target = safe_resolve(root, "sub/file.txt")
    assert str(target).startswith(str(root.resolve()))


def test_root_itself_allowed(tmp_path):
    root = tmp_path / "share"
    root.mkdir()
    assert safe_resolve(root, "") == root.resolve()


def test_dotdot_escape_blocked(tmp_path):
    root = tmp_path / "share"
    root.mkdir()
    with pytest.raises(PermissionError):
        safe_resolve(root, "../secret.txt")


def test_absolute_escape_blocked(tmp_path):
    root = tmp_path / "share"
    root.mkdir()
    with pytest.raises(PermissionError):
        safe_resolve(root, "C:/Windows/system32")


def test_sneaky_nested_escape_blocked(tmp_path):
    root = tmp_path / "share"
    root.mkdir()
    with pytest.raises(PermissionError):
        safe_resolve(root, "a/b/../../../outside.txt")
