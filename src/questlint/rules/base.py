from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from questlint.core.diagnostics import Diagnostic, Severity
from questlint.parsing.model import ParsedLua
from questlint.scope.analyzer import ScopeFacts


@dataclass(frozen=True)
class RuleContext:
    path: Path
    parsed: ParsedLua
    scope: ScopeFacts


class Rule(Protocol):
    rule_id: str
    name: str
    description: str
    severity: Severity

    def check(self, context: RuleContext) -> list[Diagnostic]: ...
