"""Execute declared argv commands with bounded, concurrently drained output."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import BinaryIO, cast

from .config import resolve_command_cwd
from .models import CommandResult, CommandSpec, StreamCapture

_BASE_ENV_NAMES = {
    "PATH",
    "SYSTEMROOT",
    "WINDIR",
    "COMSPEC",
    "PATHEXT",
    "TMP",
    "TEMP",
    "TMPDIR",
    "LANG",
    "LC_ALL",
}
_WINDOWS_NEW_PROCESS_GROUP = 0x00000200


class _BoundedBytes:
    def __init__(self, limit: int) -> None:
        self.limit = limit
        self.data = bytearray()
        self.total = 0
        self._lock = threading.Lock()

    def add(self, chunk: bytes) -> None:
        with self._lock:
            self.total += len(chunk)
            remaining = self.limit - len(self.data)
            if remaining > 0:
                self.data.extend(chunk[:remaining])

    def capture(self) -> StreamCapture:
        raw = bytes(self.data)
        return StreamCapture(
            text=raw.decode("utf-8", errors="replace"),
            total_bytes=self.total,
            retained_bytes=len(raw),
            truncated=self.total > len(raw),
        )


def inherited_environment(spec: CommandSpec) -> tuple[dict[str, str], dict[str, str]]:
    """Build the minimal child environment and return explicit values to redact."""

    env = {key: value for key, value in os.environ.items() if key in _BASE_ENV_NAMES}
    explicit: dict[str, str] = {}
    for name in spec.inherit_env:
        value = os.environ.get(name)
        if value is not None:
            env[name] = value
            explicit[name] = value
    env.setdefault("LC_ALL", "C")
    return env, explicit


def run_command(
    spec: CommandSpec,
    repo_root: Path,
) -> tuple[CommandResult, dict[str, str]]:
    """Execute one command and return its result plus inherited values to redact."""

    command_cwd = resolve_command_cwd(repo_root, spec.cwd)
    env, explicit_values = inherited_environment(spec)
    stdout_buffer = _BoundedBytes(spec.max_output_bytes)
    stderr_buffer = _BoundedBytes(spec.max_output_bytes)
    started = time.monotonic()
    process: subprocess.Popen[bytes] | None = None

    try:
        process = subprocess.Popen(
            list(resolved_argv(spec)),
            cwd=command_cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            start_new_session=os.name == "posix",
            creationflags=_WINDOWS_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        )
    except (FileNotFoundError, PermissionError, OSError) as exc:
        duration = time.monotonic() - started
        empty = StreamCapture("", 0, 0, False)
        return (
            CommandResult(
                name=spec.name,
                argv=resolved_argv(spec),
                cwd=spec.cwd,
                expected_exit_codes=spec.expected_exit_codes,
                exit_code=None,
                outcome="launch_error",
                duration_seconds=duration,
                stdout=empty,
                stderr=empty,
                error=f"{type(exc).__name__}: {exc}",
            ),
            explicit_values,
        )

    stdout_stream = cast(BinaryIO, process.stdout)
    stderr_stream = cast(BinaryIO, process.stderr)
    readers = [
        threading.Thread(
            target=_drain,
            args=(stdout_stream, stdout_buffer),
            name=f"reprobrief-{spec.name}-stdout",
            daemon=True,
        ),
        threading.Thread(
            target=_drain,
            args=(stderr_stream, stderr_buffer),
            name=f"reprobrief-{spec.name}-stderr",
            daemon=True,
        ),
    ]
    for reader in readers:
        reader.start()

    timed_out = False
    interrupted = False
    try:
        process.wait(timeout=spec.timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        _terminate_process_tree(process)
    except KeyboardInterrupt:
        interrupted = True
        _terminate_process_tree(process)
    finally:
        join_deadline = time.monotonic() + 1
        for reader in readers:
            reader.join(timeout=max(0, join_deadline - time.monotonic()))
        if any(reader.is_alive() for reader in readers):
            _kill_process_tree(process)
            for reader in readers:
                reader.join(timeout=2)

    duration = time.monotonic() - started
    exit_code = process.poll()
    if interrupted:
        outcome = "cancelled"
    elif timed_out:
        outcome = "timed_out"
    elif exit_code in spec.expected_exit_codes:
        outcome = "expected"
    else:
        outcome = "unexpected_exit"

    result = CommandResult(
        name=spec.name,
        argv=resolved_argv(spec),
        cwd=spec.cwd,
        expected_exit_codes=spec.expected_exit_codes,
        exit_code=exit_code,
        outcome=outcome,
        duration_seconds=duration,
        stdout=stdout_buffer.capture(),
        stderr=stderr_buffer.capture(),
        timed_out=timed_out,
        error="execution interrupted" if interrupted else None,
    )
    if interrupted:
        raise KeyboardInterrupt
    return result, explicit_values


def resolved_argv(spec: CommandSpec) -> tuple[str, ...]:
    """Resolve the one portable executable token without invoking a shell."""

    if spec.argv and spec.argv[0] == "{python}":
        return (sys.executable, *spec.argv[1:])
    return spec.argv


def _drain(stream: BinaryIO, buffer: _BoundedBytes) -> None:
    try:
        while True:
            chunk = stream.read(65_536)
            if not chunk:
                return
            buffer.add(chunk)
    finally:
        stream.close()


def _terminate_process_tree(process: subprocess.Popen[bytes]) -> None:
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGTERM)
        elif process.poll() is None:
            process.terminate()
        if process.poll() is None:
            process.wait(timeout=1)
    except (ProcessLookupError, subprocess.TimeoutExpired, OSError):
        _kill_process_tree(process)


def _kill_process_tree(process: subprocess.Popen[bytes]) -> None:
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        elif process.poll() is None:
            process.kill()
        if process.poll() is None:
            process.wait(timeout=2)
    except (ProcessLookupError, subprocess.TimeoutExpired, OSError):
        pass
