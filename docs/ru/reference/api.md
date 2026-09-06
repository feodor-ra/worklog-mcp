---
title: Python API
---

# Справочник: Python API

Логику можно импортировать, поэтому пакет применим и без MCP — из скрипта, из git-хука, из другого сервера. Всё перечисленное ниже экспортируется из корня пакета:

```python
from worklog_mcp import AppendResult, CheckResult, Worklog, WorklogError, build_server
```

## Worklog

::: worklog_mcp.Worklog

## AppendResult

::: worklog_mcp.AppendResult

## CheckResult

::: worklog_mcp.CheckResult

## WorklogError

::: worklog_mcp.WorklogError

## build_server

::: worklog_mcp.build_server
