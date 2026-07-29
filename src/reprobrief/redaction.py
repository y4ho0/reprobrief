"""Best-effort redaction with explicit, inspectable limits."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from pathlib import Path

from .models import RedactionSummary

_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "private-key-block",
        re.compile(
            r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----.*?"
            r"-----END (?:[A-Z0-9 ]+ )?PRIVATE KEY-----",
            re.DOTALL,
        ),
    ),
    (
        "github-token",
        re.compile(
            r"\b(?:gh[pousr]_[A-Za-z0-9]{20,255}|"
            r"github_pat_[A-Za-z0-9_]{20,255})\b"
        ),
    ),
    (
        "aws-access-key",
        re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    ),
    (
        "slack-token",
        re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,255}\b"),
    ),
    (
        "bearer-token",
        re.compile(r"(?i)\bBearer[ \t]+[A-Za-z0-9._~+/=-]{12,}\b"),
    ),
    (
        "named-secret",
        re.compile(
            r"(?i)(?:--)?(?:api[_-]?key|access[_-]?token|auth[_-]?token|"
            r"client[_-]?secret|password|passwd|pwd|token|secret)"
            r"\s*[:=]\s*[^\s,;]{1,}"
        ),
    ),
    (
        "credential-url",
        re.compile(r"(?i)\b([a-z][a-z0-9+.-]*://)([^/\s:@]+):([^/\s@]+)@"),
    ),
    (
        "email",
        re.compile(
            r"(?<![A-Za-z0-9.!#$%&'*+/=?^_`{|}~-])"
            r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
            r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+"
        ),
    ),
)


class Redactor:
    """Redact known values and high-confidence secret-like patterns."""

    def __init__(
        self,
        *,
        repo_root: Path,
        home: Path | None,
        exact_values: Mapping[str, str] | None = None,
    ) -> None:
        candidates: list[tuple[str, str]] = [
            ("repo-root", str(repo_root.absolute())),
            ("repo-root", str(repo_root.resolve())),
        ]
        if home is not None:
            candidates.extend(
                [
                    ("home", str(home.absolute())),
                    ("home", str(home.resolve())),
                ]
            )
        for name, value in (exact_values or {}).items():
            if value:
                candidates.append((f"env:{name}", value))
        # Longest first prevents a home prefix from partially masking repo-root.
        self._exact = sorted(
            {(label, value) for label, value in candidates if value},
            key=lambda item: len(item[1]),
            reverse=True,
        )
        self.summary = RedactionSummary()

    def redact(self, text: str) -> str:
        """Return redacted text and update the aggregate summary."""

        result = text
        for label, value in self._exact:
            count = result.count(value)
            if count:
                result = result.replace(value, f"<REDACTED:{label}>")
                self._record(label, count)
            alternate = value.replace("\\", "/")
            if alternate != value:
                count = result.count(alternate)
                if count:
                    result = result.replace(alternate, f"<REDACTED:{label}>")
                    self._record(label, count)

        for label, pattern in _PATTERNS:
            if label == "credential-url":
                result, count = pattern.subn(
                    lambda match: f"{match.group(1)}<REDACTED:credentials>@",
                    result,
                )
            else:
                result, count = pattern.subn(f"<REDACTED:{label}>", result)
            if count:
                self._record(label, count)
        return result

    def scan_residual(self, texts: Iterable[str]) -> list[str]:
        """Return pattern labels still present after redaction."""

        warnings: set[str] = set()
        for text in texts:
            for label, pattern in _PATTERNS:
                if pattern.search(text):
                    warnings.add(label)
        self.summary.residual_warnings = sorted(warnings)
        return self.summary.residual_warnings

    def mask(self, label: str) -> str:
        """Return a labeled placeholder and record one deliberate replacement."""

        self._record(label, 1)
        return f"<REDACTED:{label}>"

    def _record(self, label: str, count: int) -> None:
        self.summary.replacements[label] = (
            self.summary.replacements.get(label, 0) + count
        )
