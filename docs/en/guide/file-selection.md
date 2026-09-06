---
title: How the file is picked
---

# How the file is picked

Every call picks the log file fresh, from the directory and the optional pattern. There is no cached choice and no file name stored anywhere.

## The rule

1. List the directory **itself**. Subdirectories are not searched, and directories are never candidates.
2. Drop names starting with a dot. Editor scratch files and hidden metadata are not logs.
3. If a pattern is configured, keep only names it matches.
4. Of what is left, take the one **created last**.

If step 4 has nothing to choose from, the call reports `no_file` and stops.

## Why creation time, and not today's date

Deriving the file name from the current date is the obvious alternative, and it is worse in two specific ways.

It needs to know your naming scheme — the format, and for a name that spells out a month or a weekday, the language those are written in. That is a table inside the server that silently produces the wrong name the day your note template changes.

And it gets the night wrong. Work finished at half past midnight belongs to the day that just ended, in the file you have been writing in all evening, not in a file for a date that has technically started. Taking the newest file puts the line where its author expects to find it.

The failure modes differ too. A missing match degrades into "no log file found", which is a message you can act on; a computed name degrades into writing to a file nobody was looking at.

!!! note "Creation time where the platform has one"

    macOS records a birth time, and that is what is used. On filesystems that do not — Linux, most notably — the modification time stands in. It orders files created in sequence the same way; the difference only shows if you edit an older file, which then sorts as the newest.

## Choosing what counts as a log

Without a pattern, every non-hidden file in the directory is a candidate. That is the right setting for a directory that holds nothing but logs.

With anything else in there — a project note, a shopping list, an image — give a pattern, and the choice narrows to files whose name says they are logs:

```bash
worklog-mcp serve --dir ~/notes --pattern '^\d{4}-\d{2}-\d{2}\.md$'
```

The pattern is the only filter. There is no content-based detection: a file that matches the name but has no checklist reports `no_checklist` rather than falling through to the next candidate. That is deliberate — falling through would mean writing into yesterday's log because today's was still empty.
