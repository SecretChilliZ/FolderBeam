from __future__ import annotations

from pathlib import Path, PurePosixPath


def safe_resolve(root, rel: str) -> Path:
    """Resolve `rel` under `root`, refusing any path that escapes root.

    `rel` is treated as a relative POSIX-style path supplied by a client.
    Absolute inputs and `..` traversal are rejected, not normalised away.
    """
    root = Path(root).resolve()

    rel_path = PurePosixPath(rel.replace("\\", "/"))
    if rel_path.is_absolute() or (len(rel_path.parts) and rel_path.parts[0].endswith(":")):
        raise PermissionError(f"absolute path not allowed: {rel!r}")
    if ".." in rel_path.parts:
        raise PermissionError(f"parent traversal not allowed: {rel!r}")

    target = (root / Path(*rel_path.parts)).resolve()

    if target != root and root not in target.parents:
        raise PermissionError(f"path escapes jail: {rel!r}")
    return target
