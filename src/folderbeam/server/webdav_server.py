from __future__ import annotations

from pathlib import Path

from wsgidav.wsgidav_app import WsgiDAVApp

from ..config import Config


def build_dav_app(cfg: Config) -> WsgiDAVApp:
    """WebDAV app rooted (jailed) at cfg.root_dir, single user, full access."""
    root = Path(cfg.root_dir)
    root.mkdir(parents=True, exist_ok=True)

    dav_config = {
        "host": "0.0.0.0",
        "port": cfg.dav_port,
        "provider_mapping": {
            "/": str(root),  # jail: WebDAV namespace IS this folder
        },
        "simple_dc": {
            "user_mapping": {
                "*": {
                    cfg.username: {
                        "password": cfg.password,
                        "roles": [],
                    },
                },
            },
        },
        "http_authenticator": {
            "accept_basic": True,
            "accept_digest": False,
            "default_to_digest": False,
        },
        "verbose": 1,
        "logging": {"enable": False},
        "property_manager": True,
        "lock_storage": True,
        "dir_browser": {"enable": True},
    }
    return WsgiDAVApp(dav_config)


def make_server(cfg: Config):
    """Wrap the WSGI app in a stoppable cheroot server bound to all interfaces."""
    from cheroot import wsgi

    app = build_dav_app(cfg)
    server = wsgi.Server(("0.0.0.0", cfg.dav_port), app)
    return server
