"""The two tools, exercised over an in-memory MCP connection.

These go through the real protocol — the client talks to the server object with
no subprocess — so they cover the tool schemas and the structured results a
client actually receives, not just the Python functions underneath.
"""

from __future__ import annotations

import re

import pytest
from conftest import Sandbox
from mcp.client import Client
from mcp.server import MCPServer

from worklog_mcp.server import build_server

pytestmark = pytest.mark.anyio

DAILY_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")


def server(sandbox: Sandbox | None = None) -> MCPServer:
    """Build a server over the sandbox, or over no directory at all.

    Returns:
        MCPServer: Ready for an in-memory client.
    """
    return build_server(None if sandbox is None else sandbox.path, DAILY_PATTERN)


async def test_both_tools_are_offered(sandbox: Sandbox) -> None:
    async with Client(server(sandbox)) as client:
        tools = {tool.name for tool in (await client.list_tools()).tools}

    assert tools == {"append", "check"}


async def test_append_writes_and_reports_the_line(sandbox: Sandbox) -> None:
    note = sandbox.file("- [ ] item\n")

    async with Client(server(sandbox)) as client:
        result = await client.call_tool("append", {"description": "shipped the fix"})

    assert result.is_error is False
    assert result.structured_content == {
        "status": "written",
        "file": note.name,
        "line": "- [x] shipped the fix",
        "message": f'one item was appended to the checklist in "{note.name}"',
    }
    assert note.read_text(encoding="utf-8").endswith("- [x] shipped the fix\n")


async def test_append_can_be_a_dry_run(sandbox: Sandbox) -> None:
    note = sandbox.file("- [ ] item\n")

    async with Client(server(sandbox)) as client:
        result = await client.call_tool("append", {"description": "not yet", "dry_run": True})

    assert result.structured_content["status"] == "dry_run"
    assert note.read_text(encoding="utf-8") == "- [ ] item\n"


async def test_append_starts_a_checklist_when_the_file_has_none(sandbox: Sandbox) -> None:
    note = sandbox.file("# Day\n\njust prose\n")

    async with Client(server(sandbox)) as client:
        result = await client.call_tool("append", {"description": "started the list"})

    assert result.structured_content["status"] == "created"
    assert note.read_text(encoding="utf-8").endswith("\n\n- [x] started the list\n")


async def test_the_tools_are_described_for_a_model(sandbox: Sandbox) -> None:
    async with Client(server(sandbox)) as client:
        tools = {tool.name: tool for tool in (await client.list_tools()).tools}

    append = tools["append"]
    assert append.title == "Append to today's work log"
    assert append.annotations is not None
    assert append.annotations.read_only_hint is False
    assert append.annotations.idempotent_hint is True
    assert append.annotations.open_world_hint is False
    assert append.output_schema is not None
    assert "one sentence" in append.input_schema["properties"]["description"]["description"].lower()
    assert tools["check"].annotations is not None
    assert tools["check"].annotations.read_only_hint is True


async def test_a_repeated_append_is_reported_not_repeated(sandbox: Sandbox) -> None:
    sandbox.file("- [x] shipped the fix\n")

    async with Client(server(sandbox)) as client:
        result = await client.call_tool("append", {"description": "shipped the fix"})

    assert result.structured_content["status"] == "duplicate"


async def test_a_server_without_a_directory_still_answers(sandbox: Sandbox) -> None:
    del sandbox

    async with Client(server()) as client:
        result = await client.call_tool("check", {})

    assert result.is_error is False
    assert result.structured_content["status"] == "no_dir"


async def test_check_reports_the_item_count(sandbox: Sandbox) -> None:
    note = sandbox.file("- [x] one\n- [ ] two\n")

    async with Client(server(sandbox)) as client:
        result = await client.call_tool("check", {})

    assert result.structured_content == {
        "status": "ok",
        "file": note.name,
        "items": 2,
        "message": f'"{note.name}" has a checklist with 2 items',
    }


async def test_an_unreadable_file_comes_back_as_a_tool_error(sandbox: Sandbox) -> None:
    (sandbox.path / "2026-09-06.md").write_bytes(b"- [ ] \xff\xfe\n")

    async with Client(server(sandbox)) as client:
        result = await client.call_tool("append", {"description": "unreadable"})

    assert result.is_error is True
