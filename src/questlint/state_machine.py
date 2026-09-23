"""Generic annotation-driven state graph extraction; Lua is never executed."""

import re
from collections import deque
from dataclasses import dataclass, field

STATE = re.compile(r"^\s*---@state\s+([A-Za-z_][A-Za-z0-9_]*)\s*$")
TRANSITION = re.compile(
    r"^\s*---@transition\s+([A-Za-z_][A-Za-z0-9_]*)\s*->\s*([A-Za-z_][A-Za-z0-9_]*)\s*$"
)
INITIAL = re.compile(r"^\s*---@initial\s+([A-Za-z_][A-Za-z0-9_]*)\s*$")


@dataclass(frozen=True)
class State:
    name: str
    line: int


@dataclass(frozen=True)
class Transition:
    source: str
    target: str
    line: int


@dataclass
class StateGraph:
    states: list[State] = field(default_factory=list)
    transitions: list[Transition] = field(default_factory=list)
    initial: str | None = None
    annotations_present: bool = False
    malformed: list[tuple[int, str]] = field(default_factory=list)

    @property
    def names(self) -> set[str]:
        return {state.name for state in self.states}

    def reachable(self) -> set[str]:
        if self.initial not in self.names:
            return set()
        edges: dict[str, list[str]] = {name: [] for name in self.names}
        for transition in self.transitions:
            if transition.target in self.names:
                edges.setdefault(transition.source, []).append(transition.target)
        visited = {self.initial}
        queue = deque([self.initial])
        while queue:
            for target in edges.get(queue.popleft(), []):
                if target not in visited:
                    visited.add(target)
                    queue.append(target)
        return visited


def extract(text: str, configured_initial: str | None = None) -> StateGraph:
    graph = StateGraph()
    annotation_initial: str | None = None
    for line, content in enumerate(text.splitlines(), 1):
        if "---@" not in content:
            continue
        graph.annotations_present = True
        if match := STATE.match(content):
            graph.states.append(State(match.group(1), line))
        elif match := TRANSITION.match(content):
            graph.transitions.append(Transition(match.group(1), match.group(2), line))
        elif match := INITIAL.match(content):
            annotation_initial = match.group(1)
        else:
            graph.malformed.append((line, "malformed state-machine annotation"))
    graph.initial = configured_initial or annotation_initial
    return graph
