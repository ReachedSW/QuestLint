from questlint.core.diagnostics import Diagnostic, Severity
from questlint.rules.base import RuleContext


class _StateRule:
    severity = Severity.WARNING
    rule_id: str
    name: str

    def diagnostic(self, context: RuleContext, line: int, message: str) -> Diagnostic:
        return Diagnostic(context.path, line, 1, self.rule_id, self.name, self.severity, message)


class DuplicateState(_StateRule):
    rule_id = "QL501"
    name = "duplicate-state"
    description = "Reports duplicate state annotations."

    def check(self, context: RuleContext) -> list[Diagnostic]:
        seen: set[str] = set()
        result: list[Diagnostic] = []
        for state in context.state_graph.states:
            if state.name in seen:
                result.append(
                    self.diagnostic(context, state.line, f'duplicate state "{state.name}"')
                )
            seen.add(state.name)
        return result


class MissingState(_StateRule):
    rule_id = "QL502"
    name = "transition-to-missing-state"
    description = "Reports missing transition targets."

    def check(self, context: RuleContext) -> list[Diagnostic]:
        names = context.state_graph.names
        return [
            self.diagnostic(
                context, edge.line, f'transition target "{edge.target}" is not declared'
            )
            for edge in context.state_graph.transitions
            if edge.target not in names
        ]


class UnreachableState(_StateRule):
    rule_id = "QL503"
    name = "unreachable-state"
    description = "Reports states outside the initial graph."

    def check(self, context: RuleContext) -> list[Diagnostic]:
        if context.state_graph.initial not in context.state_graph.names:
            return []
        reachable = context.state_graph.reachable()
        return [
            self.diagnostic(context, state.line, f'state "{state.name}" is unreachable')
            for state in context.state_graph.states
            if state.name not in reachable
        ]


class StateWithoutExit(_StateRule):
    rule_id = "QL504"
    name = "state-without-exit"
    description = "Reports non-terminal states with no transition."

    def check(self, context: RuleContext) -> list[Diagnostic]:
        outgoing = {edge.source for edge in context.state_graph.transitions}
        return [
            self.diagnostic(context, state.line, f'state "{state.name}" has no outgoing transition')
            for state in context.state_graph.states
            if state.name not in outgoing and state.name not in context.settings.terminal_states
        ]


class InitialStateMissing(_StateRule):
    rule_id = "QL505"
    name = "initial-state-missing"
    description = "Reports an absent or invalid initial state."

    def check(self, context: RuleContext) -> list[Diagnostic]:
        graph = context.state_graph
        if graph.initial is None:
            return [self.diagnostic(context, 1, "state machine has no initial state")]
        if graph.initial not in graph.names:
            return [self.diagnostic(context, 1, f'initial state "{graph.initial}" is not declared')]
        return []
