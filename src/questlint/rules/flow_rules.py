from collections.abc import Iterator

from tree_sitter import Node

from questlint.core.diagnostics import Diagnostic, Severity
from questlint.rules.base import RuleContext


def _nodes(node: Node) -> Iterator[Node]:
    yield node
    for child in node.named_children:
        yield from _nodes(child)


class _AstRule:
    severity = Severity.WARNING
    rule_id: str
    name: str

    def diagnostic(self, context: RuleContext, node: Node, message: str) -> Diagnostic:
        return Diagnostic(
            context.path,
            node.start_point.row + 1,
            node.start_point.column + 1,
            self.rule_id,
            self.name,
            self.severity,
            message,
        )


class UnreachableCode(_AstRule):
    rule_id = "QL401"
    name = "unreachable-code"
    description = "Reports statements after return or break."

    def check(self, context: RuleContext) -> list[Diagnostic]:
        result: list[Diagnostic] = []
        for block in (n for n in _nodes(context.parsed.root) if n.type == "block"):
            stopped = False
            for statement in block.named_children:
                if stopped:
                    result.append(self.diagnostic(context, statement, "statement is unreachable"))
                if statement.type in {"return_statement", "break_statement"}:
                    stopped = True
        return result


class EmptyBranch(_AstRule):
    rule_id = "QL402"
    name = "empty-branch"
    description = "Reports empty conditional branches."

    def check(self, context: RuleContext) -> list[Diagnostic]:
        return [
            self.diagnostic(context, n, "branch is empty")
            for n in _nodes(context.parsed.root)
            if n.type == "block"
            and n.parent is not None
            and n.parent.type in {"if_statement", "elseif_statement", "else_statement"}
            and not n.named_children
        ]


class ConstantCondition(_AstRule):
    rule_id = "QL403"
    name = "constant-condition"
    description = "Reports literal if and while conditions."

    def check(self, context: RuleContext) -> list[Diagnostic]:
        result = []
        for n in _nodes(context.parsed.root):
            if (
                n.type in {"if_statement", "elseif_statement", "while_statement"}
                and n.named_children
                and n.named_children[0].type in {"false", "nil"}
            ):
                result.append(
                    self.diagnostic(context, n.named_children[0], "condition is a constant")
                )
        return result


class ExcessiveNesting(_AstRule):
    rule_id = "QL404"
    name = "excessive-nesting"
    description = "Reports deeply nested control flow."
    CONTROL = {
        "if_statement",
        "elseif_statement",
        "while_statement",
        "repeat_statement",
        "for_statement",
        "do_statement",
    }

    def check(self, context: RuleContext) -> list[Diagnostic]:
        result = []
        for n in _nodes(context.parsed.root):
            if n.type not in self.CONTROL:
                continue
            depth = sum(1 for parent in self._parents(n) if parent.type in self.CONTROL) + 1
            if depth > context.settings.max_nesting:
                result.append(
                    self.diagnostic(
                        context,
                        n,
                        f"control-flow nesting is {depth} (maximum {context.settings.max_nesting})",
                    )
                )
        return result

    def _parents(self, node: Node) -> Iterator[Node]:
        while node.parent is not None:
            node = node.parent
            yield node


class FunctionMetrics(_AstRule):
    rule_id = "QL601"
    name = "function-too-complex"
    description = "Reports function complexity and length."

    def check(self, context: RuleContext) -> list[Diagnostic]:
        result = []
        functions = [
            n
            for n in _nodes(context.parsed.root)
            if n.type in {"function_declaration", "function_definition"}
        ]
        for fn in functions:
            complexity = 1 + sum(
                1
                for n in _nodes(fn)
                if n is not fn
                and n.type
                in {
                    "if_statement",
                    "elseif_statement",
                    "while_statement",
                    "repeat_statement",
                    "for_statement",
                }
            )
            if complexity > context.settings.max_complexity:
                result.append(
                    self.diagnostic(
                        context,
                        fn,
                        "function complexity is "
                        f"{complexity} (maximum {context.settings.max_complexity})",
                    )
                )
            length = fn.end_point.row - fn.start_point.row + 1
            if length > context.settings.max_function_lines:
                result.append(
                    Diagnostic(
                        context.path,
                        fn.start_point.row + 1,
                        fn.start_point.column + 1,
                        "QL602",
                        "function-too-long",
                        Severity.WARNING,
                        "function has "
                        f"{length} lines (maximum {context.settings.max_function_lines})",
                    )
                )
        return result


class FileTooLong(_AstRule):
    rule_id = "QL603"
    name = "file-too-long"
    description = "Reports files above the configured line limit."

    def check(self, context: RuleContext) -> list[Diagnostic]:
        lines = len(context.parsed.source.decode("utf-8").splitlines())
        if lines > context.settings.max_file_lines:
            return [
                Diagnostic(
                    context.path,
                    1,
                    1,
                    self.rule_id,
                    self.name,
                    Severity.WARNING,
                    f"file has {lines} lines (maximum {context.settings.max_file_lines})",
                )
            ]
        return []
