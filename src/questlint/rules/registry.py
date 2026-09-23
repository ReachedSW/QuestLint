from questlint.rules.base import Rule
from questlint.rules.scope_rules import (
    AccidentalGlobal,
    ShadowedLocal,
    UnusedLocal,
    UnusedParameter,
)
from questlint.rules.syntax_error import SyntaxErrorRule
from questlint.rules.table_rules import DuplicateTableKey


class RuleRegistry:
    def __init__(self, rules: tuple[Rule, ...] | None = None) -> None:
        self.rules = rules or (
            SyntaxErrorRule(),
            AccidentalGlobal(),
            ShadowedLocal(),
            UnusedLocal(),
            UnusedParameter(),
            DuplicateTableKey(),
        )
