from __future__ import annotations

import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

from reprobrief.models import CommandSpec
from reprobrief.runner import inherited_environment, resolved_argv, run_command


class RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def spec(self, source: str, **overrides: object) -> CommandSpec:
        values: dict[str, object] = {
            "name": "command",
            "argv": (sys.executable, "-c", source),
            "timeout_seconds": 5.0,
            "max_output_bytes": 4096,
        }
        values.update(overrides)
        return CommandSpec(**values)

    def test_success_captures_separate_streams(self) -> None:
        result, inherited = run_command(
            self.spec("import sys; print('out'); print('err', file=sys.stderr)"),
            self.root,
        )
        self.assertEqual(result.outcome, "expected")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout.text, f"out{os.linesep}")
        self.assertEqual(result.stderr.text, f"err{os.linesep}")
        self.assertEqual(inherited, {})

    def test_python_token_resolves_and_is_recorded(self) -> None:
        spec = CommandSpec(
            name="portable",
            argv=("{python}", "-c", "print('portable')"),
            max_output_bytes=1024,
        )
        self.assertEqual(resolved_argv(spec)[0], sys.executable)
        result, _ = run_command(spec, self.root)
        self.assertEqual(result.outcome, "expected")
        self.assertEqual(result.argv[0], sys.executable)
        self.assertEqual(result.stdout.text, f"portable{os.linesep}")

    def test_expected_nonzero_is_successful_outcome(self) -> None:
        result, _ = run_command(
            self.spec("raise SystemExit(7)", expected_exit_codes=(7,)),
            self.root,
        )
        self.assertEqual(result.outcome, "expected")
        self.assertEqual(result.exit_code, 7)

    def test_unexpected_exit_is_classified(self) -> None:
        result, _ = run_command(self.spec("raise SystemExit(9)"), self.root)
        self.assertEqual(result.outcome, "unexpected_exit")
        self.assertEqual(result.exit_code, 9)

    def test_missing_binary_is_a_result_not_a_crash(self) -> None:
        result, _ = run_command(
            CommandSpec(name="missing", argv=("definitely-not-a-real-binary",)),
            self.root,
        )
        self.assertEqual(result.outcome, "launch_error")
        self.assertIsNone(result.exit_code)
        self.assertIn("FileNotFoundError", result.error or "")

    def test_large_stdout_and_stderr_are_drained_but_bounded(self) -> None:
        size = 200_000
        result, _ = run_command(
            self.spec(
                "import sys; "
                f"sys.stdout.buffer.write(b'o'*{size}); "
                f"sys.stderr.buffer.write(b'e'*{size})",
                max_output_bytes=2048,
            ),
            self.root,
        )
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout.total_bytes, size)
        self.assertEqual(result.stderr.total_bytes, size)
        self.assertEqual(result.stdout.retained_bytes, 2048)
        self.assertEqual(result.stderr.retained_bytes, 2048)
        self.assertTrue(result.stdout.truncated)
        self.assertTrue(result.stderr.truncated)

    def test_invalid_utf8_is_replaced(self) -> None:
        result, _ = run_command(
            self.spec("import sys; sys.stdout.buffer.write(b'\\xffx')"),
            self.root,
        )
        self.assertEqual(result.stdout.text, "\ufffdx")

    def test_timeout_returns_promptly(self) -> None:
        started = time.monotonic()
        result, _ = run_command(
            self.spec("import time; time.sleep(30)", timeout_seconds=1.0),
            self.root,
        )
        self.assertTrue(result.timed_out)
        self.assertEqual(result.outcome, "timed_out")
        self.assertLess(time.monotonic() - started, 5)

    def test_only_declared_environment_is_inherited(self) -> None:
        old_secret = os.environ.get("REPROBRIEF_TEST_SECRET")
        os.environ["REPROBRIEF_TEST_SECRET"] = "declared-secret-value"  # noqa: E501  # pragma: allowlist secret
        try:
            spec = self.spec(
                "import os; print(os.environ.get('REPROBRIEF_TEST_SECRET')); "
                "print(os.environ.get('REPROBRIEF_UNDECLARED'))",
                inherit_env=("REPROBRIEF_TEST_SECRET",),
            )
            env, explicit = inherited_environment(spec)
            self.assertEqual(env["REPROBRIEF_TEST_SECRET"], "declared-secret-value")
            self.assertEqual(
                explicit,
                {"REPROBRIEF_TEST_SECRET": "declared-secret-value"},  # noqa: E501  # pragma: allowlist secret
            )
            self.assertNotIn("REPROBRIEF_UNDECLARED", env)
        finally:
            if old_secret is None:
                os.environ.pop("REPROBRIEF_TEST_SECRET", None)
            else:
                os.environ["REPROBRIEF_TEST_SECRET"] = old_secret

    @unittest.skipUnless(os.name == "posix", "POSIX process-group behavior")
    def test_timeout_kills_child_holding_output_pipe(self) -> None:
        source = (
            "import subprocess, sys, time; "
            "subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)']); "
            "time.sleep(30)"
        )
        started = time.monotonic()
        result, _ = run_command(
            self.spec(source, timeout_seconds=1.0),
            self.root,
        )
        self.assertTrue(result.timed_out)
        self.assertLess(time.monotonic() - started, 5)

    @unittest.skipUnless(os.name == "posix", "POSIX process-group behavior")
    def test_exited_parent_does_not_leave_pipe_holding_child(self) -> None:
        source = (
            "import subprocess, sys; "
            "subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])"
        )
        started = time.monotonic()
        result, _ = run_command(self.spec(source), self.root)
        self.assertEqual(result.outcome, "expected")
        self.assertLess(time.monotonic() - started, 4)
