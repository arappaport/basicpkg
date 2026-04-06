"""Click CLI for basicpkg.

click is a dev dependency — this module must never be imported by library
consumers or included in import paths that don't require the CLI.

The version lookup is guarded against PackageNotFoundError so the CLI
remains functional when run directly from source (i.e. before `pip install`).
"""

from __future__ import annotations

import importlib.metadata

import click

from basicpkg.commands.stats import stats_cmd
from basicpkg.commands.transform import pipeline_cmd

try:
    _VERSION = importlib.metadata.version("basicpkg")
except importlib.metadata.PackageNotFoundError:
    # Running from source without installation — use a sentinel so callers
    # know this is not a real release version.
    _VERSION = "0.0.0.dev"


@click.group()
@click.version_option(version=_VERSION, prog_name="basicpkg")
def main() -> None:
    """basicpkg — data transformation and statistics CLI."""


main.add_command(stats_cmd)
main.add_command(pipeline_cmd)
