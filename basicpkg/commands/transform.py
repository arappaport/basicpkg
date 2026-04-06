from __future__ import annotations

import json
import sys

import click
import pandas as pd

from basicpkg.commands.stats import _render_stats
from basicpkg.main import run_pipeline


@click.command("pipeline")
@click.argument("csv_file", type=click.Path(exists=True, readable=True))
@click.option(
    "--column",
    "-c",
    required=True,
    help="Numeric column to normalise and filter.",
)
@click.option(
    "--output",
    "-o",
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
        click.echo(f"\nFiltered rows ({len(filtered_df)} above mean after normalisation):")
        click.echo(filtered_df.to_string(index=False))
        click.echo("\nStats on filtered set:")
        # stats values are dicts of str->float;
        # cast satisfies mypy after isinstance check
        _render_stats(stats)  # type: ignore[arg-type]
