# Architecture — ReproBrief 0.1.0

## Constraints

- Local command-line product; no server, database, telemetry, or runtime network.
- Runtime compatibility: CPython 3.11+.
- No runtime third-party dependencies.
- JSON recipe and JSON manifest, both schema versioned.
- Cross-platform subprocess behavior on macOS, Linux, and Windows.
- Command output must be bounded while pipes continue to drain.
- No source-file or arbitrary-file collector in 0.1.0.
- Redaction is a tested transformation, not a safety certification.
- One maintainer must be able to understand and extend the code.

## Options considered

### Option A — Python standard-library package and CLI

- Advantages: available in the current environment, rapid vertical slice,
  excellent temporary-repository/subprocess tests, built-in JSON/ZIP/dataclasses,
  straightforward GitHub-source installation
- Disadvantages: users need Python 3.11+; standalone executables would require an
  extra packager; process-tree cancellation varies by platform
- Operational burden: low; no service and no runtime dependencies
- Security implications: small dependency surface; interpreter remains external
- Testability: high
- Decision: selected

### Option B — Go static binaries

- Advantages: single-file per-platform releases, easy cross-compilation, small
  runtime footprint
- Disadvantages: Go toolchain is not present locally; more implementation effort
  before validating product value; Windows process trees still need special handling
- Operational burden: moderate release matrix and checksums
- Security implications: compact dependency surface if standard library only
- Testability: high, but local toolchain setup would delay the vertical slice
- Decision: rejected for 0.1.0; valid future rewrite only if Python installation
  materially blocks adoption

### Option C — Node.js zero-dependency CLI

- Advantages: strong reach among web developers and easy `npx` distribution
- Disadvantages: target is cross-ecosystem; Node runtime is no more universal
  than Python; process cancellation and package publication add complexity
- Operational burden: low to moderate
- Security implications: small if zero-dependency, but npm distribution is outside scope
- Testability: high
- Decision: rejected because it narrows perception toward JavaScript without
  improving the core evidence model

## System context

```text
maintainer-owned reprobrief.json
             |
             v
       ReproBrief CLI <---- explicit reporter approval
        |     |   |
        |     |   +---- bounded subprocesses (no shell)
        |     +-------- read-only Git commands
        +-------------- standard-library system facts
             |
             v
   local staging directory
             |
       redact + rescan
             |
             v
 report.md / manifest.json / command text
             |
       explicit archive request
             |
             v
          local ZIP
```

No arrow leaves the machine.

## Modules

- `models.py`: immutable dataclasses and manifest serialization
- `config.py`: recipe discovery, parsing, bounds, cwd containment, argv validation
- `facts.py`: conservative platform, runtime, clock, and Git facts
- `runner.py`: approval-ready command plans, minimized environment, streaming
  bounded capture, timeout, cancellation, exit classification
- `redaction.py`: exact values, machine roots, credential patterns, URLs, counts,
  and residual findings
- `worktree.py`: before/after porcelain snapshots and delta
- `report.py`: Markdown and JSON rendering from the same data model
- `archive.py`: staging, safe relative paths, atomic output, inspect, optional ZIP
- `cli.py`: argument parsing, exit codes, human summaries

## Data model

Manifest schema version 1:

- tool: name/version/schema
- run: ID, start/end UTC, root display value, config source, verdict
- system: OS, release, architecture, Python version
- git: availability, head, branch, dirty-before, dirty-after, delta
- commands:
  - name and argv
  - relative cwd
  - inherited env names only
  - expected exit codes
  - started/ended/duration
  - outcome classification
  - actual exit/signal
  - timeout and truncation booleans
  - output file names and retained/original-observed byte counts
- privacy: rule counts, residual findings, review-required boolean
- archive: created boolean and content list

Original secret values are never serialized.

## Control flow

1. Resolve repository root and output target.
2. Load and fully validate the recipe before running anything.
3. Build a command plan and display resolved argv/cwd/inherited env names after
   masking recognizable paths and sensitive argument values.
4. Require interactive approval or explicit noninteractive approval flag.
5. Snapshot Git status and collect conservative facts.
6. Execute commands sequentially; continue after ordinary command failure so the
   brief contains all requested evidence, but stop on user interruption.
7. Snapshot Git status again.
8. Redact in memory before writing final files.
9. Rescan redacted fields and render to a staging directory.
10. Atomically rename staging to target.
11. Create an archive only on explicit request and only when the privacy gate passes.
12. Exit with a stable code representing clean, evidence-failed, or tool-error.

## Error taxonomy

- `CONFIG_ERROR`: malformed/unsupported/unsafe recipe
- `APPROVAL_REQUIRED`: commands exist but consent is absent
- `NOT_A_REPOSITORY`: informational unless recipe requires Git
- `COMMAND_NOT_FOUND`: command result failure
- `COMMAND_EXIT_MISMATCH`: actual exit not expected
- `COMMAND_TIMEOUT`: configured deadline exceeded
- `COMMAND_INTERRUPTED`: reporter interrupted execution
- `OUTPUT_TRUNCATED`: warning with observed/retained counts
- `WORKTREE_CHANGED`: warning and non-clean verdict
- `PRIVACY_BLOCK`: residual high-confidence pattern prevents archive
- `OUTPUT_EXISTS`: no overwrite without `--force`
- `IO_ERROR`: staging/archive failure
- `INTERNAL_ERROR`: unexpected defect; concise message unless debug requested

## Timeout, cancellation, and retry

- Each command has one attempt; ReproBrief never retries user commands.
- Timeout uses monotonic time and process-group/session termination where the
  platform supports it.
- On timeout: terminate, wait a short grace period, then kill.
- On `Ctrl-C`: terminate the active command, avoid archive creation, and exit 130.
- Cross-platform descendant-process guarantees are not claimed until verified.

## Idempotency

- No automatic network or repository writes.
- Output target is refused if it exists unless `--force`.
- `--force` replaces only the exact resolved target after validating it is
  outside the repository source files and is not a broad/root path.
- Generated run IDs do not affect source files.
- ReproBrief never reverts command side effects.

## Security and trust boundaries

- Recipe is executable intent. Treat an untrusted recipe like untrusted code.
- No shell invocation; every command is an argv array.
- CWD must resolve inside the repository root.
- Environment inheritance is minimal plus explicitly named variables.
- Config cannot embed environment values; only names.
- Output limits prevent memory growth but are not a sandbox.
- No arbitrary file collection in the MVP.
- ZIP members are generated internally with validated relative names.
- User commands have the reporter's normal permissions and can be malicious;
  this is an explicit non-defended risk.

## Privacy and retention

- All processing and outputs are local.
- No telemetry or network code in the runtime package.
- Home/repository roots, exact inherited secret values, credential-like tokens,
  credential-bearing URLs, email-like values, and private-key blocks are redacted.
- The output directory and ZIP persist until the user deletes them.
- ReproBrief never uploads or automatically opens an issue.
- Every report contains a review warning.

## Observability

- Human summary to stdout; actionable errors to stderr.
- `--json` emits a stable command summary without color.
- `--debug` shows stack traces but is not enabled by default.
- Manifest timestamps use UTC; durations use monotonic time.
- No logs outside the requested output directory.

## Configuration

- Discovery: explicit `--config`, then `./reprobrief.json`, otherwise zero-config.
- Unknown top-level and command fields are rejected in schema v1.
- Command names must be case-insensitively unique portable safe slugs.
- Timeouts/output caps have hard global bounds.
- The structural schema is published under `docs/reprobrief.schema.json`; runtime
  checks additionally enforce containment, aggregate size, and portable names.

## Versioning and migration

- CLI follows semantic versioning.
- Recipe and manifest each carry `schema_version: 1`.
- A future incompatible schema is rejected with an upgrade message.
- Additive manifest fields may appear in minor releases; consumers must ignore
  unknown fields.

## Cross-platform behavior

- Paths in manifests use `/` separators and are repository-relative where possible.
- Executables are resolved by the operating system without a shell.
- Windows exit codes are numeric; POSIX signals are recorded separately.
- UTF-8 is used for files with replacement for undecodable command bytes.
- CI must cover macOS, Ubuntu, and Windows before the support claim is published.

## Extension points

- New built-in fact collectors that do not read file contents
- Alternative renderers consuming the manifest dataclasses
- Project templates for popular CLI ecosystems
- Future signed evidence, only after core adoption

Excluded extension points in 0.1.0: plugins, arbitrary file collectors, uploads,
cloud analyzers, model integrations, and issue-creation APIs.

## Test seams

- Clock and run-ID providers are injected.
- Process launcher is wrapped behind one interface.
- Git command adapter accepts a root and returns typed results.
- Redactor rules are pure transformations.
- Renderers consume immutable data only.
- Archive builder accepts an explicit file map.
