"""Shared fixtures: a temporary worklog directory and the anyio backend."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import pytest

DAILY = "2026-09-06.md"
"""Name used whenever a test does not care about the file name."""


@dataclass(frozen=True)
class Sandbox:
    """A temporary directory that tests fill with log files."""

    path: Path

    def file(self, body: str, name: str = DAILY, *, pause: bool = False) -> Path:
        """Create a log file in the sandbox.

        Args:
            body: Full contents of the file.
            name: File name; defaults to a plain dated note.
            pause: Sleep first, so this file is unambiguously newer than the
                previous one on filesystems with coarse timestamps.

        Returns:
            Path: The file that was written.
        """
        if pause:
            time.sleep(0.05)
        target = self.path / name
        target.write_text(body, encoding="utf-8")
        return target


@pytest.fixture
def sandbox(tmp_path: Path) -> Sandbox:
    """An empty worklog directory.

    Returns:
        Sandbox: Helper for creating log files inside it.
    """
    return Sandbox(path=tmp_path)


@pytest.fixture
def anyio_backend() -> str:
    """Run async tests on asyncio only.

    Returns:
        str: The backend name anyio's pytest plugin expects.
    """
    return "asyncio"
