# worklog-mcp

🇺🇸 **English** · 🇷🇺 [Русский](README.ru.md)

[![PyPI - Version](https://img.shields.io/pypi/v/worklog-mcp)](https://pypi.org/project/worklog-mcp/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/worklog-mcp)](https://pypi.org/project/worklog-mcp/)
![PyPI - Status](https://img.shields.io/pypi/status/worklog-mcp)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/worklog-mcp)
![PyPI - Downloads](https://img.shields.io/pypi/dm/worklog-mcp)
![PyPI - Format](https://img.shields.io/pypi/format/worklog-mcp)
[![MCP](https://img.shields.io/badge/MCP-server-blue)](https://modelcontextprotocol.io)
[![Typed](https://img.shields.io/badge/typing-py.typed-261230)](https://peps.python.org/pep-0561/)

[![CI](https://github.com/feodor-ra/worklog-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/feodor-ra/worklog-mcp/actions/workflows/ci.yml)
[![Docs](https://github.com/feodor-ra/worklog-mcp/actions/workflows/docs.yml/badge.svg)](https://github.com/feodor-ra/worklog-mcp/actions/workflows/docs.yml)
[![Coverage Status](https://coveralls.io/repos/github/feodor-ra/worklog-mcp/badge.svg?branch=main)](https://coveralls.io/github/feodor-ra/worklog-mcp?branch=main)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://feodor-ra.github.io/worklog-mcp/)
![GitHub Release](https://img.shields.io/github/v/release/feodor-ra/worklog-mcp)
![GitHub last commit](https://img.shields.io/github/last-commit/feodor-ra/worklog-mcp)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/feodor-ra/worklog-mcp)
[![GitHub issues](https://img.shields.io/github/issues/feodor-ra/worklog-mcp)](https://github.com/feodor-ra/worklog-mcp/issues)
![GitHub Repo stars](https://img.shields.io/github/stars/feodor-ra/worklog-mcp?style=flat)
[![License: MIT](https://img.shields.io/github/license/feodor-ra/worklog-mcp)](LICENSE)

**An MCP server that records finished work in your daily log.** Point it at a directory of log files; it appends one done item to the checklist of the newest one.

If you keep a note per day with a checklist of what got done, the assistant that did the work can write the line itself. The directory is configured once, when the server starts, so it never travels through the conversation — the model sees the file's name and the line it wrote, and nothing else.

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

That is the whole setup. The assistant now has `append` and `check`.

## Install

```bash
uv tool install worklog-mcp
```

Requires Python **3.13+**. No editor, vault format or note-taking app is assumed: a log file is any text file with a markdown checklist in it.

## Add it to your agent

<details open>
<summary><b>Claude Code</b></summary>

```bash
claude mcp add worklog -- worklog-mcp serve --dir /path/to/notes
```

Add `--scope user` to make it available in every project.
</details>

<details>
<summary><b>Claude Desktop</b> · <code>claude_desktop_config.json</code></summary>

```json
{
  "mcpServers": {
    "worklog": {
      "command": "worklog-mcp",
      "args": ["serve", "--dir", "/path/to/notes"]
    }
  }
}
```
</details>

<details>
<summary><b>Cursor</b> · <code>~/.cursor/mcp.json</code></summary>

```json
{
  "mcpServers": {
    "worklog": {
      "command": "worklog-mcp",
      "args": ["serve", "--dir", "/path/to/notes"]
    }
  }
}
```
</details>

<details>
<summary><b>VS Code</b> · <code>.vscode/mcp.json</code> — note the <code>servers</code> key</summary>

```json
{
  "servers": {
    "worklog": {
      "type": "stdio",
      "command": "worklog-mcp",
      "args": ["serve", "--dir", "/path/to/notes"]
    }
  }
}
```
</details>

<details>
<summary><b>Windsurf</b> · <code>~/.codeium/windsurf/mcp_config.json</code></summary>

```json
{
  "mcpServers": {
    "worklog": {
      "command": "worklog-mcp",
      "args": ["serve", "--dir", "/path/to/notes"]
    }
  }
}
```
</details>

<details>
<summary><b>Zed</b> · <code>settings.json</code> — <code>context_servers</code></summary>

```json
{
  "context_servers": {
    "worklog": {
      "command": "worklog-mcp",
      "args": ["serve", "--dir", "/path/to/notes"],
      "env": {}
    }
  }
}
```
</details>

<details>
<summary><b>Cline</b> · <code>cline_mcp_settings.json</code></summary>

```json
{
  "mcpServers": {
    "worklog": {
      "command": "worklog-mcp",
      "args": ["serve", "--dir", "/path/to/notes"]
    }
  }
}
```
</details>

<details>
<summary><b>Codex CLI</b> · <code>~/.codex/config.toml</code></summary>

```toml
[mcp_servers.worklog]
command = "worklog-mcp"
args = ["serve", "--dir", "/path/to/notes"]
```

Or: `codex mcp add worklog -- worklog-mcp serve --dir /path/to/notes`
</details>

<details>
<summary><b>Gemini CLI</b> · <code>~/.gemini/settings.json</code></summary>

```json
{
  "mcpServers": {
    "worklog": {
      "command": "worklog-mcp",
      "args": ["serve", "--dir", "/path/to/notes"]
    }
  }
}
```
</details>

<details>
<summary><b>OpenCode</b> · <code>opencode.json</code></summary>

```json
{
  "mcp": {
    "worklog": {
      "type": "local",
      "command": ["worklog-mcp", "serve", "--dir", "/path/to/notes"]
    }
  }
}
```
</details>

## How to use it

**1. Keep the path out of the config file, if you like.** Both options read an environment variable — `WORKLOG_DIR` and `WORKLOG_FILE_PATTERN` — so the snippet can carry no path at all:

```json
{
  "mcpServers": {
    "worklog": {
      "command": "worklog-mcp",
      "args": ["serve"],
      "env": { "WORKLOG_DIR": "/path/to/notes" }
    }
  }
}
```

**2. Narrow down which files count, if the directory holds more than logs.** `--pattern` is a regular expression matched against the file name:

```bash
worklog-mcp serve --dir ~/notes --pattern '^\d{4}-\d{2}-\d{2}\.md$'
```

Without a pattern, every non-hidden file in the directory is a candidate, and the newest one wins.

**3. Check the setup from a terminal** whenever a call reports something missing:

```bash
worklog-mcp check --dir ~/notes
# ok: file="2026-09-06.md" items=3
```

Exit codes are `0` ok, `2` no directory, `3` no log file, `4` no checklist.

## Why it's cool

- **The path stays out of the conversation.** It is a launch argument, read by the local process. Results carry a file name, never a directory.
- **It never creates a log file.** A missing file or directory is reported and the call stops, so the assistant cannot reorganize your notes. The one thing it does add is a checklist, when today's file has none yet.
- **Repeating a call is safe.** An item whose text is already in the checklist is not written twice, so a retried workflow does not double a line.
- **Your formatting survives.** The new item reuses the indent and bullet marker of the checklist's first item, and the file keeps its line endings; the write is atomic, so an editor watching the file never sees it truncated.

## Documentation

📖 **[Full documentation](https://feodor-ra.github.io/worklog-mcp/)** — configuration, ready-made client snippets, exactly how the file and the checklist are picked, the tool contracts and an API reference. Available in English and Russian.

## License

MIT — see [LICENSE](LICENSE).

---

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/badge/types-ty-261230)](https://github.com/astral-sh/ty)
[![pytest](https://img.shields.io/badge/tested%20with-pytest-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org)
[![Material for MkDocs](https://img.shields.io/badge/docs-Material%20for%20MkDocs-526CFE?logo=materialformkdocs&logoColor=white)](https://squidfunk.github.io/mkdocs-material/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)
[![Semantic Versions](https://img.shields.io/badge/SemVer-2.0.0-3F4551)](https://semver.org)
[![Keep a Changelog](https://img.shields.io/badge/Keep%20a%20Changelog-1.1.0-E05735?logo=keepachangelog&logoColor=white)](https://keepachangelog.com)
