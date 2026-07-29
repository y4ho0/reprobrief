from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import reprobrief
from reprobrief.config import load_recipe

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class DocumentationContractTests(unittest.TestCase):
    def test_all_demo_recipes_are_valid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            for example in sorted((PROJECT_ROOT / "examples/demos").glob("*.json")):
                with self.subTest(example=example.name):
                    recipe = load_recipe(example, repo)
                    self.assertGreater(len(recipe.commands), 0)

    def test_json_schema_and_evidence_json_are_parseable(self) -> None:
        paths = [
            PROJECT_ROOT / "docs/reprobrief.schema.json",
            *(PROJECT_ROOT / ".product-incubator").glob("*.json"),
        ]
        for path in paths:
            with self.subTest(path=path.name):
                json.loads(path.read_text(encoding="utf-8"))

    def test_version_is_consistent(self) -> None:
        pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn(f'version = "{reprobrief.__version__}"', pyproject)
        self.assertIn(f"## [{reprobrief.__version__}]", changelog)

    def test_readme_commands_and_boundaries_are_present(self) -> None:
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        for required in (
            "reprobrief inspect",
            "reprobrief run",
            "--yes",
            "does **not** sandbox",
            "best-effort",
            "v0.1.0",
        ):
            with self.subTest(required=required):
                self.assertIn(required, readme)

    def test_simplified_chinese_docs_match_release_contract(self) -> None:
        readme = (PROJECT_ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        security = (PROJECT_ROOT / "SECURITY.zh-CN.md").read_text(encoding="utf-8")
        privacy = (PROJECT_ROOT / "docs/privacy.zh-CN.md").read_text(encoding="utf-8")

        for required in (
            "reprobrief inspect",
            "reprobrief run",
            "--yes",
            "v0.1.0",
            "不会对命令进行沙箱隔离",
            "尽力而为",
        ):
            with self.subTest(document="README.zh-CN.md", required=required):
                self.assertIn(required, readme)

        self.assertIn("手动检查每个文件", security)
        self.assertIn("不会发起网络请求", privacy)
        self.assertIn(
            "[简体中文](README.zh-CN.md)",
            (PROJECT_ROOT / "README.md").read_text(encoding="utf-8"),
        )
        self.assertIn("[English](README.md)", readme)
        self.assertIn(
            "[简体中文](SECURITY.zh-CN.md)",
            (PROJECT_ROOT / "SECURITY.md").read_text(encoding="utf-8"),
        )
        self.assertIn("[English](SECURITY.md)", security)
        self.assertIn(
            "[简体中文](privacy.zh-CN.md)",
            (PROJECT_ROOT / "docs/privacy.md").read_text(encoding="utf-8"),
        )
        self.assertIn("[English](privacy.md)", privacy)

    def test_github_actions_are_pinned_to_commits(self) -> None:

        for workflow in (PROJECT_ROOT / ".github/workflows").glob("*.yml"):
            for line in workflow.read_text(encoding="utf-8").splitlines():
                if "uses:" not in line:
                    continue
                with self.subTest(workflow=workflow.name, line=line):
                    self.assertRegex(line, r"uses: [^@\s]+@[0-9a-f]{40}(?:\s+#.*)?$")
