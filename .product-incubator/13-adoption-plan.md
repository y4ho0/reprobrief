# Adoption Plan

Status: NOT_STARTED

No external-user use or value is claimed for 0.1.0. Stars, page views, model
judgment, and the author's own demos do not count as product validation.

## Target trials

Recruit 5–10 consented maintainers/reporters after release:

- two Python CLI/library repositories;
- one Node.js repository;
- one compiled-language repository;
- one Windows-first project;
- one project with an existing issue template or doctor command;
- a mix of first-time contributors and experienced maintainers.

Do not ask participants to expose private repositories, real credentials, or
unreviewed briefs. Use disposable failures and test credentials where possible.

## Trial record

For each user/project record:

```text
User/project or approved pseudonym
Permission to store/publish evidence
OS, ecosystem, and repository context
Failure and configured argv
Time to install
Time to first useful brief
Result and maintainer actionability
Missing/excess context
Privacy false positive/negative
Failure or abandonment point
Fix made
Would use again without prompting
Evidence link
```

## Metrics

- At least 5/10 reporters create a brief in five minutes without author help.
- At least 3/5 maintainers configure a real repository in ten minutes.
- At least three real reports avoid one missing-context follow-up.
- Fewer than 20% abandon because of setup or unclear privacy warnings.
- Track repeat use and process/code changes separately from weak star/view signals.

## Case study standard

A publishable case study requires the real initial condition, reproducible steps,
reviewed ReproBrief output, human interpretation, action taken, result, remaining
limitations, and explicit permission. Never fabricate a success story or publish
unreviewed diagnostic content.

## Iteration criteria

Prioritize correctness/security defects, then first-value blockers, repeated
target-user requests, high-leverage integrations, and measured performance.

Reconsider or pivot if users do not experience the missing-context pain, setup
consistently costs more than the brief saves, output is not actionable, privacy
barriers prevent sharing, or a direct competitor dominates the exact workflow.

Use `0.1.x` for defects/documentation corrections. Add backward-compatible
capabilities only after repeated demand; do not expand into hosted upload,
arbitrary file collection, AI diagnosis, CI replay, or a plugin ecosystem based
on a single request.
