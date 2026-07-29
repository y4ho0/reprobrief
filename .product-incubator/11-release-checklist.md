# Release Checklist

Source revision under local verification:
`70afe4a646cba03792a1a4e41a37d7f0099c635d`

## Local release readiness

- [x] Product name and target repository collision checked during research
- [x] Version `0.1.0` consistent in package, CLI, changelog, docs, and install example
- [x] Apache-2.0 license and no bundled third-party runtime libraries
- [x] Strict recipe schema and documentation examples validated
- [x] 57 unit/integration/E2E/regression/adversarial tests
- [x] Real timeout, interruption, large-output, mutation, redaction, and ZIP cases
- [x] Ruff format/lint and strict mypy
- [x] Branch coverage 87%, configured floor 85%
- [x] Bandit: zero medium/high findings; low subprocess notices manually reviewed
- [x] detect-secrets: zero findings across tracked files
- [x] Runtime dependency set empty; pip-audit reported no known vulnerabilities
- [x] Wheel and source distribution build and Twine metadata check
- [x] Fresh wheel and source-distribution installation smoke tests
- [x] Local path, personal information, generated file, and large-file scans
- [x] Threat model, privacy boundary, changelog, support, and contribution docs
- [x] Claim Gate passes with unsupported remote/user claims left `NOT_VERIFIED`
- [x] Exact public NEW_REPOSITORY publish plan resolved

## Push Gate

- [x] Strict publish preflight PASS on the committed publication plan
- [x] Authenticated GitHub login reconfirmed as `y4ho0`
- [x] `y4ho0/reprobrief` reconfirmed nonexistent at preflight
- [x] Local worktree contains only intended evidence output
- [x] Public repository created once; no alternate/suffixed target
- [x] `origin` equals the new target; remote was empty
- [x] `main` pushed without force and local/remote SHA equality verified

## Remote CI and release

- [x] Six platform/runtime CI jobs pass on the pushed revision
- [x] Static/type/coverage quality job passes on the pushed revision
- [x] CodeQL passes on the pushed revision
- [x] Default branch is `main`
- [ ] Branch ruleset/protection configured and verified, or limitation recorded
- [ ] Final release assets rebuilt from the exact release revision
- [ ] SHA-256 checksum asset generated and verified
- [ ] Annotated `v0.1.0` tag targets the exact release revision
- [ ] Non-draft, non-prerelease GitHub Release published
- [ ] Release assets downloaded and checksums verified
- [ ] Clean install from GitHub tag and installed workflow verified
- [ ] Claim matrix upgraded only for claims supported by final CI/Release evidence

## Rollback and patch policy

- Never move or overwrite `v0.1.0`.
- If a release-blocking defect appears before the Release, fix normally on `main`,
  rerun every applicable gate, rebuild, and tag only the new verified revision.
- If a defect appears after the Release, publish a documented `v0.1.1`; do not
  replace assets or history silently.
