# Problem Signals

Research date: 2026-07-29

## Evidence

### S-001 — AI output has created a verification bottleneck

- Evidence class: large developer survey
- Stack Overflow's 2025 survey reports 80% AI-tool use, only 29% trust in
  accuracy, 45% frustration with "almost right" output, and 66% spending more
  time fixing such output.
- Source:
  https://stackoverflow.blog/2025/12/29/developers-remain-willing-but-reluctant-to-use-ai-the-2025-developer-survey-results-are-here/
- Implication: a useful product should strengthen deterministic verification
  and human review context rather than generate more unverified code.
- Limitation: survey results describe a broad population and do not prove
  demand for any one verification workflow.

### S-002 — Developers do not consistently verify code they distrust

- Evidence class: independent developer survey from a code-quality vendor
- Sonar's 2026 survey of more than 1,100 developers reports that 96% do not
  fully trust functional correctness, 48% always check before commit, and 38%
  find AI-code review more effortful than review of human-written code.
- Source:
  https://www.sonarsource.com/company/press-releases/sonar-data-reveals-critical-verification-gap-in-ai-coding/
- Implication: the bottleneck is a repeatable evidence workflow with low setup
  cost, not another generic code generator.
- Limitation: Sonar sells verification products, so its interpretation has a
  commercial incentive; use the figures as evidence of the pattern, not proof
  of Sonar's preferred solution.

### S-003 — Local/CI parity still causes manual debugging

- Evidence class: current community workflow discussion
- A July 2026 DevOps discussion asks what people actually do when CI fails but
  the failure cannot be reproduced locally; responses describe retaining the
  blocking failure, reverting, or collecting reproduction evidence.
- Source:
  https://www.reddit.com/r/devops/comments/1v119en/whats_your_actual_workflow_when_a_test_fails_in/
- Implication: portable command, environment, and failure evidence has value.
- Limitation: one thread is qualitative and does not estimate prevalence.

### S-004 — CI setup and diagnosis remain slow feedback loops

- Evidence class: repeated user complaints and platform roadmap feedback
- A 2025 DevOps thread describes change/wait/fail/repeat loops and substantial
  setup/debugging burden; GitHub's 2025 Actions roadmap discussion says users
  continue to request faster builds, better caching, flexibility, reliability,
  and local composite-action context fixes.
- Sources:
  https://www.reddit.com/r/devops/comments/1k7j1bv/setting_up_devops_pipelines_is_my_worst_nightmare/
  https://github.com/orgs/community/discussions/181437
- Implication: a local tool should reuse existing project checks and shorten
  feedback without attempting to replace CI.
- Limitation: CI ecosystems vary; a universal workflow emulator would be too
  broad for an initial product.

### S-005 — Environment setup and insufficient documentation overlap

- Evidence class: large developer/manager survey
- Atlassian's 2025 DevEx study surveyed 3,500 developers and managers and
  identifies organizational inefficiency and productivity drains despite AI;
  its report groups build processes, local setup, and insufficient
  documentation as recurring friction areas.
- Source:
  https://www.atlassian.com/teams/software-development/state-of-developer-experience-2025
- Implication: executable freshness checks for setup instructions and project
  requirements may be more useful than another static onboarding checklist.
- Limitation: the public landing page exposes less detail than the report PDF
  and is enterprise-weighted.

### S-006 — Secret leakage is frequent and extends beyond source commits

- Evidence class: first-party platform telemetry and documentation
- GitHub reports more than 39 million detected secret leaks in 2024 and notes
  that secrets are often accidentally committed or intentionally stored for
  convenience. GitHub also documents exposure through issues, pull-request
  comments, discussions, and gists.
- Sources:
  https://github.blog/security/application-security/next-evolution-github-advanced-security/
  https://docs.github.com/en/code-security/concepts/secret-security/secret-leakage-risks
- Implication: any diagnostic or evidence-sharing tool must default to local
  retention, allowlisting, redaction, previews, and fail-closed sharing.
- Limitation: mature secret scanners already cover repository content; a new
  product must not merely reimplement gitleaks or GitHub Secret Protection.

### S-007 — Bug reports and AI-generated contributions often lack context

- Evidence class: maintainer workflow complaints
- A 2026 open-source-maintainer discussion says roughly 20% of submissions in
  one project's 2025 experience were low-quality AI output and argues for
  detecting missing context rather than detecting AI; maintainers specifically
  prioritize reports with recordings and logs.
- Source:
  https://www.reddit.com/r/opensource/comments/1q3f89b/open_source_is_being_ddosed_by_ai_slop_and_github/
- Implication: evidence completeness can be checked objectively without
  guessing whether content was AI-generated.
- Limitation: the reported 20% is project-specific and self-reported.

### S-008 — Diagnostic data can itself leak secrets

- Evidence class: current research prototype and platform documentation
- The 2026 IssueGuard paper describes logs, snippets, and configuration pasted
  into issue trackers as a secret-exposure path and reports that its browser
  prototype warns before submission. Apple explicitly instructs developers to
  redact identifiers in shared crash reports.
- Sources:
  https://arxiv.org/abs/2602.08072
  https://developer.apple.com/documentation/xcode/acquiring-crash-reports-and-diagnostic-logs
- Implication: automatic diagnostic capture must expose exactly what will be
  shared and distinguish redaction from a guarantee of safety.
- Limitation: IssueGuard is a prototype, and content-aware secret detection
  can produce both false positives and false negatives.

### S-009 — Maintainer support and triage load is a recurring sustainability risk

- Evidence class: open-source survey and repeated maintainer reports
- Intel's open-source community survey says 45% of respondents cited maintainer
  burnout as their top challenge; current maintainer discussions repeatedly
  mention issue triage and dependency updates.
- Sources:
  https://www.intel.com/content/www/us/en/developer/articles/community/maintainer-burnout-a-problem-what-are-we-to-do.html
  https://www.reddit.com/r/opensource/comments/1q76f90/the_maintainer_burnout_is_real_and_it_is_getting/
- Implication: products that reduce back-and-forth or generate actionable
  evidence may serve both reporters and maintainers.
- Limitation: burnout has organizational and economic causes that tooling
  cannot solve alone.

### S-010 — Flaky failures damage test signal and consume diagnosis time

- Evidence class: empirical study and live issue reports
- A 2025 empirical study analyzes 10,000 test-suite runs from 24 Java projects
  and cites industrial repair cost; active Vitest issues show timeouts that
  reproduce in ecosystem CI but not deterministically.
- Sources:
  https://arxiv.org/abs/2504.16777
  https://github.com/vitest-dev/vitest/issues/7871
- Implication: a small tool can preserve repeated-run evidence and environmental
  deltas, but automatic root-cause or repair claims would be too strong.
- Limitation: framework-specific causes make universal remediation difficult.

### S-011 — Dependency updates require manual impact interpretation

- Evidence class: current research and practitioner workflow
- A 2026 systematic review covers breaking-change propagation across Maven,
  npm, Python, web APIs, and Linux; practitioners describe reviewing automated
  update PRs, test results, and release notes before accepting upgrades.
- Sources:
  https://arxiv.org/abs/2605.24397
  https://www.reddit.com/r/programming/comments/1ojdrv9/removed/
- Implication: a product could assemble local impact evidence, but broad
  automatic migration is highly competitive and ecosystem-specific.
- Limitation: the Reddit source was removed and is retained only as a weak
  behavioral signal.

## Patterns

1. **Evidence debt:** code generation is faster, but proof of correctness,
   reviewability, and safe behavior remains fragmented.
2. **Context debt:** CI failures, bug reports, and contributions often omit the
   exact commands, environment, revision, or observable failure needed by the
   next person.
3. **Freshness debt:** documentation, setup requirements, configuration
   examples, and release instructions drift from executable behavior.
4. **Trust boundary:** logs and diagnostic bundles are useful but can expose
   credentials, identifiers, paths, and source material.
5. **Tooling boundary:** mature scanners and CI systems already exist; a viable
   product should orchestrate verifiable evidence at a narrow handoff boundary,
   not claim to replace testing, CI, SAST, or human review.

## Unresolved questions

- Will developers adopt a small evidence manifest, or is running existing
  project commands directly already sufficient?
- Is a generic evidence bundle more valuable at pre-commit/AI handoff, at CI
  failure reproduction, or at bug-report submission?
- Can secret-safe capture be useful without creating a misleading "safe to
  share" claim?
- Which candidate has a direct competitor that already owns the exact workflow?
- Can the first release support macOS, Linux, and Windows with real CI evidence
  without weakening process and timeout semantics?
