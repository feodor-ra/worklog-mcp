---
title: Tools
---

# Reference: tools

The server offers two tools. Their names reach a client prefixed with the name you gave the server, so `worklog` makes them `worklog_append` and `worklog_check`.

## append

Records one finished piece of work.

| Argument | Type | Default | Meaning |
| --- | --- | --- | --- |
| `description` | string | required | What was done, as one sentence |
| `dry_run` | boolean | `false` | Return the line that would be written, without writing it |

The result is an object with four fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `status` | string | What happened; see below |
| `file` | string \| null | Name of the log file, without its directory |
| `line` | string \| null | The line written, or that would have been written |
| `message` | string | One sentence describing the outcome |

### Statuses

| `status` | Written? | Meaning |
| --- | --- | --- |
| `written` | yes | The item was appended to an existing checklist |
| `created` | yes | The file had no checklist, so one was started with this item |
| `duplicate` | no | The checklist already held that item |
| `dry_run` | no | `dry_run` was set; `line` shows what would go in |
| `empty` | no | The description was blank after normalization |
| `no_dir` | no | No directory is configured, or it does not exist |
| `no_file` | no | The directory holds no matching file |

`created` is worth passing on to the user: their file gained a list it did not have ([details](../guide/checklist.md#created)).

The last two are prerequisites that are absent. Relay them; do not try to repair them ([why](../guide/limitations.md#creates)).

A file that is not valid UTF-8, or a write that fails, comes back as a tool **error** rather than a status, with a message naming the file and the reason.

## check

Reports whether a log file with a checklist can be found right now. Takes no arguments.

| Field | Type | Meaning |
| --- | --- | --- |
| `status` | string | `ok`, `no_dir`, `no_file` or `no_checklist` |
| `file` | string \| null | Name of the log file, without its directory |
| `items` | integer \| null | How many items the checklist already holds |
| `message` | string | One sentence describing the outcome |

It exists to tell a misconfigured server apart from a log that has not been started today. It is not a way to read the log: the items are counted, never returned.

Unlike `append`, it never starts a checklist — a file without one is reported as `no_checklist` and left alone.

## What never comes back

No result of either tool contains a filesystem path, the directory's name, or the contents of the file beyond the single line that was just written. That holds for error messages too.
