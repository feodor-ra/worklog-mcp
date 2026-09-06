---
title: Configuration
---

# Configuration

Everything the server knows is fixed when it starts. There are two settings, and each can be given as an option or as an environment variable.

| Option | Variable | Required | Meaning |
| --- | --- | --- | --- |
| `--dir` | `WORKLOG_DIR` | yes | Directory holding the log files. `~` is expanded. |
| `--pattern` | `WORKLOG_FILE_PATTERN` | no | Regular expression a file name must match. Omit to accept every file. |

Both commands, `serve` and `check`, take both settings.

## Option or variable

The option wins when both are present. Which one to use is a question about who should see the path:

```bash
worklog-mcp serve --dir ~/notes
```

```bash
export WORKLOG_DIR=~/notes
worklog-mcp serve
```

The second form keeps the path out of the client's configuration file, which matters when that file is shared, committed to a repository, or read by the assistant itself. The server reads the variable from its own environment, which it inherits from the client that launched it.

!!! warning "An empty value is not a directory"

    A client that interpolates a variable into its config can produce `--dir ""` when the variable is unset. That is treated as *not configured*, not as the current directory — every call then reports `no_dir` instead of quietly writing into wherever the client happened to be running.

## The pattern

The expression is matched against the file **name** with `search`, so anchor it yourself when you mean the whole name:

| Pattern | Matches |
| --- | --- |
| `^\d{4}-\d{2}-\d{2}\.md$` | `2026-09-06.md` |
| `^\d{2}-\d{2}-\d{4} .+\.md$` | `06-09-2026 Monday.md` |
| `\.md$` | any markdown file |
| *omitted* | any non-hidden file |

Quote it in a shell, and remember that JSON needs its backslashes doubled:

```json
["worklog-mcp", "serve", "--dir", "/path/to/notes", "--pattern", "^\\d{4}-\\d{2}-\\d{2}\\.md$"]
```

An expression that does not compile is refused at startup, with the position of the problem. There is no partial mode where a broken pattern silently accepts everything.

## Nothing else is configurable

The bullet marker, the indent, the `[x]` state and the insertion point all come from the file being written to — see [How the checklist is found](checklist.md). Which file that is comes from the directory and the pattern, and nothing else — see [How the file is picked](file-selection.md).
