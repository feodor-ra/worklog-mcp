# worklog-mcp

🇺🇸 [English](README.md) · 🇷🇺 **Русский**

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
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://feodor-ra.github.io/worklog-mcp/ru/)
![GitHub Release](https://img.shields.io/github/v/release/feodor-ra/worklog-mcp)
![GitHub last commit](https://img.shields.io/github/last-commit/feodor-ra/worklog-mcp)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/feodor-ra/worklog-mcp)
[![GitHub issues](https://img.shields.io/github/issues/feodor-ra/worklog-mcp)](https://github.com/feodor-ra/worklog-mcp/issues)
![GitHub Repo stars](https://img.shields.io/github/stars/feodor-ra/worklog-mcp?style=flat)
[![License: MIT](https://img.shields.io/github/license/feodor-ra/worklog-mcp)](LICENSE)

**MCP-сервер, который записывает сделанную работу в ваш дневной лог.** Укажите ему каталог с лог-файлами — он допишет один выполненный пункт в чек-лист самого свежего из них.

Если вы ведёте заметку на день с чек-листом сделанного, ассистент, который эту работу выполнил, может записать строку сам. Каталог задаётся один раз, при запуске сервера, и потому никогда не проходит через диалог: модель видит имя файла и записанную строку — и больше ничего.

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

Это вся настройка. У ассистента появились `append` и `check`.

## Установка

```bash
uv tool install worklog-mcp
```

Нужен Python **3.13+**. Ни редактор, ни формат хранилища, ни приложение для заметок не предполагаются: лог-файл — это любой текстовый файл с markdown-чек-листом внутри.

## Подключение к вашему агенту

<details open>
<summary><b>Claude Code</b></summary>

```bash
claude mcp add worklog -- worklog-mcp serve --dir /path/to/notes
```

Добавьте `--scope user`, чтобы сервер был доступен во всех проектах.
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
<summary><b>VS Code</b> · <code>.vscode/mcp.json</code> — здесь ключ <code>servers</code></summary>

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

Или: `codex mcp add worklog -- worklog-mcp serve --dir /path/to/notes`
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

## Как этим пользоваться

**1. При желании не пишите путь в файл конфигурации.** Обе опции читают переменную окружения — `WORKLOG_DIR` и `WORKLOG_FILE_PATTERN`, — поэтому пути в блоке может не быть вовсе:

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

**2. Сузьте выбор файлов, если в каталоге лежат не только логи.** `--pattern` — регулярное выражение, сопоставляемое с именем файла:

```bash
worklog-mcp serve --dir ~/notes --pattern '^\d{4}-\d{2}-\d{2}\.md$'
```

Без паттерна кандидатом становится любой нескрытый файл каталога, и побеждает самый свежий.

**3. Проверьте настройку из терминала**, когда вызов сообщает, что чего-то не хватает:

```bash
worklog-mcp check --dir ~/notes
# ok: file="2026-09-06.md" items=3
```

Коды возврата: `0` — порядок, `2` — нет каталога, `3` — нет лог-файла, `4` — в нём нет чек-листа.

## Почему это удобно

- **Путь не попадает в диалог.** Он аргумент запуска, который читает локальный процесс. В результатах — имя файла, никогда не каталог.
- **Лог-файлы не создаются.** Об отсутствии файла или каталога сообщается, и вызов останавливается: ассистент не может переорганизовать ваши заметки. Единственное, что он добавит, — чек-лист, если в сегодняшнем файле его ещё нет.
- **Повторный вызов безопасен.** Пункт, который уже есть в чек-листе, не пишется второй раз, поэтому перезапуск сценария не задваивает строку.
- **Ваше форматирование сохраняется.** Новый пункт наследует отступ и маркер первого пункта чек-листа, файл сохраняет свои переводы строк, а запись атомарна — редактор, следящий за файлом, никогда не увидит его обрезанным.

## Документация

📖 **[Полная документация](https://feodor-ra.github.io/worklog-mcp/ru/)** — настройка, готовые блоки для клиентов, точные правила выбора файла и чек-листа, контракты инструментов и справочник API. На русском и английском.

## Лицензия

MIT — см. [LICENSE](LICENSE).

---

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/badge/types-ty-261230)](https://github.com/astral-sh/ty)
[![pytest](https://img.shields.io/badge/tested%20with-pytest-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org)
[![Material for MkDocs](https://img.shields.io/badge/docs-Material%20for%20MkDocs-526CFE?logo=materialformkdocs&logoColor=white)](https://squidfunk.github.io/mkdocs-material/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)
[![Semantic Versions](https://img.shields.io/badge/SemVer-2.0.0-3F4551)](https://semver.org)
[![Keep a Changelog](https://img.shields.io/badge/Keep%20a%20Changelog-1.1.0-E05735?logo=keepachangelog&logoColor=white)](https://keepachangelog.com)
