# Product Decision Record

Decision date: 2026-07-29
Status: FROZEN

## Decision

Build **ReproBrief**, a local-first command-line tool that turns a
repository-defined reproduction recipe into a previewable bug-report brief tied
to exact Git state and bounded command results.

## Why selected

- The problem has independent evidence classes: large surveys and live
  maintainer/issue workflows show verification debt, missing context, and
  privacy risk.
- `envinfo`'s approximately 18.4 million weekly npm downloads demonstrate that
  developers will run a lightweight issue-context command.
- Project-specific doctor/support commands and Replicated Troubleshoot
  demonstrate the bundle pattern, while repeated internal implementations show
  maintenance cost.
- The product can deliver a complete deterministic vertical slice without a
  model API, database, hosted service, or privileged integration.
- Core value is objectively testable: exact revision, command argv, expected
  exit, stdout/stderr caps, timeout, redaction counts, and worktree changes.
- The narrowed workflow is meaningfully smaller than Kubernetes support
  tooling and meaningfully different from AI governance gates.

## Candidate reduction

### Initial pool

18 candidates were generated from observed behavior.

### First top five

1. P-001 Local change evidence runner
2. P-013 GitHub Actions hardening linter
3. P-003 Secret-aware diagnostic capsule
4. P-011 Contribution evidence gate
5. P-005 Executable documentation command verifier

### What changed after direct competition research

- P-013 was eliminated by `zizmor`.
- P-005 was eliminated by multiple Markdown runners and doctest tools.
- P-001 and P-011 were downgraded by a crowded 2026 AI-governance/evidence market.
- P-003 advanced, but was narrowed after finding that Replicated Troubleshoot
  can run standalone host collectors.
- P-017's repository-aware issue workflow was merged into P-003 rather than
  treated as a separate product.

### Final top three

| Candidate | Evidence-adjusted result | Strength | Decisive weakness |
|---|---:|---|---|
| P-003 ReproBrief direction | 60.00 | Strong demand precedent, deterministic value, short vertical slice | Reporter trust, configuration cost, and adjacent mature support-bundle tooling |
| P-001 Local change evidence runner | 55.71 | Broad AI verification pain and executable evidence | Crowded direct market with Runcap, DoneCheck, Evidence Gate, ReadyLayer, and others |
| P-008 Flaky-test witness recorder | 53.91 | Severe, objectively verifiable pain | Framework plugins and Develocity already provide retries, histories, and detection |

The score did not make the decision alone. P-003 has the clearest narrow user
handoff, strongest adjacent adoption evidence, and smallest honest first release.

## Active falsification of ReproBrief

1. **Why has a platform not absorbed this?** Many products already embed doctor
   commands. That validates the workflow but means a generic tool must save
   enough implementation effort to justify adoption.
2. **Could the gap reflect low demand?** `envinfo` usage argues against low
   demand for basic context, but demand for richer command evidence remains an
   assumption.
3. **Will users grant permissions?** A recipe can execute repository commands
   and see local state. ReproBrief must show exact argv, never invoke a shell,
   minimize inherited environment, and require explicit approval.
4. **Can setup cost exceed value?** Yes. Zero-config collection, `init`, a small
   JSON recipe, and GitHub-installable packaging are release requirements.
5. **Can a general-purpose model replace it?** A model can format a report but
   cannot independently prove local exit codes, exact Git state, timeouts, or
   side effects; sending raw logs to a model also expands the privacy boundary.
6. **Is the result verifiable?** Yes; all core fields derive from runtime and
   source-control observations.
7. **Will it work beyond a curated demo?** This remains unproven until it is run
   against multiple real repositories; the adoption plan requires 5–10 trials.
8. **Is distribution harder than implementation?** Probably. Issue templates
   and maintainer documentation are the intended channel, but external adoption
   is explicitly not a release claim.
9. **Will users trust it with their data?** Only if processing is local,
   contents are inspectable before archive creation, and privacy language
   remains limited.
10. **Can one maintainer sustain it?** A Python-standard-library core, JSON
    schema, no service, and no automatic platform inventory beyond a small
    fact set keep the burden bounded.

## Main failure thesis

ReproBrief fails if maintainers prefer a few lines of project-specific scripting
or `envinfo`, or if reporters refuse to install and approve a diagnostic tool.
It also fails if redaction warnings create more fear than confidence.

## Reversal conditions

Reopen product selection only if one of these is found before release:

- A mature general developer tool matches the exact revision/command/worktree/
  privacy-preview workflow with strong adoption.
- Cross-platform subprocess and interruption semantics cannot be implemented
  honestly within the MVP boundary.
- A clean installation cannot reach first value without burdensome setup.
- Redaction and preview cannot be worded without creating unsafe confidence.

## Alternatives rejected

- **AI code reviewer:** crowded, model-dependent, and hard to verify objectively.
- **GitHub Actions linter:** mature direct competitor.
- **Environment drift checker:** crowded with current scanners.
- **Release verifier:** GitHub now provides native digests and release verification.
- **Executable docs runner:** established alternatives and syntax fragmentation.
- **CI emulator:** platform complexity exceeds a solo MVP.
- **Automatic flaky-test repair:** framework-specific and high complexity.

## Name check

`reprobrief` had no matching GitHub repository, PyPI distribution, npm package,
or repository under `y4ho0` when checked on 2026-07-29. This is a bounded
availability check, not a trademark determination.

## What would reverse the decision after release

- Fewer than 3 of 10 target maintainers can configure it without author help.
- Fewer than 5 of 10 reporters reach a useful brief in five minutes.
- Privacy warnings or false positives cause more than 20% of trial runs to be abandoned.
- Real trials show that environment inventory alone resolves the same cases.

Owner: product maintainer
