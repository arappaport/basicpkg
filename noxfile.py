"""Nox task automation.

Dependencies are installed directly via pip (not via poetry-inside-nox) to
avoid the overhead of embedding a build tool in every session venv.

Session reference:
    lint       ruff check + ruff format --check  (read-only, reuse_venv=True)
    format     ruff format + ruff check --fix    (writes files, not in defaults)
    typecheck  mypy --strict                     (reuse_venv=True)
    tests      pytest matrix over 3.10/3.11/3.12
    safety     pip-audit on runtime deps only
    ci         lint + typecheck + tests-3.11 as a fast PR gate
"""

from __future__ import annotations

import nox

PYTHON_VERSIONS = ["3.10", "3.11", "3.12"]

# Intentionally minimal: fast feedback for the most common Python version.
# Developers opt into the full matrix with `nox -s tests`.
nox.options.sessions = ["lint", "typecheck", "tests-3.11"]

# Mirrors [tool.poetry.dependencies] in pyproject.toml.
# Kept here as a constant so the safety session and test sessions stay aligned.
_RUNTIME_DEPS = ["pandas>=2.2"]

# Dev-tool subset needed to run the test suite.
_TEST_DEPS = [
    "pandas>=2.2",
    "pandas-stubs>=2.2",
    "click>=8.1",
    "pytest>=8.1",
    "pytest-cov>=5.0",
    "tomli>=2.0; python_version < '3.11'",
]


@nox.session(python="3.11", reuse_venv=True)
def lint(session: nox.Session) -> None:
    """Lint and format-check with ruff (read-only; fails on any violation)."""
    session.install("ruff")
    session.run("ruff", "check", "basicpkg", "tests", "noxfile.py")
    session.run("ruff", "format", "--check", "basicpkg", "tests", "noxfile.py")


@nox.session(python="3.11", reuse_venv=True)
def format(session: nox.Session) -> None:
    """Auto-format and fix lint violations in-place with ruff."""
    session.install("ruff")
    session.run("ruff", "format", "basicpkg", "tests", "noxfile.py")
    session.run("ruff", "check", "--fix", "basicpkg", "tests", "noxfile.py")


@nox.session(python="3.11", reuse_venv=True)
def typecheck(session: nox.Session) -> None:
    """Run mypy --strict over the package source."""
    session.install("mypy", "pandas-stubs", "click", *_RUNTIME_DEPS)
    session.run("mypy", "basicpkg", "--strict")


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run pytest with branch coverage across the Python version matrix."""
    session.install(*_TEST_DEPS)
    # Install the package in editable mode so `import basicpkg` resolves correctly.
    session.install("-e", ".", "--no-deps")
    # Extra args forwarded from CLI: nox -s tests-3.11 -- -k test_stats -v
    session.run("pytest", *session.posargs)


@nox.session(python="3.11", reuse_venv=False)
def safety(session: nox.Session) -> None:
    """Audit runtime dependencies for known CVEs via pip-audit.

    Dev deps are intentionally excluded — end-users never install them,
    so CVEs in dev tools don't affect library consumers.
    """
    session.install("pip-audit", *_RUNTIME_DEPS)
    session.run("pip-audit")


@nox.session(python="3.11")
def ci(session: nox.Session) -> None:
    """Composite fast gate: lint + typecheck + tests-3.11.

    Intended for PR checks. Full matrix testing runs as a parallel CI job.
    Sessions cannot call each other in Nox, so logic is inlined here.
    """
    session.install("ruff")
    session.run("ruff", "check", "basicpkg", "tests")
    session.run("ruff", "format", "--check", "basicpkg", "tests")

    session.install("mypy", "pandas-stubs", "click", *_RUNTIME_DEPS)
    session.run("mypy", "basicpkg", "--strict")

    session.install(*_TEST_DEPS)
    session.install("-e", ".", "--no-deps")
    session.run("pytest", *session.posargs)
