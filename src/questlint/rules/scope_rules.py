from questlint.core.diagnostics import Diagnostic, Severity
from questlint.rules.base import RuleContext
from questlint.scope.analyzer import STANDARD_GLOBALS


class _ScopeRule:
    rule_id: str
    name: str
    severity = Severity.WARNING

    def diagnostic(self, context: RuleContext, line: int, column: int, message: str) -> Diagnostic:
        return Diagnostic(
            context.path, line, column, self.rule_id, self.name, self.severity, message
        )


class AccidentalGlobal(_ScopeRule):
    rule_id = "QL201"
    name = "accidental-global-assignment"
    description = "Warns when an assignment creates a non-standard global."

    def check(self, context: RuleContext) -> list[Diagnostic]:
        return [
            self.diagnostic(
                context, loc.line, loc.column, f'global "{name}" is assigned without local'
            )
            for name, loc in context.scope.globals_assigned
            if name not in STANDARD_GLOBALS and name not in context.settings.globals_allowed
        ]


class ShadowedLocal(_ScopeRule):
    rule_id = "QL203"
    name = "shadowed-local"
    description = "Warns when a local shadows an outer local."

    def check(self, context: RuleContext) -> list[Diagnostic]:
        return [
            self.diagnostic(context, loc.line, loc.column, f'local "{name}" shadows an outer local')
            for name, loc in context.scope.shadows
        ]


class UnusedLocal(_ScopeRule):
    rule_id = "QL204"
    name = "unused-local"
    description = "Warns when a local is never read."

    def check(self, context: RuleContext) -> list[Diagnostic]:
        return [
            self.diagnostic(context, s.line, s.column, f'local "{s.name}" is never read')
            for s in context.scope.locals
            if s.reads == 0 and not s.name.startswith("_")
        ]


class UnusedParameter(_ScopeRule):
    rule_id = "QL205"
    name = "unused-function-parameter"
    description = "Warns when a function parameter is never read."

    def check(self, context: RuleContext) -> list[Diagnostic]:
        return [
            self.diagnostic(context, s.line, s.column, f'parameter "{s.name}" is never read')
            for s in context.scope.parameters
            if s.reads == 0 and not s.name.startswith("_")
        ]
