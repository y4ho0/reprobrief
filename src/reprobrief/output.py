"""Safely materialize reports and optional archives."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import zipfile
from collections.abc import Mapping
from pathlib import Path

from .errors import OutputError

_MARKER_FILE = "manifest.json"


def write_report_directory(
    target: Path,
    *,
    report_markdown: str,
    manifest_json: str,
    command_files: Mapping[str, str],
    force: bool,
) -> None:
    """Write a complete report using a sibling staging directory."""

    target = target.absolute()
    if target.is_symlink():
        raise OutputError(
            f"refusing to write through an output symbolic link: {target}"
        )
    target = target.resolve()
    parent = target.parent
    parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not force:
        raise OutputError(f"output already exists (use --force to replace): {target}")
    if target.exists() and not _is_owned_report(target):
        raise OutputError(
            "refusing to replace a directory not recognized as ReproBrief "
            f"output: {target}"
        )

    staging = Path(tempfile.mkdtemp(prefix=f".{target.name}.tmp-", dir=parent))
    backup: Path | None = None
    try:
        (staging / "commands").mkdir()
        _write_text(staging / "report.md", report_markdown)
        _write_text(staging / _MARKER_FILE, manifest_json)
        _write_text(
            staging / "README.md",
            "# ReproBrief output\n\n"
            "Review `report.md`, `manifest.json`, and every command output file "
            "before sharing. Best-effort redaction is not a privacy guarantee.\n",
        )
        for relative, content in command_files.items():
            destination = staging / relative
            if destination.parent != staging / "commands":
                raise OutputError(f"invalid command output path: {relative}")
            _write_text(destination, content)

        if target.exists():
            backup = Path(tempfile.mkdtemp(prefix=f".{target.name}.old-", dir=parent))
            backup.rmdir()
            os.replace(target, backup)
        os.replace(staging, target)
        if backup is not None:
            shutil.rmtree(backup)
    except Exception:
        if backup is not None and backup.exists() and not target.exists():
            os.replace(backup, target)
        if staging.exists():
            shutil.rmtree(staging)
        raise


def create_archive(report_dir: Path, destination: Path, *, force: bool) -> None:
    """Create a deterministic-member ZIP from generated regular files only."""

    report_dir = report_dir.absolute()
    if report_dir.is_symlink():
        raise OutputError(f"report directory must not be a symbolic link: {report_dir}")
    report_dir = report_dir.resolve()
    destination = destination.absolute()
    if destination.is_symlink():
        raise OutputError(
            f"refusing to replace an archive symbolic link: {destination}"
        )
    destination = destination.resolve()
    try:
        destination.relative_to(report_dir)
    except ValueError:
        pass
    else:
        raise OutputError("archive destination must be outside the report directory")
    if destination.exists() and not force:
        raise OutputError(
            f"archive already exists (use --force to replace): {destination}"
        )
    if destination.is_dir():
        raise OutputError(f"archive path is a directory: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.tmp-{os.getpid()}")
    try:
        with zipfile.ZipFile(
            temporary,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as archive:
            for path in sorted(report_dir.rglob("*")):
                if path.is_symlink():
                    raise OutputError(f"refusing to archive a symbolic link: {path}")
                if path.is_file():
                    relative = path.relative_to(report_dir)
                    archive.write(
                        path, arcname=f"{report_dir.name}/{relative.as_posix()}"
                    )
        os.replace(temporary, destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _is_owned_report(path: Path) -> bool:
    marker = path / _MARKER_FILE
    if not path.is_dir() or not marker.is_file() or marker.is_symlink():
        return False
    try:
        parsed = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False
    return (
        isinstance(parsed, dict)
        and parsed.get("schema_version") == 1
        and parsed.get("generator", {}).get("name") == "reprobrief"
    )


def _write_text(path: Path, content: str) -> None:
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        raise OutputError(f"could not write {path.name}: {exc}") from exc
