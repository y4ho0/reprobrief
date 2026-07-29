"""Render the local report and machine-readable manifest."""

from __future__ import annotations

import json
import shlex
from dataclasses import replace
from datetime import UTC, datetime
from typing import Any

from .models import CommandResult, GitSnapshot, json_ready
from .redaction import Redactor

REPORT_SCHEMA_VERSION = 1
_SENSITIVE_ARG_FLAGS = {
    "--api-key",
    "--api_key",
    "--access-token",
    "--access_token",
    "--auth-token",
    "--auth_token",
    "--client-secret",
    "--client_secret",
    "--password",
    "--passwd",
    "--pwd",
    "--secret",
    "--token",
}


def redact_result(result: CommandResult, redactor: Redactor) -> CommandResult:
    """Redact every string that can contain child-process or path data."""

    return replace(
        result,
        argv=redact_argv(result.argv, redactor),
        cwd=redactor.redact(result.cwd),
        stdout=replace(
            result.stdout,
            text=redactor.redact(result.stdout.text),
        ),
        stderr=replace(
            result.stderr,
            text=redactor.redact(result.stderr.text),
        ),
        error=redactor.redact(result.error) if result.error else None,
    )


def redact_argv(argv: tuple[str, ...], redactor: Redactor) -> tuple[str, ...]:
    """Redact an argument vector, including values after sensitive flags."""

    redacted: list[str] = []
    mask_next = False
    for arg in argv:
        if mask_next:
            redacted.append(redactor.mask("argv-secret"))
            mask_next = False
            continue
        redacted.append(redactor.redact(arg))
        if arg.lower() in _SENSITIVE_ARG_FLAGS:
            mask_next = True
    return tuple(redacted)


def redact_git(snapshot: GitSnapshot, redactor: Redactor) -> GitSnapshot:
    """Redact status paths and errors before serialization."""

    return replace(
        snapshot,
        branch=redactor.redact(snapshot.branch) if snapshot.branch else None,
        status=tuple(redactor.redact(line) for line in snapshot.status),
        error=redactor.redact(snapshot.error) if snapshot.error else None,
    )


def git_delta(before: GitSnapshot, after: GitSnapshot) -> dict[str, list[str]]:
    """Compute a deterministic set delta for porcelain status entries."""

    before_set = set(before.status)
    after_set = set(after.status)
    return {
        "appeared": sorted(after_set - before_set),
        "disappeared": sorted(before_set - after_set),
        "unchanged": sorted(before_set & after_set),
    }


def build_manifest(
    *,
    facts: dict[str, Any],
    git_before: GitSnapshot,
    git_after: GitSnapshot,
    results: list[CommandResult],
    redactor: Redactor,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """Construct the stable JSON manifest."""

    timestamp = generated_at or datetime.now(UTC)
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "generated_at": timestamp.isoformat().replace("+00:00", "Z"),
        "generator": {
            "name": "reprobrief",
            "version": facts["reprobrief"],
        },
        "privacy": {
            "notice": (
                "Best-effort redaction is not a guarantee. Review every file "
                "before sharing."
            ),
            "replacement_counts": dict(sorted(redactor.summary.replacements.items())),
            "residual_pattern_warnings": list(redactor.summary.residual_warnings),
        },
        "system": facts,
        "git": {
            "before": json_ready(git_before),
            "after": json_ready(git_after),
            "worktree_delta": git_delta(git_before, git_after),
        },
        "commands": [json_ready(result) for result in results],
        "summary": {
            "commands_total": len(results),
            "commands_expected": sum(
                result.outcome == "expected" for result in results
            ),
            "commands_unexpected": sum(
                result.outcome != "expected" for result in results
            ),
            "worktree_changed": git_before.status != git_after.status,
        },
    }


def render_markdown(manifest: dict[str, Any]) -> str:
    """Render a readable report from the canonical manifest."""

    system = manifest["system"]
    git = manifest["git"]
    summary = manifest["summary"]
    lines = [
        "# Reproduction Brief",
        "",
        "> Review every generated file before sharing. Redaction is best-effort,",
        "> not a guarantee that the brief contains no sensitive information.",
        "",
        "## Summary",
        "",
        f"- Generated: `{_inline(manifest['generated_at'])}`",
        f"- Revision: `{_inline(git['before'].get('head') or 'unavailable')}`",
        f"- Commands: {summary['commands_total']}",
        f"- Expected outcomes: {summary['commands_expected']}",
        f"- Unexpected outcomes: {summary['commands_unexpected']}",
        f"- Worktree changed during run: `{str(summary['worktree_changed']).lower()}`",
        "",
        "## Environment",
        "",
        f"- Operating system: `{_inline(system['operating_system'])}`",
        f"- OS release: `{_inline(system['operating_system_release'])}`",
        f"- Architecture: `{_inline(system['architecture'])}`",
        f"- Python: `{_inline(system['python'])}`",
        f"- ReproBrief: `{_inline(system['reprobrief'])}`",
        "",
        "## Git",
        "",
        f"- Available: `{str(git['before']['available']).lower()}`",
        f"- Branch: `{_inline(git['before'].get('branch') or 'unavailable')}`",
        f"- HEAD before: `{_inline(git['before'].get('head') or 'unavailable')}`",
        f"- HEAD after: `{_inline(git['after'].get('head') or 'unavailable')}`",
        "",
        "### Worktree delta",
        "",
    ]
    delta = git["worktree_delta"]
    if not delta["appeared"] and not delta["disappeared"]:
        lines.append("No status-entry changes detected.")
    else:
        for label in ("appeared", "disappeared"):
            lines.append(f"**{label.title()}**")
            lines.append("")
            entries = delta[label]
            if entries:
                lines.extend(f"- `{_inline(entry)}`" for entry in entries)
            else:
                lines.append("- None")
            lines.append("")

    lines.extend(["## Commands", ""])
    if not manifest["commands"]:
        lines.extend(
            [
                "No commands were configured. This brief contains only conservative",
                "system and Git facts.",
                "",
            ]
        )
    for command in manifest["commands"]:
        argv = " ".join(shlex.quote(arg) for arg in command["argv"])
        lines.extend(
            [
                f"### {command['name']}",
                "",
                f"- Command: `{_inline(argv)}`",
                f"- Working directory: `{_inline(command['cwd'])}`",
                f"- Outcome: `{command['outcome']}`",
                f"- Exit code: `{command['exit_code']}`",
                f"- Duration: `{command['duration_seconds']:.3f}s`",
                (
                    f"- stdout: {command['stdout']['retained_bytes']} retained / "
                    f"{command['stdout']['total_bytes']} total bytes"
                ),
                (
                    f"- stderr: {command['stderr']['retained_bytes']} retained / "
                    f"{command['stderr']['total_bytes']} total bytes"
                ),
                (
                    f"- Captured files: `commands/{command['name']}.stdout.txt`, "
                    f"`commands/{command['name']}.stderr.txt`"
                ),
                "",
            ]
        )

    privacy = manifest["privacy"]
    lines.extend(["## Privacy review", ""])
    counts = privacy["replacement_counts"]
    if counts:
        lines.append("Redactions applied:")
        lines.append("")
        lines.extend(f"- `{label}`: {count}" for label, count in counts.items())
    else:
        lines.append("No known values or high-confidence token patterns were redacted.")
    lines.extend(["", privacy["notice"], ""])
    if privacy["residual_pattern_warnings"]:
        lines.extend(
            [
                "**Do not share yet:** residual secret-like patterns were detected:",
                "",
                *[f"- `{label}`" for label in privacy["residual_pattern_warnings"]],
                "",
            ]
        )
    return "\n".join(lines)


def manifest_json(manifest: dict[str, Any]) -> str:
    return json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _inline(value: object) -> str:
    return str(value).replace("`", r"\`").replace("\n", " ")
