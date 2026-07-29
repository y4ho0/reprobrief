"""Command-line interface for ReproBrief."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TypedDict

from .config import load_recipe
from .errors import ExitCode, OutputError, RecipeError
from .facts import collect_git_snapshot, collect_system_facts
from .models import CommandResult, Recipe
from .output import create_archive, write_report_directory
from .redaction import Redactor
from .report import (
    build_manifest,
    manifest_json,
    redact_argv,
    redact_git,
    redact_result,
    render_markdown,
)
from .runner import resolved_argv, run_command
from .version import __version__

_DEFAULT_CONFIG = "reprobrief.json"
_DEFAULT_OUTPUT = "reprobrief-output"


class _PreviewCommand(TypedDict):
    name: str
    argv: list[str]
    declared_argv: list[str]
    cwd: str
    expected_exit_codes: list[int]
    timeout_seconds: float
    max_output_bytes_per_stream: int
    inherited_environment_names: list[str]


class _Preview(TypedDict):
    schema_version: int
    will_execute: list[_PreviewCommand]
    will_collect: list[str]
    will_not_collect: list[str]
    privacy_warning: str
    git_available: bool
    git_head: str | None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reprobrief",
        description=(
            "Create a previewable reproduction brief from bounded command output "
            "and conservative Git/system facts."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="action")

    run_parser = subparsers.add_parser("run", help="run a recipe and write a brief")
    _add_common_recipe_arguments(run_parser)
    run_parser.add_argument(
        "--output",
        type=Path,
        default=Path(_DEFAULT_OUTPUT),
        help=f"report directory (default: {_DEFAULT_OUTPUT})",
    )
    run_parser.add_argument(
        "--yes",
        action="store_true",
        help="approve the displayed commands without an interactive prompt",
    )
    run_parser.add_argument(
        "--force",
        action="store_true",
        help="replace only recognized ReproBrief output and archive paths",
    )
    run_parser.add_argument(
        "--archive",
        nargs="?",
        const="",
        metavar="PATH",
        help="also create a ZIP (default: OUTPUT.zip)",
    )

    inspect_parser = subparsers.add_parser(
        "inspect",
        help="preview collectors and declared commands without executing them",
    )
    _add_common_recipe_arguments(inspect_parser)
    inspect_parser.add_argument(
        "--json",
        action="store_true",
        help="emit the preview as JSON",
    )

    init_parser = subparsers.add_parser(
        "init",
        help="write a minimal example recipe",
    )
    init_parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path(_DEFAULT_CONFIG),
        help=f"recipe path (default: {_DEFAULT_CONFIG})",
    )
    return parser


def _add_common_recipe_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="repository root (default: current directory)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help=(
            "recipe path; when omitted, use reprobrief.json if present, "
            "otherwise collect facts only"
        ),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.action is None:
        parser.print_help()
        return int(ExitCode.OK)
    try:
        if args.action == "init":
            return _init_recipe(args.path)
        repo_root = args.repo.resolve()
        if not repo_root.is_dir():
            raise RecipeError(f"repository root is not a directory: {repo_root}")
        config_path = _select_config(args.config, repo_root)
        recipe = load_recipe(config_path, repo_root)
        if args.action == "inspect":
            return _inspect(repo_root, recipe, as_json=args.json)
        if args.action == "run":
            return _run(
                repo_root=repo_root,
                recipe=recipe,
                output=args.output,
                assume_yes=args.yes,
                force=args.force,
                archive=args.archive,
            )
    except RecipeError as exc:
        _error(str(exc))
        return int(ExitCode.RECIPE_INVALID)
    except OutputError as exc:
        _error(str(exc))
        return int(ExitCode.OUTPUT_ERROR)
    except KeyboardInterrupt:
        _error("cancelled; any running command was terminated")
        return int(ExitCode.CANCELLED)
    except OSError as exc:
        _error(f"operating-system error: {exc}")
        return int(ExitCode.OUTPUT_ERROR)
    return int(ExitCode.USAGE)


def _select_config(requested: Path | None, repo_root: Path) -> Path | None:
    if requested is not None:
        return requested if requested.is_absolute() else repo_root / requested
    conventional = repo_root / _DEFAULT_CONFIG
    return conventional if conventional.exists() else None


def _preview(repo_root: Path, recipe: Recipe) -> _Preview:
    git = collect_git_snapshot(repo_root)
    redactor = _display_redactor(repo_root, recipe)
    return {
        "schema_version": 1,
        "will_execute": [
            {
                "name": command.name,
                "argv": list(redact_argv(resolved_argv(command), redactor)),
                "declared_argv": list(redact_argv(command.argv, redactor)),
                "cwd": command.cwd,
                "expected_exit_codes": list(command.expected_exit_codes),
                "timeout_seconds": command.timeout_seconds,
                "max_output_bytes_per_stream": command.max_output_bytes,
                "inherited_environment_names": list(command.inherit_env),
            }
            for command in recipe.commands
        ],
        "will_collect": [
            "OS name, release, and architecture",
            "Python and ReproBrief versions",
            "Git HEAD, branch, and porcelain status paths",
            "declared command exit code, duration, bounded stdout, and bounded stderr",
            "Git status delta after execution",
        ],
        "will_not_collect": [
            "source-file contents",
            ".env files",
            "browser, editor, chat, or AI prompt history",
            "hostnames, usernames, network addresses, or hardware identifiers",
            "undeclared environment variables",
        ],
        "privacy_warning": (
            "Best-effort redaction cannot guarantee a secret-free report. "
            "Recognized sensitive argument values are masked in this preview. "
            "Review every generated file before sharing."
        ),
        "git_available": git.available,
        "git_head": git.head,
    }


def _inspect(repo_root: Path, recipe: Recipe, *, as_json: bool) -> int:
    preview = _preview(repo_root, recipe)
    if as_json:
        print(json.dumps(preview, indent=2, sort_keys=True))
        return int(ExitCode.OK)
    print("ReproBrief inspection (nothing was executed)")
    print()
    print("Commands:")
    if not recipe.commands:
        print("  (none; conservative facts only)")
    for command, item in zip(recipe.commands, preview["will_execute"], strict=True):
        print(f"  - {command.name}: {json.dumps(item['argv'])}")
        if item["argv"] != item["declared_argv"]:
            print(f"    declared={json.dumps(item['declared_argv'])}")
        print(
            f"    cwd={command.cwd!r}, timeout={command.timeout_seconds:g}s, "
            f"limit={command.max_output_bytes} bytes per stream"
        )
        if command.inherit_env:
            print(f"    inherits names only: {', '.join(command.inherit_env)}")
    print()
    print("Collects:")
    for collector in preview["will_collect"]:
        print(f"  - {collector}")
    print()
    print(f"Privacy: {preview['privacy_warning']}")
    return int(ExitCode.OK)


def _run(
    *,
    repo_root: Path,
    recipe: Recipe,
    output: Path,
    assume_yes: bool,
    force: bool,
    archive: str | None,
) -> int:
    _print_execution_plan(recipe, repo_root)
    if recipe.commands and not assume_yes and not _confirm():
        _error("not approved; no command was executed")
        return int(ExitCode.USAGE)

    git_before_raw = collect_git_snapshot(repo_root)
    facts = collect_system_facts()
    raw_results: list[CommandResult] = []
    inherited_values: dict[str, str] = {}
    for command in recipe.commands:
        print(f"Running {command.name}...", file=sys.stderr, flush=True)
        result, explicit = run_command(command, repo_root)
        raw_results.append(result)
        inherited_values.update(explicit)
    git_after_raw = collect_git_snapshot(repo_root)

    redactor = Redactor(
        repo_root=repo_root,
        home=_home_path(),
        exact_values=inherited_values,
    )
    results = [redact_result(result, redactor) for result in raw_results]
    git_before = redact_git(git_before_raw, redactor)
    git_after = redact_git(git_after_raw, redactor)
    redactor.scan_residual(
        [
            text
            for result in results
            for text in (
                *result.argv,
                result.cwd,
                result.stdout.text,
                result.stderr.text,
                result.error or "",
            )
        ]
        + list(git_before.status)
        + list(git_after.status)
    )
    manifest = build_manifest(
        facts=facts,
        git_before=git_before,
        git_after=git_after,
        results=results,
        redactor=redactor,
    )
    output_path = output if output.is_absolute() else repo_root / output
    files: dict[str, str] = {}
    for result in results:
        files[f"commands/{result.name}.stdout.txt"] = _stream_file(
            result.stdout.text,
            result.stdout.total_bytes,
            result.stdout.retained_bytes,
            result.stdout.truncated,
        )
        files[f"commands/{result.name}.stderr.txt"] = _stream_file(
            result.stderr.text,
            result.stderr.total_bytes,
            result.stderr.retained_bytes,
            result.stderr.truncated,
        )
    write_report_directory(
        output_path,
        report_markdown=render_markdown(manifest),
        manifest_json=manifest_json(manifest),
        command_files=files,
        force=force,
    )
    print(f"Wrote {output_path.resolve()}", file=sys.stderr)

    if archive is not None:
        archive_path = (
            output_path.with_suffix(".zip") if archive == "" else Path(archive)
        )
        if not archive_path.is_absolute():
            archive_path = repo_root / archive_path
        create_archive(output_path, archive_path, force=force)
        print(f"Wrote {archive_path.resolve()}", file=sys.stderr)

    has_failure = any(result.outcome != "expected" for result in results)
    if redactor.summary.residual_warnings:
        _error(
            "report was written, but residual secret-like patterns require review: "
            + ", ".join(redactor.summary.residual_warnings)
        )
        return int(ExitCode.EXECUTION_FAILED)
    return int(ExitCode.EXECUTION_FAILED if has_failure else ExitCode.OK)


def _print_execution_plan(recipe: Recipe, repo_root: Path) -> None:
    if not recipe.commands:
        print(
            "No commands configured; collecting conservative system and "
            "Git facts only.",
            file=sys.stderr,
        )
        return
    redactor = _display_redactor(repo_root, recipe)
    print("Commands declared by the recipe:", file=sys.stderr)
    for command in recipe.commands:
        print(
            f"  {command.name}: "
            f"{json.dumps(list(redact_argv(resolved_argv(command), redactor)))} "
            f"(cwd={command.cwd!r}, timeout={command.timeout_seconds:g}s)",
            file=sys.stderr,
        )
    print(
        "No shell is used. Review all generated files before sharing.",
        file=sys.stderr,
    )


def _confirm() -> bool:
    if not sys.stdin.isatty():
        _error("interactive approval unavailable; inspect, then pass --yes")
        return False
    print("Execute these commands? [y/N] ", end="", file=sys.stderr, flush=True)
    response = sys.stdin.readline().strip().lower()
    return response in {"y", "yes"}


def _display_redactor(repo_root: Path, recipe: Recipe) -> Redactor:
    exact_values = {
        name: value
        for command in recipe.commands
        for name in command.inherit_env
        if (value := os.environ.get(name)) is not None
    }
    return Redactor(
        repo_root=repo_root,
        home=_home_path(),
        exact_values=exact_values,
    )


def _home_path() -> Path | None:
    home_text = (
        os.environ.get("USERPROFILE") if os.name == "nt" else os.environ.get("HOME")
    )
    return Path(home_text) if home_text else None


def _stream_file(text: str, total: int, retained: int, truncated: bool) -> str:
    suffix = ""
    if truncated:
        suffix = (
            f"\n\n[ReproBrief truncated this stream: retained {retained} "
            f"of {total} bytes.]\n"
        )
    return text + suffix


def _init_recipe(path: Path) -> int:
    content = {
        "schema_version": 1,
        "commands": [
            {
                "name": "tests",
                "argv": ["{python}", "-m", "unittest", "discover", "-s", "tests"],
                "cwd": ".",
                "expected_exit_codes": [0],
                "timeout_seconds": 120,
                "max_output_bytes": 65536,
                "inherit_env": [],
            }
        ],
    }
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(content, handle, indent=2)
            handle.write("\n")
    except FileExistsError as exc:
        raise OutputError(f"refusing to overwrite existing recipe: {path}") from exc
    print(f"Wrote {path.resolve()}")
    return int(ExitCode.OK)


def _error(message: str) -> None:
    print(f"reprobrief: {message}", file=sys.stderr)
