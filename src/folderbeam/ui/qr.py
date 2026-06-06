from __future__ import annotations

import io
import qrcode


def qr_png_bytes(text: str) -> bytes:
    """Render `text` as a QR PNG and return the raw bytes."""
    img = qrcode.make(text)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def qr_pixmap(text: str):
    """Return a QPixmap of the QR. Imported lazily so non-GUI tests stay light."""
    from PySide6.QtGui import QPixmap
    pm = QPixmap()
    pm.loadFromData(qr_png_bytes(text), "PNG")
    return pm
