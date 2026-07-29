# ReproBrief

English | [简体中文](README.zh-CN.md)

When someone says “this project fails,” ReproBrief helps them create a local,
reviewable reproduction package instead of sending only a screenshot or a
partial error message.

It is for maintainers who need complete bug-report context and for contributors
or users who need to provide it. The package shows the command that ran, a
limited amount of its output, basic environment facts, and the repository state
at the time of the failure.

The package stays on the user's machine; ReproBrief does not automatically
upload it. ReproBrief runs only the programs declared in a JSON recipe that the
user can inspect and approve. It is **not a sandbox**, and every generated file
must be reviewed before it is shared.

## Have you run into this?

A user reports that a project failed and attaches one error screenshot. The
maintainer still has to ask:

- What exact command did you run?
- Which Python version and operating system were you using?
- What did the command print before it failed?
- Which Git revision was checked out?
- Did the command or local worktree contain uncommitted changes?

That back-and-forth delays diagnosis and makes important context easy to lose.
ReproBrief gathers the same bounded set of facts on every run and puts them in
one package that the reporter can inspect before handing it to the maintainer.
This is the intended workflow, not a claim of external-user validation.

## What ReproBrief does

```text
A reviewed reproduction command
→ one approved local run
→ a reviewable report directory and optional ZIP
```

ReproBrief:

- runs commands only after showing the plan and receiving approval;
- records the resolved command arguments, exit code, duration, and outcome;
- keeps a configurable, limited prefix of standard output and standard error
  (`stdout` and `stderr`) while still draining both streams;
- records conservative operating-system, Python, ReproBrief, and Git facts;
- compares the Git worktree state before and after the command;
- applies best-effort masking to recognized paths, explicitly inherited values,
  and selected high-confidence sensitive patterns;
- writes a local human-readable report, structured record, command output files,
  and an optional ZIP.

It does not collect source files, `.env` files, browser/editor/chat content, or
prompts. ReproBrief itself makes no network request, although an approved child
command can independently read files, modify the repository, or use the network.

## See the result

After a successful run with `--archive`, the repository contains:

```text
reprobrief-output/
├── README.md
├── manifest.json
├── report.md
└── commands/
    ├── tests.stderr.txt
    └── tests.stdout.txt
reprobrief-output.zip
```

- `report.md` is the problem summary intended for a person to read.
- `manifest.json` is the schema-versioned structured record for tools or deeper
  inspection.
- `commands/` contains the retained portion of each command's standard output
  and standard error.
- The generated `README.md` repeats the review and privacy warning beside the
  evidence.
- `reprobrief-output.zip` contains the same generated files. After reviewing
  every file, a user can choose to attach it to an issue or send it through a
  channel they control. ReproBrief never sends it automatically.

An unexpected exit or timeout can still produce this package. The failed
observation is often the evidence the maintainer needs.

## Install

ReproBrief requires CPython 3.11 or newer. It is not published on PyPI; install
the verified `v0.1.0` GitHub release directly:

```console
python -m pip install "reprobrief @ git+https://github.com/y4ho0/reprobrief.git@v0.1.0"
reprobrief --version
```

Expected version output:

```text
reprobrief 0.1.0
```

For an isolated installation, use a tool such as
[`pipx`](https://pipx.pypa.io/stable/):

```console
pipx install "git+https://github.com/y4ho0/reprobrief.git@v0.1.0"
```

The [v0.1.0 Release](https://github.com/y4ho0/reprobrief/releases/tag/v0.1.0)
also provides a wheel, source distribution, and `SHA256SUMS`.

## Quick start

Use these four steps in the repository where a failure occurs.

1. **Create a recipe file.** This writes `reprobrief.json`; it will not replace
   an existing file.

   ```console
   reprobrief init
   ```

2. **Describe the real reproduction command.** Edit `reprobrief.json`. This is
   the smallest valid configuration for Python's built-in test runner; replace
   `argv` with the command that reproduces the actual issue.

   ```json
   {
     "schema_version": 1,
     "commands": [
       {
         "name": "tests",
         "argv": ["{python}", "-m", "unittest", "discover", "-s", "tests"]
       }
     ]
   }
   ```

3. **Preview without executing.** Confirm the resolved program, arguments,
   working directory, timeout, output limit, and facts that will be collected.

   ```console
   reprobrief inspect
   ```

> [!IMPORTANT]
> The next step executes the programs declared by `reprobrief.json`. Inspect the
> recipe first and run only commands you trust. ReproBrief does **not** sandbox
> them. Review every generated file before sharing; masking is best-effort, not
> a privacy guarantee.

4. **Approve the command and create the package.** `--yes` records explicit
   non-interactive approval; `--archive` also creates the ZIP.

   ```console
   reprobrief run --yes --archive
   ```

You should see two `Wrote` lines ending in:

```text
.../reprobrief-output
.../reprobrief-output.zip
```

Open `reprobrief-output/report.md` first, then inspect `manifest.json` and every
file in `commands/`. Nothing is uploaded. For an interactive approval prompt,
use `reprobrief run` instead and answer `y` only after reviewing the plan.

## When to use ReproBrief

- A bug report is missing the exact command, complete bounded logs, or basic
  environment facts.
- A maintainer needs the Git revision and before/after worktree state from the
  same observation as the failure.
- A reporter wants one local package that can be checked before sharing.
- A project does not want diagnostic evidence uploaded to a third-party service
  automatically.
- A repository can provide a small, trusted reproduction recipe.

## When not to use ReproBrief

- The repository or command is untrusted and must run inside a real security
  sandbox.
- A report must be guaranteed to contain no secret or private information.
- The workflow requires automatic upload, hosted storage, or remote execution.
- The goal is full file-access, system-call, or network-traffic tracing.
- The goal is automatic diagnosis, repair, or faithful replay of a CI machine.

Use a sandbox, tracer, hosted support system, or project-specific diagnostic
tool when those are the actual requirements.

## What it creates or changes

- `reprobrief init` creates only the requested recipe file and refuses to
  overwrite an existing one.
- `reprobrief run` creates `reprobrief-output/` by default. `--archive` also
  creates `reprobrief-output.zip`.
- An existing output is never replaced by default. `--force` replaces only a
  directory or archive that ReproBrief recognizes as its own; symbolic-link
  output targets are rejected.
- ReproBrief does not reset or undo child-command side effects. The approved
  command can change files, run other programs, or use the network with the
  invoking user's permissions.
- ReproBrief has no account, server, background process, or hidden remote copy.
  Remove the generated directory, ZIP, and recipe when they are no longer
  needed. A pip installation can be removed with `python -m pip uninstall
  reprobrief`.

Without a recipe, `reprobrief run` collects only conservative system and Git
facts and executes no declared command.

## Security and privacy

ReproBrief reduces some accidental disclosure; it does not make arbitrary logs
safe. It masks exact repository/home paths, explicitly inherited values, and a
tested set of high-confidence credential, email, URL-credential, and private-key
shapes.

It does **not**:

- sandbox or make recipe commands safe;
- discover every secret format or semantic identifier;
- stop an approved command from accessing files, credentials, or the network;
- protect against a malicious repository, executable, dependency, or operating
  system;
- inspect command output discarded beyond the configured byte limit;
- upload, encrypt, sign, or attest a report;
- guarantee complete process-tree cleanup on every operating system.

Read the full [security policy](SECURITY.md),
[privacy and threat model](docs/privacy.md), and [design](docs/design.md) before
using ReproBrief in an automated workflow.

## Configuration reference

Each command in the JSON configuration file has these fields:

| Field | Required | Meaning |
| --- | --- | --- |
| `name` | yes | Safe filename key, unique in the recipe |
| `argv` | yes | Non-empty program and argument array; never a shell string |
| `cwd` | no | Existing directory beneath the repository; default `.` |
| `expected_exit_codes` | no | Exit codes classified as expected; default `[0]` |
| `timeout_seconds` | no | `1`–`300`; default `30` |
| `max_output_bytes` | no | Bytes retained **per stream**, `1024`–`1048576`; default `65536` |
| `inherit_env` | no | Environment-variable **names** explicitly passed to the command |

Unknown fields are errors. The machine-readable structure is
[`docs/reprobrief.schema.json`](docs/reprobrief.schema.json). Runtime validation
also checks repository containment, aggregate argument size, case-insensitive
name collisions, and portable output filenames.

When the first `argv` item is exactly `{python}`, ReproBrief replaces it with
the interpreter running ReproBrief. `inspect` shows both the declaration and
resolved executable. The token is rejected in every other argument position.

Child commands receive a small portability environment (`PATH`, temporary
directory variables, locale, and Windows process variables where present) plus
the names in `inherit_env`. Explicitly inherited values are registered for exact
replacement before persistence, but a program can transform, split, encode, or
hash a value in a way ReproBrief cannot recognize. Prefer disposable test
credentials with no external value.

Command output is continuously drained to avoid pipe deadlock, but only the
configured prefix of each stream is retained. Byte counts and truncation are
recorded. Git status is captured before execution and again before report files
are written.

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Package written and every command had an expected outcome |
| `2` | Usage or approval failure |
| `3` | Invalid recipe or repository input |
| `4` | Package written, but a command failed/timed out or privacy review is required |
| `5` | Output/archive error |
| `130` | Interrupted by the user |

An unexpected command outcome still produces a package when the output can be
written.

## Demos

Three bounded recipes live in [`examples/demos`](examples/demos):

- `success.json`: expected output and exit;
- `unexpected-exit.json`: a real failing observation and exit code;
- `mutation-and-redaction.json`: an explicit environment value and worktree
  mutation (use only in a disposable repository).

Run the safe success example without copying it:

```console
reprobrief inspect --config examples/demos/success.json
reprobrief run --config examples/demos/success.json --yes --output demo-brief
```

## Development and contribution

No third-party test framework is required:

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
