from questlint.core.diagnostics import Diagnostic, Severity
from questlint.rules.base import RuleContext


class SyntaxErrorRule:
    rule_id = "QL101"
    name = "syntax-error"
    description = "Reports Lua syntax errors."
    severity = Severity.ERROR

    def check(self, context: RuleContext) -> list[Diagnostic]:
        diagnostics = []
        for node in context.parsed.errors():
            diagnostics.append(
                Diagnostic(
                    context.path,
                    node.start_point.row + 1,
                    node.start_point.column + 1,
                    self.rule_id,
                    self.name,
                    self.severity,
                    "invalid Lua syntax",
                )
            )
        return diagnostics
