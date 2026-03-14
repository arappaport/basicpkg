# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-01

### Added

- `normalise_column` — min-max normalisation of a DataFrame column to [0, 1].
- `filter_above_mean` — row filter returning only rows strictly above the column mean.
- `summary_stats` — per-column descriptive statistics as a plain JSON-serialisable dict.
- `describe_dataframe` — batch statistics across all numeric columns in a DataFrame.
- `run_pipeline` — composable normalise → filter → describe pipeline.
- CLI entry point (`basicpkg stats`, `basicpkg pipeline`) via Click (dev dependency).
- Nox sessions: `lint`, `format`, `typecheck`, `tests`, `safety`, `ci`.
- GitHub Actions CI: separate lint, typecheck, test matrix, and CVE audit jobs.
- pre-commit hooks: ruff lint + ruff-format on every commit.
- `py.typed` marker (PEP 561) for inline type information.
