from gha_lint.parser import load_workflow
from gha_lint.rules import ALL_RULES

SHA = "b4ffde65f46336ab88eb53be808477a5b2f4c8a2"  # any 40-char hex string works as a fixture


def lint(tmp_path, text):
    f = tmp_path / "w.yml"
    f.write_text(text)
    workflow, source = load_workflow(f)
    return [x for r in ALL_RULES for x in r.check(str(f), workflow, source)]


def test_clean_workflow_has_no_findings(tmp_path):
    findings = lint(tmp_path, f"""
permissions:
  contents: read
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@{SHA}
      - run: echo hello
""")
    assert findings == []


def test_flags_tag_pinned_action(tmp_path):
    findings = lint(tmp_path, """
permissions: read-all
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
""")
    assert [f.rule_id for f in findings] == ["unpinned-action"]


def test_flags_script_injection(tmp_path):
    findings = lint(tmp_path, """
permissions: read-all
on: issues
jobs:
  greet:
    runs-on: ubuntu-latest
    steps:
      - run: echo "${{ github.event.issue.title }}"
""")
    assert "script-injection" in [f.rule_id for f in findings]


def test_flags_missing_permissions(tmp_path):
    findings = lint(tmp_path, """
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo hi
""")
    assert "broad-permissions" in [f.rule_id for f in findings]
