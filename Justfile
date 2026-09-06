# Show available recipes.
help:
    @just --list --unsorted

# Check formatting, lint rules and types.
lint:
    uv run ruff format --check
    uv run ruff check
    uv run ty check

# Run the test suite with coverage.
test:
    uv run pytest --cov

# Serve the documentation site locally with live reload.
docs:
    uv run --group docs mkdocs serve

# Build the documentation site in strict mode.
docs-build:
    uv run --group docs mkdocs build --strict

# Build the distributions and run the smoke test against both.
smoke:
    uv build
    uv run --isolated --no-project --with dist/*.whl scripts/smoke_test.py
    uv run --isolated --no-project --with dist/*.tar.gz scripts/smoke_test.py
