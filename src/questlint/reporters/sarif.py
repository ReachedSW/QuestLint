import json

from questlint.core.diagnostics import Diagnostic, Severity
from questlint.rules.registry import RuleRegistry
from questlint.version import __version__


def render(diagnostics: list[Diagnostic]) -> str:
    rules = [
        {
            "id": rule.rule_id,
            "name": rule.name,
            "shortDescription": {"text": rule.description},
            "defaultConfiguration": {"level": _level(rule.severity)},
        }
        for rule in RuleRegistry().rules
    ]
    rules.extend(
        [
            {
                "id": "QL001",
                "name": "invalid-suppression",
                "shortDescription": {"text": "Reports invalid tool directives."},
                "defaultConfiguration": {"level": "warning"},
            },
            {
                "id": "QL602",
                "name": "function-too-long",
                "shortDescription": {"text": "Reports functions above the configured line limit."},
                "defaultConfiguration": {"level": "warning"},
            },
        ]
    )
    rules.sort(key=lambda rule: str(rule["id"]))
    results = [
        {
            "ruleId": diagnostic.rule_id,
            "level": _level(diagnostic.severity),
            "message": {"text": diagnostic.message},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": str(diagnostic.path).replace("\\", "/")},
                        "region": {"startLine": diagnostic.line, "startColumn": diagnostic.column},
                    }
                }
            ],
        }
        for diagnostic in diagnostics
    ]
    return json.dumps(
        {
            "version": "2.1.0",
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "runs": [
                {
                    "tool": {
                        "driver": {"name": "QuestLint", "version": __version__, "rules": rules}
                    },
                    "results": results,
                }
            ],
        },
        ensure_ascii=False,
    )


def _level(severity: Severity) -> str:
    return {Severity.ERROR: "error", Severity.WARNING: "warning", Severity.INFO: "note"}[severity]
