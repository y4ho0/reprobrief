"""Typed data models shared across the application."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CommandSpec:
    name: str
    argv: tuple[str, ...]
    cwd: str = "."
    expected_exit_codes: tuple[int, ...] = (0,)
    timeout_seconds: float = 30.0
    max_output_bytes: int = 65_536
    inherit_env: tuple[str, ...] = ()


@dataclass(frozen=True)
class Recipe:
    schema_version: int
    commands: tuple[CommandSpec, ...]
    source: Path | None = None


@dataclass(frozen=True)
class StreamCapture:
    text: str
    total_bytes: int
    retained_bytes: int
    truncated: bool


@dataclass(frozen=True)
class CommandResult:
    name: str
    argv: tuple[str, ...]
    cwd: str
    expected_exit_codes: tuple[int, ...]
    exit_code: int | None
    outcome: str
    duration_seconds: float
    stdout: StreamCapture
    stderr: StreamCapture
    timed_out: bool = False
    error: str | None = None


@dataclass(frozen=True)
class GitSnapshot:
    available: bool
    head: str | None
    branch: str | None
    status: tuple[str, ...] = ()
    error: str | None = None


@dataclass
class RedactionSummary:
    replacements: dict[str, int] = field(default_factory=dict)
    residual_warnings: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return sum(self.replacements.values())


def json_ready(value: Any) -> Any:
    """Convert dataclasses, paths, and tuples into JSON-compatible values."""

    if hasattr(value, "__dataclass_fields__"):
        return json_ready(asdict(value))
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_ready(item) for item in value]
    return value
