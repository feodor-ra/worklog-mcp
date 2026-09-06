---
title: How the checklist is found
---

# How the checklist is found

Inside the chosen file, the item goes into the **first** checklist, after its last line. This page is the whole of that rule, because it is the part that has to behave predictably on a file you did not write for a machine.

## The rule

1. Skip a YAML frontmatter block, if the file opens with one.
2. Skip fenced code blocks — a markdown example inside triple backticks is not a checklist.
3. Find the first line that looks like `- [ ]` or `- [x]`, at any indent, with `-`, `*` or `+` as the marker. That is the checklist.
4. Walk forward to the end of that block: further items, nested items, their continuation lines and the blank lines between them all belong to it. The block ends at the first line that goes back to a shallower level, or at a code fence.
5. Insert the new item right after that last line.

The new item reuses the indent and the bullet marker of the checklist's **first** item, and is always written as done — `[x]`. Line endings are preserved, including CRLF, and so is a missing newline at the end of the file.

## A worked example

Given this file:

```markdown
---
tags: [daily]
---

# 2026-09-06

- [x] reviewed the release checklist
    - [ ] follow up on the failing job
      still waiting on the runner

- [ ] look at the import failures

## Notes

- [ ] read the RFC
```

An `append` with *fixed the CSV import in the reports service* produces:

```markdown
---
tags: [daily]
---

# 2026-09-06

- [x] reviewed the release checklist
    - [ ] follow up on the failing job
      still waiting on the runner

- [ ] look at the import failures
- [x] fixed the CSV import in the reports service

## Notes

- [ ] read the RFC
```

Three things to read off it: the frontmatter list was not mistaken for a checklist, the nested item and its continuation line stayed inside the block, and the checklist under **Notes** was left alone because the first checklist wins.

## When there is no checklist { #created }

A log file that has none gets one started at its end, and the call comes back as `created` rather than `written`. A file that exists but is still empty of structure is a day that has not been written in yet, not a reason to refuse the entry.

The new list is minimal — a `-` bullet, no indent, no heading of its own:

```markdown
# 2026-09-06

Slow morning, mostly meetings.
```

becomes

```markdown
# 2026-09-06

Slow morning, mostly meetings.

- [x] fixed the CSV import in the reports service
```

The blank line before it is not cosmetic: a list glued to the paragraph above it is not a list at all, and the file would render as one run-on paragraph.

From then on the file has a checklist like any other, so the next entry is an ordinary `written` that extends it.

This is the one and only thing the server creates. The log **file** is still never created — see [Limitations](limitations.md#creates) — and `check` never starts a list either: it reports `no_checklist` and leaves the file untouched.

## Why the first one

A daily note tends to open with the list that matters — what is being done today — and to collect other lists further down: reading, errands, someone else's tasks. Appending to the last checklist would put work in whichever list happens to be at the bottom that day. The first one is stable, and it is the one you look at.

If your file is organised the other way round, there is no setting for it. Move the work list to the top, or point the server at a directory whose files are shaped that way.

## The description

The sentence given to `append` is collapsed to a single line: runs of whitespace become one space, and newlines disappear. A leading list or checkbox marker is stripped, so a description that arrives as `- [ ] fixed the import` is written as one item and not as a marker inside an item.

A description that is empty after all that comes back as `empty`, and nothing is written.

## Duplicates

Before writing, the existing items in the block are compared with the new one, ignoring markers and whitespace differences. A match returns `duplicate` and touches nothing. This is what makes a retried workflow safe: the same call twice leaves one line, not two.
