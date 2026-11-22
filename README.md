# Portfolio

Cybersecurity analyst currently completing a bachelor's degree in cybersecurity, with a background in high-pressure operations and team leadership. This repo collects my builds, tools, security analyses, and coursework. Each is written up as a short report: what it is, why I built it, how it works, and what I learned.

## Projects

| Project | What it is | Tech | Status |
|---|---|---|---|
| [HaleHound CYD build](projects/halehound/) | Handheld RF security multitool with amplified sub-GHz/2.4 GHz radios, NFC, and GPS, plus a full wiring reference and troubleshooting log | ESP32, SPI, RF hardware | In progress |
| [SIEM tool](projects/siem-tool/) | Log parsers + YAML detection engine mapped to MITRE ATT&CK, with HTML/JSON alert reports ([repo](https://github.com/cntcheatkarma-stack/siem_tool)) | Python, SQLite, pytest | v0.1 complete |
| [Flock ALPR detector](projects/flock-detector/) | Passive Wi-Fi + BLE scanner that detects license plate reader cameras and scores its confidence | MicroPython, ESP32-S3 | Prototype |
| [gha-lint](projects/gha-lint/) | Linter for GitHub Actions workflows: unpinned actions, script injection, broad token permissions | Python, PyYAML, pytest | In progress |
| [Weather station mesh node](projects/weather-station/) | Roof-mounted sensor node on a LoRa mesh, queried in plain English through a local LLM | Meshtastic, Python, local AI | Planning |
| [Logic Lights](projects/logic-lights/) | Browser game for learning logic gates with randomly generated circuits | HTML, JavaScript | Complete |
| [Statistics calculator](projects/stats-calculator/) | Menu-driven CLI for descriptive stats, confidence intervals, and correlation/regression | Python (stdlib only) | Complete |
| [Battery meter](projects/battery-meter/) | Live color-coded terminal battery meter | Python, psutil | Complete |

## Security analyses

Log and packet analysis exercises. See [analyses/](analyses/).

- [PowerShell Event 4104: file deletion / anti-forensics](analyses/powershell-4104-file-deletion.md)
- [TCP SYN header breakdown](analyses/tcp-syn-header.md)

## Concepts

Tools I'm designing next. See [concepts/](concepts/).

- Backlog: PCAP analyzer, phishing analyzer, file integrity monitor, dependency checker, password auditor

## Coursework

Web development exercises (HTML, CSS, JavaScript). See [coursework/](coursework/).

## Education

- B.S. in Cybersecurity (in progress)

## Certifications

- [Google Cybersecurity Professional Certificate](certifications/google-cybersecurity-professional-certificate.pdf)
- In progress: CompTIA Security+, OSCP
