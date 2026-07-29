# Candidate Pool

Generated: 2026-07-29

Candidates begin with observed behavior or failure, not a product name.

| ID | Repeated behavior / problem | Candidate workflow | Objective first value | Principal risk |
|---|---|---|---|---|
| P-001 | Developers and AI agents run scattered checks, then report "done" without a durable record of revision, commands, exits, timeouts, or workspace side effects. | Run a small declared validation plan locally and emit a redacted, machine-readable evidence pack. | A reviewable pass/fail artifact tied to one Git revision and worktree state. | `make`, task runners, CI, and agent tools may be sufficient substitutes. |
| P-002 | CI fails while local checks pass, causing manual comparison of runner, environment, commands, and logs. | Convert an existing CI failure and workflow subset into a local reproduction manifest. | One locally runnable reproduction attempt with captured deltas. | Full CI emulation is platform-specific and already served by tools such as `act`. |
| P-003 | Bug reporters manually gather versions, commands, logs, and Git state and may accidentally include secrets. | Capture an allowlisted, previewable diagnostic capsule with deterministic redaction and provenance. | A shareable report directory whose contents are visible before export. | Redaction can create false confidence and support-bundle tools exist per ecosystem. |
| P-004 | Setup instructions drift; new contributors discover missing tools and versions only after a failed build. | Execute declarative onboarding checks in a clean temporary directory and report undocumented prerequisites. | A reproducible setup-freshness report. | Containers/devcontainers are strong substitutes and clean-room setup is expensive. |
| P-005 | README and documentation commands become stale and users discover errors by copy/paste. | Extract explicitly opted-in shell blocks and verify expected exits/output in isolated fixtures. | A failing document location with the real command result. | Many language-specific doctest and Markdown runners already exist. |
| P-006 | `.env.example`, code lookups, CI variables, and documentation disagree about required configuration. | Compare declared config keys across known project surfaces without reading secret values. | A missing/unused/undocumented configuration-key report. | Static extraction is language-specific and false positives can be noisy. |
| P-007 | Releases are announced before tag, revision, version, asset checksum, and installation path agree. | Verify a local/remote release evidence manifest and perform an install smoke test. | A deterministic list of inconsistent release claims. | Release automation platforms cover parts of the workflow. |
| P-008 | Teams rerun flaky tests manually and lose run-to-run timing, order, environment, and failure clusters. | Repeat a command under controlled seeds/order and persist a flakiness witness bundle. | A reproducible sequence showing pass/fail instability. | Framework-native rerun plugins are easier for many users. |
| P-009 | Dependency-update PRs require reading release notes, testing, and determining whether breakage is reachable. | Assemble version delta, changelog links, changed APIs, and local test evidence into one impact ledger. | A review packet for one dependency bump. | Ecosystem breadth and mature bots make scope difficult. |
| P-010 | Paths, executable names, line endings, shell syntax, and case sensitivity break only on another OS. | Scan changed files and project commands for portability hazards, then run portable fixtures. | Exact file/line warnings with bounded claims. | Static heuristics may be noisy; cross-platform CI is the stronger proof. |
| P-011 | Maintainers receive PRs—often AI-assisted—that omit problem links, tests, risk, and reproduction evidence. | Validate repository-defined contribution evidence requirements locally and in CI. | A concrete list of missing evidence, independent of authorship. | Templates and branch protection can cover simple cases. |
| P-012 | Agent sessions and developer handoffs lose the exact dirty state, decisions, commands, and remaining failures. | Export a local handoff capsule containing allowlisted Git state, decisions, and validation results. | Another developer can see what changed and what remains without reading chat history. | Agent vendors may absorb this, and source inclusion creates privacy risk. |
| P-013 | GitHub Actions workflows silently use floating third-party action tags or risky permissions. | Check workflow references, permissions, and trigger patterns against a small transparent ruleset. | A line-level hardening report. | `zizmor` and other mature workflow security linters are direct competitors. |
| P-014 | Local scripts and CI duplicate the same checks but drift in flags, versions, and order. | Compare CI command extraction with declared local validation commands. | A parity diff before the next CI failure. | YAML and shell interpretation is complex and platform-specific. |
| P-015 | Timeout and interrupt paths are rarely tested; child processes or temporary files survive cancellation. | Exercise a CLI command under timeout and signal scenarios while checking cleanup invariants. | A deterministic cleanup/exit-semantics report. | Narrow audience and OS-specific process behavior. |
| P-016 | Developers paste logs or diffs into issues, PRs, and prompts without checking for secrets or private paths. | Scan text on stdin locally, classify risky spans, and produce a redacted preview. | Immediate warning before a paste leaves the machine. | Mature secret scanners and browser prototypes overlap strongly. |
| P-017 | Maintainers repeatedly ask reporters for versions, reproduction steps, expected behavior, and minimal projects. | Turn repository issue requirements into a local interactive evidence checklist and bundle. | A complete issue body plus attached evidence index. | GitHub issue forms already collect structured fields. |
| P-018 | Published build artifacts cannot be reproduced from the source/tag, weakening supply-chain confidence. | Rebuild twice under a constrained recipe and report byte-level or normalized differences. | A reproducibility verdict plus diff summary. | Containers, Nix, and ecosystem reproducible-build projects are strong substitutes. |

## Initial non-goals shared by all candidates

- No model API as the sole core engine or correctness oracle.
- No claim to create a security sandbox.
- No automatic upload of source, logs, or diagnostics.
- No replacement for CI, human review, SAST, or secret rotation.
- No large hosted platform for the first release.
