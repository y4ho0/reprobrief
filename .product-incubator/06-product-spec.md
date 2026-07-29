# Product Specification — ReproBrief

Status: FROZEN
Version target: 0.1.0

## 1. Problem

When a command fails only for a contributor or user, maintainers repeatedly ask
for the same missing evidence: exact revision, environment, command, exit code,
complete-but-bounded output, and whether the command changed the workspace.
Reporters gather this manually, omit material context, or paste logs that expose
tokens and machine-specific paths. Generic environment inventory is helpful but
does not bind the observed failure to a reproducible command and repository state.

## 2. Target user

Initial maintainer:

- Maintains an open-source CLI or developer tool in a Git repository.
- Can add one JSON file and a documentation link.
- Wants better bug reports without hosting a service or building a custom doctor command.

Initial reporter:

- Can run a CLI in a local checkout.
- Can inspect files before attaching them to an issue.
- May use macOS, Linux, or Windows and Python 3.11 or newer.

## 3. Jobs To Be Done

When a project command fails on my machine, I want to produce the exact bounded
runtime and repository evidence the maintainer requested, so I can file an
actionable issue without manually assembling logs or uploading unseen data.

When I maintain a developer tool, I want to declare a small reproduction recipe,
so reporters give me consistent evidence without my team implementing a custom
support-bundle subsystem.

## 4. Evidence

### Demand evidence

- Stack Overflow 2025: high AI use, falling trust, almost-right debugging burden.
- Current CI/local-parity and maintainer discussions: missing reproduction context.
- GitHub: secret leaks are common and can occur in issue/comment surfaces.
- `envinfo`: very high package usage and issue-template integration.

### Competitor evidence

- `envinfo` is the primary alternative for environment facts.
- Replicated Troubleshoot is the strongest adjacent architecture and can run
  standalone host collectors.
- Product-specific doctor/support-bundle commands are the common substitute.
- IssueGuard demonstrates pre-submission secret warnings.

### Unresolved assumptions

- Maintainers will prefer a reusable recipe to a custom script.
- Reporters will install and approve the tool.
- A concise brief resolves enough back-and-forth to earn repeat use.

## 5. Positioning

One sentence:

> ReproBrief turns a maintainer-declared reproduction command into a local,
> previewable bug-report brief tied to exact Git state, bounded output, and
> explicit privacy warnings.

- Target user: open-source CLI/developer-tool maintainers and their issue reporters
- Category: local developer diagnostics / reproducible bug-report evidence
- Primary alternative: `envinfo` plus manually pasted command output
- Unique boundary: repository revision + explicit argv + expected exit + strict
  timeout/output limits + before/after worktree state + local preview
- Market conclusion: `PARTIAL_OVERLAP`

## 6. Core workflow

```text
maintainer adds reprobrief.json (optional)
→ reporter runs reprobrief collect
→ ReproBrief shows exact commands and asks for approval
→ bounded collectors and commands run without a shell
→ sensitive patterns and local roots are redacted
→ post-run Git state is compared
→ report.md + manifest.json + bounded command files are written locally
→ reporter inspects them
→ optional archive is created only by explicit request
```

Zero-config mode collects only the conservative built-in facts and Git state.

## 7. MVP capabilities

### Capability: configuration

- User value: one small project-owned recipe
- Input: `reprobrief.json`, schema version 1
- Output: validated in-memory recipe or line/field-specific error
- Happy path: project metadata and argv-array commands load; `{python}` in
  `argv[0]` resolves to the running interpreter for portable recipes
- Failure path: unknown schema, traversal cwd, shell string, invalid timeout,
  output limit, duplicate name, or impossible expected exit is rejected
- Evidence required: unit and fixture tests for every validation branch

### Capability: conservative built-in collection

- User value: useful context without configuration
- Input: current directory
- Output: OS family/release, architecture, Python/ReproBrief version, UTC time,
  Git revision/branch/status when available
- Happy path: all available facts are recorded
- Failure path: missing Git or non-repository directory produces an explicit
  unavailable status, not a crash
- Evidence required: integration tests inside/outside temporary Git repositories

### Capability: explicit command execution

- User value: binds a real reproduction or diagnostic command to evidence
- Input: argv array, relative cwd, expected exit list, timeout, output cap, and
  explicitly inherited environment-variable names
- Output: start/end UTC, duration, exit/signal/timeout status, redacted bounded
  stdout/stderr, expected-exit verdict
- Happy path: approved command completes within bounds
- Failure path: missing executable, denied approval, nonexpected exit, timeout,
  interruption, large output, or spawn failure is classified
- Evidence required: unit/integration/E2E tests for each path

### Capability: privacy processing

- User value: removes common credentials and machine roots before files are written
- Input: captured text plus exact values of explicitly inherited/redaction env names
- Output: redacted text, per-rule counts, residual high-confidence findings
- Happy path: known fixtures are replaced and originals are absent
- Failure path: residual high-confidence finding blocks archive creation
- Evidence required: seeded secret/private-path tests and repository-wide secret scan

### Capability: worktree integrity evidence

- User value: knows whether diagnostic commands altered the original project
- Input: Git porcelain status before and after
- Output: added/removed/changed status entries and a warning verdict
- Happy path: no change
- Failure path: mutation is recorded, overall evidence verdict is non-clean, and
  ReproBrief does not attempt to revert anything
- Evidence required: integration test with a command that creates/modifies files

### Capability: report, manifest, inspect, and archive

- User value: readable and machine-readable evidence that can be inspected first
- Input: complete collection result
- Output: `report.md`, `manifest.json`, bounded command text files,
  `README.txt`, and optional ZIP
- Happy path: output directory is atomically committed and inspect lists contents
- Failure path: existing output, partial write, privacy block, or unsafe archive
  path produces a clear error and no overwrite without `--force`
- Evidence required: schema tests, deterministic fixture assertions, ZIP traversal
  checks, archive content/hash verification

## 8. Non-goals

- Diagnose root cause, fix code, or generate tests.
- Judge whether a contribution was AI-generated.
- Replace CI, testing, SAST, secret scanners, issue forms, or human review.
- Guarantee that a report is safe to share or free of secrets.
- Capture source files, `.env` files, credentials, browser data, prompts, or chat history.
- Upload, open an issue, or call any network service.
- Execute shell strings, pipelines, redirects, or command substitution.
- Provide a security sandbox or contain malicious commands.
- Emulate CI or containers.
- Collect Kubernetes/cloud infrastructure state.
- Publish to PyPI/npm in version 0.1.0.

## 9. Supported environment

- CPython 3.11, 3.12, 3.13, and 3.14
- macOS, Linux, and Windows only after corresponding CI passes
- Git is optional for zero-config facts but required for revision/worktree claims
- Fully offline after installation

## 10. Performance and resource budgets

- Default timeout: 15 seconds per command
- Configurable timeout: 1–300 seconds
- Default retained output: 64 KiB per stream per command
- Configurable retained output: 1 KiB–1 MiB
- Readers must drain excess output without retaining it in memory
- Built-in collection target: under one second on the release test fixture,
  excluding user commands; no public performance claim until benchmarked
- No database, daemon, telemetry, or background process

## 11. Success metrics

Release engineering:

- All required unit, integration, E2E, regression, failure, privacy, and install tests pass.
- Supported-platform CI is green on the release commit.
- Every README command is exercised by tests or release smoke checks.
- Seeded credentials and machine roots do not appear in generated outputs.

Post-release product validation:

- At least 5 of 10 reporters generate a useful brief in five minutes without author help.
- At least 3 of 5 maintainers can configure a real repository in ten minutes.
- At least 3 real reports avoid one round of missing-context follow-up.
- Abandonment from setup or privacy warnings stays below 20%.

## 12. Risks and mitigations

- **Privacy:** redaction is incomplete → local-only, preview first, limited claims,
  exact-value redaction, residual scan, no source capture.
- **Command trust:** repository recipe can run code → argv only, resolved preview
  with recognizable sensitive values masked, explicit approval, minimized
  inherited env, no sandbox claim.
- **Workspace mutation:** commands may change files → pre/post status, warnings,
  no automatic cleanup.
- **Platform behavior:** interruption differs by OS → platform CI and bounded claims.
- **Data quality:** too little context → maintainers choose commands and expected exits.
- **Data excess:** too much output → strict caps and no arbitrary file collectors.
- **Distribution:** extra install step → GitHub install, zipapp/wheel assets, zero-config mode.
- **Maintenance:** environment detectors become stale → conservative standard-library facts.
- **Abuse:** malicious config → treat recipe as executable code and require consent.

## 13. Claim boundaries

Allowed only after evidence:

- "Runs locally and makes no network requests during collection" requires source
  inspection plus network-isolation E2E.
- "Does not collect source files or `.env` files" requires archive inventory tests.
- "Redacts tested credential patterns and configured exact values" requires fixture tests.
- "Supports macOS, Linux, and Windows" requires green CI on each release commit.
- "Stops commands at configured timeouts" requires platform integration tests.
- "Detects worktree changes" requires Git integration tests.
- "Installable from GitHub" requires clean-environment release installation.

Forbidden:

- "Safe to share"
- "Finds all secrets"
- "Sandboxed"
- "Prevents data leaks"
- "Proves the bug"
- "Market validated"
- "Works with every project"
