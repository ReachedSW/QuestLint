from dataclasses import dataclass, field


@dataclass
class Symbol:
    name: str
    line: int
    column: int
    kind: str
    reads: int = 0


@dataclass
class Scope:
    parent: "Scope | None" = None
    symbols: dict[str, Symbol] = field(default_factory=dict)

    def resolve(self, name: str) -> Symbol | None:
        current: Scope | None = self
        while current is not None:
            if name in current.symbols:
                return current.symbols[name]
            current = current.parent
        return None

    def outer(self, name: str) -> Symbol | None:
        return self.parent.resolve(name) if self.parent else None
