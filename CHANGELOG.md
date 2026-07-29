# Changelog

All notable changes are documented here.

## [Unreleased]

### Documentation

- Added a complete Simplified Chinese README, security policy, and privacy/threat
  model with language navigation and documentation-contract coverage.
- Reorganized both READMEs around the reader's problem, visible result, shortest
  first-value workflow, suitable use cases, and action-adjacent safety guidance.

## [0.1.0] - 2026-07-29

### Added

- Schema-versioned JSON recipes with strict validation and no shell execution.
- Explicit pre-run inspection and approval.
- Conservative system/Git facts and before/after worktree status.
- Real subprocess execution with timeouts, process-group cleanup, continuously
  drained bounded stdout/stderr, and stable outcome classification.
- Best-effort redaction for exact paths, explicitly inherited values, and tested
  high-confidence secret-like patterns.
- Atomic local report directories, JSON and Markdown output, and optional ZIP.
- Cross-platform CI, unit/integration/end-to-end/adversarial tests, and three
  runnable demonstrations.

[0.1.0]: https://github.com/y4ho0/reprobrief/releases/tag/v0.1.0
