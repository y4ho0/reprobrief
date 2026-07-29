from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from reprobrief.models import (
    CommandResult,
    GitSnapshot,
    StreamCapture,
)
from reprobrief.redaction import Redactor
from reprobrief.report import (
    build_manifest,
    git_delta,
    manifest_json,
    redact_result,
    render_markdown,
)


class ReportTests(unittest.TestCase):
    def result(self, stdout: str = "ok\n") -> CommandResult:
        return CommandResult(
            name="tests",
            argv=("tool", "test"),
            cwd=".",
            expected_exit_codes=(0,),
            exit_code=0,
            outcome="expected",
            duration_seconds=0.125,
            stdout=StreamCapture(stdout, len(stdout), len(stdout), False),
            stderr=StreamCapture("", 0, 0, False),
        )

    def test_git_delta(self) -> None:
        before = GitSnapshot(True, "a", "main", (" M old", "?? same"))
        after = GitSnapshot(True, "a", "main", (" M new", "?? same"))
        self.assertEqual(
            git_delta(before, after),
            {
                "appeared": [" M new"],
                "disappeared": [" M old"],
                "unchanged": ["?? same"],
            },
        )

    def test_manifest_and_markdown_share_canonical_data(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            redactor = Redactor(repo_root=root, home=None)
            before = GitSnapshot(True, "a" * 40, "main")
            after = GitSnapshot(True, "a" * 40, "main", ("?? created.txt",))
            manifest = build_manifest(
                facts={
                    "operating_system": "TestOS",
                    "operating_system_release": "1",
                    "architecture": "x",
                    "python": "3.11",
                    "python_implementation": "CPython",
                    "reprobrief": "0.1.0",
                },
                git_before=before,
                git_after=after,
                results=[self.result()],
                redactor=redactor,
                generated_at=datetime(2026, 7, 29, tzinfo=UTC),
            )
        self.assertEqual(manifest["generated_at"], "2026-07-29T00:00:00Z")
        self.assertTrue(manifest["summary"]["worktree_changed"])
        markdown = render_markdown(manifest)
        self.assertIn("`expected`", markdown)
        self.assertIn("`?? created.txt`", markdown)
        serialized = manifest_json(manifest)
        self.assertTrue(serialized.endswith("\n"))
        self.assertIn('"schema_version": 1', serialized)

    def test_result_redaction_covers_all_untrusted_strings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            token = "ghp_" + "Z" * 36
            redactor = Redactor(repo_root=root, home=None)
            result = self.result(stdout=token)
            result = CommandResult(
                **{
                    **result.__dict__,
                    "argv": ("tool", token),
                    "error": token,
                }
            )
            redacted = redact_result(result, redactor)
        self.assertNotIn(token, redacted.stdout.text)
        self.assertNotIn(token, redacted.argv)
        self.assertNotIn(token, redacted.error or "")

    def test_separate_secret_argument_is_masked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            redactor = Redactor(repo_root=Path(directory), home=None)
            result = self.result()
            result = CommandResult(
                **{
                    **result.__dict__,
                    "argv": ("tool", "--password", "ordinary-value", "safe"),
                }
            )
            redacted = redact_result(result, redactor)
        self.assertEqual(
            redacted.argv,
            ("tool", "--password", "<REDACTED:argv-secret>", "safe"),
        )
