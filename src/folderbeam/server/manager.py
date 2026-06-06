from __future__ import annotations

import threading

from werkzeug.serving import make_server

from ..config import Config
from .http_ui import create_app
from .webdav_server import build_dav_app


class _WsgiThread(threading.Thread):
    """Run any WSGI app on a werkzeug server that can be shut down cleanly."""

    def __init__(self, app, port: int):
        super().__init__(daemon=True)
        self._srv = make_server("0.0.0.0", port, app, threaded=True)

    def run(self):
        self._srv.serve_forever()

    def shutdown(self):
        self._srv.shutdown()


class ServerManager:
    """Owns both listeners (WebDAV + HTTP UI). Start and stop together."""

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._threads: list[_WsgiThread] = []

    def is_running(self) -> bool:
        return any(t.is_alive() for t in self._threads)

    def start(self) -> None:
        if self.is_running():
            return
        ui_app = create_app(self.cfg)
        dav_app = build_dav_app(self.cfg)
        self._threads = [
            _WsgiThread(dav_app, self.cfg.dav_port),
            _WsgiThread(ui_app, self.cfg.ui_port),
        ]
        for t in self._threads:
            t.start()

    def stop(self) -> None:
        for t in self._threads:
            t.shutdown()
        for t in self._threads:
            t.join(timeout=3)
        self._threads = []
