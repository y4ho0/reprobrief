from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from reprobrief.redaction import Redactor


class RedactionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.home = self.root / "home"
        self.repo = self.home / "repo"
        self.repo.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_exact_paths_and_environment_values_are_redacted(self) -> None:
        redactor = Redactor(
            repo_root=self.repo,
            home=self.home,
            exact_values={"API_TOKEN": "tiny"},
        )
        text = f"{self.repo}/file {self.home}/other tiny"
        result = redactor.redact(text)
        self.assertNotIn(str(self.repo), result)
        self.assertNotIn(str(self.home), result)
        self.assertNotIn("tiny", result)
        self.assertIn("<REDACTED:repo-root>", result)
        self.assertEqual(redactor.summary.total, 3)

    def test_token_email_credentials_and_private_key_are_redacted(self) -> None:
        token = "ghp_" + "A" * 36
        key = "-----BEGIN PRIVATE KEY-----\nsecret material\n-----END PRIVATE KEY-----"  # noqa: E501  # pragma: allowlist secret
        text = (
            f"{token} person@example.com https://alice:password@example.com/path\n{key}"  # noqa: E501  # pragma: allowlist secret
        )
        redactor = Redactor(repo_root=self.repo, home=self.home)
        result = redactor.redact(text)
        for forbidden in (
            token,
            "person@example.com",
            "alice:password",
            "secret material",
        ):
            self.assertNotIn(forbidden, result)
        self.assertGreaterEqual(redactor.summary.total, 4)

    def test_named_secret_assignment_is_redacted(self) -> None:
        redactor = Redactor(repo_root=self.repo, home=self.home)
        result = redactor.redact("--password=ordinary-value token:other")
        self.assertNotIn("ordinary-value", result)
        self.assertNotIn("other", result)
        self.assertEqual(redactor.summary.replacements["named-secret"], 2)

    def test_benign_text_is_preserved(self) -> None:
        redactor = Redactor(repo_root=self.repo, home=self.home)
        text = "test failed at module.py:42 with status expected"
        self.assertEqual(redactor.redact(text), text)
        self.assertEqual(redactor.summary.total, 0)

    def test_residual_scan_is_separate_and_deterministic(self) -> None:
        redactor = Redactor(repo_root=self.repo, home=self.home)
        token = "AKIA" + "A" * 16
        self.assertEqual(redactor.scan_residual([token, token]), ["aws-access-key"])
