from __future__ import annotations

from functools import wraps
from pathlib import Path

from flask import (
    Flask, request, Response, render_template_string,
    send_file, redirect, url_for, abort,
)
from werkzeug.utils import secure_filename

from ..config import Config
from .auth import check_credentials
from .jail import safe_resolve

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FolderBeam</title>
<link rel="icon" href="/favicon.ico">
<style>
 :root { color-scheme: dark; }
 body { background:#202020; color:#e0e0e0; font-family:'Segoe UI',sans-serif; margin:0; padding:1rem; }
 h1 { font-size:1.1rem; font-weight:600; }
 a { color:#4cc2ff; text-decoration:none; }
 table { width:100%; border-collapse:collapse; margin-top:.5rem; }
 td,th { padding:.4rem .6rem; border-bottom:1px solid #333; text-align:left; }
 form.inline { display:inline; }
 button, input[type=submit] { background:#0067c0; color:#fff; border:0; border-radius:4px;
   padding:.35rem .7rem; cursor:pointer; }
 button.danger { background:#a52a2a; }
 .bar { margin:.6rem 0; display:flex; gap:.5rem; flex-wrap:wrap; align-items:center; }
 input[type=text], input[type=file] { background:#2b2b2b; color:#e0e0e0;
   border:1px solid #444; border-radius:4px; padding:.3rem; }
</style></head><body>
<h1>FolderBeam &mdash; /{{ rel }}</h1>
<div class="bar">
 {% if rel %}<a href="{{ url_for('browse', subpath=parent) }}">.. up</a>{% endif %}
 <form class="inline" method="post" action="{{ url_for('upload') }}" enctype="multipart/form-data">
  <input type="hidden" name="path" value="{{ rel }}">
  <input type="file" name="file" required>
  <input type="submit" value="Upload">
 </form>
 <form class="inline" method="post" action="{{ url_for('mkdir') }}">
  <input type="hidden" name="path" value="{{ rel }}">
  <input type="text" name="name" placeholder="new folder" required>
  <button>Mkdir</button>
 </form>
</div>
<table>
 <tr><th>Name</th><th>Size</th><th>Actions</th></tr>
 {% for e in entries %}
 <tr>
  <td>{% if e.is_dir %}&#128193; <a href="{{ url_for('browse', subpath=e.rel) }}">{{ e.name }}/</a>
      {% else %}&#128196; <a href="{{ url_for('download', subpath=e.rel) }}">{{ e.name }}</a>{% endif %}</td>
  <td>{{ e.size }}</td>
  <td>
   <form class="inline" method="post" action="{{ url_for('rename') }}">
    <input type="hidden" name="path" value="{{ e.rel }}">
    <input type="text" name="name" placeholder="rename to" required>
    <button>Rename</button>
   </form>
   <form class="inline" method="post" action="{{ url_for('delete') }}"
         onsubmit="return confirm('Delete {{ e.name }}?')">
    <input type="hidden" name="path" value="{{ e.rel }}">
    <button class="danger">Delete</button>
   </form>
  </td>
 </tr>
 {% endfor %}
</table>
</body></html>"""


def _join_rel(base: str, name: str) -> str:
    base = base.strip("/")
    return f"{base}/{name}".strip("/")


def create_app(cfg: Config) -> Flask:
    app = Flask(__name__)
    root = Path(cfg.root_dir)
    root.mkdir(parents=True, exist_ok=True)

    def require_auth(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            auth = request.authorization
            if not auth or not check_credentials(
                auth.username or "", auth.password or "", cfg.username, cfg.password
            ):
                return Response(
                    "Auth required", 401,
                    {"WWW-Authenticate": 'Basic realm="FolderBeam"'},
                )
            return fn(*a, **kw)
        return wrapper

    def resolve(rel: str) -> Path:
        try:
            return safe_resolve(root, rel)
        except PermissionError:
            abort(403)

    @app.get("/")
    @app.get("/browse/<path:subpath>")
    @require_auth
    def browse(subpath: str = ""):
        target = resolve(subpath)
        if not target.is_dir():
            abort(404)
        entries = []
        for child in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
            entries.append({
                "name": child.name,
                "rel": _join_rel(subpath, child.name),
                "is_dir": child.is_dir(),
                "size": "" if child.is_dir() else child.stat().st_size,
            })
        parent = subpath.rsplit("/", 1)[0] if "/" in subpath else ""
        return render_template_string(PAGE, rel=subpath, parent=parent, entries=entries)

    @app.get("/download/<path:subpath>")
    @require_auth
    def download(subpath: str):
        target = resolve(subpath)
        if not target.is_file():
            abort(404)
        return send_file(target, as_attachment=True, download_name=target.name)

    @app.post("/upload")
    @require_auth
    def upload():
        base = request.form.get("path", "")
        f = request.files.get("file")
        if not f or not f.filename:
            abort(400)
        name = secure_filename(f.filename)
        dest = resolve(_join_rel(base, name))
        f.save(dest)
        return redirect(url_for("browse", subpath=base))

    @app.post("/mkdir")
    @require_auth
    def mkdir():
        base = request.form.get("path", "")
        name = secure_filename(request.form.get("name", ""))
        if not name:
            abort(400)
        resolve(_join_rel(base, name)).mkdir(parents=True, exist_ok=True)
        return redirect(url_for("browse", subpath=base))

    @app.post("/rename")
    @require_auth
    def rename():
        rel = request.form.get("path", "")
        new_name = secure_filename(request.form.get("name", ""))
        if not new_name:
            abort(400)
        src = resolve(rel)
        parent_rel = rel.rsplit("/", 1)[0] if "/" in rel else ""
        dst = resolve(_join_rel(parent_rel, new_name))
        src.rename(dst)
        return redirect(url_for("browse", subpath=parent_rel))

    @app.post("/delete")
    @require_auth
    def delete():
        rel = request.form.get("path", "")
        target = resolve(rel)
        parent_rel = rel.rsplit("/", 1)[0] if "/" in rel else ""
        if target.is_dir():
            import shutil
            shutil.rmtree(target)
        else:
            target.unlink()
        return redirect(url_for("browse", subpath=parent_rel))

    @app.get("/favicon.ico")
    def favicon():
        # Unauthenticated on purpose: the browser tab icon should load at the
        # login prompt, before credentials are entered.
        from ..resources import icon_path
        p = icon_path()
        if not p.exists():
            abort(404)
        return send_file(p)

    return app
