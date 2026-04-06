# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

```bash
# Install all dependencies (required before running anything)
poetry install --with dev

# Lint (read-only check)
nox -s lint

# Auto-format and fix lint violations in-place
nox -s format

# Type check
nox -s typecheck

# Run tests (Python 3.13 only)
nox -s tests-3.13

# Run full test matrix (3.10, 3.12, 3.13)
nox -s tests

# Run a single test file or test by keyword
nox -s tests-3.13 -- -k test_stats
nox -s tests-3.13 -- tests/test_transform.py -v

# Run the full CI gate (lint + typecheck + tests-3.13)
nox -s ci

# Audit runtime deps for CVEs
nox -s safety
```

## Architecture

### Dependency boundary: library vs CLI

The package enforces a strict split:
- **Runtime deps** (`pandas` only) — what library consumers install
- **Dev deps** (`click`, pytest, ruff, mypy, etc.) — never exposed to consumers

`click` is intentionally absent from `[tool.poetry.dependencies]`. The CLI lives entirely under `basicpkg/cli.py` and `basicpkg/commands/`, and those modules must never be imported outside of CLI context.

### Core library (`basicpkg/stats.py`, `basicpkg/transform.py`)

Pure functions that operate on pandas DataFrames. All functions return new DataFrames — originals are never mutated. Stats functions return plain `dict[str, float]` (not DataFrames) to stay JSON-serializable. Zero-variance inputs raise `ValueError` immediately rather than silently producing NaN.

### Pipeline entry point (`basicpkg/main.py`)

`run_pipeline(df, column)` orchestrates the full flow: `normalise_column` → `filter_above_mean` → `describe_dataframe`. This is the primary programmatic API.

### CLI layer (`basicpkg/cli.py`, `basicpkg/commands/`)

Click group (`main`) with two sub-commands registered from `commands/stats.py` and `commands/transform.py`. The CLI entry point is `basicpkg.cli:main` (dev-only install via `poetry install --with dev`).

### Public API (`basicpkg/__init__.py`)

Re-exports `summary_stats`, `describe_dataframe`, `normalise_column`, `filter_above_mean`. The `py.typed` marker enables downstream mypy usage.

## Tooling Notes

- **ruff** handles both linting and formatting (replaces flake8 + black + isort). Config is in `[tool.ruff]` in `pyproject.toml`. Line length is 120.
- **mypy** runs in `--strict` mode with no exceptions. `pandas-stubs` provides pandas type information.
- **pytest** enforces 85% branch coverage via `--cov-fail-under=85`. Tests will fail if coverage drops below this.
- **Nox sessions reuse venvs** (`reuse_venv=True`) for speed except `safety` — don't be surprised if `nox -s lint` skips installation after the first run.
- The `noxfile.py` is in `basicpkg/` (the inner package directory), not the repo root.
