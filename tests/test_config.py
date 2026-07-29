from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from reprobrief.config import load_recipe, parse_recipe, resolve_command_cwd
from reprobrief.errors import RecipeError


class ConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_valid_recipe_is_normalized(self) -> None:
        raw = {
            "schema_version": 1,
            "commands": [
                {
                    "name": "unit",
                    "argv": ["python", "-m", "unittest"],
                    "expected_exit_codes": [0, 1, 1],
                    "inherit_env": ["EXAMPLE", "EXAMPLE"],
                }
            ],
        }
        recipe = parse_recipe(raw, self.root)
        self.assertEqual(recipe.commands[0].expected_exit_codes, (0, 1))
        self.assertEqual(recipe.commands[0].inherit_env, ("EXAMPLE",))
        self.assertEqual(recipe.commands[0].max_output_bytes, 65_536)

    def test_load_reports_json_location(self) -> None:
        path = self.root / "bad.json"
        path.write_text('{"schema_version":', encoding="utf-8")
        with self.assertRaisesRegex(RecipeError, r"line 1, column"):
            load_recipe(path, self.root)

    def test_unknown_fields_are_rejected(self) -> None:
        with self.assertRaisesRegex(RecipeError, "unknown recipe"):
            parse_recipe(
                {"schema_version": 1, "commands": [], "surprise": True},
                self.root,
            )
        with self.assertRaisesRegex(RecipeError, "unknown field"):
            parse_recipe(
                {
                    "schema_version": 1,
                    "commands": [{"name": "x", "argv": ["true"], "shell": True}],
                },
                self.root,
            )

    def test_invalid_boundaries_are_rejected(self) -> None:
        base = {"name": "x", "argv": ["true"]}
        mutations = [
            {"name": "../x"},
            {"argv": []},
            {"timeout_seconds": 0},
            {"timeout_seconds": 301},
            {"max_output_bytes": 1023},
            {"max_output_bytes": 1_048_577},
            {"expected_exit_codes": []},
            {"inherit_env": ["BAD-NAME"]},
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaises(RecipeError):
                parse_recipe(
                    {
                        "schema_version": 1,
                        "commands": [{**base, **mutation}],
                    },
                    self.root,
                )

    def test_environment_names_cannot_collide_by_case(self) -> None:
        with self.assertRaisesRegex(RecipeError, "case-insensitive duplicate"):
            parse_recipe(
                {
                    "schema_version": 1,
                    "commands": [
                        {
                            "name": "x",
                            "argv": ["true"],
                            "inherit_env": ["EXAMPLE", "example"],
                        }
                    ],
                },
                self.root,
            )

    def test_duplicate_names_are_rejected(self) -> None:
        with self.assertRaisesRegex(RecipeError, "duplicate command"):
            parse_recipe(
                {
                    "schema_version": 1,
                    "commands": [
                        {"name": "same", "argv": ["a"]},
                        {"name": "same", "argv": ["b"]},
                    ],
                },
                self.root,
            )
        with self.assertRaisesRegex(RecipeError, "duplicate command"):
            parse_recipe(
                {
                    "schema_version": 1,
                    "commands": [
                        {"name": "Same", "argv": ["a"]},
                        {"name": "same", "argv": ["b"]},
                    ],
                },
                self.root,
            )

    def test_command_names_are_portable_filenames(self) -> None:
        for name in ("CON", "nul.txt", "x."):
            with (
                self.subTest(name=name),
                self.assertRaisesRegex(RecipeError, "portable filename"),
            ):
                parse_recipe(
                    {
                        "schema_version": 1,
                        "commands": [{"name": name, "argv": ["true"]}],
                    },
                    self.root,
                )

    def test_python_token_is_only_valid_as_program(self) -> None:
        recipe = parse_recipe(
            {
                "schema_version": 1,
                "commands": [{"name": "x", "argv": ["{python}", "--version"]}],
            },
            self.root,
        )
        self.assertEqual(recipe.commands[0].argv[0], "{python}")
        with self.assertRaisesRegex(RecipeError, "only as its program"):
            parse_recipe(
                {
                    "schema_version": 1,
                    "commands": [{"name": "x", "argv": ["echo", "{python}"]}],
                },
                self.root,
            )

    def test_cwd_cannot_escape_lexically(self) -> None:
        with self.assertRaisesRegex(RecipeError, "escapes"):
            resolve_command_cwd(self.root, "../outside")

    def test_cwd_cannot_escape_through_symlink(self) -> None:
        outside = self.root.parent
        link = self.root / "outside"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("symbolic links unavailable")
        with self.assertRaisesRegex(RecipeError, "escapes"):
            parse_recipe(
                {
                    "schema_version": 1,
                    "commands": [
                        {"name": "escape", "argv": ["true"], "cwd": "outside"}
                    ],
                },
                self.root,
            )

    def test_missing_recipe_is_clear(self) -> None:
        with self.assertRaisesRegex(RecipeError, "does not exist"):
            load_recipe(self.root / "missing.json", self.root)

    def test_recipe_size_is_bounded(self) -> None:
        path = self.root / "huge.json"
        path.write_bytes(b" " * 1_048_577)
        with self.assertRaisesRegex(RecipeError, "larger than 1 MiB"):
            load_recipe(path, self.root)

    def test_recipe_directory_is_reported_as_input_error(self) -> None:
        with self.assertRaisesRegex(RecipeError, "cannot be read"):
            load_recipe(self.root, self.root)

    def test_recipe_source_is_absolute(self) -> None:
        path = self.root / "recipe.json"
        path.write_text(
            json.dumps({"schema_version": 1, "commands": []}),
            encoding="utf-8",
        )
        self.assertEqual(load_recipe(path, self.root).source, path.resolve())
