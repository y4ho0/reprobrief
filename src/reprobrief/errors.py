"""Domain errors and stable command-line exit codes."""

from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    """Stable process exit codes for automation."""

    OK = 0
    USAGE = 2
    RECIPE_INVALID = 3
    EXECUTION_FAILED = 4
    OUTPUT_ERROR = 5
    CANCELLED = 130


class ReproBriefError(Exception):
    """Base class for expected user-facing failures."""


class RecipeError(ReproBriefError):
    """A recipe is invalid or cannot be loaded."""


class ExecutionError(ReproBriefError):
    """A declared command could not be executed as planned."""


class OutputError(ReproBriefError):
    """A report or archive could not be safely written."""
