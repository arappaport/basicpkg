from __future__ import annotations

import json
import sys

import click
import pandas as pd

from basicpkg.stats import describe_dataframe, summary_stats


def _render_stats(stats: dict[str, dict[str, float]]) -> None:
    """Write a stats dict to stdout in human-readable columnar form."""
    for col_name, col_stats in stats.items():
        click.echo(f"\n── {col_name} ──")
        for stat_name, val in col_stats.items():
            click.echo(f"  {stat_name:<8}: {val:.4f}")


@click.command("stats")
@click.argument("csv_file", type=click.Path(exists=True, readable=True))
@click.option(
    "--column",
    "-c",
    default=None,
    help="Column to analyse. Defaults to all numeric columns.",
)
@click.option(
    "--output",
    "-o",
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
                f"[ERROR] Column '{column}' not found. Available: {list(df.columns)}",
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
