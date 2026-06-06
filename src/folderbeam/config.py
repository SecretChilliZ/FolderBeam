from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

DEFAULT_ROOT = r"D:/folderbeam"


@dataclass
class Config:
    root_dir: str = DEFAULT_ROOT
    dav_port: int = 8080
    ui_port: int = 8081
    username: str = "user"
    password: str = "change-me"
    enable_wan: bool = False  # STERILISED seam, see wan_gateway.py

    def save(self, path: Path) -> None:
        path = Path(path)
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "Config":
        path = Path(path)
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        known = {f: data[f] for f in cls.__dataclass_fields__ if f in data}
        return cls(**known)
