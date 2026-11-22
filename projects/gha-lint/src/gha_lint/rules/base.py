from dataclasses import dataclass
from typing import Any


@dataclass
class Finding:
    rule_id: str
    message: str
    path: str
    line: int | None = None


def find_line(source: str, needle: str) -> int | None:
    """Return the 1-based line where `needle` first appears, or None."""
    for number, text in enumerate(source.splitlines(), start=1):
        if needle in text:
            return number
    return None


class Rule:
    id: str = ""
    description: str = ""

    def check(self, path: str, workflow: dict[str, Any], source: str) -> list[Finding]:
        raise NotImplementedError
