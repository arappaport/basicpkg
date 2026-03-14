"""DataFrame transformation utilities."""

from __future__ import annotations

import pandas as pd


def normalise_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Min-max normalise *column* to [0, 1] and return a new DataFrame.

    A copy is always returned so callers retain their original data —
    critical in pipeline contexts where one DataFrame feeds multiple branches.

    Args:
        df:     Source DataFrame containing *column*.
        column: Name of the numeric column to normalise.

    Returns:
        New DataFrame identical to *df* except *column* is scaled to [0, 1].

    Raises:
        KeyError:   *column* is not present in *df*.
        ValueError: *column* has zero variance; min-max is undefined (0 / 0).
    """
    if column not in df.columns:
        raise KeyError(f"'{column}' not found; available: {list(df.columns)}")

    col_min = float(df[column].min())
    col_max = float(df[column].max())

    # Zero variance would produce NaN silently via 0/0 — fail fast instead
    # so the error surfaces at the call site, not somewhere downstream.
    if col_min == col_max:
        raise ValueError(
            f"'{column}' has zero variance (all values == {col_min}); "
            "min-max normalisation is undefined."
        )

    result = df.copy()
    result[column] = (df[column] - col_min) / (col_max - col_min)
    return result


def filter_above_mean(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Return rows where *column* is strictly greater than the column mean.

    Args:
        df:     Source DataFrame.
        column: Numeric column used as the filter criterion.

    Returns:
        Filtered DataFrame (new object; *df* is not modified).

    Raises:
        KeyError: *column* is not present in *df*.
    """
    if column not in df.columns:
        raise KeyError(f"'{column}' not found; available: {list(df.columns)}")

    return df[df[column] > df[column].mean()]
