import time
import urllib.request
import base64
from pathlib import Path
import pytest
from folderbeam.config import Config
from folderbeam.server.manager import ServerManager


def _free_ports():
    import socket
    ports = []
    socks = []
    for _ in range(2):
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        ports.append(s.getsockname()[1])
        socks.append(s)
    for s in socks:
        s.close()
    return ports


def test_start_status_stop(tmp_path):
    root = tmp_path / "share"
    root.mkdir()
    (root / "hello.txt").write_text("hi", encoding="utf-8")
    dav_port, ui_port = _free_ports()
    cfg = Config(root_dir=str(root), dav_port=dav_port, ui_port=ui_port,
                 username="alice", password="secret")
    mgr = ServerManager(cfg)
    assert mgr.is_running() is False

    mgr.start()
    try:
        time.sleep(1.0)  # let both threads bind
        assert mgr.is_running() is True

        token = base64.b64encode(b"alice:secret").decode()
        req = urllib.request.Request(
            f"http://127.0.0.1:{ui_port}/",
            headers={"Authorization": f"Basic {token}"},
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            body = r.read()
        assert b"hello.txt" in body
    finally:
        mgr.stop()
        time.sleep(0.5)

    assert mgr.is_running() is False
