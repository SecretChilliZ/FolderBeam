import base64
from io import BytesIO
from pathlib import Path
import pytest
from folderbeam.config import Config
from folderbeam.server.webdav_server import build_dav_app


@pytest.fixture
def dav(tmp_path):
    root = tmp_path / "share"
    root.mkdir()
    (root / "hello.txt").write_text("hi", encoding="utf-8")
    cfg = Config(root_dir=str(root), username="alice", password="secret")
    return build_dav_app(cfg), root


def _start_response_collector():
    captured = {}

    def start_response(status, headers, exc_info=None):
        captured["status"] = status
        captured["headers"] = headers
    return start_response, captured


def _env(method, path, auth=None):
    env = {
        "REQUEST_METHOD": method,
        "SCRIPT_NAME": "",
        "PATH_INFO": path,
        "QUERY_STRING": "",
        "SERVER_NAME": "test",
        "SERVER_PORT": "80",
        "wsgi.input": BytesIO(b""),
        "wsgi.errors": BytesIO(),
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "http",
        "wsgi.multithread": True,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
        "CONTENT_LENGTH": "0",
        "HTTP_DEPTH": "0",
    }
    if auth:
        token = base64.b64encode(auth.encode()).decode()
        env["HTTP_AUTHORIZATION"] = f"Basic {token}"
    return env


def test_app_builds(dav):
    app, _ = dav
    assert callable(app)


def test_propfind_requires_auth(dav):
    app, _ = dav
    sr, captured = _start_response_collector()
    list(app(_env("PROPFIND", "/"), sr))
    assert captured["status"].startswith("401")


def test_propfind_with_auth_ok(dav):
    app, _ = dav
    sr, captured = _start_response_collector()
    list(app(_env("PROPFIND", "/", auth="alice:secret"), sr))
    assert captured["status"].split()[0] in ("207", "200")
