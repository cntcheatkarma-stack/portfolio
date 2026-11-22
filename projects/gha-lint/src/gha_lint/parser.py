from pathlib import Path
from typing import Any, Iterator

import yaml


def load_workflow(path: Path) -> tuple[dict[str, Any], str]:
    source = path.read_text(encoding="utf-8")
    data = yaml.safe_load(source)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    return data, source


def iter_steps(workflow: dict[str, Any]) -> Iterator[tuple[str, dict[str, Any]]]:
    """Yield (job_name, step) for every step in every job.

    Note: PyYAML parses the bare key `on:` as the boolean True, so look for
    True, not "on", if you ever need the trigger section.
    """
    for job_name, job in (workflow.get("jobs") or {}).items():
        if not isinstance(job, dict):
            continue
        for step in job.get("steps") or []:
            if isinstance(step, dict):
                yield job_name, step
