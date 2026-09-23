from questlint.core.diagnostics import Diagnostic
from questlint.core.source import SourceFile
from questlint.parsing.parser import LuaParser
from questlint.rules.base import RuleContext
from questlint.rules.registry import RuleRegistry
from questlint.scope.analyzer import ScopeAnalyzer


class Analyzer:
    def __init__(self, registry: RuleRegistry | None = None) -> None:
        self.parser = LuaParser()
        self.registry = registry or RuleRegistry()

    def analyze(self, source: SourceFile) -> list[Diagnostic]:
        parsed = self.parser.parse(source.text)
        facts = ScopeAnalyzer(parsed).analyze()
        context = RuleContext(source.path, parsed, facts)
        if any(parsed.errors()):
            diagnostics = self.registry.rules[0].check(context)
        else:
            diagnostics = [
                diagnostic for rule in self.registry.rules for diagnostic in rule.check(context)
            ]
        return sorted(diagnostics)
