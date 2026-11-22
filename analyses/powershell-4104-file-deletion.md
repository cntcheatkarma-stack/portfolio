# Analysis: PowerShell Script Block Log (Event 4104), File Deletion

**Type:** Log analysis / DFIR practice
**Artifact:** Windows `Microsoft-Windows-PowerShell/Operational` event, ID 4104

## The evidence

```json
"EventData": {
  "MessageNumber": 1, "MessageTotal": 1, "Path": "",
  "ScriptBlockId": "b0d4f117-b6d4-449b-a179-2c59d6b4f548",
  "ScriptBlockText": "del .\\Top_Secret.txt"
},
"System": {
  "Channel": "Microsoft-Windows-PowerShell/Operational",
  "Computer": "MarySue", "EventID": 4104, "EventRecordID": 8428,
  "Execution": { "ProcessID": 1216, "ThreadID": 4080 }
}
```

## Assessment

Possible **anti-forensics or data destruction.** Someone on host `MarySue` used PowerShell to delete `Top_Secret.txt`, and Script Block Logging recorded the exact command.

## Findings

| Field | What it tells us |
|---|---|
| Event 4104 | Script Block Logging records the code that actually ran, so this is direct evidence, not inference. |
| `del .\Top_Secret.txt` | `del` is an alias for `Remove-Item`. The file skips the Recycle Bin. |
| `Path` is empty | The command was typed interactively or piped in, not run from a `.ps1` file. That points to a person at the keyboard or a remote shell. |
| `MessageNumber 1 / 1` | The whole script block fit in one event. Nothing else ran in that block. |
| `.\` relative path | The full folder isn't in this event. It has to come from other evidence. |
| PID 1216 / TID 4080 | The key for linking this event to related ones. |
| Record 7940 vs EventRecordID 8428 | Probably just the parsing tool's row number, but worth checking for gaps that could mean the log was cleared or wrapped. |
| Missing `TimeCreated` / `UserID` | The most important fields (when and who). Pull them from the full record. |

## Investigation plan

1. **Pivot on PID 1216.** Pull all 4103/4104 events and the 40961/40962 session-start events. A `cd` or `Set-Location` reveals the folder, and earlier commands may show the file being read, copied, or sent out first.
2. **PSReadLine history.** `%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt` often holds the full command sequence.
3. **Recover the file.** Parse `$MFT` and `$UsnJrnl:$J` for `Top_Secret.txt` to get the full path and deletion time, and possibly recover the content.
4. **Attribute the session.** Correlate the UserID and timestamp with Security 4624 logons (RDP or WinRM?). If Sysmon is installed, check events 23/26 (file delete) and 1 (process creation) for PID 1216 and its parent.
5. **Look for more cleanup.** Security 1102 (audit log cleared), System 104, and a wiped history file.

## Skills demonstrated

Windows event log analysis, PowerShell logging, building a DFIR timeline, and spotting anti-forensics.
