"""Click CLI for basicpkg.

click is a dev dependency — this module must never be imported by library
consumers or included in import paths that don't require the CLI.

The version lookup is guarded against PackageNotFoundError so the CLI
remains functional when run directly from source (i.e. before `pip install`).
"""

from __future__ import annotations

import importlib.metadata
import json
import sys

import click
import pandas as pd

from basicpkg.main import run_pipeline
from basicpkg.stats import describe_dataframe, summary_stats

try:
    _VERSION = importlib.metadata.version("basicpkg")
except importlib.metadata.PackageNotFoundError:
    # Running from source without installation — use a sentinel so callers
    # know this is not a real release version.
    _VERSION = "0.0.0.dev"


def _render_stats(stats: dict[str, dict[str, float]]) -> None:
    """Write a stats dict to stdout in human-readable columnar form."""
    for col_name, col_stats in stats.items():
        click.echo(f"\n── {col_name} ──")
        for stat_name, val in col_stats.items():
            click.echo(f"  {stat_name:<8}: {val:.4f}")


@click.group()
@click.version_option(version=_VERSION, prog_name="basicpkg")
def main() -> None:
    """basicpkg — data transformation and statistics CLI."""


@main.command("stats")
@click.argument("csv_file", type=click.Path(exists=True, readable=True))
@click.option(
    "--column", "-c",
    default=None,
    help="Column to analyse. Defaults to all numeric columns.",
)
@click.option(
    "--output", "-o",
    type=click.Choice(["pretty", "json"], case_sensitive=False),
    default="pretty",
    show_default=True,
    help="Output format.",
)
def stats_cmd(csv_file: str, column: str | None, output: str) -> None:
    """Print descriptive statistics for CSV_FILE."""
    try:
        df = pd.read_csv(csv_file)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"[ERROR] Cannot read '{csv_file}': {exc}", err=True)
        sys.exit(1)

    if column is not None:
        if column not in df.columns:
            click.echo(
                f"[ERROR] Column '{column}' not found. "
                f"Available: {list(df.columns)}",
                err=True,
            )
            sys.exit(1)
        result: dict[str, dict[str, float]] = {column: summary_stats(df, column)}
    else:
        result = describe_dataframe(df)

    if output == "json":
        click.echo(json.dumps(result, indent=2))
    else:
        _render_stats(result)


@main.command("pipeline")
@click.argument("csv_file", type=click.Path(exists=True, readable=True))
@click.option(
    "--column", "-c",
    required=True,
    help="Numeric column to normalise and filter.",
)
@click.option(
    "--output", "-o",
    type=click.Choice(["pretty", "json"], case_sensitive=False),
    default="pretty",
    show_default=True,
    help="Output format.",
)
def pipeline_cmd(csv_file: str, column: str, output: str) -> None:
    """Run normalise → filter → stats pipeline on CSV_FILE."""
    try:
        df = pd.read_csv(csv_file)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"[ERROR] Cannot read '{csv_file}': {exc}", err=True)
        sys.exit(1)

    try:
        pipeline_result = run_pipeline(df, column)
    except (KeyError, ValueError) as exc:
        click.echo(f"[ERROR] Pipeline failed: {exc}", err=True)
        sys.exit(1)

    filtered_df = pipeline_result["filtered"]
    stats = pipeline_result["stats"]

    if not isinstance(filtered_df, pd.DataFrame):
        click.echo("[ERROR] Unexpected type for filtered output.", err=True)
        sys.exit(1)

    if not isinstance(stats, dict):
        click.echo("[ERROR] Unexpected type for stats output.", err=True)
        sys.exit(1)

    if output == "json":
        click.echo(
            json.dumps(
                {
                    "stats": stats,
                    "filtered_rows": filtered_df.to_dict(orient="records"),
                },
                indent=2,
            )
        )
    else:
        click.echo(
            f"\nFiltered rows ({len(filtered_df)} above mean after normalisation):"
        )
        click.echo(filtered_df.to_string(index=False))
        click.echo("\nStats on filtered set:")
        # stats values are dicts of str->float;
        # cast satisfies mypy after isinstance check
        _render_stats(stats)  # type: ignore[arg-type]
