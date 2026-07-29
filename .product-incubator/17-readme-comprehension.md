# README Gate

Status: **PASS_INTERNAL**

## Automated checks

### `README.md`
- PASS

### `README.zh-CN.md`
- PASS

## Bilingual checks

### `README.md` ↔ `README.zh-CN.md`
- PASS

## Manual comprehension review

- Status: `INTERNAL_PASS`
- Reviewer: `INTERNAL_STRUCTURED_REVIEW`
- Comprehension score: `5/5`
- Time to first value: `1` minutes

Automated structure checks do not prove that a new reader understands the product.

## Before this change

The previous README opened with installation, a full recipe, configuration details, and only then the generated result. The information was accurate, but a first-time reader had to understand the interface before seeing the problem, the outcome, or whether the tool fit their situation.

## Information architecture decision

Both language versions now use the same 14-section journey: problem scenario, product boundary, result preview, installation, first-value workflow, use and non-use cases, side effects, safety and privacy, reference material, and contribution details. The order answers “why, what, what do I get, how do I try it, and what can go wrong?” before moving into advanced configuration.

The result preview is text rather than a screenshot because the v0.1.0 output is a small filesystem package whose names and roles can be shown more accurately and accessibly as a tree. No unverified visual claim was added.

## Internal five-question review

1. **What problem does it solve?** Incomplete failure reports otherwise require maintainers to repeatedly ask for the command, bounded output, environment, and Git context.
2. **Who is it for?** Maintainers and contributors or users preparing a useful, reviewable failure report.
3. **What does the user get?** A local report directory and optional ZIP with `report.md`, `manifest.json`, and bounded command streams.
4. **Does it upload data?** No. ReproBrief creates the package locally and does not automatically upload or send it.
5. **What is the main risk or cost?** An approved recipe executes trusted programs without a sandbox, and the generated package still requires manual review before sharing.

Result: `5/5` — `INTERNAL_READABILITY_CHECK_PASSED`.

This is a structured internal review, not evidence from an independent reader: `EXTERNAL_COMPREHENSION_NOT_VERIFIED`.

## First-value verification

On 2026-07-29, a clean virtual environment installed the exact documented `v0.1.0` Git reference in 6.20 seconds. In a disposable Git repository, the documented `init`, `inspect`, and `run --yes --archive` sequence produced `reprobrief-output/` and `reprobrief-output.zip` in 1 second; the command exited with the expected code, the manifest reported ReproBrief 0.1.0, both stream files were bounded, and the repository HEAD did not change.

A separate real-terminal run used plain `reprobrief run`, accepted the confirmation prompt, and produced the expected report directory. This confirms both documented execution paths without changing the product code or release.

## Residual limitations

- External comprehension has not been verified with an independent new user.
- The measured time comes from a prepared local test repository and a warm network; other systems and network conditions will vary.
- Best-effort redaction is not a guarantee, so users must still inspect every generated file before sharing.
