# Release evidence — ReproBrief v0.1.0

Date: 2026-07-29
Release revision: `b06cd83b1015bbf9d79938a952ef09c875d0c585`
Release: <https://github.com/y4ho0/reprobrief/releases/tag/v0.1.0>

## Exact revision and remote gates

- CI <https://github.com/y4ho0/reprobrief/actions/runs/30416261670> passed
  the static/coverage job and all six CPython 3.11/3.14 jobs on hosted Ubuntu,
  macOS, and Windows.
- CodeQL <https://github.com/y4ho0/reprobrief/actions/runs/30416261666>
  passed on the same revision.
- The annotated `v0.1.0` tag object
  `78898410a39ce53d7a5228f3fa16f1cddf3fcd21` resolves to the release
  revision. No tag or Release with that name existed before creation.
- The GitHub Release is published, non-draft, and non-prerelease.

## Exact-revision artifacts

The wheel and source distribution were rebuilt from a `git archive` of the
release revision, not from a mutable working tree. Twine accepted both metadata
records. The wheel contained 18 safe relative members, declared version 0.1.0,
and no `Requires-Dist`. The source distribution contained 35 safe relative
non-link members.

| Asset | Bytes | SHA-256 |
|---|---:|---|
| `reprobrief-0.1.0-py3-none-any.whl` | 27,839 | `58dcbcbd9370a88f22fe1ddd6c9772bb745932ffaadceeebac443425a93de8ed` |
| `reprobrief-0.1.0.tar.gz` | 34,648 | `bfa516cebee82b656bf5d8bbaa16b9fd3356bb637e50b93a5a351f0cc930f094` |
| `SHA256SUMS` | 190 | `9e6791991b393861aef5fe3c631aee80966c9658a4506d43033a86b15cb520eb` |

All three assets were downloaded back from the Release. Both packages passed
the downloaded checksum file and were byte-identical to the local exact-revision
artifacts.

## Clean installation and workflow

A new virtual environment installed:

```text
reprobrief @ git+https://github.com/y4ho0/reprobrief.git@v0.1.0
```

Package direct-URL metadata resolved `v0.1.0` to the release revision.
`reprobrief --version` returned 0.1.0 and `pip check` passed. In a fresh Git
repository, the installed command previewed and executed the packaged success
recipe, captured the exact before/after Git revision, produced an expected
exit-0 manifest and bounded streams, and wrote a valid ZIP.

Separate clean wheel and source-distribution environments passed version and
dependency checks. The three packaged demos also passed their bounded outcomes:
success plus ZIP, unexpected exit 7 classified through CLI exit 4, and a real
worktree mutation with the explicitly inherited value absent from generated
files.

The final evidence update also passed 57 tests, the 87% branch-coverage floor,
Ruff, strict mypy, compile checks, Claim Gate, an intended-file secret scan with
zero findings, Bandit with zero medium/high findings, and pip-audit with no known
vulnerability in the empty runtime dependency set.

## Repository protection

`main` protection was enabled before this evidence update. It requires pull
requests, strict up-to-date results for the seven CI jobs and CodeQL, linear
history, resolved conversations, and administrator enforcement. Force pushes and
branch deletion are disabled. Active ruleset
<https://github.com/y4ho0/reprobrief/rules/19940807> targets `v*` tags, has no
bypass actors, reports that the current user can never bypass it, and forbids tag
update and deletion.

## Boundary

The tag is annotated but not cryptographically signed, and `SHA256SUMS` is not a
publisher signature. The checks prove byte consistency within the tested
download path. Package-registry distribution and external-user adoption are not
claimed.
