from folderbeam.ui.qr import qr_png_bytes


def test_qr_png_bytes_nonempty():
    data = qr_png_bytes("http://192.168.1.50:8081/")
    assert isinstance(data, (bytes, bytearray))
    assert data[:8] == b"\x89PNG\r\n\x1a\n"  # PNG magic
