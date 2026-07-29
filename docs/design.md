# Design

## Why this shape

ReproBrief is a handoff tool, not a general diagnostics platform. Its useful
unit is one observation that binds:

1. a maintainer-declared argument vector;
2. an exact Git revision and before/after status;
3. an expected-exit contract;
4. bounded stdout and stderr;
5. a visible privacy warning and redaction summary.

Generic environment inventory already exists. ReproBrief's distinction is that
the observed command, repository state, output limits, and worktree delta travel
together in one local, inspectable artifact.

## Modules

```text
config → facts(before) → runner → facts(after)
                   ↓
          redaction → manifest → Markdown/files → optional ZIP
```

- `config.py` rejects ambiguity at the input boundary. The sole portable
  executable token, `{python}`, is valid only as `argv[0]` and resolves before
  preview and execution.
- `facts.py` reads conservative system metadata and Git porcelain status.
- `runner.py` executes argv without a shell and drains two bounded streams.
- `redaction.py` performs exact-value and high-confidence pattern replacement.
- `report.py` builds one canonical versioned manifest and its Markdown view.
- `output.py` stages a complete directory before publishing it atomically.
- `cli.py` owns preview, approval, orchestration, and stable exit codes.

There is no plugin system, database, cache, retry loop, or background worker in
0.1.0.

## Failure semantics

- Invalid input stops before any declared command runs.
- A launch error, timeout, or unexpected exit is recorded as a command result.
- Independent declared commands continue after a prior unexpected result.
- User interruption terminates the active process group where the OS permits and
  returns 130; no partial report is claimed.
- The report is staged in a sibling directory. Existing user directories and
  symbolic-link targets are refused.
- `--force` recognizes ownership from the schema and generator marker, then uses
  a backup rename so a failed replacement can restore the prior report.
- Archive creation includes only regular generated files and rejects links.

## Compatibility and evolution

Recipe and manifest both start at schema version 1. Unknown recipe fields are
errors so misspellings cannot silently weaken a limit. Additive manifest fields
may appear within schema 1; a breaking interpretation requires schema 2.

The supported runtime is CPython 3.11+. CI exercises Linux, macOS, and Windows.
Process-tree behavior is strongest on POSIX process groups; the README states
the Windows limitation rather than claiming a universal sandbox or job object.
