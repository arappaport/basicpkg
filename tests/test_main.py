"""Unit tests for basicpkg.main.run_pipeline.

Integration-level: confirms that transform + stats compose correctly.
Numeric correctness is already proven in test_transform / test_stats.
"""

from __future__ import annotations

import pandas as pd
import pytest

from basicpkg.main import run_pipeline


class TestRunPipeline:
    """run_pipeline: return structure, type contracts, and error propagation."""

    def test_return_keys(self, sample_df: pd.DataFrame) -> None:
        assert set(run_pipeline(sample_df, "value").keys()) == {
            "normalised",
            "filtered",
            "stats",
        }

    @pytest.mark.parametrize("key", ["normalised", "filtered"])
    def test_dataframe_outputs(self, sample_df: pd.DataFrame, key: str) -> None:
        assert isinstance(run_pipeline(sample_df, "value")[key], pd.DataFrame)

    def test_stats_is_dict(self, sample_df: pd.DataFrame) -> None:
        assert isinstance(run_pipeline(sample_df, "value")["stats"], dict)

    def test_filtered_row_count(self, sample_df: pd.DataFrame) -> None:
        # Normalised [10..50] → [0, 0.25, 0.5, 0.75, 1.0]; mean = 0.5.
        # Rows strictly above 0.5: two rows (0.75 and 1.0).
        result = run_pipeline(sample_df, "value")
        assert isinstance(result["filtered"], pd.DataFrame)
        assert len(result["filtered"]) == 2

    def test_input_not_mutated(self, sample_df: pd.DataFrame) -> None:
        original = sample_df["value"].tolist()
        run_pipeline(sample_df, "value")
        assert sample_df["value"].tolist() == original

    def test_zero_variance_raises_value_error(
        self, zero_variance_df: pd.DataFrame
    ) -> None:
        with pytest.raises(ValueError, match="zero variance"):
            run_pipeline(zero_variance_df, "value")

    @pytest.mark.parametrize("bad_col", ["nonexistent", "label", ""])
    def test_bad_column_raises(self, sample_df: pd.DataFrame, bad_col: str) -> None:
        with pytest.raises((KeyError, ValueError)):
            run_pipeline(sample_df, bad_col)
