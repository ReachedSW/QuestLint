from questlint.core.config import Settings
from questlint.core.diagnostics import Diagnostic, Severity
from questlint.core.source import SourceFile
from questlint.core.suppressions import parse_suppressions
from questlint.parsing.parser import LuaParser
from questlint.rules.base import RuleContext
from questlint.rules.registry import RuleRegistry
from questlint.scope.analyzer import ScopeAnalyzer


class Analyzer:
    def __init__(
        self, registry: RuleRegistry | None = None, settings: Settings | None = None
    ) -> None:
        self.parser = LuaParser()
        self.registry = registry or RuleRegistry()
        self.settings = settings or Settings()

    def analyze(self, source: SourceFile) -> list[Diagnostic]:
        parsed = self.parser.parse(source.text)
        facts = ScopeAnalyzer(parsed).analyze()
        context = RuleContext(source.path, parsed, facts, self.settings)
        if any(parsed.errors()):
            diagnostics = self.registry.rules[0].check(context)
        else:
            rules = self.registry.select(self.settings.select, self.settings.ignore)
            suppressions = parse_suppressions(source.text, self.registry.ids)
            diagnostics = [
                diagnostic
                for rule in rules
                for diagnostic in rule.check(context)
                if not suppressions.hides(diagnostic.line, diagnostic.rule_id)
            ]
            diagnostics.extend(
                Diagnostic(
                    source.path, line, 1, "QL001", "invalid-suppression", Severity.WARNING, message
                )
                for line, message in suppressions.errors
            )
        return sorted(diagnostics)
