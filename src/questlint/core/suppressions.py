import re
from dataclasses import dataclass

DIRECTIVE = re.compile(r"^\s*--\s*questlint-(disable-next-line|disable|enable)\s+(.+?)\s*$")


@dataclass(frozen=True)
class Suppressions:
    by_line: dict[int, frozenset[str]]
    errors: tuple[tuple[int, str], ...]

    def hides(self, line: int, rule_id: str) -> bool:
        return rule_id in self.by_line.get(line, frozenset())


def parse_suppressions(text: str, valid: set[str]) -> Suppressions:
    active: set[str] = set()
    by_line: dict[int, frozenset[str]] = {}
    next_line: dict[int, set[str]] = {}
    errors: list[tuple[int, str]] = []
    lines = text.splitlines()
    for index, line in enumerate(lines, 1):
        by_line[index] = frozenset(active | next_line.pop(index, set()))
        match = DIRECTIVE.match(line)
        if not match:
            if "questlint-" in line and line.lstrip().startswith("--"):
                errors.append((index, "malformed questlint suppression directive"))
            continue
        action, raw_rules = match.groups()
        rules = {part.strip() for part in raw_rules.split(",") if part.strip()}
        invalid = rules - valid
        if not rules or invalid:
            errors.append(
                (index, f"invalid suppression rule: {', '.join(sorted(invalid or rules))}")
            )
            continue
        if action == "disable-next-line":
            next_line.setdefault(index + 1, set()).update(rules)
        elif action == "disable":
            active.update(rules)
        else:
            active.difference_update(rules)
    return Suppressions(by_line, tuple(errors))
