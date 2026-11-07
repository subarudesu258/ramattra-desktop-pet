"""Loading baked sprite frames into Tk images.

The PNGs are produced by ``tools/gen_sprites.py`` and committed, so this module
only needs tkinter.  Frames live on a solid colour-key background (magenta),
which is what lets the window be genuinely transparent on Windows.
"""

from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path

COLOUR_KEY = "#ff00fe"
ASSET_DIR = Path(__file__).resolve().parent.parent / "assets"


class SpriteLibrary:
    """Lazily loads and caches the frames of every animation clip."""

    def __init__(self, base: Path | None = None, master: tk.Misc | None = None) -> None:
        self.base = Path(base) if base else ASSET_DIR
        self.master = master
        manifest = json.loads((self.base / "manifest.json").read_text(encoding="utf-8"))
        self.manifest: dict[str, dict] = manifest
        self._cache: dict[str, list[tk.PhotoImage]] = {}

    # -- queries -----------------------------------------------------------
    def clip_names(self) -> list[str]:
        return sorted(self.manifest)

    def size(self, clip: str) -> tuple[int, int]:
        w, h = self.manifest[clip]["size"]
        return int(w), int(h)

    def scale(self, clip: str) -> int:
        """How much the 1:1 artwork was upscaled when it was baked."""
        return int(self.manifest[clip].get("scale", 1))

    # -- loading -----------------------------------------------------------
    def frames(self, clip: str) -> list[tk.PhotoImage]:
        if clip not in self.manifest:
            raise KeyError(f"unknown clip {clip!r}; known: {', '.join(self.clip_names())}")
        if clip not in self._cache:
            entry = self.manifest[clip]
            folder = self.base / entry["dir"]
            self._cache[clip] = [
                tk.PhotoImage(master=self.master, file=str(folder / name)) for name in entry["frames"]
            ]
        return self._cache[clip]

    def first(self, clip: str) -> tk.PhotoImage:
        return self.frames(clip)[0]
