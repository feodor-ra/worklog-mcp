---
title: Changelog
---

# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-09-06

### Added

- First release. An MCP server with two tools: `append`, which adds one done
  item to the first checklist of the newest file in a directory, and `check`,
  which reports which file that is and how many items it already holds.
- A log file with no checklist gets one started at its end, reported as the
  status `created`. The log file itself is still never created.
- Configuration at launch only — `--dir` / `WORKLOG_DIR` and `--pattern` /
  `WORKLOG_FILE_PATTERN` — so the directory never travels through a
  conversation, and no result carries a filesystem path.
- A `worklog-mcp check` subcommand for diagnosing the setup from a terminal,
  with exit codes separating a missing directory, a missing log file and a
  missing checklist.
- The importable Python API behind both: `Worklog`, `AppendResult`,
  `CheckResult`, `WorklogError` and `build_server`.
