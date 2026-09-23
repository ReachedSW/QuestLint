from questlint.rules.base import Rule
from questlint.rules.flow_rules import (
    ConstantCondition,
    EmptyBranch,
    ExcessiveNesting,
    FileTooLong,
    FunctionMetrics,
    UnreachableCode,
)
from questlint.rules.scope_rules import (
    AccidentalGlobal,
    ShadowedLocal,
    UnusedLocal,
    UnusedParameter,
)
from questlint.rules.state_rules import (
    DuplicateState,
    InitialStateMissing,
    MissingState,
    StateWithoutExit,
    UnreachableState,
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
            UnreachableCode(),
            EmptyBranch(),
            ConstantCondition(),
            ExcessiveNesting(),
            FunctionMetrics(),
            FileTooLong(),
            DuplicateState(),
            MissingState(),
            UnreachableState(),
            StateWithoutExit(),
            InitialStateMissing(),
        )

    @property
    def ids(self) -> set[str]:
        return {rule.rule_id for rule in self.rules}

    def select(
        self, patterns: tuple[str, ...] | None, ignored: tuple[str, ...]
    ) -> tuple[Rule, ...]:
        def expand(items: tuple[str, ...]) -> set[str]:
            found: set[str] = set()
            for item in items:
                if item.endswith("x"):
                    item = item[:-1]
                matches = {rule_id for rule_id in self.ids if rule_id.startswith(item)}
                if not matches or not item.startswith("QL") or not item[2:].isdigit():
                    raise ValueError(f"unknown rule ID or prefix: {item}")
                found.update(matches)
            return found

        selected = self.ids if patterns is None else expand(patterns)
        return tuple(rule for rule in self.rules if rule.rule_id in selected - expand(ignored))
