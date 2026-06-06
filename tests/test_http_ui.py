import base64
from io import BytesIO
from pathlib import Path
import pytest
from folderbeam.config import Config
from folderbeam.server.http_ui import create_app


@pytest.fixture
def app(tmp_path):
    root = tmp_path / "share"
    root.mkdir()
    (root / "hello.txt").write_text("hi", encoding="utf-8")
    cfg = Config(root_dir=str(root), username="alice", password="secret")
    return create_app(cfg), root


def _auth(user="alice", pw="secret"):
    token = base64.b64encode(f"{user}:{pw}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def test_listing_requires_auth(app):
    flask_app, _ = app
    client = flask_app.test_client()
    r = client.get("/")
    assert r.status_code == 401


def test_listing_shows_file(app):
    flask_app, _ = app
    client = flask_app.test_client()
    r = client.get("/", headers=_auth())
    assert r.status_code == 200
    assert b"hello.txt" in r.data


def test_upload(app):
    flask_app, root = app
    client = flask_app.test_client()
    data = {"file": (BytesIO(b"new content"), "new.txt")}
    r = client.post("/upload", data=data, headers=_auth(),
                    content_type="multipart/form-data")
    assert r.status_code in (200, 302)
    assert (root / "new.txt").read_bytes() == b"new content"


def test_mkdir(app):
    flask_app, root = app
    client = flask_app.test_client()
    r = client.post("/mkdir", data={"path": "", "name": "newdir"}, headers=_auth())
    assert r.status_code in (200, 302)
    assert (root / "newdir").is_dir()


def test_delete(app):
    flask_app, root = app
    client = flask_app.test_client()
    r = client.post("/delete", data={"path": "hello.txt"}, headers=_auth())
    assert r.status_code in (200, 302)
    assert not (root / "hello.txt").exists()


def test_rename(app):
    flask_app, root = app
    client = flask_app.test_client()
    r = client.post("/rename", data={"path": "hello.txt", "name": "renamed.txt"},
                    headers=_auth())
    assert r.status_code in (200, 302)
    assert (root / "renamed.txt").exists()
    assert not (root / "hello.txt").exists()


def test_download(app):
    flask_app, _ = app
    client = flask_app.test_client()
    r = client.get("/download/hello.txt", headers=_auth())
    assert r.status_code == 200
    assert r.data == b"hi"


def test_traversal_blocked(app):
    flask_app, _ = app
    client = flask_app.test_client()
    r = client.get("/download/../../secret.txt", headers=_auth())
    assert r.status_code in (400, 403, 404)


def test_favicon_unauthenticated(app):
    flask_app, _ = app
    client = flask_app.test_client()
    r = client.get("/favicon.ico")  # no auth header on purpose
    assert r.status_code == 200
    assert r.data[:4] == b"\x00\x00\x01\x00"  # ICO magic
