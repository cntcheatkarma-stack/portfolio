# gha-lint: GitHub Actions Workflow Linter

**Status:** In progress (starter framework working, 4/4 tests passing)
**Category:** AppSec / DevSecOps, CI/CD supply-chain security
**Language:** Python 3.10+, PyYAML, pytest

## Goal

A beginner-friendly command-line linter that scans `.github/workflows/*.yml` files and flags risky patterns. Mature tools like zizmor already cover this space. This is a learning project for understanding CI/CD attack surface by building the checks myself.

## Rules

| Rule ID | What it catches | Why it matters |
|---|---|---|
| `unpinned-action` | `uses: owner/action@v4` instead of a full 40-character commit SHA | A tag can be moved to point at malicious code (supply-chain risk) |
| `script-injection` | `${{ github.event.issue.title }}` and similar values used directly in `run:` | Attacker-controlled text such as PR titles or issue bodies runs as shell commands |
| `broad-permissions` | A missing top-level `permissions:` block, `write-all`, or any `write` grant | Least privilege for the workflow's `GITHUB_TOKEN` |

## Usage

```bash
pip install -e ".[dev]"
pytest
gha-lint .github/workflows
```

Example output:

```
.github/workflows/ci.yml:12: [unpinned-action] 'actions/checkout@v4' is not pinned to a commit SHA (job 'test')
```

The exit code is 1 when there are findings, so CI fails on risky workflows.

## Structure

```
src/gha_lint/
├── cli.py               # entry point, walks files, prints findings
├── parser.py            # YAML loading + step iterator
└── rules/
    ├── base.py          # Finding dataclass + Rule interface
    ├── __init__.py      # rule registry
    ├── unpinned_actions.py
    ├── script_injection.py
    └── permissions.py
tests/test_rules.py
.github/workflows/ci.yml # the linter lints itself
```

Adding a rule means writing one class and adding one line to the registry.

## Current state

The linter currently flags its own `ci.yml`, because that file still uses `@v4`/`@v5` tags. Pinning those to real commit SHAs is milestone 6.

## Milestones

1. [x] Scaffold and parser
2. [x] Unpinned-actions rule and tests
3. [x] Script-injection rule and tests
4. [x] Permissions rule and tests
5. [x] CLI
6. [ ] Pin CI actions to SHAs so the linter passes on itself
7. [ ] `--json` output flag
8. [ ] Config file to disable rules or allowlist trusted owners (for example `actions/*`)
9. [ ] Switch to `ruamel.yaml` for exact line numbers

## Known limits

- `find_line` is a plain text search, so it can report the wrong line when the same text appears twice.
- The injection regex only catches direct `${{ }}` interpolation, not every unsafe data flow.

## References

- GitHub Docs: "Security hardening for GitHub Actions" and "Script injections"
- [zizmor](https://github.com/woodruffw/zizmor), a mature tool to compare against
