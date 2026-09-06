"""Finding the log file, finding its checklist, and appending one item to it.

This module is the whole behaviour of the package; ``server`` and ``cli`` are
thin shells over it. Nothing here knows about MCP, and nothing here ever puts a
filesystem path into a result: callers get the file's *name* and the line that
was written, never the directory they live in.
"""

from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

CHECKLIST_ITEM = re.compile(r"^(\s*)([-*+]) \[[ xX]\]\s*")
LIST_ITEM = re.compile(r"^(\s*)(?:[-*+]|\d+[.)])\s")
FENCE = re.compile(r"^\s*(```|~~~)")
LEADING_MARKER = re.compile(r"^(?:[-*+]\s+)?(?:\[[ xX]\]\s*)?")

AppendStatus = Literal["written", "created", "duplicate", "dry_run", "empty", "no_dir", "no_file"]
"""Outcome of an append: what happened, or why nothing happened."""

CheckStatus = Literal["ok", "no_dir", "no_file", "no_checklist"]
"""Outcome of a check: the setup works, or the first thing that is missing."""

MissingStatus = Literal["no_dir", "no_file"]
"""The two ways reaching the log file can come up empty."""

NO_DIR_MESSAGE = "the worklog directory is not configured or does not exist"

NEW_MARKER = "-"
"""Bullet used when a checklist has to be started; an existing one is copied instead."""


class WorklogError(RuntimeError):
    """The log file was found but could not be read or written.

    Raised for a file that is not valid UTF-8 and for a failed write. Every
    other outcome is a status on the result model, not an exception.
    """


class AppendResult(BaseModel):
    """What ``Worklog.append`` did."""

    status: AppendStatus = Field(
        description=(
            "What happened. 'written': the item was appended to an existing checklist. 'created': the "
            "file had no checklist, so one was started at its end with this item. 'duplicate': the "
            "checklist already had it, nothing was written. 'dry_run': nothing was written because "
            "dry_run was set. 'empty': the description was blank. 'no_dir', 'no_file': the directory "
            "or the log file is missing — report it and stop, never create either."
        ),
    )
    file: str | None = Field(
        default=None,
        description="Name of the log file, without its directory. Null when no file was reached.",
    )
    line: str | None = Field(
        default=None,
        description="The exact line written, or that would have been written. Null when nothing was written.",
    )
    message: str = Field(description="One sentence describing the outcome, safe to repeat to the user.")


class CheckResult(BaseModel):
    """What ``Worklog.check`` found."""

    status: CheckStatus = Field(
        description=(
            "'ok': a log file with a checklist was found. 'no_checklist': the file is there but has no "
            "checklist yet, which the next append would start. 'no_dir', 'no_file': the directory or "
            "the log file itself is missing."
        ),
    )
    file: str | None = Field(
        default=None,
        description="Name of the log file, without its directory. Null when no file was reached.",
    )
    items: int | None = Field(
        default=None,
        description="How many items the checklist already holds. Null unless the status is 'ok'.",
    )
    message: str = Field(description="One sentence describing the outcome, safe to repeat to the user.")


@dataclass(frozen=True)
class _Checklist:
    """Boundaries and shape of the checklist an item will be appended to."""

    start: int
    end: int
    indent: str
    marker: str


@dataclass(frozen=True)
class _Document:
    """A log file split into lines, remembering how to put it back together."""

    path: Path
    lines: list[str]
    newline: str
    trailing: str


@dataclass(frozen=True)
class _Missing:
    """Why the log file could not be reached, in a form both results accept."""

    status: MissingStatus
    message: str


@dataclass(frozen=True)
class Worklog:
    """A directory of log files, plus an optional filter on their names.

    Attributes:
        directory: Where the log files live; ``None`` when it was never
            configured, which every operation reports as ``no_dir``.
        pattern: Applied to a candidate's file name with ``search``; when it is
            ``None`` every non-hidden file in the directory is a candidate.
    """

    directory: Path | None
    pattern: re.Pattern[str] | None = None

    def append(self, description: str, *, dry_run: bool = False) -> AppendResult:
        """Append one done item to the checklist of the newest log file.

        The item is written as ``[x]``, reusing the indent and the bullet
        marker of the checklist's first item. An item whose text is already in
        the checklist is not written again, so retrying a workflow never
        doubles a line.

        A log file with no checklist at all gets one started at its end — the
        file itself is never created, but an empty day is not a reason to
        refuse the entry.

        Args:
            description: What was done, as one sentence. Leading list and
                checkbox markers are stripped, and whitespace is collapsed.
            dry_run: Report the line that would be written without touching
                the file.

        Returns:
            AppendResult: The outcome, the file's name and the line involved.

        Raises:
            WorklogError: The file is not valid UTF-8, or the write failed.
        """
        text = _normalize(description)
        if not text:
            return AppendResult(status="empty", message="the description is empty, so there is nothing to write")

        located = self._locate()
        if isinstance(located, _Missing):
            return AppendResult(status=located.status, message=located.message)
        document, checklist = located

        name = document.path.name
        if checklist is None:
            return self._start(document, text, dry_run=dry_run)

        line = f"{checklist.indent}{checklist.marker} [x] {text}"
        block = document.lines[checklist.start : checklist.end + 1]
        if any(CHECKLIST_ITEM.match(item) and _item_text(item) == text for item in block):
            return AppendResult(
                status="duplicate",
                file=name,
                line=line,
                message=f'"{name}" already has this item, so nothing was written',
            )

        if dry_run:
            return AppendResult(
                status="dry_run",
                file=name,
                line=line,
                message=f'one item would be appended to the checklist in "{name}"',
            )

        document.lines.insert(checklist.end + 1, line)
        _write_atomic(document)
        return AppendResult(
            status="written",
            file=name,
            line=line,
            message=f'one item was appended to the checklist in "{name}"',
        )

    @staticmethod
    def _start(document: _Document, text: str, *, dry_run: bool) -> AppendResult:
        """Start a checklist at the end of a log file that has none.

        Returns:
            AppendResult: ``created``, or ``dry_run`` when nothing was written.
        """
        name = document.path.name
        line = f"{NEW_MARKER} [x] {text}"
        if dry_run:
            return AppendResult(
                status="dry_run",
                file=name,
                line=line,
                message=f'"{name}" has no checklist; one would be started with this item',
            )

        # A list glued to the paragraph above it is not a list, so the blank
        # line is part of writing a checklist, not cosmetics.
        if document.lines and document.lines[-1].strip():
            document.lines.append("")
        document.lines.append(line)
        _write_atomic(document)
        return AppendResult(
            status="created",
            file=name,
            line=line,
            message=f'"{name}" had no checklist, so one was started with this item',
        )

    def check(self) -> CheckResult:
        """Report whether a log file with a checklist can be found right now.

        Reads nothing back to the caller beyond the file's name and how many
        items its checklist already holds — it is a setup probe, not a way to
        look at the file.

        Returns:
            CheckResult: ``ok`` plus the file name and item count, or the first
                thing that is missing. Unlike :meth:`append`, this never starts
                a checklist — it reports ``no_checklist`` and leaves the file
                alone.

        Raises:
            WorklogError: The file is not valid UTF-8.
        """
        located = self._locate()
        if isinstance(located, _Missing):
            return CheckResult(status=located.status, message=located.message)
        document, checklist = located

        name = document.path.name
        if checklist is None:
            return CheckResult(
                status="no_checklist",
                file=name,
                message=f'"{name}" has no checklist yet; the next append will start one',
            )

        block = document.lines[checklist.start : checklist.end + 1]
        items = sum(1 for line in block if CHECKLIST_ITEM.match(line))
        return CheckResult(status="ok", file=name, items=items, message=f'"{name}" has a checklist with {items} items')

    def _locate(self) -> tuple[_Document, _Checklist | None] | _Missing:
        """Find the newest log file, and the first checklist in it if it has one.

        Returns:
            tuple[_Document, _Checklist | None] | _Missing: The file and its
                checklist — ``None`` when the file has none — or which
                prerequisite is absent.
        """
        if self.directory is None or not self.directory.is_dir():
            return _Missing(status="no_dir", message=NO_DIR_MESSAGE)

        path = _latest_file(self.directory, self.pattern)
        if path is None:
            missing = (
                "no file in the worklog directory matches the configured pattern"
                if self.pattern is not None
                else "the worklog directory holds no files"
            )
            return _Missing(status="no_file", message=missing)

        document = _read(path)
        return document, _find_checklist(document.lines)


def _created_at(path: Path) -> float:
    """Creation time where the platform records one, last modification otherwise.

    Returns:
        float: Seconds since the epoch, for ordering candidates only.
    """
    stat = path.stat()
    # float() because st_birthtime is untyped: the platform may not have it.
    return float(getattr(stat, "st_birthtime", stat.st_mtime))


def _latest_file(directory: Path, pattern: re.Pattern[str] | None) -> Path | None:
    """Newest matching file in the directory itself, ignoring subdirectories.

    Today's date is never computed: the file for today is the one created last,
    so the newest file is the right one — and work finished after midnight
    lands where its author expects to find it.

    Args:
        directory: Searched without recursion; hidden files are skipped.
        pattern: Matched against the file name with ``search``, or ``None`` to
            accept every candidate.

    Returns:
        Path | None: The newest candidate, or ``None`` when there is none.
    """
    candidates = [item for item in directory.iterdir() if item.is_file() and not item.name.startswith(".")]
    if pattern is not None:
        candidates = [item for item in candidates if pattern.search(item.name)]
    if not candidates:
        return None
    return max(candidates, key=_created_at)


def _read(path: Path) -> _Document:
    """Read a log file, remembering its line ending and whether it ends in one.

    Returns:
        _Document: The file's lines and how to write them back.

    Raises:
        WorklogError: The file is not valid UTF-8.
    """
    try:
        # newline="" keeps CRLF intact; the default would translate it away and
        # the file would silently come back with its line endings rewritten.
        text = path.read_text(encoding="utf-8", newline="")
    except UnicodeDecodeError as error:
        message = f'"{path.name}" is not valid UTF-8'
        raise WorklogError(message) from error
    newline = "\r\n" if "\r\n" in text else "\n"
    trailing = newline if text.endswith("\n") else ""
    return _Document(path=path, lines=text.splitlines(), newline=newline, trailing=trailing)


def _write_atomic(document: _Document) -> None:
    """Replace the file in one step, through a temporary file beside it.

    Editors watch these files, so none of them may ever observe a truncated
    one. A failure at any point leaves the original untouched and removes the
    temporary file.

    Raises:
        WorklogError: The temporary file could not be created, written or
            moved into place.
    """
    text = document.newline.join(document.lines) + document.trailing
    try:
        handle = tempfile.NamedTemporaryFile(  # ruff: ignore[open-file-with-context-handler]  # closed below, then renamed over the original
            "w",
            encoding="utf-8",
            dir=document.path.parent,
            prefix=".worklog-",
            suffix=".tmp",
            delete=False,
            newline="",
        )
    except OSError as error:
        raise WorklogError(_write_failed(document.path, error)) from error

    temporary = Path(handle.name)
    try:
        with handle:
            handle.write(text)
        temporary.replace(document.path)
    except OSError as error:
        temporary.unlink(missing_ok=True)
        raise WorklogError(_write_failed(document.path, error)) from error


def _write_failed(path: Path, error: OSError) -> str:
    """Phrase a write failure without naming the directory.

    Returns:
        str: The message carried by the raised :class:`WorklogError`.
    """
    return f'cannot write "{path.name}": {error.strerror}'


def _skip_frontmatter(lines: list[str]) -> int:
    """Index of the first line after a YAML frontmatter block.

    Returns:
        int: Where the document's body starts; ``0`` when there is no
            frontmatter.
    """
    if not lines or lines[0].rstrip() != "---":
        return 0
    for index in range(1, len(lines)):
        if lines[index].rstrip() in {"---", "..."}:
            return index + 1
    return 0


def _toggle_fence(fence: str | None, token: str, line: str) -> str | None:
    """Track whether the document is currently inside a fenced code block.

    A fence is closed only by its own token, so backticks inside a tilde block
    leave it open.

    Returns:
        str | None: The token holding the block open, or ``None`` outside one.
    """
    if fence is None:
        return token
    if line.strip().startswith(fence):
        return None
    return fence


def _find_checklist(lines: list[str]) -> _Checklist | None:
    """Locate the FIRST checklist in the document.

    A file may hold several checklists; the first one from the top wins and the
    rest are left alone. Fenced code blocks are skipped, so a markdown example
    inside triple backticks is not mistaken for a checklist.

    Returns:
        _Checklist | None: Boundaries and shape of the block, or ``None`` when
            the document has no checklist.
    """
    index = _skip_frontmatter(lines)
    fence: str | None = None

    while index < len(lines):
        line = lines[index]
        opening = FENCE.match(line)
        if opening:
            fence = _toggle_fence(fence, opening.group(1), line)
        elif fence is None:
            item = CHECKLIST_ITEM.match(line)
            if item:
                indent, marker = item.group(1), item.group(2)
                end = _block_end(lines, index, indent)
                return _Checklist(start=index, end=end, indent=indent, marker=marker)
        index += 1

    return None


def _block_end(lines: list[str], start: int, indent: str) -> int:
    """Index of the last line belonging to the checklist that starts at ``start``.

    The block runs to the last sibling or nested item, keeping the blank lines
    and continuation lines inside it, and stops at the first line that returns
    to a shallower level or opens a code fence.

    Returns:
        int: Index of that last line; the new item goes right after it.
    """
    end = start
    index = start + 1
    base = len(indent)
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if FENCE.match(line):
            break
        current = len(line) - len(line.lstrip())
        if LIST_ITEM.match(line) and current >= base:
            end = index
        elif current > base:
            end = index  # a continuation line of the item above
        else:
            break
        index += 1
    return end


def _item_text(line: str) -> str:
    """Text of a checklist item, without its marker and with collapsed spaces.

    Returns:
        str: The comparable form used to recognise a duplicate.
    """
    return " ".join(CHECKLIST_ITEM.sub("", line, count=1).split())


def _normalize(raw: str) -> str:
    """Reduce a description to the single line that will be written.

    Returns:
        str: One line without a leading list or checkbox marker; empty when
            nothing is left to write.
    """
    description = " ".join(raw.split())
    return LEADING_MARKER.sub("", description, count=1).strip()
