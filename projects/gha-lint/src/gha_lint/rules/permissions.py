from .base import Finding, Rule, find_line


class BroadPermissions(Rule):
    id = "broad-permissions"
    description = "Workflows should declare least-privilege GITHUB_TOKEN permissions."

    def check(self, path, workflow, source):
        findings = []
        if "permissions" not in workflow:
            findings.append(Finding(
                self.id,
                "No top-level 'permissions' block; the token gets the repo default, "
                "which may be read-write",
                path,
            ))

        scopes = [("workflow", workflow.get("permissions"))]
        for name, job in (workflow.get("jobs") or {}).items():
            if isinstance(job, dict):
                scopes.append((f"job '{name}'", job.get("permissions")))

        for scope, perms in scopes:
            if perms == "write-all":
                findings.append(Finding(self.id, f"{scope} uses write-all", path,
                                        find_line(source, "write-all")))
            elif isinstance(perms, dict):
                for key, level in perms.items():
                    if level == "write":
                        findings.append(Finding(
                            self.id,
                            f"{scope} grants write on '{key}'",
                            path,
                            find_line(source, f"{key}: write"),
                        ))
        return findings
