---
title: Command line
---

# Command line

The package installs one command with two subcommands. `serve` is what a client runs; `check` is for you.

```console
$ worklog-mcp --help
Usage: worklog-mcp [OPTIONS] COMMAND [ARGS]...

  Append what you did to the checklist of the newest file in a directory.

Commands:
  serve  Run the MCP server on stdio. This is the command an MCP client starts.
  check  Report which log file would be written to, and how many items it holds.
```

Both subcommands take `--dir` and `--pattern`; see [Configuration](configuration.md).

## serve

```bash
worklog-mcp serve --dir ~/notes
```

Speaks the Model Context Protocol on standard input and output, so running it in a terminal looks like a hang — that is a client's job, not yours. It exits when the client closes the connection.

The directory is not validated at startup, on purpose. A server that refused to start would show up in a client as a broken connection with no tools and no explanation; instead it starts, offers both tools, and every call reports `no_dir` until the directory is there. That also survives a directory that lives on a drive mounted after login.

## check

```bash
worklog-mcp check --dir ~/notes
```

```text
ok: file="2026-09-06.md" items=3
```

It answers one question — which file would `append` write to, and how many items its checklist already holds. It is a probe, not a viewer: the items themselves are never printed.

## Exit codes

| Code | Meaning | What to do |
| --- | --- | --- |
| `0` | A log file with a checklist was found | Nothing |
| `1` | The file is not valid UTF-8 | Fix the file's encoding |
| `2` | No directory configured, or it does not exist | Check `--dir` / `WORKLOG_DIR`; also returned for a bad pattern or bad arguments |
| `3` | The directory holds no matching file | Create today's log, or loosen `--pattern` |
| `4` | The file has no checklist yet | Nothing — the next `append` starts one |

Code `3` is the one that means *your notes are not where the server expects*, and it is the reason `check` exists: it distinguishes "the server is misconfigured" from "today's file is not started yet". Code `4` is not a fault at all — `check` reports the file has no checklist, and an `append` would start one.

Failures are printed on standard error, prefixed with `worklog-mcp:`, and never contain the directory path.
