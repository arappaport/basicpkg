"""basicpkg public API.

Import from here, not from sub-modules, to get a stable interface.
Sub-module names and internal structure are implementation details
that may change between releases without a semver bump.
"""

from __future__ import annotations

from basicpkg.stats import describe_dataframe, summary_stats
from basicpkg.transform import filter_above_mean, normalise_column

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "describe_dataframe",
    "filter_above_mean",
    "normalise_column",
    "summary_stats",
]
