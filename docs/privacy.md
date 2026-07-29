# Privacy and threat model

English | [简体中文](privacy.zh-CN.md)

## Assets

- credentials available to the invoking user or child process;
- private paths and repository filenames;
- command stdout/stderr and error text;
- repository revision and dirty-state metadata;
- integrity of the developer's worktree;
- integrity of published source and release artifacts.

## Trust boundaries

The user, recipe, repository, PATH-resolved executables, operating system, Git
binary, and build/release pipeline are separate trust inputs. ReproBrief assumes
the user has reviewed and trusts the recipe and programs it launches. It does
not assume that command output is safe.

## Data flow and persistence

ReproBrief itself makes no network request. It reads the selected JSON recipe,
non-identifying platform fields, and Git's revision/branch/porcelain status. It
runs declared programs, captures a bounded prefix of both output streams, and
writes a local report. The child program may independently read files or use the
network because it is not sandboxed.

No environment values are serialized as fields. A small portability environment
is passed implicitly; additional names require recipe declaration. Values for
those additional names are registered for exact replacement before persistence.

## Mitigations

| Threat | Mitigation |
| --- | --- |
| Shell injection | `argv` arrays and `shell=False`; no shell recipe field |
| Directory escape | Resolved `cwd` must remain beneath the repository |
| Output deadlock/exhaustion | Concurrent pipe drains, per-stream retained-byte caps, timeout |
| Child left after timeout | New POSIX session/process group; terminate then kill |
| Accidental overwrite | Exclusive writes, ownership marker, staged replacement, link rejection |
| ZIP path/link abuse | Generated regular files only, controlled relative member names |
| Common secret/path disclosure | Exact-value replacement plus tested pattern redaction |
| Terminal preview disclosure | Recognized sensitive argv values are masked before display |
| False safety claim | Warning in preview, report, output README, and public documentation |
| Silent worktree mutation | Git status before and after commands; no automatic revert |
| Supply-chain change | No runtime dependencies; pinned CI action commits; checksums on release |

## Residual risk

No finite regular-expression set recognizes every credential or private value.
Commands can transform secrets, mix them with other text, write outside the
report, access the network, or modify the repository. Output discarded beyond
the cap is not analyzed. Filenames in Git status may themselves be sensitive.
PATH lookup can select an unexpected executable. Windows cleanup cannot promise
termination of every descendant without a stronger platform-specific job
object.

Consequently:

- inspect a recipe before approving it;
- run untrusted projects in a separate sandbox you control;
- use disposable/test credentials;
- review every report file before sharing;
- do not treat ReproBrief output as an attestation or security clearance.
