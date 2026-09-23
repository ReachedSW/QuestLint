from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, order=True)
class Diagnostic:
    path: Path
    line: int
    column: int
    rule_id: str
    rule_name: str
    severity: Severity
    message: str
