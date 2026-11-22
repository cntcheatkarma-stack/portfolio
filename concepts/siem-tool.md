# Concept: SIEM Tool

**Status:** Concept / design
**Repo:** [siem_tool](https://github.com/cntcheatkarma-stack/siem_tool)
**Focus:** SOC / blue team

## Goal

A lightweight Security Information and Event Management (SIEM) tool that collects logs, normalizes them into a common format, runs detection rules, and raises alerts. It's meant to show the core SOC workflow end to end: **collect → parse → detect → alert → investigate**.

## Scope (v1)

### Log sources
- Linux `auth.log` / `secure` (SSH, sudo)
- Windows Security event logs exported as EVTX or JSON (4624/4625 logons, 4672 special privileges, 4720 account created)
- Windows PowerShell script-block logging (Event 4104)

### Detections

| Rule | Logic | MITRE ATT&CK |
|---|---|---|
| Brute force | N failed logins for one account or source IP within T minutes | T1110 |
| Success after failures | A successful login following a burst of failures from the same source | T1110 |
| Privilege escalation | New sudo use or a special-privileges logon by an unexpected account | T1078 / T1548 |
| New account created | Event 4720 outside a change window | T1136 |
| Suspicious PowerShell | 4104 events with encoded commands, download cradles, or file deletion | T1059.001 |
| Impossible travel | Logins for one user from distant locations too close together in time | T1078 |

### Output
- Alerts with severity, the rule that fired, and the raw log lines as evidence
- A simple dashboard or HTML report with counts over time, top source IPs, and top targeted accounts
- JSON export for use in other tools

## Architecture

```
log files --> parsers --> normalized events --> rule engine --> alerts --> report / dashboard
                               |
                          event store (SQLite)
```

- **Parsers:** one module per log type, all producing the same event schema (timestamp, host, user, source IP, action, outcome, raw line)
- **Rule engine:** rules written in YAML so new detections need no code changes, with the same idea as Sigma rules
- **Store:** SQLite to keep it simple and portable

## Skills demonstrated

Log parsing and normalization, detection engineering, mapping to MITRE ATT&CK, tuning to reduce false positives, and incident triage write-ups.

## Milestones

1. [ ] Linux auth.log parser and event schema
2. [ ] Brute-force and success-after-failure rules, with tests built on sample logs
3. [ ] Windows event parsing (4624/4625/4672/4720)
4. [ ] YAML rule format
5. [ ] HTML report / dashboard
6. [ ] Write up a sample investigation from the alerts

## Test data

Uses only synthetic logs or public sample datasets. No real organization's logs.
