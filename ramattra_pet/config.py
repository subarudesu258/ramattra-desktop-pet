"""Persisted settings, stored per-user and resilient to read-only locations.

Preference order: ``%APPDATA%`` → ``%LOCALAPPDATA%`` → ``~/.RamattraPet``.
The first directory that accepts a write wins, so the pet still remembers where
it was even in sandboxes or locked-down profiles.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

log = logging.getLogger(__name__)

APP_NAME = "RamattraPet"
FILE_NAME = "config.json"


def candidate_dirs() -> list[Path]:
    """Places we may keep configuration, most preferred first."""
    out: list[Path] = []
    for var in ("APPDATA", "LOCALAPPDATA"):
        base = os.environ.get(var)
        if base:
            out.append(Path(base) / APP_NAME)
    out.append(Path.home() / f".{APP_NAME}")
    # last resort: portable mode next to the package (also survives locked profiles)
    out.append(Path(__file__).resolve().parent.parent)
    return out


def data_dir() -> Path:
    """The directory that is actually writable (falls back to the first candidate)."""
    for d in candidate_dirs():
        try:
            d.mkdir(parents=True, exist_ok=True)
            probe = d / ".write-test"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
            return d
        except OSError:
            continue
    return candidate_dirs()[0]


@dataclass
class Config:
    """Everything the pet remembers between runs."""

    x: int | None = None
    y: int | None = None
    form: str = "omnic"            # "omnic" | "nemesis" | "special"
    zoom: int = 1                  # 1..3, multiplies the baked 3x sprite
    topmost: bool = True
    muted: bool = False
    idle_sleep_seconds: int = 300   # nap after five quiet minutes
    idle_talk_min: int = 45         # seconds between random voice lines
    idle_talk_max: int = 130
    bubble_seconds: float = 3.2

    extra: dict = field(default_factory=dict)

    # -- validation -------------------------------------------------------
    def normalised(self) -> "Config":
        if self.form not in ("omnic", "nemesis", "special"):
            self.form = "omnic"
        self.zoom = max(1, min(3, int(self.zoom)))
        self.idle_sleep_seconds = max(30, int(self.idle_sleep_seconds))
        self.idle_talk_min = max(10, int(self.idle_talk_min))
        self.idle_talk_max = max(self.idle_talk_min + 5, int(self.idle_talk_max))
        self.bubble_seconds = min(15.0, max(1.0, float(self.bubble_seconds)))
        return self


def config_path() -> Path:
    return data_dir() / FILE_NAME


def load(path: Path | None = None) -> Config:
    candidates = [path] if path else [d / FILE_NAME for d in candidate_dirs()]
    for candidate in candidates:
        try:
            # utf-8-sig: editors such as Notepad may add a BOM, and a plain
            # utf-8 read would then fail json parsing and silently reset the pet.
            raw = json.loads(Path(candidate).read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            continue
        if not isinstance(raw, dict):
            continue
        known = set(Config.__dataclass_fields__)
        return Config(**{k: v for k, v in raw.items() if k in known}).normalised()
    return Config()


def save(cfg: Config, path: Path | None = None) -> Path:
    """Write atomically, trying every candidate directory in turn."""
    payload = json.dumps(asdict(cfg), indent=2, ensure_ascii=False)
    targets = [path] if path else [d / FILE_NAME for d in candidate_dirs()]
    last_error: OSError | None = None
    for target in targets:
        try:
            target = Path(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.with_suffix(".tmp")
            tmp.write_text(payload, encoding="utf-8")
            tmp.replace(target)
            return target
        except OSError as exc:
            last_error = exc
            continue
    raise last_error or OSError("no writable configuration directory")
