from folderbeam.resources import icon_path


def test_icon_bundled_and_valid():
    p = icon_path()
    assert p.exists(), f"icon missing at {p}"
    assert p.suffix == ".ico"
    assert p.read_bytes()[:4] == b"\x00\x00\x01\x00"  # ICO magic
