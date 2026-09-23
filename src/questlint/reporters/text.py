from collections import Counter

from questlint.core.diagnostics import Diagnostic, Severity


def format_diagnostic(diagnostic: Diagnostic) -> str:
    return (
        f"{diagnostic.path}:{diagnostic.line}:{diagnostic.column} {diagnostic.rule_id} "
        f"{diagnostic.rule_name}: {diagnostic.message}"
    )


def summary(files: int, diagnostics: list[Diagnostic]) -> str:
    counts = Counter(d.severity for d in diagnostics)
    parts = [f"{files} file{'s' if files != 1 else ''} checked"]
    for severity in (Severity.WARNING, Severity.ERROR, Severity.INFO):
        if counts[severity]:
            parts.append(
                f"{counts[severity]} {severity.value}{'s' if counts[severity] != 1 else ''}"
            )
    return ", ".join(parts)
