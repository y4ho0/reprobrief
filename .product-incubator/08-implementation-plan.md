# Implementation Plan

## Vertical slice

```text
temporary Git repository
→ one JSON command recipe
→ explicit approval
→ real subprocess execution
→ exact exit/stdout/stderr + Git before/after
→ redacted report.md and manifest.json
→ automated E2E assertion
→ installed `reprobrief` entry point
```

## Milestones

1. Package, version, CLI help/version, recipe parser, data model.
2. Minimal system/Git facts and one successful command.
3. Report/manifest renderer and atomic output directory.
4. Timeout, nonzero, missing command, output truncation, and worktree mutation.
5. Redaction, residual privacy gate, inspect, and explicit ZIP.
6. Unit/integration/E2E/regression suite and three demos.
7. Documentation, packaging, clean install smoke test.
8. Security/privacy audit, Claim Gate, Push Gate, GitHub CI and release.

## Change loop

For each behavior:

```text
specify observable behavior
→ add or update test
→ implement smallest change
→ run targeted test
→ inspect real output
→ run related integration tests
→ record defects and regression coverage
```

## Rollback

- No existing repository or remote is modified during implementation.
- Local changes remain uncommitted until quality gates pass.
- ReproBrief never cleans or reverts user-command side effects.
- Failed output staging directories are scoped to the exact requested parent.
- GitHub creation and push occur only after publication preflight.

## Principal implementation risks

- Draining large stdout/stderr without unbounded memory or deadlock.
- Terminating subprocesses consistently on three operating systems.
- Preventing machine roots or seeded secrets from reaching disk.
- Atomic output without unsafe overwrite behavior.
- Keeping the configuration small enough for adoption.
