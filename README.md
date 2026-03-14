# basicpkg

[![CI](https://github.com/yourorg/basicpkg/actions/workflows/ci.yml/badge.svg)](https://github.com/yourorg/basicpkg/actions)
[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Coverage](https://img.shields.io/badge/coverage-%E2%89%8585%25-brightgreen)](htmlcov/index.html)
[![PyPI](https://img.shields.io/pypi/v/basicpkg)](https://pypi.org/project/basicpkg/)

---

## Overview

`basicpkg` is a production-quality Python package template wiring together Poetry,
Click, pytest, mypy, ruff, Nox, pre-commit, and GitHub Actions with correct
dependency boundaries from the start. It demonstrates a real-world pattern where
the core library requires only `pandas` at runtime and the CLI layer (`click`) is
a dev-only concern, keeping library consumers' dependency graphs lean.

---

## Package layout

```
basicpkg/
├── basicpkg/
│   ├── __init__.py           # Public API; re-exports all symbols
│   ├── py.typed              # PEP 561 marker — tells mypy types ship inline
│   ├── cli.py                # Click CLI (stats, pipeline sub-commands)
│   ├── main.py               # run_pipeline(); programmatic entry point
│   ├── stats.py              # summary_stats, describe_dataframe
│   └── transform.py          # normalise_column, filter_above_mean
├── tests/
│   ├── conftest.py           # Shared fixtures: sample_df, zero_variance_df, tmp_csv
│   ├── test_init.py          # Public API surface + version sync checks
│   ├── test_cli.py           # CLI integration tests (CliRunner)
│   ├── test_main.py          # Pipeline unit tests
│   ├── test_stats.py         # Stats module unit tests
│   └── test_transform.py     # Transform module unit tests
├── .github/
│   └── workflows/
│       └── ci.yml            # Separate lint / typecheck / tests / safety jobs
├── .pre-commit-config.yaml   # ruff lint + ruff-format on every commit
├── .gitignore
├── CHANGELOG.md
├── LICENSE
├── noxfile.py                # Task automation: lint, format, typecheck, tests, safety, ci
├── poetry.lock               # Committed for reproducible installs
└── pyproject.toml            # All tool config co-located here
```

---

## Prerequisites

| Tool       | Min version | Install                          |
|------------|-------------|----------------------------------|
| Python     | 3.10        | [python.org](https://python.org) |
| Poetry     | 1.8         | `pip install poetry`             |
| Nox        | 2024.3      | `pip install nox`                |
| pre-commit | 3.7         | `pip install pre-commit`         |

---

## Installation

```bash
git clone https://github.com/yourorg/basicpkg.git
cd basicpkg

# Install runtime + all dev dependencies (includes click for the CLI)
poetry install --with dev

# Activate the managed virtualenv
poetry shell

# Install git hooks so ruff runs on every commit
pre-commit install
```

> **Library-only install** (no CLI, no click):
> ```bash
> pip install basicpkg
> ```
> The library imports only `pandas`. `click` is never required.

---

## CLI usage

The `basicpkg` command is available after `poetry install --with dev`.

### Help

```bash
basicpkg --help
basicpkg stats    --help
basicpkg pipeline --help
```

### `stats` — descriptive statistics from a CSV file

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--column` | `-c` | all numeric cols | Column to analyse |
| `--output` | `-o` | `pretty` | `pretty` or `json` |

```bash
# All numeric columns, pretty output
basicpkg stats data.csv

# Single column
basicpkg stats data.csv -c price

# JSON output (pipe-friendly)
basicpkg stats data.csv -c price -o json
```

**Example pretty output:**

```
── value ──
  mean    : 30.0000
  median  : 30.0000
  std     : 15.8114
  min     : 10.0000
  max     : 50.0000
  count   : 5.0000
```

**Example JSON output:**

```json
{
  "value": {
    "mean": 30.0,
    "median": 30.0,
    "std": 15.811388300841896,
    "min": 10.0,
    "max": 50.0,
    "count": 5.0
  }
}
```

### `pipeline` — normalise → filter → stats

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--column` | `-c` | ✓ | Numeric column to process |
| `--output` | `-o` | — | `pretty` or `json` |

```bash
basicpkg pipeline data.csv -c price
basicpkg pipeline data.csv -c price -o json
```

**What the pipeline does:**

1. Min-max normalises `--column` to [0, 1].
2. Retains only rows where the normalised value is strictly above the mean.
3. Returns descriptive stats on the retained subset.

### Quick demo

```bash
printf 'value,label\n10,a\n20,b\n30,c\n40,d\n50,e\n' > /tmp/demo.csv

basicpkg stats    /tmp/demo.csv
basicpkg pipeline /tmp/demo.csv -c value -o json
```

---

## Running tests

### Full suite with coverage report

```bash
poetry run pytest
```

The run fails if branch coverage drops below **85%**.

### Useful flags

| Command | Purpose |
|---------|---------|
| `pytest -v` | Verbose test names |
| `pytest tests/test_transform.py -v` | Single file |
| `pytest -k "zero_variance"` | Keyword filter |
| `pytest -s` | Show stdout (debug) |
| `pytest --tb=long` | Full tracebacks |
| `pytest --cov-report=html` | Write HTML report to `htmlcov/` |

```bash
# Open HTML coverage report (macOS / Linux)
poetry run pytest --cov-report=html && open htmlcov/index.html
```

---

## Nox sessions

```bash
nox -l           # list all available sessions
nox              # run defaults: lint, typecheck, tests-3.11
nox -s <name>    # run one specific session
```

| Session | Description |
|---------|-------------|
| `lint` | ruff lint + format check (read-only; safe for CI) |
| `format` | ruff auto-format + fix violations in-place |
| `typecheck` | mypy `--strict` over `basicpkg/` |
| `tests-3.10` | pytest + coverage on Python 3.10 |
| `tests-3.11` | pytest + coverage on Python 3.11 |
| `tests-3.12` | pytest + coverage on Python 3.12 |
| `safety` | pip-audit CVE scan on runtime deps only |
| `ci` | lint + typecheck + tests-3.11 (fast PR gate) |

### Passing extra arguments to pytest

```bash
# Run one test file verbosely
nox -s tests-3.11 -- tests/test_transform.py -v

# Filter by test name
nox -s tests-3.11 -- -k "zero_variance" -v
```

### Full Python version matrix

```bash
nox -s tests     # runs 3.10, 3.11, 3.12 sequentially
```

---

## Development workflow

```bash
# 1. Install everything and wire up git hooks
poetry install --with dev
pre-commit install

# 2. Make your changes

# 3. Auto-format before committing
nox -s format

# 4. Run the full local gate
nox -s ci

# 5. (Optional) Run the full Python version matrix
nox -s tests

# 6. Commit — pre-commit runs ruff automatically
git add .
git commit -m "feat: describe your change"

# 7. Update CHANGELOG.md under [Unreleased] before opening a PR
```

---

## Library API

The library requires only `pandas`. `click` is never imported.

```python
import pandas as pd

from basicpkg import (
    describe_dataframe,
    filter_above_mean,
    normalise_column,
    summary_stats,
)
from basicpkg.main import run_pipeline

df = pd.DataFrame({"price": [10, 20, 30, 40, 50], "qty": [1, 2, 3, 4, 5]})

# Individual functions
print(summary_stats(df, "price"))
# {'mean': 30.0, 'median': 30.0, 'std': 15.81, 'min': 10.0, 'max': 50.0, 'count': 5.0}

print(describe_dataframe(df))
# {'price': {...}, 'qty': {...}}

normalised = normalise_column(df, "price")   # returns new DataFrame
filtered   = filter_above_mean(df, "price")  # rows where price > mean

# Full pipeline in one call
result = run_pipeline(df, "price")
print(result["filtered"])   # pd.DataFrame — rows above mean after normalisation
print(result["stats"])      # nested dict of stats on the filtered subset
```

---

## Contributing

1. Fork and clone the repository.
2. Run `poetry install --with dev && pre-commit install`.
3. Create a feature branch: `git checkout -b feat/your-feature`.
4. Write tests first — ensure `nox -s ci` passes before opening a PR.
5. Add an entry under `[Unreleased]` in `CHANGELOG.md`.
6. Open a pull request against `main`.

---

## Licence

[MIT](LICENSE)
