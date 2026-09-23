from dataclasses import dataclass, field

from tree_sitter import Node

from questlint.parsing.model import ParsedLua
from questlint.scope.symbols import Scope, Symbol

STANDARD_GLOBALS = frozenset(
    {
        "_G",
        "assert",
        "collectgarbage",
        "coroutine",
        "debug",
        "dofile",
        "error",
        "getmetatable",
        "io",
        "ipairs",
        "load",
        "loadfile",
        "math",
        "next",
        "os",
        "package",
        "pairs",
        "pcall",
        "print",
        "rawequal",
        "rawget",
        "rawlen",
        "rawset",
        "require",
        "select",
        "setmetatable",
        "string",
        "table",
        "tonumber",
        "tostring",
        "type",
        "utf8",
        "xpcall",
    }
)


@dataclass(frozen=True)
class Location:
    line: int
    column: int


@dataclass
class ScopeFacts:
    globals_assigned: list[tuple[str, Location]] = field(default_factory=list)
    shadows: list[tuple[str, Location]] = field(default_factory=list)
    locals: list[Symbol] = field(default_factory=list)
    parameters: list[Symbol] = field(default_factory=list)


class ScopeAnalyzer:
    def __init__(self, parsed: ParsedLua) -> None:
        self.parsed = parsed
        self.facts = ScopeFacts()

    def analyze(self) -> ScopeFacts:
        self._visit_block(self.parsed.root, Scope())
        return self.facts

    def _loc(self, node: Node) -> Location:
        return Location(node.start_point.row + 1, node.start_point.column + 1)

    def _declare(self, scope: Scope, node: Node, kind: str) -> None:
        name = self.parsed.text(node)
        if scope.outer(name) is not None:
            self.facts.shadows.append((name, self._loc(node)))
        symbol = Symbol(name, node.start_point.row + 1, node.start_point.column + 1, kind)
        scope.symbols[name] = symbol
        (self.facts.parameters if kind == "parameter" else self.facts.locals).append(symbol)

    def _read(self, scope: Scope, node: Node) -> None:
        symbol = scope.resolve(self.parsed.text(node))
        if symbol is not None:
            symbol.reads += 1

    def _identifiers(self, node: Node) -> list[Node]:
        return [child for child in node.children if child.type == "identifier"]

    def _visit_block(self, node: Node, scope: Scope) -> None:
        for child in node.named_children:
            self._visit_statement(child, scope)

    def _visit_statement(self, node: Node, scope: Scope) -> None:
        if node.type == "variable_declaration":
            assignment = next(
                (n for n in node.named_children if n.type == "assignment_statement"), None
            )
            if assignment is not None:
                names = self._identifiers(assignment.named_children[0])
                expressions = (
                    assignment.named_children[1] if len(assignment.named_children) > 1 else None
                )
                if expressions is not None:
                    self._visit_expression(expressions, scope)
                for name in names:
                    self._declare(scope, name, "local")
            return
        if node.type == "function_declaration":
            is_local = any(c.type == "local" for c in node.children)
            function_name = next((c for c in node.children if c.type == "identifier"), None)
            if is_local and function_name is not None:
                self._declare(scope, function_name, "local")
            elif function_name is not None:
                self.facts.globals_assigned.append(
                    (self.parsed.text(function_name), self._loc(function_name))
                )
            self._visit_function(node, scope)
            return
        if node.type == "assignment_statement":
            variables, expressions = node.named_children
            for variable in variables.named_children:
                if (
                    variable.type == "identifier"
                    and scope.resolve(self.parsed.text(variable)) is None
                ):
                    self.facts.globals_assigned.append(
                        (self.parsed.text(variable), self._loc(variable))
                    )
                elif variable.type != "identifier":
                    self._visit_expression(variable, scope)
            self._visit_expression(expressions, scope)
            return
        if node.type == "if_statement":
            for child in node.named_children:
                if child.type == "block":
                    self._visit_block(child, Scope(scope))
                else:
                    self._visit_expression(child, scope)
            return
        if node.type in {"while_statement", "repeat_statement", "do_statement"}:
            for child in node.named_children:
                if child.type == "block":
                    self._visit_block(child, Scope(scope))
                else:
                    self._visit_expression(child, scope)
            return
        if node.type == "for_statement":
            loop_scope = Scope(scope)
            clause = next((c for c in node.named_children if c.type.endswith("_clause")), None)
            if clause is not None:
                loop_variables = next(
                    (c for c in clause.named_children if c.type == "variable_list"), None
                )
                expressions = next(
                    (c for c in clause.named_children if c.type == "expression_list"), None
                )
                if expressions is not None:
                    self._visit_expression(expressions, scope)
                if loop_variables is not None:
                    for loop_name in self._identifiers(loop_variables):
                        self._declare(loop_scope, loop_name, "local")
            for child in node.named_children:
                if child.type == "block":
                    self._visit_block(child, loop_scope)
            return
        self._visit_expression(node, scope)

    def _visit_function(self, node: Node, parent: Scope) -> None:
        function_scope = Scope(parent)
        parameters = next((c for c in node.children if c.type == "parameters"), None)
        if parameters is not None:
            for name in self._identifiers(parameters):
                self._declare(function_scope, name, "parameter")
        function_body = next((c for c in node.children if c.type == "block"), None)
        if function_body is not None:
            self._visit_block(function_body, function_scope)

    def _visit_expression(self, node: Node, scope: Scope) -> None:
        if node.type == "function_definition":
            self._visit_function(node, scope)
            return
        if node.type == "identifier":
            self._read(scope, node)
            return
        for child in node.named_children:
            self._visit_expression(child, scope)
