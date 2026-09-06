---
title: Client snippets
---

# Client snippets

The server speaks stdio and takes no arguments beyond its two settings, so it fits the standard shape every MCP client uses. Give it the name you want its tools prefixed with — `worklog` below, which makes the tools `worklog_append` and `worklog_check`.

The command is always the same:

```bash
worklog-mcp serve --dir /path/to/notes
```

Everything on this page is that command, spelled the way each client expects.

## The usual shape

Most clients take an `mcpServers` object. Only the file it goes in differs:

=== "Claude Desktop"

    `claude_desktop_config.json` — Settings → Developer → Edit Config.

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

=== "Cursor"

    `~/.cursor/mcp.json` for every project, `.cursor/mcp.json` for one.

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

=== "Windsurf"

    `~/.codeium/windsurf/mcp_config.json`.

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

=== "Cline"

    `cline_mcp_settings.json` — the extension's **MCP Servers → Configure** button.

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

=== "Gemini CLI"

    `~/.gemini/settings.json`, or `.gemini/settings.json` in a project.

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

## The exceptions

Four clients use a shape of their own.

=== "VS Code"

    `.vscode/mcp.json` in a workspace, or **MCP: Open User Configuration** for all of them. The key is `servers`, not `mcpServers`:

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

=== "Zed"

    `settings.json`, under `context_servers`:

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

=== "Codex CLI"

    `~/.codex/config.toml`, or `.codex/config.toml` in a project — TOML, not JSON:

    ```toml
    [mcp_servers.worklog]
    command = "worklog-mcp"
    args = ["serve", "--dir", "/path/to/notes"]
    ```

    Or add it from the terminal:

    ```bash
    codex mcp add worklog -- worklog-mcp serve --dir /path/to/notes
    ```

=== "OpenCode"

    `opencode.json`, under `mcp`, with the command as one array:

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

## Claude Code

One command, no file to edit:

```bash
claude mcp add worklog -- worklog-mcp serve --dir /path/to/notes
```

Add `--scope user` to make it available in every project instead of the current one.

## Keeping the path out of the config file

Both settings read an environment variable — `WORKLOG_DIR` and `WORKLOG_FILE_PATTERN` — so the config file can carry no path at all. That matters when the file is shared, committed to a repository, or read by the assistant itself.

Most clients take an `env` block:

```json
{
  "mcpServers": {
    "worklog": {
      "command": "worklog-mcp",
      "args": ["serve"],
      "env": {
        "WORKLOG_DIR": "/path/to/notes",
        "WORKLOG_FILE_PATTERN": "^\\d{4}-\\d{2}-\\d{2}\\.md$"
      }
    }
  }
}
```

Some go further. OpenCode interpolates `{env:NAME}` into any configuration value, so the variable can stay in your shell profile:

```json
{
  "mcp": {
    "worklog": {
      "type": "local",
      "command": ["worklog-mcp", "serve", "--dir", "{env:WORKLOG_DIR}"]
    }
  }
}
```

Gemini CLI does the same with `$VAR` and `${VAR}` inside its `env` block, and Claude Code takes `--env` on the command line:

```bash
claude mcp add worklog --env WORKLOG_DIR=/path/to/notes -- worklog-mcp serve
```

!!! note "Remember the escaping"

    A regular expression in JSON needs its backslashes doubled — `"^\\d{4}"` — and in TOML a basic string does too. In a shell, quote it.

## When the command is not found

A client started from a desktop launcher may not have the `PATH` your shell has, and `uv tool install` puts its commands in `~/.local/bin`. Two ways out: give the absolute path to the command, or run it through uv, which resolves the tool itself:

```json
{
  "command": "uvx",
  "args": ["--from", "worklog-mcp", "worklog-mcp", "serve", "--dir", "/path/to/notes"]
}
```

The `uvx` form also skips the install step entirely, at the cost of a slower first start.

## Checking the wiring

If the tools do not appear, run the same command by hand — with `check` instead of `serve`, which prints a verdict rather than waiting on stdin:

```bash
worklog-mcp check --dir /path/to/notes
```

That separates a broken configuration from a broken client: if `check` answers `ok` and the client still shows nothing, the problem is on the client's side.
