"""Unit tests for basicpkg.stats."""

from __future__ import annotations

import math

import pandas as pd
import pytest

from basicpkg.stats import describe_dataframe, summary_stats


class TestSummaryStats:
    """summary_stats: schema stability, numeric accuracy, and error contracts."""

    EXPECTED_KEYS = {"mean", "median", "std", "min", "max", "count"}

    def test_schema_keys(self, sample_df: pd.DataFrame) -> None:
        assert set(summary_stats(sample_df, "value").keys()) == self.EXPECTED_KEYS

    def test_all_values_are_python_float(self, sample_df: pd.DataFrame) -> None:
        # type(v) is float (not numpy.float64) ensures JSON-serialisability
        # without a custom encoder — important for the CLI's json output path.
        result = summary_stats(sample_df, "value")
        assert all(type(v) is float for v in result.values())

    @pytest.mark.parametrize(
        "stat,expected",
        [
            ("mean", 30.0),
            ("median", 30.0),
            ("min", 10.0),
            ("max", 50.0),
            ("count", 5.0),
        ],
    )
    def test_known_stat_values(self, sample_df: pd.DataFrame, stat: str, expected: float) -> None:
        assert summary_stats(sample_df, "value")[stat] == pytest.approx(expected)

    def test_std_uses_ddof1(self, sample_df: pd.DataFrame) -> None:
        # Verify we match pandas sample std (ddof=1), not population std (ddof=0).
        expected = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0]).std()
        assert summary_stats(sample_df, "value")["std"] == pytest.approx(expected)

    def test_single_row_std_is_nan(self) -> None:
        # ddof=1 with n=1 is mathematically undefined → NaN.
        df = pd.DataFrame({"x": [42.0]})
        result = summary_stats(df, "x")
        assert result["count"] == pytest.approx(1.0)
        assert math.isnan(result["std"])

    @pytest.mark.parametrize("bad_col", ["missing", "nonexistent", "VALUE"])
    def test_missing_column_raises_key_error(self, sample_df: pd.DataFrame, bad_col: str) -> None:
        with pytest.raises(KeyError):
            summary_stats(sample_df, bad_col)


class TestDescribeDataframe:
    """describe_dataframe: column filtering and structural output."""

    def test_numeric_columns_are_present(self, sample_df: pd.DataFrame) -> None:
        result = describe_dataframe(sample_df)
        assert "value" in result
        assert "score" in result

    def test_non_numeric_columns_are_absent(self, sample_df: pd.DataFrame) -> None:
        assert "label" not in describe_dataframe(sample_df)

    def test_each_entry_has_correct_keys(self, sample_df: pd.DataFrame) -> None:
        expected = {"mean", "median", "std", "min", "max", "count"}
        for col_stats in describe_dataframe(sample_df).values():
            assert set(col_stats.keys()) == expected

    def test_empty_dataframe_returns_empty_dict(self) -> None:
        assert describe_dataframe(pd.DataFrame()) == {}

    def test_all_string_columns_returns_empty_dict(self) -> None:
        df = pd.DataFrame({"a": ["x", "y"], "b": ["p", "q"]})
        assert describe_dataframe(df) == {}
