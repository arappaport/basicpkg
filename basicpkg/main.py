"""Programmatic pipeline entry point.

Separated from cli.py so the library is usable without click installed.
Only pandas (a declared runtime dependency) is required to import this module.
"""

from __future__ import annotations

import pandas as pd

from basicpkg.stats import describe_dataframe
from basicpkg.transform import filter_above_mean, normalise_column


def run_pipeline(df: pd.DataFrame, column: str) -> dict[str, object]:
    """Normalise, filter, and describe a DataFrame column in one call.

    Composes the three core library operations into a reusable pipeline:
    normalise → filter above mean → compute stats on the retained rows.

    Args:
        df:     Input DataFrame.
        column: Numeric column to process.

    Returns:
        Dict with keys:
            ``normalised`` — full DataFrame with *column* scaled to [0, 1].
            ``filtered``   — subset of rows above the post-normalisation mean.
            ``stats``      — describe_dataframe output on *filtered*.

    Raises:
        KeyError:   *column* is not present in *df*.
        ValueError: *column* has zero variance.
    """
    normalised = normalise_column(df, column)
    filtered = filter_above_mean(normalised, column)
    stats = describe_dataframe(filtered)
    return {"normalised": normalised, "filtered": filtered, "stats": stats}


if __name__ == "__main__":  # pragma: no cover
    # Quick smoke-test: python -m basicpkg.main
    _df = pd.DataFrame({"value": [10, 20, 30, 40, 50], "label": list("abcde")})
    _result = run_pipeline(_df, "value")
    print("Normalised:")
    print(_result["normalised"])
    print("\nFiltered:")
    print(_result["filtered"])
    print("\nStats:")
    print(_result["stats"])
