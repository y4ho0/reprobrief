# Test Strategy

## Unit

- Recipe validation: schema, unknown fields, argv, cwd containment, ranges,
  duplicate names, expected exits, env names.
- Redaction: exact values, home/root paths, token shapes, credentials in URLs,
  email-like values, private keys, overlaps, Unicode, false-positive fixtures.
- Bounded capture: exact boundary, truncation flags, byte counts, invalid UTF-8.
- Git status normalization and delta.
- Manifest serialization and Markdown escaping.
- Error classification and CLI exit mapping.
- Archive member validation and deterministic inventory.

## Integration

- Real subprocess success, expected nonzero, unexpected nonzero, missing binary.
- Separate stdout/stderr, interleaving independence, empty output, large output.
- Timeout and interruption with child cleanup checks proportionate to platform.
- Minimized environment and explicit inherited names.
- Commands in a relative subdirectory.
- Real temporary Git repository: clean, dirty, untracked, mutation after command.
- Atomic output, existing target refusal, scoped `--force`, partial-write failure.
- ZIP generation and extraction to a fresh directory.

## End-to-end

1. Clean temp repository, `reprobrief init`, edit fixture recipe, approve, collect,
   inspect, archive, and verify manifest/report.
2. Reproduction command exits with the configured failure code and is treated as
   expected evidence.
3. Seeded token, home path, repo path, email, and oversized output are redacted/
   truncated and originals are absent from every generated file and ZIP member.

## Regression

- Every implementation defect gets the smallest stable regression fixture.
- Required initial regressions:
  - command produces more than pipe buffer capacity without deadlock
  - token split across input chunks is still redacted
  - output directory cannot escape through command name
  - Windows-style paths redact on non-Windows fixtures
  - archive contains no absolute or parent-traversal member

## Failure and boundary paths

- Empty/missing/invalid config
- Unsupported schema
- Permission denied
- Git absent/non-repository
- Timeout at minimum/maximum
- Ctrl-C
- Huge stdout and stderr simultaneously
- Invalid command bytes
- All commands fail
- Optional command fails
- Worktree mutation
- Residual privacy finding
- Output already exists
- Read-only output parent
- Unsupported Python

## Security and privacy

- Seed fake credentials from multiple providers; never use real secrets.
- Repository scan and generated-artifact scan with at least two tools or one tool
  plus independent pattern checks.
- Verify no network attempt during collection in an isolated test.
- Verify recipe never invokes a shell and cwd cannot leave the repository.
- Verify inherited environment contains only the baseline and declared names.
- Verify report language never says "safe to share."
- Inspect package, wheel, sdist/zipapp, ZIP, and Git history before release.

## Installation smoke

From clean virtual environments:

- Install wheel from local build.
- Install from GitHub release/tag after publication.
- `reprobrief --help`
- `reprobrief --version`
- zero-config successful collection
- configured successful collection
- configured error workflow with actionable output

## Platform matrix

- Ubuntu latest: Python 3.11 and 3.14
- macOS latest: Python 3.11 and 3.14
- Windows latest: Python 3.11 and 3.14
- Local macOS runtime: current Python 3.14

Version pins will be adjusted to versions actually available in GitHub Actions.

## Quality commands

To be frozen with the repository toolchain:

- format check
- static lint
- type check
- build
- unit/integration/E2E/regression tests
- installation smoke
- dependency audit
- secret scan
- documentation link and example checks
- Claim Gate
