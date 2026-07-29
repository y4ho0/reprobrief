# Context

Product: ReproBrief
Domain: developer workflows, reliability, and AI-generated code governance
Status: RELEASE_CANDIDATE
Started: 2026-07-29 (Asia/Shanghai)

## Goal

Discover an evidence-backed developer problem, falsify weak opportunities, freeze a
small open-source product, implement and test its real core workflow, pass security,
privacy, claim, and publication gates, and publish a verified `v0.1.0` release.

## Target users

- Professional and self-taught software developers
- Solo developers and student developers
- Open-source maintainers and small engineering teams
- Developers using AI coding tools

## Constraints

- Generate at least 15 behavior-derived candidates before narrowing.
- Use current external evidence and inspect direct, adjacent, substitute, failed, and
  abandoned solutions.
- Prefer deterministic, locally verifiable value and a short time to first result.
- Avoid costly infrastructure, thin model wrappers, and unnecessary platform scope.
- Maintain all material evidence and decisions in `.product-incubator/`.
- Do not modify any synced project reference under `sources/`.
- Do not publish secrets, private data, machine-specific paths, caches, logs, or
  unrelated artifacts.
- Public GitHub publication is authorized only for owner `y4ho0`, after all gates pass.
- Never force-push, rewrite a published tag, overwrite an existing repository, or
  modify an unrelated repository.

## Available tools and permissions

- Local file creation and code execution: VERIFIED
- Python 3.14, Node.js 25, Git 2.50, GitHub CLI 2.94: VERIFIED
- Internet research and current source inspection: AVAILABLE
- GitHub authenticated login: `y4ho0` (verified 2026-07-29)
- GitHub token scopes reported by the client: repository and workflow access
- Public repository: `https://github.com/y4ho0/reprobrief`, default branch `main`
- Verified product revision: `70afe4a646cba03792a1a4e41a37d7f0099c635d`
- Requested `incubate-product` skill: supplied by the user and package validation passed

## Assumptions

- The final product will be a local-first developer tool unless evidence favors
  another equally maintainable shape.
- A public repository under `y4ho0` and a non-prerelease `v0.1.0` are the intended
  publication targets.
- External user adoption is a post-release validation phase; it will not be
  misrepresented as already achieved.

## Reversibility and authorization

- R0 research and diagnostics: proceed.
- R1 local files, tests, fixtures, and commits in this isolated workspace: proceed.
- R2 bounded GitHub repository setup: authorized after Push Gate.
- R3 public release: explicitly authorized by the goal after Release Gate.
- Paid services, destructive remote actions, unrelated data exposure, and account
  changes remain outside scope unless separately necessary and authorized.

## Success criteria

- Evidence-supported product choice survives direct competition and falsification.
- A new user can install and run a real workflow that produces a useful result.
- Unit, integration, end-to-end, regression, failure, boundary, interruption, and
  installation tests pass without weakened expectations.
- Dependency, secret, privacy, repository, documentation, and claim audits pass.
- A new public repository owned by `y4ho0` uses `main`, has passing GitHub Actions,
  an immutable `v0.1.0` tag, a non-draft/non-prerelease Release, verified assets and
  SHA-256 checksums, and a GitHub-based installation smoke test.

## Initial risks

- Broad developer-tool scope can produce shallow evidence; narrow by observed behavior.
- Attractive ideas may already be absorbed by mature platforms.
- Distribution and trust can be harder than implementation.
- Cross-platform claims require real CI evidence.
- GitHub repository name collision must be checked immediately before remote creation.
- Release claims must remain limited because external user validation is not yet done.
