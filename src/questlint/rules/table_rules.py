from tree_sitter import Node

from questlint.core.diagnostics import Diagnostic, Severity
from questlint.rules.base import RuleContext


class DuplicateTableKey:
    rule_id = "QL301"
    name = "duplicate-table-key"
    description = "Warns about duplicate static keys in a table literal."
    severity = Severity.WARNING

    def check(self, context: RuleContext) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for table in self._nodes(context.parsed.root, "table_constructor"):
            seen: set[str] = set()
            for field in (child for child in table.named_children if child.type == "field"):
                key = self._key(context, field)
                if key is None:
                    continue
                if key in seen:
                    diagnostics.append(
                        Diagnostic(
                            context.path,
                            field.start_point.row + 1,
                            field.start_point.column + 1,
                            self.rule_id,
                            self.name,
                            self.severity,
                            f'duplicate table key "{key}"',
                        )
                    )
                seen.add(key)
        return diagnostics

    def _nodes(self, node: Node, kind: str) -> list[Node]:
        # Parser traversal remains contained in this parser-aware rule.
        result = []
        if node.type == kind:
            result.append(node)
        for child in node.children:
            result.extend(self._nodes(child, kind))
        return result

    def _key(self, context: RuleContext, field: Node) -> str | None:
        first = next((c for c in field.children if c.is_named), None)
        if first is None:
            return None
        if first.type == "identifier":
            return context.parsed.text(first)
        if first.type == "string":
            return context.parsed.text(first)[1:-1]
        return None
