"""The command line: option and environment wiring, and the exit codes."""

from __future__ import annotations

import pytest
from conftest import Sandbox
from typer.testing import CliRunner

from worklog_mcp.cli import app

PATTERN = r"^\d{4}-\d{2}-\d{2}\.md$"

runner = CliRunner()


def test_check_reports_the_file_and_the_count(sandbox: Sandbox) -> None:
    note = sandbox.file("- [x] one\n- [ ] two\n")

    result = runner.invoke(app, ["check", "--dir", str(sandbox.path), "--pattern", PATTERN])

    assert result.exit_code == 0
    assert result.stdout.strip() == f'ok: file="{note.name}" items=2'


def test_the_directory_can_come_from_the_environment(sandbox: Sandbox, monkeypatch: pytest.MonkeyPatch) -> None:
    sandbox.file("- [ ] one\n")
    monkeypatch.setenv("WORKLOG_DIR", str(sandbox.path))
    monkeypatch.setenv("WORKLOG_FILE_PATTERN", PATTERN)

    result = runner.invoke(app, ["check"])

    assert result.exit_code == 0
    assert "items=1" in result.stdout


def test_a_blank_directory_is_treated_as_unset(sandbox: Sandbox) -> None:
    sandbox.file("- [ ] one\n")

    result = runner.invoke(app, ["check", "--dir", ""])

    assert result.exit_code == 2
    assert "not configured" in result.stderr


def test_a_missing_log_file_exits_three(sandbox: Sandbox) -> None:
    result = runner.invoke(app, ["check", "--dir", str(sandbox.path), "--pattern", PATTERN])

    assert result.exit_code == 3


def test_a_missing_checklist_exits_four(sandbox: Sandbox) -> None:
    sandbox.file("just prose\n")

    result = runner.invoke(app, ["check", "--dir", str(sandbox.path), "--pattern", PATTERN])

    assert result.exit_code == 4


def test_an_unreadable_file_exits_one(sandbox: Sandbox) -> None:
    (sandbox.path / "2026-09-06.md").write_bytes(b"- [ ] \xff\xfe\n")

    result = runner.invoke(app, ["check", "--dir", str(sandbox.path), "--pattern", PATTERN])

    assert result.exit_code == 1
    assert "UTF-8" in result.stderr


def test_a_broken_pattern_is_refused(sandbox: Sandbox) -> None:
    result = runner.invoke(app, ["check", "--dir", str(sandbox.path), "--pattern", "["])

    assert result.exit_code == 2
    assert "regular expression" in result.stderr


def test_serve_starts_the_server(sandbox: Sandbox, monkeypatch: pytest.MonkeyPatch) -> None:
    started: dict[str, object] = {}

    def capture(self: object, transport: str = "stdio", **kwargs: object) -> None:
        del kwargs
        started["transport"] = transport
        started["server"] = self

    monkeypatch.setattr("mcp.server.MCPServer.run", capture)

    result = runner.invoke(app, ["serve", "--dir", str(sandbox.path)])

    assert result.exit_code == 0
    assert started["transport"] == "stdio"


def test_bare_invocation_shows_help() -> None:
    result = runner.invoke(app, [])

    assert result.exit_code != 0
    assert "serve" in result.stdout
