"""Packaging smoke test — run against the built wheel/sdist before publishing.

Exercises the public API end to end from an installed distribution, so a broken
build, a missing module or a dropped ``py.typed`` is caught before it reaches
PyPI. Run as ``uv run --isolated --no-project --with dist/*.whl scripts/smoke_test.py``.
"""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from mcp.client import Client

import worklog_mcp
from worklog_mcp import Worklog, build_server


async def tool_names(directory: Path) -> set[str]:
    """Connect to the server in memory and list what it offers.

    Returns:
        set[str]: Names of the registered tools.
    """
    async with Client(build_server(directory)) as client:
        return {tool.name for tool in (await client.list_tools()).tools}


def main() -> None:
    """Write one item into a throwaway log file and check the MCP surface."""
    assert (Path(worklog_mcp.__file__).parent / "py.typed").is_file(), "py.typed is missing from the distribution"

    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        note = directory / "2026-09-06.md"
        note.write_text("# Day\n\n- [ ] planned\n", encoding="utf-8")

        worklog = Worklog(directory=directory)
        assert worklog.check().items == 1

        result = worklog.append("shipped the release")
        assert result.status == "written"
        assert result.file == note.name
        assert result.line == "- [x] shipped the release"
        assert note.read_text(encoding="utf-8").endswith("- [x] shipped the release\n")

        assert worklog.append("shipped the release").status == "duplicate"

        bare = directory / "2026-09-07.md"
        bare.write_text("# Day\n", encoding="utf-8")
        assert worklog.append("started a fresh list").status == "created"
        assert bare.read_text(encoding="utf-8") == "# Day\n\n- [x] started a fresh list\n"

        assert asyncio.run(tool_names(directory)) == {"append", "check"}

    print("smoke test: ok")  # ruff: ignore[print]


if __name__ == "__main__":
    main()
