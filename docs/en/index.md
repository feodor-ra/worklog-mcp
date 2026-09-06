---
title: Overview
---

# worklog-mcp

**An MCP server that records finished work in your daily log.** Point it at a directory of log files; it appends one done item to the checklist of the newest one.

---

## Why

If you keep a note per day with a checklist of what got done, the assistant that did the work can write the line itself, at the moment the work finishes. What makes that worth wiring up rather than asking for a sentence to paste is where the configuration lives: the directory is a launch argument, read by the local process, so it never travels through the conversation. The model asks for one thing — append this sentence — and learns two: which file was written, and what line went into it.

The rest of the design follows from being let into someone's notes:

<div class="grid cards" markdown>

-   :material-folder-lock: **The path stays out of the conversation**

    Configured once when the server starts. Every result carries a file name, never a directory.

-   :material-file-hidden: **It never creates a log file**

    A missing file or directory is reported, and the call stops. Only a missing checklist is started for you.

-   :material-repeat-off: **Repeating a call is safe**

    An item already in the checklist is not written again, so a retried workflow does not double a line.

-   :material-format-align-left: **Your formatting survives**

    Indent, bullet marker and line endings are taken from the file, and the write is atomic.

</div>

## What it looks like

A log file before:

```markdown
# 2026-09-06

- [x] reviewed the release checklist
- [ ] look at the import failures
```

The assistant calls `append` with *fixed the CSV import in the reports service, an unhandled empty row*, and the file becomes:

```markdown
# 2026-09-06

- [x] reviewed the release checklist
- [ ] look at the import failures
- [x] fixed the CSV import in the reports service, an unhandled empty row
```

Nothing else in the file moves.

!!! info "Requirements"

    Python 3.13+ and an MCP client. No editor, vault format or note-taking app is assumed: a log file is any text file with a markdown checklist in it.

## Install

```bash
uv tool install worklog-mcp
```

## Next

- [Quickstart](quickstart.md) — from install to the first written line.
- [Configuration](guide/configuration.md) — the two options and their environment variables.
- [Client snippets](guide/clients.md) — ready-made blocks for Claude Code and Desktop, Cursor, VS Code, Windsurf, Zed, Cline, Codex CLI, Gemini CLI and OpenCode.
