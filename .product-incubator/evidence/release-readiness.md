# Release-readiness evidence

Date: 2026-07-29
Source revision: `70afe4a646cba03792a1a4e41a37d7f0099c635d`
Local environment: macOS 26.0 arm64, CPython 3.14.0

This file records bounded local evidence. It does not substitute for remote
platform CI, a GitHub tag/Release, or external-user validation.

## Static and test gates

- Ruff 0.16.0 `check`: passed.
- Ruff 0.16.0 `format --check`: passed.
- mypy 2.3.0 strict mode: passed for 12 source modules.
- `unittest`: 57 tests passed, zero failures, zero skips on macOS.
- coverage.py 7.15.2 with branch measurement: 87% aggregate; configured floor 85%.
- `compileall`: passed for source and tests.
- Git diff whitespace check: passed.

The suite includes unit, real subprocess, temporary Git repository,
end-to-end, regression, adversarial, documentation-contract, installation,
timeout, dual-stream large-output, symbolic-link, traversal, privacy, and real
POSIX interruption cases.

## Runtime and end-to-end

Fresh environments exercised:

- installation from a locally built wheel;
- installation from a locally built source distribution;
- `reprobrief --version` and `python -m reprobrief --version`;
- a successful recipe and ZIP archive;
- an unexpected exit recorded as exit 7 while the CLI correctly returned 4;
- a worktree mutation that appeared in the before/after delta;
- an explicitly inherited test value that was absent from all generated files;
- SIGINT returning 130, terminating the tested child, and writing no partial report.

These executions prove local behavior. The three-OS claim additionally passed
the GitHub Actions matrix at the named source revision.

## Security and privacy

- Bandit 1.9.4: zero medium/high findings, five low/high-confidence notices.
  The notices are the intentional `subprocess` imports/calls and PATH lookup for
  Git/approved recipe programs. All use argument arrays; recipe execution uses
  `shell=False`. No finding was suppressed with `# nosec`.
- detect-secrets 1.5.0 with all plugins: zero findings across tracked files.
  Deliberately fake redaction fixtures have narrow inline allowlist comments.
- Manual tracked-file scan: no local user paths, authenticated user ID, private
  email, temporary gate path, known token-shaped value, or file over 1 MiB.
- Manual data-flow review: no client networking, telemetry, arbitrary-file
  collector, `.env` reader, source collector, or upload path exists.
- GitHub Actions are pinned to full 40-character commits and checkout credentials
  are not persisted.
- Apache-2.0 is present. There are no bundled third-party runtime libraries or
  third-party license files to reconcile.

Residual boundary: the recipe and its child programs are trusted inputs.
ReproBrief is not a sandbox and best-effort redaction is not a privacy guarantee.

## Dependency and package audit

- `pyproject.toml` declares `dependencies = []`.
- Built wheel METADATA contained no `Requires-Dist` field.
- pip-audit 2.10.1 reported: `No known vulnerabilities found` for
  `requirements-runtime.txt`, the empty runtime dependency set.
- build 1.5.0 created wheel and source distribution from a Git archive.
- twine 7.0.0 accepted both package metadata records.
- Wheel inventory contained 18 safe relative members; sdist inventory contained
  35 safe relative non-link members.

Local artifacts are provisional until rebuilt from the final release revision;
their final SHA-256 values are therefore recorded in the GitHub Release, not
frozen here.

## Open gates

- Branch protection/ruleset, immutable tag, Release, final asset checksums, and
  install from the GitHub tag/release channel.
- External-user value remains unverified and belongs to the adoption sprint.
