from __future__ import annotations

import contextlib
import io
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import zipfile
from contextlib import suppress
from pathlib import Path
from unittest import mock

from reprobrief.cli import main
from reprobrief.errors import ExitCode
from tests.helpers import make_git_repo, python_command, write_recipe

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.head = make_git_repo(self.root)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_inspect_does_not_execute(self) -> None:
        created = self.root / "should-not-exist"
        write_recipe(
            self.root,
            [
                {
                    "name": "mutation",
                    "argv": python_command(
                        f"from pathlib import Path; Path({str(created)!r}).touch()"
                    ),
                }
            ],
        )
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(["inspect", "--repo", str(self.root)])
        self.assertEqual(code, ExitCode.OK)
        self.assertIn("nothing was executed", stdout.getvalue())
        self.assertFalse(created.exists())

    def test_inspect_masks_sensitive_arguments_and_inherited_values(self) -> None:
        old = os.environ.get("REPROBRIEF_PREVIEW_VALUE")
        os.environ["REPROBRIEF_PREVIEW_VALUE"] = "preview-private-value"
        try:
            write_recipe(
                self.root,
                [
                    {
                        "name": "private",
                        "argv": [
                            "tool",
                            "--password",
                            "ordinary-password",
                            "preview-private-value",
                        ],
                        "inherit_env": ["REPROBRIEF_PREVIEW_VALUE"],
                    }
                ],
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(["inspect", "--repo", str(self.root), "--json"])
        finally:
            if old is None:
                os.environ.pop("REPROBRIEF_PREVIEW_VALUE", None)
            else:
                os.environ["REPROBRIEF_PREVIEW_VALUE"] = old
        preview = stdout.getvalue()
        self.assertEqual(code, ExitCode.OK)
        self.assertNotIn("ordinary-password", preview)
        self.assertNotIn("preview-private-value", preview)
        self.assertIn("<REDACTED:argv-secret>", preview)
        self.assertIn("<REDACTED:env:REPROBRIEF_PREVIEW_VALUE>", preview)

    def test_end_to_end_success_redacts_and_detects_mutation(self) -> None:
        token = "ghp_" + "A" * 36
        old = os.environ.get("REPROBRIEF_E2E_TOKEN")
        os.environ["REPROBRIEF_E2E_TOKEN"] = token
        try:
            write_recipe(
                self.root,
                [
                    {
                        "name": "reproduce",
                        "argv": python_command(
                            "import os, pathlib, sys; "
                            "print('visible stdout'); "
                            "print(os.environ['REPROBRIEF_E2E_TOKEN']); "
                            "print('visible stderr', file=sys.stderr); "
                            "pathlib.Path('created.txt').write_text('changed')"
                        ),
                        "inherit_env": ["REPROBRIEF_E2E_TOKEN"],
                        "max_output_bytes": 4096,
                    }
                ],
            )
            output = self.root / "brief"
            archive = self.root / "brief.zip"
            code = main(
                [
                    "run",
                    "--repo",
                    str(self.root),
                    "--output",
                    str(output),
                    "--yes",
                    "--archive",
                    str(archive),
                ]
            )
        finally:
            if old is None:
                os.environ.pop("REPROBRIEF_E2E_TOKEN", None)
            else:
                os.environ["REPROBRIEF_E2E_TOKEN"] = old
        self.assertEqual(code, ExitCode.OK)
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual(manifest["git"]["before"]["head"], self.head)
        self.assertTrue(manifest["summary"]["worktree_changed"])
        self.assertEqual(manifest["commands"][0]["outcome"], "expected")
        all_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in output.rglob("*")
            if path.is_file()
        )
        self.assertNotIn(token, all_text)
        self.assertIn("<REDACTED:env:REPROBRIEF_E2E_TOKEN>", all_text)
        self.assertIn("visible stdout", all_text)
        with zipfile.ZipFile(archive) as opened:
            self.assertIn("brief/report.md", opened.namelist())

    def test_unexpected_exit_writes_report_and_returns_failure(self) -> None:
        write_recipe(
            self.root,
            [{"name": "fails", "argv": python_command("raise SystemExit(12)")}],
        )
        output = self.root / "brief"
        code = main(
            [
                "run",
                "--repo",
                str(self.root),
                "--output",
                str(output),
                "--yes",
            ]
        )
        self.assertEqual(code, ExitCode.EXECUTION_FAILED)
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual(manifest["commands"][0]["exit_code"], 12)

    def test_no_config_collects_facts_only(self) -> None:
        output = self.root / "facts"
        code = main(["run", "--repo", str(self.root), "--output", str(output)])
        self.assertEqual(code, ExitCode.OK)
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual(manifest["summary"]["commands_total"], 0)

    def test_noninteractive_commands_require_yes(self) -> None:
        write_recipe(
            self.root,
            [{"name": "ok", "argv": python_command("print('ok')")}],
        )
        with mock.patch.object(sys.stdin, "isatty", return_value=False):
            code = main(["run", "--repo", str(self.root)])
        self.assertEqual(code, ExitCode.USAGE)
        self.assertFalse((self.root / "reprobrief-output").exists())

    def test_init_never_overwrites(self) -> None:
        path = self.root / "new-recipe.json"
        self.assertEqual(main(["init", str(path)]), ExitCode.OK)
        original = path.read_text()
        self.assertEqual(main(["init", str(path)]), ExitCode.OUTPUT_ERROR)
        self.assertEqual(path.read_text(), original)

    @unittest.skipUnless(os.name == "posix", "POSIX signal and process-group behavior")
    def test_real_interrupt_cleans_up_and_writes_no_partial_report(self) -> None:
        child_pid_file = self.root / "child.pid"
        output = self.root / "interrupted-brief"
        write_recipe(
            self.root,
            [
                {
                    "name": "wait",
                    "argv": python_command(
                        "import os, time; from pathlib import Path; "
                        f"Path({str(child_pid_file)!r}).write_text(str(os.getpid())); "
                        "time.sleep(30)"
                    ),
                    "timeout_seconds": 30,
                }
            ],
        )
        env = dict(os.environ)
        env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "reprobrief",
                "run",
                "--repo",
                str(self.root),
                "--output",
                str(output),
                "--yes",
            ],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        child_pid: int | None = None
        try:
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                if child_pid_file.exists():
                    child_pid = int(child_pid_file.read_text(encoding="utf-8"))
                    break
                self.assertIsNone(process.poll(), "CLI exited before child started")
                time.sleep(0.02)
            self.assertIsNotNone(child_pid, "child command did not start")
            process.send_signal(signal.SIGINT)
            _, stderr = process.communicate(timeout=8)
            self.assertEqual(process.returncode, ExitCode.CANCELLED, stderr)
            self.assertIn("cancelled", stderr)
            self.assertFalse(output.exists())
            assert child_pid is not None
            with self.assertRaises(ProcessLookupError):
                os.kill(child_pid, 0)
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate(timeout=3)
            if child_pid is not None:
                with suppress(ProcessLookupError):
                    os.kill(child_pid, signal.SIGKILL)
