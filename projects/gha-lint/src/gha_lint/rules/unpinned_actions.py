import re

from .base import Finding, Rule, find_line
from ..parser import iter_steps

SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class UnpinnedActions(Rule):
    id = "unpinned-action"
    description = "Actions should be pinned to a full commit SHA."

    def check(self, path, workflow, source):
        findings = []
        for job, step in iter_steps(workflow):
            uses = step.get("uses")
            if not isinstance(uses, str) or uses.startswith(("./", "docker://")):
                continue
            ref = uses.rsplit("@", 1)[-1] if "@" in uses else ""
            if not SHA_RE.match(ref):
                findings.append(Finding(
                    self.id,
                    f"'{uses}' is not pinned to a commit SHA (job '{job}')",
                    path,
                    find_line(source, uses),
                ))
        return findings
