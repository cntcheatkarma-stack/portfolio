import re

from .base import Finding, Rule, find_line
from ..parser import iter_steps

UNTRUSTED = re.compile(
    r"\$\{\{\s*github\.event\."
    r"(issue\.title|issue\.body|pull_request\.title|pull_request\.body"
    r"|pull_request\.head\.ref|comment\.body|review\.body"
    r"|head_commit\.message)\s*\}\}"
)


class ScriptInjection(Rule):
    id = "script-injection"
    description = "Untrusted event data must not be interpolated into run: scripts."

    def check(self, path, workflow, source):
        findings = []
        for job, step in iter_steps(workflow):
            script = step.get("run")
            if not isinstance(script, str):
                continue
            for match in UNTRUSTED.finditer(script):
                findings.append(Finding(
                    self.id,
                    f"{match.group(0)} used in run: (job '{job}'); "
                    "pass it through an env: variable instead",
                    path,
                    find_line(source, match.group(0)),
                ))
        return findings
