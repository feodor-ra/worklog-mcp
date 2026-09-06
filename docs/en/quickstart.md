---
title: Quickstart
---

# Quickstart

In a few minutes: install the server, point it at your notes, confirm it finds them, and let an assistant write the first line.

## 1. Install

```bash
uv tool install worklog-mcp
```

This puts a `worklog-mcp` command on your `PATH`. Nothing else is needed — the server has no state and no configuration file of its own.

## 2. Confirm it finds your log

Before wiring anything into a client, ask the command itself:

```bash
worklog-mcp check --dir ~/notes
```

```text
ok: file="2026-09-06.md" items=3
```

That is the file an `append` would write to, and the number of items its first checklist already holds. If the answer is not `ok`, the [CLI page](guide/cli.md) maps each exit code to what is missing.

If the directory holds more than logs, narrow it down with a regular expression matched against file names:

```bash
worklog-mcp check --dir ~/notes --pattern '^\d{4}-\d{2}-\d{2}\.md$'
```

## 3. Add it to your client

=== "OpenCode"

    ```json
    {
      "mcp": {
        "worklog": {
          "type": "local",
          "command": ["worklog-mcp", "serve", "--dir", "/path/to/your/notes"]
        }
      }
    }
    ```

=== "Claude Code"

    ```bash
    claude mcp add worklog -- worklog-mcp serve --dir /path/to/your/notes
    ```

=== "Generic"

    ```json
    {
      "mcpServers": {
        "worklog": {
          "command": "worklog-mcp",
          "args": ["serve", "--dir", "/path/to/your/notes"]
        }
      }
    }
    ```

Restart the client. Two tools appear, `append` and `check`, prefixed with the name you gave the server.

## 4. Write the first line

Ask the assistant to record what it just did. It calls `append` with one sentence, and reports back the file and the line:

```text
one item was appended to the checklist in "2026-09-06.md"
- [x] fixed the CSV import in the reports service, an unhandled empty row
```

Ask it again with the same sentence and nothing happens — the call comes back as `duplicate`. To see the line without writing it, the tool takes `dry_run`.

## Next

- [Configuration](guide/configuration.md) — passing the directory through the environment instead.
- [How the file is picked](guide/file-selection.md) and [how the checklist is found](guide/checklist.md) — the two rules worth knowing before trusting it with real notes.
- [Tools](reference/tools.md) — every status the two tools can return.
