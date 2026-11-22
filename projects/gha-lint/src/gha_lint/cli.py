import argparse
import sys
from pathlib import Path

from .parser import load_workflow
from .rules import ALL_RULES


def lint_file(path: Path):
    workflow, source = load_workflow(path)
    findings = []
    for rule in ALL_RULES:
        findings.extend(rule.check(str(path), workflow, source))
    return findings


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="gha-lint")
    parser.add_argument("paths", nargs="*", default=[".github/workflows"])
    args = parser.parse_args(argv)

    files: list[Path] = []
    for raw in args.paths:
        p = Path(raw)
        if p.is_dir():
            files += sorted(p.glob("*.yml")) + sorted(p.glob("*.yaml"))
        else:
            files.append(p)

    count = 0
    for f in files:
        for finding in lint_file(f):
            print(f"{finding.path}:{finding.line or 1}: [{finding.rule_id}] {finding.message}")
            count += 1
    return 1 if count else 0


if __name__ == "__main__":
    sys.exit(main())
