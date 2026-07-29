# ReproBrief

ReproBrief turns a maintainer-declared reproduction command into a reviewable
bug-report brief tied to the exact Git state in which it ran.

It records command arguments, exit status, bounded stdout/stderr, conservative
system facts, and the Git worktree before and after execution. It then applies
best-effort redaction and writes everything locally for you to inspect.

ReproBrief is deliberately small:

- no account, hosted service, telemetry, or runtime network access;
- no shell interpolation—commands are argument arrays;
- no source-file, `.env`, browser, editor, chat, or prompt collection;
- no third-party runtime dependencies;
- no claim that generated output is secret-free or that commands are sandboxed.

> [!IMPORTANT]
> A `reprobrief.json` file can ask ReproBrief to execute programs. Inspect the
> recipe and run `reprobrief inspect` before approval. Only run recipes you
> trust. ReproBrief does **not** sandbox commands. Review every generated file
> before sharing; redaction is best-effort, not a privacy guarantee.

## Install

ReproBrief requires CPython 3.11 or newer.

From the tagged GitHub release:

```console
python -m pip install "reprobrief @ git+https://github.com/y4ho0/reprobrief.git@v0.1.0"
reprobrief --version
```

For an isolated install, use a tool such as
[`pipx`](https://pipx.pypa.io/stable/):

```console
pipx install "git+https://github.com/y4ho0/reprobrief.git@v0.1.0"
```

## Quick start

In the repository where a failure occurs:

```console
reprobrief init
```

Edit the generated `reprobrief.json` so its argument array describes the real
reproduction command:

```json
{
  "schema_version": 1,
  "commands": [
    {
      "name": "tests",
      "argv": ["{python}", "-m", "unittest", "discover", "-s", "tests"],
      "cwd": ".",
      "expected_exit_codes": [0],
      "timeout_seconds": 120,
      "max_output_bytes": 65536,
      "inherit_env": []
    }
  ]
}
```

Preview the collectors and resolved argument structure:

```console
reprobrief inspect
```

Recognized paths, environment values, and secret-like arguments are masked in
terminal previews. Inspect the recipe file itself when you need to compare the
literal declaration.

Run after reviewing the preview:

```console
reprobrief run
```

For non-interactive use, `--yes` records the caller's explicit approval:

```console
reprobrief run --yes --archive
```

The default output is `reprobrief-output/`; `--archive` additionally creates
`reprobrief-output.zip`. Neither is uploaded.

Without a recipe, `reprobrief run` collects only conservative system and Git
facts and executes nothing.

## What the recipe controls

Each command has these fields:

| Field | Required | Meaning |
| --- | --- | --- |
| `name` | yes | Safe filename key, unique in the recipe |
| `argv` | yes | Non-empty program and argument array; never a shell string |
| `cwd` | no | Existing directory beneath the repository; default `.` |
| `expected_exit_codes` | no | Exit codes classified as expected; default `[0]` |
| `timeout_seconds` | no | `1`–`300`; default `30` |
| `max_output_bytes` | no | Bytes retained **per stream**, `1024`–`1048576`; default `65536` |
| `inherit_env` | no | Environment-variable **names** to explicitly pass to the command |

Unknown fields are errors. The structural machine-readable definition is
[`docs/reprobrief.schema.json`](docs/reprobrief.schema.json). Runtime validation
also checks repository containment, aggregate argument size, case-insensitive
name collisions, and portable output filenames.

When the first `argv` item is exactly `{python}`, ReproBrief replaces it with
the interpreter running ReproBrief. `inspect` displays both the declaration and
resolved executable, and the report records the resolved argument vector. The
token is rejected in every other argument position.

Child commands receive a small portability environment (`PATH`, temporary
directory variables, locale, and Windows process variables where present) plus
the names in `inherit_env`. Explicitly inherited values are registered for
exact-value redaction and are never written as manifest fields. A program can
still transform, split, encode, hash, or otherwise reveal a secret in a way
ReproBrief cannot recognize. Prefer test credentials with no external value.

## Output

```text
reprobrief-output/
├── README.md
├── manifest.json
├── report.md
└── commands/
    ├── tests.stderr.txt
    └── tests.stdout.txt
```

`manifest.json` is the canonical schema-versioned record. `report.md` is a
human-readable rendering. Large streams are continuously drained to avoid
pipe deadlock, but only the configured prefix is retained; byte counts and
truncation are recorded.

Git status is captured before command execution and again before report files
are written. ReproBrief reports newly appeared and disappeared status entries.
It never resets or reverts command side effects.

An existing output directory is never replaced by default. `--force` replaces
only a directory with a valid ReproBrief marker. Symbolic-link output targets
are rejected.

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Brief written and every command had an expected outcome |
| `2` | Usage or approval failure |
| `3` | Invalid recipe or repository input |
| `4` | Brief written, but a command failed/timed out or privacy review is required |
| `5` | Output/archive error |
| `130` | Interrupted by the user |

An unexpected command outcome still produces a brief when the output can be
written. That failed observation is usually the evidence a maintainer needs.

## Security and privacy boundaries

ReproBrief reduces accidental disclosure; it does not make arbitrary logs safe.
It redacts exact repository/home paths, explicitly inherited values, and a
tested set of high-confidence credential, email, and private-key shapes.

It does **not**:

- sandbox or make recipe commands safe;
- discover every secret format or semantic identifier;
- stop a command from accessing files, credentials, or the network;
- protect against a malicious repository, executable, dependency, or OS;
- inspect command output that was discarded beyond the byte cap;
- upload, encrypt, sign, or attest a report;
- guarantee complete process-tree cleanup on every operating system.

See [Security](SECURITY.md), [privacy model](docs/privacy.md), and
[design](docs/design.md) before adopting ReproBrief in an automated workflow.

## Demos

Three bounded recipes live in [`examples/demos`](examples/demos):

- `success.json`: expected output and exit;
- `unexpected-exit.json`: a real failing observation and exit code;
- `mutation-and-redaction.json`: an explicit environment value and worktree
  mutation (use only in a disposable repository).

Run one without copying it:

```console
reprobrief inspect --config examples/demos/success.json
reprobrief run --config examples/demos/success.json --yes --output demo-brief
```

## Development

No test framework dependency is required:

```console
PYTHONPATH=src python -m unittest discover -s tests -v
```

Install from a local checkout and run the smoke path:

```console
python -m pip install --no-deps .
reprobrief --version
reprobrief inspect --config examples/demos/success.json
```

Read [CONTRIBUTING.md](CONTRIBUTING.md) for the quality and change process.

## License

Apache-2.0. See [LICENSE](LICENSE).
