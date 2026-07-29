# Contributing

Thanks for improving ReproBrief.

## Before opening a change

For behavior changes, open an issue describing the user problem and the smallest
observable outcome. Security-sensitive changes should use private vulnerability
reporting instead.

Keep the initial product boundary intact: local execution, explicit recipes,
bounded output, no runtime service, no telemetry, and no third-party runtime
dependencies without a decision record.

## Local checks

Use Python 3.11 or newer:

```console
PYTHONPATH=src python -m unittest discover -s tests -v
python -m compileall -q src tests
python -m pip install --no-deps .
reprobrief --version
```

Tests use real temporary repositories and subprocesses. A new bug should receive
a regression test when feasible. Do not weaken path, redaction, timeout, output
limit, or atomic-write assertions to make a change pass.

## Pull requests

- Keep the change focused and explain its privacy/security effect.
- Update README, schema, examples, and changelog when the user contract changes.
- Add no generated report, credential, environment dump, or local path.
- Confirm that all checks pass on the same revision.

By submitting a contribution, you agree that it is licensed under Apache-2.0.

