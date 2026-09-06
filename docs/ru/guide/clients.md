---
title: Настройка клиентов
---

# Настройка клиентов

Сервер говорит по stdio и не принимает аргументов, кроме двух своих настроек, поэтому укладывается в стандартную форму, которую использует любой MCP-клиент. Имя, которое вы ему дадите, станет префиксом инструментов — с именем `worklog` ниже они будут называться `worklog_append` и `worklog_check`.

Команда всегда одна и та же:

```bash
worklog-mcp serve --dir /path/to/notes
```

Всё на этой странице — она же, записанная так, как ждёт каждый конкретный клиент.

## Обычная форма

Большинство клиентов принимают объект `mcpServers`. Различается только файл, в который он кладётся:

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

    `~/.cursor/mcp.json` для всех проектов, `.cursor/mcp.json` для одного.

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

    `cline_mcp_settings.json` — кнопка **MCP Servers → Configure** в расширении.

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

    `~/.gemini/settings.json` или `.gemini/settings.json` в проекте.

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

## Исключения

Четыре клиента используют собственную форму.

=== "VS Code"

    `.vscode/mcp.json` в рабочей области или команда **MCP: Open User Configuration** для всех. Ключ здесь `servers`, а не `mcpServers`:

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

    `settings.json`, под ключом `context_servers`:

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

    `~/.codex/config.toml` или `.codex/config.toml` в проекте — TOML, а не JSON:

    ```toml
    [mcp_servers.worklog]
    command = "worklog-mcp"
    args = ["serve", "--dir", "/path/to/notes"]
    ```

    Либо добавить из терминала:

    ```bash
    codex mcp add worklog -- worklog-mcp serve --dir /path/to/notes
    ```

=== "OpenCode"

    `opencode.json`, под ключом `mcp`, команда — одним массивом:

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

Одна команда, править ничего не нужно:

```bash
claude mcp add worklog -- worklog-mcp serve --dir /path/to/notes
```

Добавьте `--scope user`, чтобы сервер был доступен во всех проектах, а не только в текущем.

## Как не писать путь в файл конфигурации

Обе настройки читают переменную окружения — `WORKLOG_DIR` и `WORKLOG_FILE_PATTERN`, — поэтому в файле конфигурации пути может не быть вовсе. Это важно, когда файл общий, лежит в репозитории или его читает сам ассистент.

Большинство клиентов принимают блок `env`:

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

Некоторые идут дальше. OpenCode подставляет `{env:NAME}` в любое значение конфигурации, так что переменная может остаться в профиле шелла:

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

Gemini CLI делает то же самое через `$VAR` и `${VAR}` внутри своего блока `env`, а Claude Code принимает `--env` прямо в командной строке:

```bash
claude mcp add worklog --env WORKLOG_DIR=/path/to/notes -- worklog-mcp serve
```

!!! note "Не забудьте про экранирование"

    Регулярному выражению в JSON нужны удвоенные обратные слэши — `"^\\d{4}"`, — и в обычной строке TOML тоже. В шелле его нужно закавычить.

## Если команда не находится

У клиента, запущенного из графической оболочки, `PATH` может отличаться от шелловского, а `uv tool install` кладёт команды в `~/.local/bin`. Выходов два: указать абсолютный путь к команде или запускать её через uv, который сам находит инструмент:

```json
{
  "command": "uvx",
  "args": ["--from", "worklog-mcp", "worklog-mcp", "serve", "--dir", "/path/to/notes"]
}
```

Форма с `uvx` заодно позволяет обойтись без установки — ценой более медленного первого старта.

## Как проверить подключение

Если инструменты не появились, запустите ту же команду руками — с `check` вместо `serve`, потому что она печатает вердикт, а не ждёт данных на stdin:

```bash
worklog-mcp check --dir /path/to/notes
```

Это отделяет сломанную конфигурацию от сломанного клиента: если `check` отвечает `ok`, а клиент по-прежнему ничего не показывает, дело в клиенте.
