"""Shared test helpers.

Temporary directories are created inside the project instead of the OS temp
folder so the suite also works under restrictive sandboxes that allow writes to
the workspace only.
"""

from __future__ import annotations

import shutil
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parent.parent
TMP_ROOT = ROOT / "_tmp_tests"


@contextmanager
def temp_dir() -> Iterator[Path]:
    """A throwaway directory inside the project.

    ``tempfile.mkdtemp`` is avoided on purpose: it applies a restrictive ACL that
    some sandboxes treat as a denial for the very process that created it.
    """
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    path = TMP_ROOT / f"tmp_{uuid.uuid4().hex[:10]}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
