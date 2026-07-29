from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from reprobrief.facts import collect_git_snapshot, collect_system_facts
from tests.helpers import make_git_repo


class FactsTests(unittest.TestCase):
    def test_system_facts_omit_direct_identifiers(self) -> None:
        facts = collect_system_facts()
        self.assertEqual(
            set(facts),
            {
                "operating_system",
                "operating_system_release",
                "architecture",
                "python",
                "python_implementation",
                "reprobrief",
            },
        )

    def test_non_repository_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot = collect_git_snapshot(Path(directory))
        self.assertFalse(snapshot.available)
        self.assertEqual(snapshot.error, "not a Git worktree")

    def test_real_repository_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            head = make_git_repo(root)
            (root / "tracked.txt").write_text("changed\n", encoding="utf-8")
            (root / "untracked.txt").write_text("new\n", encoding="utf-8")
            snapshot = collect_git_snapshot(root)
        self.assertTrue(snapshot.available)
        self.assertEqual(snapshot.head, head)
        self.assertEqual(snapshot.branch, "main")
        self.assertIn(" M tracked.txt", snapshot.status)
        self.assertIn("?? untracked.txt", snapshot.status)
