import json

from questlint.core.diagnostics import Diagnostic
from questlint.version import __version__


def render(files_checked: int, diagnostics: list[Diagnostic]) -> str:
    return json.dumps(
        {
            "version": __version__,
            "files_checked": files_checked,
            "diagnostics": [
                {
                    "path": str(d.path).replace("\\", "/"),
                    "line": d.line,
                    "column": d.column,
                    "rule": d.rule_id,
                    "name": d.rule_name,
                    "severity": d.severity.value,
                    "message": d.message,
                }
                for d in diagnostics
            ],
        },
        ensure_ascii=False,
        sort_keys=True,
    )
