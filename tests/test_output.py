from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from reprobrief.errors import OutputError
from reprobrief.output import create_archive, write_report_directory


def marker() -> str:
    return json.dumps(
        {
            "schema_version": 1,
            "generator": {"name": "reprobrief", "version": "0.1.0"},
        }
    )


class OutputTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.target = self.root / "output"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write(self, *, force: bool = False, report: str = "report") -> None:
        write_report_directory(
            self.target,
            report_markdown=report,
            manifest_json=marker(),
            command_files={
                "commands/test.stdout.txt": "out",
                "commands/test.stderr.txt": "err",
            },
            force=force,
        )

    def test_complete_directory_is_written(self) -> None:
        self.write()
        self.assertEqual((self.target / "report.md").read_text(), "report")
        self.assertEqual(
            (self.target / "commands/test.stdout.txt").read_text(),
            "out",
        )

    def test_existing_output_requires_force(self) -> None:
        self.write()
        with self.assertRaisesRegex(OutputError, "already exists"):
            self.write(report="new")
        self.assertEqual((self.target / "report.md").read_text(), "report")

    def test_force_only_replaces_owned_output(self) -> None:
        self.target.mkdir()
        (self.target / "user.txt").write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(OutputError, "not recognized"):
            self.write(force=True)
        self.assertEqual((self.target / "user.txt").read_text(), "keep")

    def test_force_replaces_owned_output(self) -> None:
        self.write()
        self.write(force=True, report="replacement")
        self.assertEqual((self.target / "report.md").read_text(), "replacement")

    def test_output_symlink_is_rejected(self) -> None:
        real = self.root / "real"
        real.mkdir()
        try:
            self.target.symlink_to(real, target_is_directory=True)
        except OSError:
            self.skipTest("symbolic links unavailable")
        with self.assertRaisesRegex(OutputError, "symbolic link"):
            self.write(force=True)

    def test_archive_has_only_relative_generated_members(self) -> None:
        self.write()
        archive = self.root / "brief.zip"
        create_archive(self.target, archive, force=False)
        with zipfile.ZipFile(archive) as opened:
            names = opened.namelist()
        self.assertIn("output/report.md", names)
        self.assertTrue(
            all(not name.startswith("/") and ".." not in name for name in names)
        )

    def test_archive_inside_report_is_rejected(self) -> None:
        self.write()
        with self.assertRaisesRegex(OutputError, "outside"):
            create_archive(
                self.target,
                self.target / "bad.zip",
                force=False,
            )
