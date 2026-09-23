from collections.abc import Iterator
from dataclasses import dataclass

from tree_sitter import Node, Tree


@dataclass(frozen=True)
class ParsedLua:
    """Small parser boundary; native nodes do not escape into rule modules."""

    source: bytes
    tree: Tree

    @property
    def root(self) -> Node:
        return self.tree.root_node

    def text(self, node: Node) -> str:
        return self.source[node.start_byte : node.end_byte].decode("utf-8")

    def errors(self) -> Iterator[Node]:
        def visit(node: Node) -> Iterator[Node]:
            if node.is_error or node.is_missing:
                yield node
            for child in node.children:
                yield from visit(child)

        yield from visit(self.root)
