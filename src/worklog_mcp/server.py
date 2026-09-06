"""The MCP server: two tools over one :class:`~worklog_mcp.logfile.Worklog`.

The directory and the file-name pattern are fixed when the server starts, so a
client never passes them — and never sees them.

Every field of both tool descriptors is spelled out below rather than inferred,
because the descriptor is the only thing a model has to go on. The descriptions
in particular are part of the wire protocol: they are written as instructions to
a model — when to call, what comes back, what the tool will not do — not as
notes to a maintainer.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated

from mcp.server import MCPServer
from mcp.types import ToolAnnotations
from pydantic import Field

from worklog_mcp.logfile import AppendResult, CheckResult, Worklog

SERVER_NAME = "worklog"

DOCS_URL = "https://feodor-ra.github.io/worklog-mcp/"

APPEND_DESCRIPTION = """\
Record ONE finished piece of work in the user's log for today.

Call this the moment a task is actually done — a fix landed, a change was
pushed, a question was answered — and once per piece of work. Do not call it to
plan something, to take a note, or to save a partial result.

The item is appended as a completed entry to the checklist of the newest file in
the log directory. That directory is configured when the server starts: you do
not choose it, you cannot pass it, and you will not be told what it is.

Write `description` as one plain sentence in the past tense, in the language the
user writes their log in, naming what changed and — for a bug — why it happened.
Leave out issue keys, links and branch names unless the user asks for them.

The call is idempotent: repeating the same sentence returns `duplicate` and
writes nothing, so retrying after an error is safe.

If today's file has no checklist yet, one is started at the end of it and you
get `created` instead of `written` — say so when you report back, since the
file gained a list it did not have.

The log file itself is never created. If the directory or the file is missing
you get `no_dir` or `no_file`: report that to the user in one line and stop — do
not create a file, do not look for the log yourself, and do not ask the user for
the path.

Returns the status, the log file's NAME (never its path) and the exact line
written. Set `dry_run` to see that line without writing it."""

CHECK_DESCRIPTION = """\
Check that a log file with a checklist can be found right now.

Use it to diagnose an `append` that came back `no_dir` or `no_file`: it tells
you whether the server is misconfigured or the user has simply not started
today's log yet. It takes no arguments and changes nothing — a file with no
checklist is reported as `no_checklist` here, not started, which only `append`
does.

Returns the log file's NAME and how many items its checklist already holds. It
is not a way to read the log — the items themselves are never returned, and no
other tool returns them either. Do not call it before every append; the append
reports the same conditions by itself."""


def build_server(directory: Path | None, pattern: re.Pattern[str] | None = None) -> MCPServer:
    """Create the MCP server for one worklog directory.

    The directory is not validated here. A server that refused to start on a
    missing directory would show up in a client as a broken connection with no
    tools; instead every call reports ``no_dir``, which a caller can act on.

    Args:
        directory: Where the log files live, or ``None`` when it was never
            configured.
        pattern: Optional filter on candidate file names.

    Returns:
        MCPServer: A server exposing the ``append`` and ``check`` tools.
    """
    worklog = Worklog(directory=directory, pattern=pattern)
    mcp = MCPServer(SERVER_NAME)

    @mcp.tool(
        name="append",
        title="Append to today's work log",
        description=APPEND_DESCRIPTION,
        annotations=ToolAnnotations(
            title="Append to today's work log",
            read_only_hint=False,
            # It only ever adds a line; no item is edited, reordered or removed.
            destructive_hint=False,
            # The same description twice leaves one line, not two.
            idempotent_hint=True,
            # One local directory, fixed at startup — no network, no discovery.
            open_world_hint=False,
        ),
        meta={"docs": f"{DOCS_URL}reference/tools/"},
        structured_output=True,
    )
    def append(
        description: Annotated[
            str,
            Field(
                description=(
                    "What was done, as ONE sentence in the past tense, in the user's own language. "
                    "Name the change and, for a bug, its cause. No issue keys, links or branch names. "
                    "Line breaks are collapsed and a leading '- ' or '- [ ]' marker is stripped."
                ),
                min_length=1,
            ),
        ],
        *,
        dry_run: Annotated[
            bool,
            Field(
                description=(
                    "Return the line that would be written without touching the file. "
                    "Use only when the user asked to preview the entry."
                ),
            ),
        ] = False,
    ) -> AppendResult:
        """Append one done item; see :data:`APPEND_DESCRIPTION` for the model-facing text.

        Returns:
            AppendResult: The outcome, the log file's name and the line.
        """
        return worklog.append(description, dry_run=dry_run)

    @mcp.tool(
        name="check",
        title="Check the work log setup",
        description=CHECK_DESCRIPTION,
        annotations=ToolAnnotations(
            title="Check the work log setup",
            # Reads one file and returns a count; writes nothing.
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
        meta={"docs": f"{DOCS_URL}reference/tools/"},
        structured_output=True,
    )
    def check() -> CheckResult:
        """Probe the setup; see :data:`CHECK_DESCRIPTION` for the model-facing text.

        Returns:
            CheckResult: Whether the setup works, or the first thing missing.
        """
        return worklog.check()

    return mcp
