from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from questlint.core.config import Settings
from questlint.core.diagnostics import Diagnostic, Severity
from questlint.parsing.model import ParsedLua
from questlint.scope.analyzer import ScopeFacts
from questlint.state_machine import StateGraph


@dataclass(frozen=True)
class RuleContext:
    path: Path
    parsed: ParsedLua
    scope: ScopeFacts
    settings: Settings
    state_graph: StateGraph


class Rule(Protocol):
    rule_id: str
    name: str
    description: str
    severity: Severity

    def check(self, context: RuleContext) -> list[Diagnostic]: ...
