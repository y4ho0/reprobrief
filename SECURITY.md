# Security policy

English | [简体中文](SECURITY.zh-CN.md)

## Supported versions

Until a later release exists, only the latest `0.1.x` release is supported.

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting feature in this repository.
Do not include live credentials, private repository contents, or a brief that
has not been manually reviewed.

If private reporting is unavailable, open a public issue containing only a
minimal non-sensitive description and ask the maintainer for a private channel.

You can expect an initial acknowledgement within seven days. A confirmed issue
will receive a severity assessment, remediation plan, and coordinated disclosure
date. This is a small open-source project, so these are targets rather than a
service-level agreement.

## Product boundary

ReproBrief executes trusted, explicitly approved recipes. It does not sandbox
commands, prevent network access, or protect the host from malicious code.

Generated briefs are local and receive best-effort redaction. That transformation
cannot prove that a report is safe to share. Always inspect every file. The full
threat model and mitigations are in [`docs/privacy.md`](docs/privacy.md).
