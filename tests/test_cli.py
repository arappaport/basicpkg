"""Integration tests for the Click CLI.

CliRunner invokes commands in-process — no subprocess overhead.
catch_exceptions=False lets pytest surface real tracebacks on unexpected
errors instead of silently capturing them in result.exception.
"""

from __future__ import annotations

import json
import re

import pytest
from click.testing import CliRunner

from basicpkg.cli import main


@pytest.fixture()
def runner() -> CliRunner:
    """mix_stderr=False keeps stdout and stderr separate for precise assertions."""
    return CliRunner(mix_stderr=False)


class TestMainGroup:
    """Top-level CLI group: help text and version format."""

    def test_help_exits_zero(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["--help"], catch_exceptions=False)
        assert result.exit_code == 0

    def test_version_is_semver(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["--version"], catch_exceptions=False)
        assert result.exit_code == 0
        # Must match MAJOR.MINOR.PATCH or the dev sentinel 0.0.0.dev
        assert re.search(r"\d+\.\d+\.\d+", result.output), (
            f"Version output did not contain a semver string: {result.output!r}"
        )


class TestStatsCommand:
    """stats sub-command: column selection, output formats, error exits."""

    def test_all_numeric_columns_in_pretty_output(
        self, runner: CliRunner, tmp_csv: str
    ) -> None:
        result = runner.invoke(main, ["stats", tmp_csv], catch_exceptions=False)
        assert result.exit_code == 0
        assert "value" in result.output
        assert "score" in result.output

    def test_single_column_excludes_others(
        self, runner: CliRunner, tmp_csv: str
    ) -> None:
        result = runner.invoke(
            main, ["stats", tmp_csv, "-c", "value"], catch_exceptions=False
        )
        assert result.exit_code == 0
        assert "value" in result.output
        assert "score" not in result.output

    def test_json_output_is_valid_and_has_expected_keys(
        self, runner: CliRunner, tmp_csv: str
    ) -> None:
        result = runner.invoke(
            main, ["stats", tmp_csv, "-o", "json"], catch_exceptions=False
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "mean" in data["value"]

    @pytest.mark.parametrize("bad_col", ["ghost", "NONEXISTENT", "123"])
    def test_bad_column_exits_nonzero(
        self, runner: CliRunner, tmp_csv: str, bad_col: str
    ) -> None:
        result = runner.invoke(main, ["stats", tmp_csv, "-c", bad_col])
        assert result.exit_code != 0

    def test_nonexistent_file_exits_nonzero(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["stats", "/no/such/file.csv"])
        assert result.exit_code != 0


class TestPipelineCommand:
    """pipeline sub-command: output structure, JSON correctness, error exits."""

    def test_pretty_output_contains_row_count(
        self, runner: CliRunner, tmp_csv: str
    ) -> None:
        result = runner.invoke(
            main, ["pipeline", tmp_csv, "-c", "value"], catch_exceptions=False
        )
        assert result.exit_code == 0
        assert "Filtered rows" in result.output

    def test_json_has_required_top_level_keys(
        self, runner: CliRunner, tmp_csv: str
    ) -> None:
        result = runner.invoke(
            main, ["pipeline", tmp_csv, "-c", "value", "-o", "json"],
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "stats" in data
        assert "filtered_rows" in data

    def test_filtered_row_count_in_json_output(
        self, runner: CliRunner, tmp_csv: str
    ) -> None:
        result = runner.invoke(
            main, ["pipeline", tmp_csv, "-c", "value", "-o", "json"],
            catch_exceptions=False,
        )
        data = json.loads(result.output)
        # Normalised [10..50]: two rows have value > 0.5 (the post-normalisation mean)
        assert len(data["filtered_rows"]) == 2

    def test_missing_column_flag_exits_nonzero(
        self, runner: CliRunner, tmp_csv: str
    ) -> None:
        # --column is required; Click must reject the call before our code runs.
        result = runner.invoke(main, ["pipeline", tmp_csv])
        assert result.exit_code != 0

    @pytest.mark.parametrize("bad_col", ["ghost", "label"])
    def test_bad_column_exits_nonzero(
        self, runner: CliRunner, tmp_csv: str, bad_col: str
    ) -> None:
        result = runner.invoke(main, ["pipeline", tmp_csv, "-c", bad_col])
        assert result.exit_code != 0
