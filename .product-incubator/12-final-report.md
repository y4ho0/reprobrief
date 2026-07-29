# Final Report

Primary status: PARTIAL

Reason: the local product and local gates are complete, but GitHub publication,
remote platform CI, branch protection, `v0.1.0` Release, asset verification, and
install-from-GitHub evidence are still open. External adoption is explicitly a
post-release validation phase and is not required to misstate this initial
technical release as adopted.

## 1. Executive outcome

ReproBrief is a working local-first CLI, not a prototype screen or model wrapper.
It turns a reviewed repository recipe into a local reproduction brief containing
the resolved command, exact Git revision, expected/observed exit, bounded
stdout/stderr, conservative system facts, and worktree status before/after.

## 2. Product and target user

Initial maintainer: an open-source CLI/developer-tool maintainer who repeatedly
asks issue reporters for exact revision, environment, command, exit, output, and
workspace context.

Initial reporter: a contributor/user who can run one reviewed local command and
inspect a generated directory before sharing it.

Positioning: a repository-neutral evidence handoff contract with explicit
execution bounds and privacy warnings—not a generic environment dump, support
upload service, sandbox, or automated diagnosis engine.

## 3. Research scope and dated market conclusion

Research on 2026-07-29 combined large developer surveys, current community
workflows, GitHub security telemetry/documentation, recent research, direct and
adjacent repositories, package usage, and dormant products.

The broad pain is verification and missing-context debt. The narrower opportunity
survived because environment inventory (`envinfo`), infrastructure support
bundles (Replicated Troubleshoot), issue forms, and project-specific doctor
commands do not jointly bind an ordinary repository's declared reproduction argv,
Git state, bounded results, mutation delta, and review-before-share boundary.

The conclusion is bounded: external evidence supports the problem and existing
workarounds; it does not prove that ReproBrief itself has adoption or superior
outcomes.

## 4. Candidate comparison and eliminations

Eighteen behavior-derived candidates were scored in three rounds.

Final top five:

1. P-003 secret-aware diagnostic capsule — 60.00
2. P-001 local change evidence runner — 55.71
3. P-008 flaky-test witness recorder — 53.91
4. P-011 contribution gate — 53.64
5. P-007 release verifier — 52.83

P-003 ranked first in consecutive rounds after direct-competitor,
distribution, and falsification work. Strong alternatives were rejected or
narrowed because mature direct tools occupied the core (Actions hardening),
platform capabilities reduced the gap (release verification), or the feasible
MVP did not cover the real problem breadth (flaky remediation/environment drift).
The decision and reversal triggers are in `05-decision-record.md`.

## 5. Decision and non-goals

Frozen product: **ReproBrief 0.1.0**.

Non-goals include arbitrary file/source collection, `.env` reading, upload,
accounts, telemetry, AI diagnosis, sandboxing, CI replay, automatic cleanup,
plugin systems, and a claim that redaction makes output safe.

## 6. Implemented workflow

```text
strict JSON recipe or facts-only mode
→ resolved and privacy-masked inspection
→ interactive or explicit noninteractive approval
→ Git/system snapshot
→ sequential real argv execution without a shell
→ concurrent bounded stdout/stderr drain and timeout/cancellation
→ second Git snapshot and mutation delta
→ in-memory best-effort redaction and residual scan
→ staged local Markdown/JSON/stream files
→ optional explicit ZIP
```

The installed CLI supports `init`, `inspect`, `run`, `--archive`, `--force`,
`--version`, stable exit classes, and a portable `{python}` executable token.

## 7. Architecture

The implementation uses CPython 3.11+ and only the standard library at runtime.
Modules separate recipe validation, system/Git facts, execution, redaction,
manifest/report rendering, safe output/ZIP handling, and CLI orchestration.
There is no server, database, cache, worker, network client, or runtime
third-party library.

## 8. Verification matrix

Local source revision:
`f546e344f33ecb72119987271da6802498313bf4`

- 57 tests passed on macOS 26.0 arm64 / CPython 3.14.0.
- Branch coverage: 87%; enforced floor: 85%.
- Ruff format/lint and strict mypy: passed.
- Real dual-stream large output, timeout descendants, SIGINT, invalid UTF-8,
  missing binary, nonzero exit, Git mutation, symlink/traversal, archive, and
  installed end-to-end cases: passed.
- Wheel/sdist construction, Twine metadata, fresh installs, and three demos:
  passed locally.
- Remote platform CI: pending.

## 9. Security and privacy

Bandit found zero medium/high issues; five low notices correspond to intentional
subprocess use and PATH lookup. detect-secrets found zero tracked-file findings.
No runtime dependency exists; pip-audit reported no known vulnerability for the
empty runtime set. Actions are pinned to full commits.

The product executes trusted approved programs and does not sandbox them.
Redaction is best-effort. Child commands can access files/network, transformed
secrets may remain, Git filenames may be private, and Windows descendant cleanup
is not a universal guarantee. Every output file must be reviewed before sharing.

## 10. Release status

Target: public `https://github.com/y4ho0/reprobrief`, branch `main`, version
`v0.1.0`. Publication is explicitly authorized but has not yet occurred at this
report checkpoint. Package-registry publication is outside scope.

## 11. Claim Gate

Local Claim Gate is defined in `10-claim-matrix.json`. Claims for the local
workflow, bounded execution, named redaction behavior, guarded output, Git delta,
zero runtime dependencies, and no ReproBrief networking/telemetry path are
verified with bounded evidence. Cross-platform support, formal release, and
external value remain `NOT_VERIFIED` until their required evidence exists.

## 12. Known limitations

- Requires CPython 3.11+ and a user-provided/repository-provided recipe for full value.
- Git is optional for execution but necessary for revision/status evidence.
- Child commands are trusted, unsandboxed, and can modify more than Git reports.
- Output is prefix-bounded per stream; discarded bytes are not privacy-scanned.
- Redaction can miss unknown or transformed sensitive values and can over-redact.
- POSIX process groups are stronger than the 0.1.0 Windows cleanup mechanism.
- No external-user evidence yet demonstrates saved time or adoption.

## 13. Adoption plan

`13-adoption-plan.md` defines 5–10 non-fabricated, consented post-release trials,
time-to-value/actionability metrics, privacy constraints, case-study rules, and
pivot criteria. No demo is represented as an external-user case study.

## 14. Next-version recommendations

Do not expand scope before real trials. First address correctness/security
defects and first-value blockers. Candidate improvements—only after repeated
demand—include a Windows Job Object implementation, schema-aware editor hints,
and project-template snippets. Hosted upload, AI interpretation, file collection,
and plugin ecosystems remain excluded without new evidence and threat modeling.
