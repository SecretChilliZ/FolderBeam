from __future__ import annotations

import socket


def lan_ip() -> str:
    """Best-effort primary LAN IPv4. Opens a UDP socket to a public IP
    (no packets sent) so the OS picks the outbound interface address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def client_urls(ip: str, dav_port: int, ui_port: int) -> dict[str, str]:
    return {
        "webdav": f"http://{ip}:{dav_port}/",
        "browser": f"http://{ip}:{ui_port}/",
    }
