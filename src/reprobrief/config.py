"""Load and validate the intentionally small recipe schema."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from .errors import RecipeError
from .models import CommandSpec, Recipe

_TOP_LEVEL_KEYS = {"schema_version", "commands"}
_COMMAND_KEYS = {
    "name",
    "argv",
    "cwd",
    "expected_exit_codes",
    "timeout_seconds",
    "max_output_bytes",
    "inherit_env",
}
_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_ENV_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_MAX_RECIPE_BYTES = 1_048_576
_WINDOWS_DEVICE_NAMES = {
    "aux",
    "con",
    "nul",
    "prn",
    *(f"com{number}" for number in range(1, 10)),
    *(f"lpt{number}" for number in range(1, 10)),
}


def empty_recipe() -> Recipe:
    """Return the conservative zero-configuration recipe."""

    return Recipe(schema_version=1, commands=())


def load_recipe(path: Path | None, repo_root: Path) -> Recipe:
    """Load *path* or return an empty recipe when no path was supplied."""

    if path is None:
        return empty_recipe()
    try:
        with path.open("rb") as handle:
            payload = handle.read(_MAX_RECIPE_BYTES + 1)
        if len(payload) > _MAX_RECIPE_BYTES:
            raise RecipeError("recipe is larger than 1 MiB")
        raw = json.loads(payload.decode("utf-8"))
    except FileNotFoundError as exc:
        raise RecipeError(f"recipe does not exist: {path}") from exc
    except PermissionError as exc:
        raise RecipeError(f"recipe is not readable: {path}") from exc
    except UnicodeDecodeError as exc:
        raise RecipeError(f"recipe must be UTF-8: {path}") from exc
    except OSError as exc:
        raise RecipeError(f"recipe cannot be read: {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RecipeError(
            f"recipe is not valid JSON at line {exc.lineno}, column {exc.colno}: "
            f"{exc.msg}"
        ) from exc
    except RecursionError as exc:
        raise RecipeError("recipe JSON is nested too deeply") from exc
    recipe = parse_recipe(raw, repo_root)
    return Recipe(
        schema_version=recipe.schema_version,
        commands=recipe.commands,
        source=path.resolve(),
    )


def parse_recipe(raw: Any, repo_root: Path) -> Recipe:
    """Validate decoded JSON and construct a recipe."""

    if not isinstance(raw, dict):
        raise RecipeError("recipe root must be a JSON object")
    unknown = set(raw) - _TOP_LEVEL_KEYS
    if unknown:
        raise RecipeError(f"unknown recipe field(s): {', '.join(sorted(unknown))}")
    if raw.get("schema_version") != 1:
        raise RecipeError("schema_version must be 1")
    commands_raw = raw.get("commands")
    if not isinstance(commands_raw, list):
        raise RecipeError("commands must be a JSON array")
    if len(commands_raw) > 50:
        raise RecipeError("commands may contain at most 50 entries")

    commands: list[CommandSpec] = []
    names: set[str] = set()
    for index, item in enumerate(commands_raw):
        command = _parse_command(item, index, repo_root)
        normalized_name = command.name.casefold()
        if normalized_name in names:
            raise RecipeError(f"duplicate command name: {command.name}")
        names.add(normalized_name)
        commands.append(command)
    return Recipe(schema_version=1, commands=tuple(commands))


def _parse_command(raw: Any, index: int, repo_root: Path) -> CommandSpec:
    prefix = f"commands[{index}]"
    if not isinstance(raw, dict):
        raise RecipeError(f"{prefix} must be a JSON object")
    unknown = set(raw) - _COMMAND_KEYS
    if unknown:
        raise RecipeError(
            f"{prefix} has unknown field(s): {', '.join(sorted(unknown))}"
        )

    name = raw.get("name")
    if not isinstance(name, str) or not _NAME.fullmatch(name):
        raise RecipeError(
            f"{prefix}.name must match {_NAME.pattern!r} and be at most 64 characters"
        )
    if name.endswith(".") or name.split(".", 1)[0].casefold() in _WINDOWS_DEVICE_NAMES:
        raise RecipeError(f"{prefix}.name is not a portable filename: {name}")
    argv_raw = raw.get("argv")
    if (
        not isinstance(argv_raw, list)
        or not argv_raw
        or len(argv_raw) > 100
        or not all(
            isinstance(arg, str) and arg and "\x00" not in arg for arg in argv_raw
        )
    ):
        raise RecipeError(
            f"{prefix}.argv must be a non-empty array of at most 100 non-empty strings"
        )
    if sum(len(arg.encode("utf-8")) for arg in argv_raw) > 32_768:
        raise RecipeError(f"{prefix}.argv is larger than 32 KiB")
    if "{python}" in argv_raw[1:]:
        raise RecipeError(f"{prefix}.argv may use {{python}} only as its program")

    cwd = raw.get("cwd", ".")
    if not isinstance(cwd, str) or not cwd or "\x00" in cwd:
        raise RecipeError(f"{prefix}.cwd must be a non-empty string")
    _validate_cwd(repo_root, cwd, prefix)

    exits_raw = raw.get("expected_exit_codes", [0])
    if (
        not isinstance(exits_raw, list)
        or not exits_raw
        or len(exits_raw) > 32
        or not all(type(code) is int and -255 <= code <= 255 for code in exits_raw)
    ):
        raise RecipeError(
            f"{prefix}.expected_exit_codes must contain 1-32 integers from -255 to 255"
        )
    expected_exit_codes = tuple(dict.fromkeys(exits_raw))

    timeout = raw.get("timeout_seconds", 30)
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not 1 <= timeout <= 300
    ):
        raise RecipeError(f"{prefix}.timeout_seconds must be between 1 and 300")

    output_limit = raw.get("max_output_bytes", 65_536)
    if type(output_limit) is not int or not 1_024 <= output_limit <= 1_048_576:
        raise RecipeError(f"{prefix}.max_output_bytes must be between 1024 and 1048576")

    inherit_raw = raw.get("inherit_env", [])
    if (
        not isinstance(inherit_raw, list)
        or len(inherit_raw) > 50
        or not all(
            isinstance(name, str) and _ENV_NAME.fullmatch(name) for name in inherit_raw
        )
    ):
        raise RecipeError(
            f"{prefix}.inherit_env must contain at most 50 valid environment names"
        )
    inherited_names = tuple(dict.fromkeys(inherit_raw))
    if len({name.casefold() for name in inherited_names}) != len(inherited_names):
        raise RecipeError(
            f"{prefix}.inherit_env contains case-insensitive duplicate names"
        )

    return CommandSpec(
        name=name,
        argv=tuple(argv_raw),
        cwd=cwd,
        expected_exit_codes=expected_exit_codes,
        timeout_seconds=float(timeout),
        max_output_bytes=output_limit,
        inherit_env=inherited_names,
    )


def resolve_command_cwd(repo_root: Path, relative: str) -> Path:
    """Resolve a declared working directory without allowing root escape."""

    try:
        candidate = (repo_root / relative).resolve()
        root = repo_root.resolve()
    except (OSError, RuntimeError) as exc:
        raise RecipeError(f"command cwd cannot be resolved: {relative}") from exc
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise RecipeError(f"command cwd escapes the repository: {relative}") from exc
    return candidate


def _validate_cwd(repo_root: Path, relative: str, prefix: str) -> None:
    if Path(relative).is_absolute():
        raise RecipeError(f"{prefix}.cwd must be relative to the repository")
    candidate = resolve_command_cwd(repo_root, relative)
    if not candidate.exists():
        raise RecipeError(f"{prefix}.cwd does not exist: {relative}")
    if not candidate.is_dir():
        raise RecipeError(f"{prefix}.cwd is not a directory: {relative}")
    if os.path.commonpath((str(repo_root.resolve()), str(candidate))) != str(
        repo_root.resolve()
    ):
        raise RecipeError(f"{prefix}.cwd escapes the repository")
