"""Shared test helpers."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def run_git(path: Path, *args: str) -> str:
    env = dict(os.environ)
    env.update(
        {
            "GIT_AUTHOR_NAME": "ReproBrief Tests",
            "GIT_AUTHOR_EMAIL": "tests@example.invalid",
            "GIT_COMMITTER_NAME": "ReproBrief Tests",
            "GIT_COMMITTER_EMAIL": "tests@example.invalid",
        }
    )
    completed = subprocess.run(
        ["git", *args],
        cwd=path,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def make_git_repo(path: Path) -> str:
    run_git(path, "init", "-b", "main")
    (path / "tracked.txt").write_text("initial\n", encoding="utf-8")
    run_git(path, "add", "tracked.txt")
    run_git(path, "commit", "-m", "initial")
    return run_git(path, "rev-parse", "HEAD").strip()


def write_recipe(path: Path, commands: list[dict[str, object]]) -> Path:
    recipe = path / "reprobrief.json"
    recipe.write_text(
        json.dumps({"schema_version": 1, "commands": commands}, indent=2) + "\n",
        encoding="utf-8",
    )
    return recipe


def python_command(source: str) -> list[str]:
    return [sys.executable, "-c", source]
