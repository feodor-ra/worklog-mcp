---
title: Limitations
---

# Limitations

An honest list of what this server does not do, and why.

## It never creates a log file { #creates }

No log file, no directory, no heading. If today's file does not exist, the call reports `no_file` — an outcome to relay, not a problem to fix.

These are someone's notes, and a server that created files would eventually create the wrong one: a second file for a day that already had one under a different name, or a file in a directory that was only temporarily unmounted. Reporting the gap costs one line in a conversation; guessing costs trust in the whole log.

The one exception is the checklist itself. A file that exists but holds no checklist gets one started at its end, and the call returns `created` ([details](checklist.md#created)). The reasoning is the mirror image: the user already decided that this file is today's log by creating it, and a list appended to its end cannot land in the wrong day or displace anything that was there.

## It only ever appends { #appends }

One item, at the end of one checklist. It does not tick existing items, reorder them, edit them, remove them, or touch a second checklist. There is no `remove` tool and no `update` tool.

## It cannot read your log back { #reads }

`check` returns a file name and a count. `append` returns a file name and the line it wrote. No tool returns the contents of a log file, and there is no resource to subscribe to. If an assistant needs to know what is already in your notes, it has to be given that some other way — which is the point: the log is written to, not read from.

## One directory per server { #directory }

The directory is fixed at startup. Two directories means two server entries in your client, with different names. There is no tool argument for choosing a directory at call time, because that argument would put the path back into the conversation.

## Markdown checklists only { #markdown }

The item is recognised by the `- [ ]` shape, and written the same way. Org-mode, plain bullets, numbered lists and tables are not checklists to this server.

## Whitespace is normalized { #whitespace }

A multi-line description becomes one line. That is not configurable: a checklist item is a line, and a paragraph pasted into one would break the block boundaries that everything else depends on.

## Concurrent writes { #concurrency }

The write is atomic — the file is replaced in one step, so nothing ever observes it truncated. It is not locked. Two servers appending to the same file at the same instant, or you saving in an editor at that instant, can still lose one of the two changes. In practice these calls are seconds apart and this has no consequence, but it is not a database.
