# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this is

`worklog-mcp` — an MCP server that appends one done item to the checklist of the
newest file in a directory. Published to PyPI, installed with `uv tool install`,
configured only by launch arguments.

## The constraint everything follows from

The point of the package is that an assistant can write into someone's work log
**without being told where that log lives**. The directory is personal, and a
path that travels through a model's context is both a privacy leak and a
fragility: some setups rewrite or redact paths in transit, and a mangled path
fails silently.

That is why:

- **The directory is a launch argument, never a tool argument.** Adding a
  per-call directory parameter would put the path back into the model's context
  and defeat the package's reason to exist. Do not add one.
- **No result, and no error message, may contain a filesystem path.** Results
  carry the file's *name*. `tests/test_logfile.py` has a test asserting this
  across every status; keep it passing.
- **An empty `--dir` is "not configured", not `Path(".")`.** A client
  interpolating an unset variable produces `--dir ""`, and `Path("")` is the
  current directory — which would silently write into wherever the client was
  launched. `cli._directory` handles this; do not simplify it away.
- **A log file is never created.** No file, no directory. A missing one is a
  status to report, never a thing to repair — these are someone's notes, and a
  wrong guess costs trust in the whole log. The single exception is the
  checklist: a file that exists but has none gets one started at its end
  (status `created`), because the user already chose that file by creating it
  and a list appended at the end cannot displace anything. `check` does not
  make that exception — it reports `no_checklist` and writes nothing.

## Layout

- `src/worklog_mcp/logfile.py` — all the behaviour. `server` and `cli` are thin
  shells over it and hold no logic of their own.
- `src/worklog_mcp/server.py` — the two MCP tools. **Their docstrings are the
  prompt**: MCP ships them to the client as tool descriptions, so they are
  written as instructions to a model (when to call, what comes back, what the
  tool will not do), not as notes to a maintainer.
- `src/worklog_mcp/cli.py` — typer app, `serve` and `check`. Both options carry
  an `envvar`, which is what lets a client pass the directory without writing it
  into its config file.
- `tests/` — `conftest.py` provides the `sandbox` fixture; `test_logfile.py`
  covers the checklist parsing and file selection, which is where the subtle
  behaviour lives.
- `scripts/smoke_test.py` — run against the built wheel and sdist in
  `publish.yml`; catches a broken build and a dropped `py.typed`.

## Conventions

- **Docstrings**: English, Google style, `Returns:` starts with the type
  (`str: Description`). Ruff enforces the convention and mkdocstrings publishes
  them as the API reference, so the reference is written once, in the code.
- **Coverage is 100% with branch coverage on**, and `fail_under = 100`. A branch
  that cannot be reached is restructured or tested, not excused by lowering the
  gate.
- **Runtime dependencies use `~=`** so a major bump is never picked up silently.
  `ruff` and `ty` are pinned exactly instead: a patch release of either adds
  rules and would break CI on an unrelated commit. Dependabot proposes both
  weekly, in two groups — runtime and tooling — so a bump that changes what
  users install is never buried in a batch of CI-only bumps.
- **Commits**: Conventional Commits with English descriptions. Version bumps are
  a separate `chore(release)` commit made with `uv version --bump`, and that same
  commit updates both changelog pages.
- **Do not add a root `CHANGELOG.md`** — the changelog lives at
  `docs/{en,ru}/changelog.md` and is a tab in the docs nav. GitHub Release notes
  are taken from there.
- **Examples in the documentation are generic.** Log entries in the docs use
  invented, neutral service names; never a real company's internal system.

## Docs

Material for MkDocs, bilingual via `mkdocs-static-i18n` in folder mode
(`docs/en/**` at the site root, `docs/ru/**` under `/ru/`; `nav_translations`
localize the four nav sections, page titles come from each file's front matter).
The two translations are line-for-line mirrors: same headings, same code blocks.
Headings that other pages link to carry explicit `{ #anchor }` slugs so the
Russian page keeps the same fragment.

The API reference pages are `:::` blocks, identical in both locales — the
generated reference stays English on the Russian site, which is deliberate.

`docs/*/guide/clients.md` carries a configuration snippet per MCP client. Client
config formats drift; verify against the client's own documentation before
editing a snippet, and note that VS Code uses `servers`, Zed uses
`context_servers` and Codex uses TOML, while everything else uses `mcpServers`.

Local: `just docs` to serve, `just docs-build` for the strict build. Published
to GitHub Pages by `.github/workflows/docs.yml` (Pages source must be set to
"GitHub Actions" in the repository settings).

There are **no tests over the documentation**, by design. Three things stand in:
`mkdocs build --strict` fails on a broken link or a `:::` naming a symbol that no
longer exists; `ruff format --check` also formats Python inside Markdown, so the
examples are syntax-checked; and `scripts/smoke_test.py` is an executable version
of the quickstart.

`context7.json` indexes `docs/en` for AI assistants, and `overrides/main.html`
injects the Context7 widget into the built site.

## Release

1. `uv version --bump <patch|minor|major>` plus the changelog entry, as one
   `chore(release)` commit.
2. Tag and publish a **GitHub Release** — `publish.yml` fires on
   `release: published`, reruns CI, builds, smoke-tests both artifacts and
   publishes via PyPI Trusted Publishing (OIDC, environment `pypi`, no token).
   A bare `git push --tags` publishes nothing.
