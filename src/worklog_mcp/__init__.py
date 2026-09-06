"""An MCP server that records finished work in a directory of log files.

The public surface is small on purpose: build a :class:`Worklog` to use the
logic directly, or :func:`build_server` to expose it over MCP.
"""

from worklog_mcp.logfile import AppendResult, CheckResult, Worklog, WorklogError
from worklog_mcp.server import build_server

__all__ = ["AppendResult", "CheckResult", "Worklog", "WorklogError", "build_server"]
