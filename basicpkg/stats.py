"""Descriptive statistics helpers."""

from __future__ import annotations

import pandas as pd


def summary_stats(df: pd.DataFrame, column: str) -> dict[str, float]:
    """Compute descriptive statistics for a single numeric column.

    Returns a plain dict rather than a DataFrame so results are directly
    JSON-serialisable without a custom encoder — useful for CLI output
    and logging.

    Args:
        df:     Source DataFrame.
        column: Name of the target numeric column.

    Returns:
        Dict with keys: mean, median, std, min, max, count.

    Raises:
        KeyError: *column* is not present in *df*.
    """
    if column not in df.columns:
        raise KeyError(f"'{column}' not found; available: {list(df.columns)}")

    s: pd.Series[float] = df[column].astype(float)

    # Explicit key set gives a stable, versioned schema — df.describe() varies
    # across pandas versions and includes unwanted percentiles by default.
    return {
        "mean": float(s.mean()),
        "median": float(s.median()),
        "std": float(s.std()),
        "min": float(s.min()),
        "max": float(s.max()),
        "count": float(s.count()),
    }


def describe_dataframe(df: pd.DataFrame) -> dict[str, dict[str, float]]:
    """Run summary_stats over every numeric column in *df*.

    Non-numeric columns are silently skipped so this function is safe to call
    on mixed-type DataFrames without pre-filtering.

    Args:
        df: Source DataFrame; may contain mixed dtypes.

    Returns:
        Nested dict: ``{column_name: summary_stats_output}``.
        Empty dict if *df* contains no numeric columns.
    """
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    return {col: summary_stats(df, col) for col in numeric_cols}
