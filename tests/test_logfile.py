"""Choosing the log file, parsing its checklist, and appending one item.

This is where the subtle behaviour lives: which file wins, what counts as a
checklist, where exactly the new line goes, and what happens when the directory,
the file or the checklist is missing.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from conftest import Sandbox

from worklog_mcp.logfile import Worklog, WorklogError, _find_checklist, _skip_frontmatter

DAILY_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")


def worklog(sandbox: Sandbox, pattern: re.Pattern[str] | None = DAILY_PATTERN) -> Worklog:
    """Build a worklog over the sandbox.

    Returns:
        Worklog: Configured with the sandbox directory and the given pattern.
    """
    return Worklog(directory=sandbox.path, pattern=pattern)


def test_appends_to_the_end_of_the_checklist(sandbox: Sandbox) -> None:
    note = sandbox.file("# Day\n\n- [x] first\n- [ ] second\n")

    result = worklog(sandbox).append("fixed the CSV import in the reports service")

    assert result.status == "written"
    assert result.file == note.name
    assert result.line == "- [x] fixed the CSV import in the reports service"
    assert note.read_text(encoding="utf-8") == (
        "# Day\n\n- [x] first\n- [ ] second\n- [x] fixed the CSV import in the reports service\n"
    )


def test_a_repeated_item_is_not_written_twice(sandbox: Sandbox) -> None:
    note = sandbox.file("- [x] fixed the import\n")

    result = worklog(sandbox).append("  fixed the   import  ")

    assert result.status == "duplicate"
    assert note.read_text(encoding="utf-8").count("fixed the import") == 1


def test_the_first_checklist_wins(sandbox: Sandbox) -> None:
    note = sandbox.file("## Work\n- [x] one\n\n## Home\n- [ ] two\n- [ ] three\n")

    worklog(sandbox).append("new")

    assert note.read_text(encoding="utf-8") == "## Work\n- [x] one\n- [x] new\n\n## Home\n- [ ] two\n- [ ] three\n"


def test_frontmatter_is_not_a_checklist(sandbox: Sandbox) -> None:
    note = sandbox.file("---\ntags:\n  - [ ] not a checklist\n---\n\n- [ ] real\n")

    worklog(sandbox).append("after the frontmatter")

    assert note.read_text(encoding="utf-8").endswith("- [ ] real\n- [x] after the frontmatter\n")


def test_unterminated_frontmatter_is_ignored() -> None:
    assert _skip_frontmatter(["---", "tags:", "  - one"]) == 0


def test_a_checklist_inside_a_code_fence_is_not_a_checklist(sandbox: Sandbox) -> None:
    note = sandbox.file("```md\n- [ ] example\n```\n\n- [ ] real\n")

    worklog(sandbox).append("past the code block")

    assert note.read_text(encoding="utf-8") == "```md\n- [ ] example\n```\n\n- [ ] real\n- [x] past the code block\n"


def test_a_fence_of_another_token_does_not_close_the_block(sandbox: Sandbox) -> None:
    note = sandbox.file("~~~md\n- [ ] example\n```\n- [ ] still inside\n~~~\n\n- [ ] real\n")

    worklog(sandbox).append("outside every fence")

    assert note.read_text(encoding="utf-8").endswith("- [ ] real\n- [x] outside every fence\n")


def test_a_fence_after_the_checklist_ends_the_block(sandbox: Sandbox) -> None:
    note = sandbox.file("- [ ] item\n```md\nsample\n```\n")

    worklog(sandbox).append("before the fence")

    assert note.read_text(encoding="utf-8") == "- [ ] item\n- [x] before the fence\n```md\nsample\n```\n"


def test_the_item_goes_after_the_whole_block(sandbox: Sandbox) -> None:
    note = sandbox.file(
        "- [ ] top\n    - [ ] nested\n      continued\n\n- [ ] more\n\n## Next\ntext\n",
    )

    worklog(sandbox).append("at the end of the block")

    assert note.read_text(encoding="utf-8") == (
        "- [ ] top\n    - [ ] nested\n      continued\n\n- [ ] more\n- [x] at the end of the block\n\n## Next\ntext\n"
    )


def test_marker_and_indent_come_from_the_first_item(sandbox: Sandbox) -> None:
    note = sandbox.file("  * [ ] a starred item\n")

    result = worklog(sandbox).append("same marker")

    assert result.line == "  * [x] same marker"
    assert note.read_text(encoding="utf-8").endswith("  * [x] same marker\n")


def test_a_file_without_a_checklist_gets_one(sandbox: Sandbox) -> None:
    note = sandbox.file("# Day\n\njust prose\n")

    result = worklog(sandbox).append("started the list")

    assert result.status == "created"
    assert result.file == note.name
    assert result.line == "- [x] started the list"
    assert note.read_text(encoding="utf-8") == "# Day\n\njust prose\n\n- [x] started the list\n"


def test_a_started_checklist_is_separated_from_the_text_above(sandbox: Sandbox) -> None:
    note = sandbox.file("prose\n")

    worklog(sandbox).append("needs a blank line")

    # Glued to the paragraph, the item would not be a list at all.
    assert note.read_text(encoding="utf-8") == "prose\n\n- [x] needs a blank line\n"


def test_a_trailing_blank_line_is_not_doubled(sandbox: Sandbox) -> None:
    note = sandbox.file("# Day\n\n")

    worklog(sandbox).append("after the blank line")

    assert note.read_text(encoding="utf-8") == "# Day\n\n- [x] after the blank line\n"


def test_a_checklist_can_be_started_in_an_empty_file(sandbox: Sandbox) -> None:
    note = sandbox.file("")

    result = worklog(sandbox).append("the very first entry")

    assert result.status == "created"
    assert note.read_text(encoding="utf-8") == "- [x] the very first entry"


def test_starting_a_checklist_can_be_a_dry_run(sandbox: Sandbox) -> None:
    note = sandbox.file("# Day\n\njust prose\n")

    result = worklog(sandbox).append("must not land", dry_run=True)

    assert result.status == "dry_run"
    assert result.line == "- [x] must not land"
    assert note.read_text(encoding="utf-8") == "# Day\n\njust prose\n"


def test_a_second_entry_extends_the_started_checklist(sandbox: Sandbox) -> None:
    note = sandbox.file("# Day\n")
    log = worklog(sandbox)

    log.append("first")
    result = log.append("second")

    assert result.status == "written"
    assert note.read_text(encoding="utf-8") == "# Day\n\n- [x] first\n- [x] second\n"


def test_the_pattern_filters_candidates(sandbox: Sandbox) -> None:
    sandbox.file("- [ ] item\n", name="Project Alpha.md")
    sandbox.file("- [ ] item\n", name="заметки дня.md")

    result = worklog(sandbox).append("not found")

    assert result.status == "no_file"
    assert "pattern" in result.message


def test_without_a_pattern_any_file_counts(sandbox: Sandbox) -> None:
    note = sandbox.file("- [ ] item\n", name="заметки дня.md")

    result = worklog(sandbox, pattern=None).append("into whatever is newest")

    assert result.status == "written"
    assert result.file == note.name


def test_an_empty_directory_reports_no_file(sandbox: Sandbox) -> None:
    result = worklog(sandbox, pattern=None).append("nothing here")

    assert result.status == "no_file"
    assert "no files" in result.message


def test_hidden_files_are_not_candidates(sandbox: Sandbox) -> None:
    sandbox.file("- [ ] item\n", name=".hidden.md")

    result = worklog(sandbox, pattern=None).append("skipped")

    assert result.status == "no_file"


def test_directories_are_not_candidates(sandbox: Sandbox) -> None:
    (sandbox.path / "2026-09-05.md").mkdir()

    result = worklog(sandbox).append("skipped")

    assert result.status == "no_file"


def test_the_newest_file_wins(sandbox: Sandbox) -> None:
    older = sandbox.file("- [ ] yesterday\n", name="2026-09-05.md")
    newer = sandbox.file("- [ ] today\n", pause=True)

    worklog(sandbox).append("into the newest")

    assert newer.read_text(encoding="utf-8").endswith("- [x] into the newest\n")
    assert "into the newest" not in older.read_text(encoding="utf-8")


def test_dry_run_writes_nothing(sandbox: Sandbox) -> None:
    note = sandbox.file("- [ ] item\n")

    result = worklog(sandbox).append("must not land", dry_run=True)

    assert result.status == "dry_run"
    assert result.line == "- [x] must not land"
    assert note.read_text(encoding="utf-8") == "- [ ] item\n"


def test_an_empty_description_is_refused(sandbox: Sandbox) -> None:
    note = sandbox.file("- [ ] item\n")

    result = worklog(sandbox).append("   \n  ")

    assert result.status == "empty"
    assert result.file is None
    assert note.read_text(encoding="utf-8") == "- [ ] item\n"


def test_a_leading_marker_is_stripped(sandbox: Sandbox) -> None:
    note = sandbox.file("- [ ] item\n")

    worklog(sandbox).append("- [ ] already carries a marker")

    assert note.read_text(encoding="utf-8").endswith("- [x] already carries a marker\n")


def test_line_endings_and_a_missing_final_newline_are_preserved(sandbox: Sandbox) -> None:
    note = sandbox.path / "2026-09-06.md"
    note.write_bytes(b"# Day\r\n\r\n- [ ] item")

    worklog(sandbox).append("keeps CRLF")

    assert note.read_bytes() == b"# Day\r\n\r\n- [ ] item\r\n- [x] keeps CRLF"


def test_an_unconfigured_directory_reports_no_dir() -> None:
    result = Worklog(directory=None).append("nowhere")

    assert result.status == "no_dir"


def test_a_missing_directory_reports_no_dir(tmp_path: Path) -> None:
    result = Worklog(directory=tmp_path / "absent").append("nowhere")

    assert result.status == "no_dir"


def test_a_file_that_is_not_utf8_is_an_error(sandbox: Sandbox) -> None:
    (sandbox.path / "2026-09-06.md").write_bytes(b"- [ ] \xff\xfe item\n")

    with pytest.raises(WorklogError, match="valid UTF-8"):
        worklog(sandbox).append("unreadable")


def test_a_failed_write_is_an_error_and_leaves_no_temporary_file(
    sandbox: Sandbox,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sandbox.file("- [ ] item\n")

    def explode(self: Path, target: Path) -> Path:  # ruff: ignore[unused-function-argument]
        message = "disk on fire"
        raise OSError(28, message)

    monkeypatch.setattr(Path, "replace", explode)

    with pytest.raises(WorklogError, match="cannot write"):
        worklog(sandbox).append("doomed")

    assert list(sandbox.path.glob(".worklog-*")) == []


def test_a_read_only_directory_is_an_error(sandbox: Sandbox) -> None:
    sandbox.file("- [ ] item\n")
    sandbox.path.chmod(0o500)

    try:
        with pytest.raises(WorklogError, match="cannot write"):
            worklog(sandbox).append("nowhere to spool")
    finally:
        sandbox.path.chmod(0o700)


def test_no_result_ever_carries_a_path(sandbox: Sandbox) -> None:
    sandbox.file("- [ ] item\n")
    log = worklog(sandbox)
    results = [
        log.append("written"),
        log.append("written"),
        log.append("dry", dry_run=True),
        log.append(""),
        Worklog(directory=None).append("x"),
        Worklog(directory=None).check(),
        worklog(Sandbox(path=sandbox.path / "absent")).check(),
    ]

    for result in results:
        assert str(sandbox.path) not in result.model_dump_json()


def test_check_reports_the_file_and_its_item_count(sandbox: Sandbox) -> None:
    note = sandbox.file("- [x] one\n- [ ] two\n\ntext\n")

    result = worklog(sandbox).check()

    assert result.status == "ok"
    assert result.file == note.name
    assert result.items == 2


def test_check_reports_a_missing_checklist(sandbox: Sandbox) -> None:
    sandbox.file("just prose\n")

    result = worklog(sandbox).check()

    assert result.status == "no_checklist"
    assert result.items is None


def test_a_document_without_a_checklist_has_no_block() -> None:
    assert _find_checklist(["# Day", "", "prose"]) is None
