# Competitor Matrix

Research date: 2026-07-29

## Search scope

- Web search across product sites, official documentation, GitHub repositories,
  npm, PyPI, VS Code Marketplace, GitHub Marketplace, Reddit, and current papers.
- GitHub repository metadata and issue searches for maintenance, limitations,
  privacy, timeout, and cross-platform signals.
- Representative queries:
  - `local validation evidence pack command runner git revision`
  - `AI code proof gate deterministic evidence bundle`
  - `generic diagnostic support bundle CLI redaction`
  - `envinfo bug report environment report`
  - `repository configurable support bundle command`
  - `Markdown shell code block test runner`
  - `pull request evidence gate required tests`
  - `GitHub release tag version asset install verifier`
  - `.env code example drift checker`

## Results for the initial top five

| Candidate | Result | Decision |
|---|---|---|
| P-001 Local change evidence runner | `DIRECT_COMPETITOR_FOUND` | Keep only as comparison. Runcap, DoneCheck, Evidence Gate, ReadyLayer, Gilded Code, Codesteward, and NAOS all market deterministic evidence or proof gates for AI-assisted delivery. The category is active but crowded and mostly unproven. |
| P-013 GitHub Actions hardening linter | `DIRECT_COMPETITOR_FOUND` | Eliminate. `zizmor` is mature, active, focused, and widely adopted; a new ruleset would add little. |
| P-003 Secret-aware diagnostic capsule | `PARTIAL_OVERLAP` | Advance. `envinfo` proves demand for issue-report context; product-specific support bundles and Kubernetes frameworks prove the workflow. No inspected mature tool combines repository-configured local commands, Git/worktree evidence, strict timeouts, privacy findings, preview, and no-upload defaults for general developer projects. |
| P-011 Contribution evidence gate | `DIRECT_COMPETITOR_FOUND` | Downgrade and merge its useful evidence-completeness boundary into P-003. ReadyLayer, Evidence Gate, Gilded Code, and multiple new governance tools target PR evidence directly. |
| P-005 Executable documentation verifier | `DIRECT_COMPETITOR_FOUND` | Eliminate. `mdsh`, `shelltestrunner`, `upmd`, Cram, Markdown task runners, doctest tools, and snippet sync tools cover the workflow. |

## Representative products and alternatives

### envinfo

- URL: https://github.com/tabrindle/envinfo
- Status/date checked: active; last pushed 2026-06-03; checked 2026-07-29
- Target user: JavaScript and cross-platform developers filing issues
- Primary problem: missing OS, binary, SDK, browser, and package-version context
- Core workflow: run `envinfo` and paste text/JSON/Markdown into an issue
- License/pricing: MIT; open source
- Strengths: version 7.21.0, zero dependencies, about 18.4 million weekly npm
  downloads, 1,535 dependent packages, integration in major issue templates
- Weaknesses: environment inventory rather than reproduction-command evidence
  or a reviewable bundle; open issues include local path exposure (#296, #151),
  hangs (#243, #266), and Windows behavior (#238, #262)
- Overlap: system/tool facts and issue-report output
- Difference: does not bind a reproduction command, exit expectation, timeout,
  output cap, Git revision, worktree mutations, or export preview into one pack
- Adoption signal: extremely strong npm usage
- Maintenance signal: active
- Taxonomy: partial direct competitor / strong substitute
- Effect: validates demand while forcing a narrower, privacy- and evidence-led
  product boundary

### Replicated Troubleshoot

- URL: https://github.com/replicatedhq/troubleshoot
- Status/date checked: active; last pushed 2026-07-28; checked 2026-07-29
- Target user: Kubernetes application vendors and cluster operators; host
  collectors can also run directly without a Kubernetes dependency
- Primary problem: preflight checks and post-installation support bundles
- Core workflow: vendor declares collectors, redactors, and analyzers; operator
  creates a bundle
- License/pricing: Apache-2.0; open source
- Strengths: mature declarative model, command/data collectors, redaction,
  analyzers, 584 stars and 110 forks
- Weaknesses: product language, analyzers, and distribution remain
  Kubernetes/infrastructure-oriented even when host collectors run standalone;
  issues show redaction and portability are difficult, including open Windows
  redaction failure #1607 and JSON-redactor request #1457
- Overlap: declarative collectors, commands, redaction, and archives
- Difference: the proposed product binds ordinary source-repository revision,
  expected command exit, output limits, and before/after worktree state into an
  issue-ready preview; it does not provide cluster collectors or remediation analyzers
- Adoption signal: established Kubernetes integrations
- Maintenance signal: active
- Taxonomy: adjacent competitor / architecture precedent
- Effect: proves feasibility and exposes privacy/platform failure modes to test

### Project-specific `doctor` and support-bundle commands

- URLs:
  - https://coder.com/docs/support/support-bundle
  - https://www.hooklistener.com/guides/cli-diagnostics
  - https://docs.github.com/en/enterprise-server@3.17/admin/monitoring-and-managing-your-instance/monitoring-your-instance/about-support-bundles
- Status/date checked: current documentation checked 2026-07-29
- Target user: customers or users of one product
- Primary problem: give that product's support team relevant diagnostics
- Core workflow: run the product's built-in command and send an archive
- License/pricing: varies
- Strengths: product authors know the exact context required
- Weaknesses: every maintainer must build and test its own implementation;
  privacy language often warns that automatic redaction is not sufficient
- Overlap: the desired end-user experience
- Difference: proposed product is a reusable toolkit and portable pack schema
- Adoption signal: common across infrastructure products
- Maintenance signal: maintained with each product
- Taxonomy: substitute / evidence of repeated internal implementation
- Effect: supports a maintainer-focused reusable tool, not a universal diagnosis engine

### IssueGuard

- URL: https://arxiv.org/abs/2602.08072
- Status/date checked: research paper, February 2026
- Target user: GitHub issue authors
- Primary problem: secrets pasted into unstructured issue content
- Core workflow: browser-side live warnings before submission
- License/pricing: research prototype; not established as a mature product
- Strengths: directly studies the pre-submission privacy boundary and reports
  an F1 score of 92.70% on its benchmark
- Weaknesses: secret classification is probabilistic and not a full diagnostic workflow
- Overlap: pre-share warning and redaction
- Difference: proposed product also captures bounded runtime evidence and emits
  a fully inspectable local directory
- Adoption signal: research evidence only
- Maintenance signal: not established
- Taxonomy: research prototype / adjacent competitor
- Effect: prohibits any "safe to share" guarantee and supports fail-closed warnings

### zizmor

- URL: https://github.com/zizmorcore/zizmor
- Status/date checked: active; last pushed 2026-07-28; checked 2026-07-29
- Target user: GitHub Actions maintainers
- Primary problem: insecure workflow syntax, permissions, triggers, and dependencies
- Core workflow: audit workflow files locally, in CI, pre-commit, or an IDE
- License/pricing: MIT; open source
- Strengths: 5,944 stars, 225 forks, active releases, SARIF, fixes, broad rules
- Weaknesses: limited to CI configuration security by design
- Overlap: deterministic local/CI gate
- Difference: no bug-report evidence workflow
- Adoption signal: strong, including documented use by WordPress and ASF
- Maintenance signal: very active
- Taxonomy: direct competitor to P-013
- Effect: eliminates P-013

### Runcap / AI Agent Manager

- URL: https://github.com/kirder24-code/ai-agent-manager
- Status/date checked: created 2026-05-28; last pushed 2026-06-29
- Target user: teams governing AI coding missions
- Primary problem: constrain agent scope/spend and require CI replay
- Core workflow: local control layer plus a proof gate before merge eligibility
- License/pricing: MIT; open source
- Strengths: local-first, base-commit verifier, explicit proof language
- Weaknesses: very new, 10 stars, agent-governance scope
- Overlap: local command evidence and merge gating
- Difference: proposed diagnostic pack serves reporter-to-maintainer handoff and
  does not govern agents or decide merge eligibility
- Adoption signal: early only
- Maintenance signal: recent but not yet established
- Taxonomy: direct competitor to P-001; adjacent to P-003
- Effect: materially lowers P-001's competition score

### Evidence Gate, ReadyLayer, Gilded Code, Codesteward, and NAOS

- URLs:
  - https://evidence-gate.dev/
  - https://ready-layer.com/
  - https://gildedcode.com/
  - https://codesteward.ai/
  - https://www.naos-governance.com/
- Status/date checked: active websites indexed in July 2026
- Target user: teams using AI coding agents and needing PR/governance evidence
- Primary problem: deterministic policy, review, test, provenance, or audit artifacts
- Core workflow: integrate with Git/CI and attach evidence to pull requests
- License/pricing: mixed; several claim open-source components
- Strengths: direct positioning around AI verification and governance
- Weaknesses: many are very new; adoption and open-source depth are not yet clear
- Overlap: evidence schemas, command/test results, review packets
- Difference: proposed P-003 is a local diagnostic handoff, not compliance,
  authorship attribution, or a hosted PR gate
- Adoption signal: insufficient public evidence
- Maintenance signal: emerging
- Taxonomy: direct competitors to P-001/P-011; adjacent to P-003
- Effect: P-001 and P-011 no longer lead

### Markdown runners and executable documentation tools

- URLs:
  - https://github.com/bashup/mdsh
  - https://github.com/zimbatm/mdsh
  - https://github.com/rezigned/upmd
  - https://github.com/simonmichael/shelltestrunner
- Status/date checked: mixed; checked 2026-07-29
- Target user: maintainers of executable docs and command-line examples
- Primary problem: run commands or tests described in Markdown
- Core workflow: parse annotated blocks and execute or compare their output
- License/pricing: open source
- Strengths: multiple established approaches; active `zimbatm/mdsh`; new `upmd`
- Weaknesses: inconsistent annotation and isolation models
- Overlap: almost the full P-005 workflow
- Difference: none strong enough for a solo-maintained first product
- Adoption signal: multiple repositories and package integrations
- Maintenance signal: active and dormant variants
- Taxonomy: direct competitors to P-005
- Effect: eliminates P-005

### GitHub Release verification and release automation

- URLs:
  - https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/verify-release-integrity
  - https://cli.github.com/manual/gh_release_verify
  - https://github.com/slsa-framework/slsa-verifier
- Status/date checked: current; checked 2026-07-29
- Target user: release publishers and consumers
- Primary problem: release/asset integrity and provenance
- Core workflow: attest and verify release metadata and digests
- License/pricing: GitHub CLI and SLSA verifier are open source
- Strengths: platform-native immutable digests and attestations
- Weaknesses: do not execute every project's documented install workflow
- Overlap: much of P-007's release integrity claim
- Difference: only install-smoke orchestration remains distinctive
- Adoption signal: platform-native
- Maintenance signal: active
- Taxonomy: strong substitute / partial direct competitor to P-007
- Effect: P-007 is not selected

### Environment drift scanners

- URLs:
  - https://envdrift.tinyship.ai/
  - https://pypi.org/project/envsniff/
  - https://pypi.org/project/dotdrift/
- Status/date checked: active products in 2026
- Target user: application developers using environment variables
- Primary problem: `.env.example`, code, CI, and docs drift
- Core workflow: scan files and report missing/stale keys
- License/pricing: mixed
- Strengths: several products already match P-006's proposed surface
- Weaknesses: heuristic extraction and crowded naming/positioning
- Overlap: direct
- Difference: no material boundary remains for an initial general tool
- Adoption signal: emerging and fragmented
- Maintenance signal: active
- Taxonomy: direct competitors to P-006
- Effect: P-006 is not selected

## Failed, dormant, or weakly adopted analogues

### Solidarity

- URL: https://github.com/infinitered/solidarity
- Purpose: declare and verify development-environment requirements across machines
- Signal: 639 stars, but last pushed 2024-07-14; historic issues show hangs,
  platform-specific detection, and plugin maintenance burden
- Lesson: automatically detecting every developer tool is a long-lived
  cross-platform maintenance commitment; P-003 must prefer explicit commands,
  strict timeouts, and a small built-in fact set.

### appoptics/release-verification

- URL: https://github.com/appoptics/release-verification
- Purpose: verify that a released npm/RubyGems/PyPI package matches tagged source
- Signal: last pushed 2023-06-26, zero stars, and no npm dependents
- Lesson: release verification alone may be too periodic and ecosystem-heavy
  to earn adoption.

### bashup/mdsh

- URL: https://github.com/bashup/mdsh
- Purpose: Markdown-based literate programming and testing
- Signal: 204 stars, but last pushed 2022-07-01 while newer alternatives exist
- Lesson: executable-doc tools fragment around syntax and runner assumptions;
  another general Markdown runner is unlikely to differentiate.

## Leading-opportunity market conclusion

`PARTIAL_OVERLAP`

The search found mature components and strong substitutes, especially `envinfo`
for environment facts and Replicated Troubleshoot for declarative support
bundles. It did not establish a mature, widely adopted, general developer CLI
with the exact repository-configured workflow proposed for ReproBrief:

```text
show declared commands
→ collect bounded environment/Git facts
→ run without a shell under timeout and output limits
→ record worktree side effects
→ redact and rescan
→ emit a previewable local report and manifest
→ never upload automatically
```

Known limitations:

- Search cannot prove no exact tool exists.
- New AI-governance and support tooling is appearing quickly in 2026.
- `envinfo` may already be sufficient for many issue templates.
- Automatic redaction is fallible; the product must warn rather than certify.
- Maintainers still bear configuration and distribution cost.
