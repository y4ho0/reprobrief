"""Collect a deliberately small set of non-identifying system and Git facts."""

from __future__ import annotations

import platform
import subprocess
from pathlib import Path
from typing import Any

from .models import GitSnapshot
from .version import __version__


def collect_system_facts() -> dict[str, Any]:
    """Return system facts without hostnames, usernames, IPs, or identifiers."""

    return {
        "operating_system": platform.system() or "unknown",
        "operating_system_release": platform.release() or "unknown",
        "architecture": platform.machine() or "unknown",
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "reprobrief": __version__,
    }


def collect_git_snapshot(repo_root: Path) -> GitSnapshot:
    """Collect revision and status without reading repository file contents."""

    if not _inside_worktree(repo_root):
        return GitSnapshot(
            available=False,
            head=None,
            branch=None,
            error="not a Git worktree",
        )
    try:
        head = _git(repo_root, "rev-parse", "HEAD").strip()
        branch = _git(repo_root, "branch", "--show-current").strip() or None
        status_text = _git(
            repo_root,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        )
        return GitSnapshot(
            available=True,
            head=head,
            branch=branch,
            status=tuple(status_text.splitlines()),
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return GitSnapshot(
            available=False,
            head=None,
            branch=None,
            error=f"Git inspection failed: {type(exc).__name__}",
        )


def _inside_worktree(repo_root: Path) -> bool:
    try:
        return _git(repo_root, "rev-parse", "--is-inside-work-tree").strip() == "true"
    except (OSError, subprocess.SubprocessError):
        return False


def _git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        check=True,
        timeout=10,
        env=_git_environment(),
    )
    return completed.stdout.decode("utf-8", errors="replace")


def _git_environment() -> dict[str, str]:
    import os

    env = {
        key: value
        for key, value in os.environ.items()
        if key
        in {
            "PATH",
            "SYSTEMROOT",
            "WINDIR",
            "COMSPEC",
            "PATHEXT",
            "TMP",
            "TEMP",
            "TMPDIR",
        }
    }
    env.update(
        {
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_TERMINAL_PROMPT": "0",
            "LC_ALL": "C",
        }
    )
    return env
