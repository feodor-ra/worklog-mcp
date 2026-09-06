"""Command line: serve the MCP server, or check the setup from a terminal.

Both commands take the same two options, and each option can also be given as
an environment variable — which is what makes the directory configurable
without ever writing it into a client's config file.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated

import typer

from worklog_mcp.logfile import Worklog, WorklogError
from worklog_mcp.server import build_server

EXIT_ERROR = 1
EXIT_NO_DIR = 2
EXIT_NO_FILE = 3
EXIT_NO_CHECKLIST = 4

EXIT_CODES = {"no_dir": EXIT_NO_DIR, "no_file": EXIT_NO_FILE, "no_checklist": EXIT_NO_CHECKLIST}

DirectoryOption = Annotated[
    str | None,
    typer.Option(
        "--dir",
        envvar="WORKLOG_DIR",
        help="Directory holding the log files. Required, as an option or as the variable.",
    ),
]
PatternOption = Annotated[
    str | None,
    typer.Option(
        "--pattern",
        envvar="WORKLOG_FILE_PATTERN",
        help="Regular expression a file name must match. Omit to accept every file.",
    ),
]

app = typer.Typer(
    name="worklog-mcp",
    help="Append what you did to the checklist of the newest file in a directory.",
    no_args_is_help=True,
    add_completion=False,
)


def _directory(raw: str | None) -> Path | None:
    """Turn the option's raw value into a directory, treating blank as unset.

    An empty string is what a client's config produces when a variable it
    interpolates is not set. It must not become ``Path(".")``, which is a real
    directory and would put the log file somewhere surprising.

    Returns:
        Path | None: The directory, or ``None`` when nothing was configured.
    """
    if raw is None or not raw.strip():
        return None
    return Path(raw).expanduser()


def _pattern(raw: str | None) -> re.Pattern[str] | None:
    """Compile the file-name pattern.

    Returns:
        re.Pattern[str] | None: The compiled pattern, or ``None`` when the
            option was omitted.

    Raises:
        BadParameter: The expression does not compile.
    """
    if raw is None:
        return None
    try:
        return re.compile(raw)
    except re.error as error:
        message = f"not a valid regular expression: {error}"
        raise typer.BadParameter(message) from error


@app.command()
def serve(directory: DirectoryOption = None, pattern: PatternOption = None) -> None:
    """Run the MCP server on stdio. This is the command an MCP client starts."""
    build_server(_directory(directory), _pattern(pattern)).run(transport="stdio")


@app.command()
def check(directory: DirectoryOption = None, pattern: PatternOption = None) -> None:
    """Report which log file would be written to, and how many items it holds.

    Raises:
        Exit: With `1` when the file cannot be read, `2` when no directory is
            configured, `3` when it holds no log file and `4` when that file
            has no checklist.
    """
    worklog = Worklog(directory=_directory(directory), pattern=_pattern(pattern))
    try:
        result = worklog.check()
    except WorklogError as error:
        typer.echo(f"worklog-mcp: {error}", err=True)
        raise typer.Exit(EXIT_ERROR) from error

    if result.status != "ok":
        typer.echo(f"worklog-mcp: {result.message}", err=True)
        raise typer.Exit(EXIT_CODES[result.status])

    typer.echo(f'ok: file="{result.file}" items={result.items}')
