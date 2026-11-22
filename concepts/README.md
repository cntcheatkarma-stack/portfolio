# Concepts

Design notes for tools I'm planning. Each one moves to `projects/` once it has working code.

Built so far: [SIEM tool](../projects/siem-tool/) (moved from concept to project).

## Ideas backlog

| Idea | Summary | Focus |
|---|---|---|
| PCAP traffic analyzer | Reads packet captures with Python + Scapy and flags port scans, suspicious DNS such as possible tunneling, and cleartext credentials | Network security |
| Phishing email analyzer | Parses a raw email, checks SPF/DKIM/DMARC, extracts URLs and attachments, and scores how suspicious it is | SOC / email security |
| File integrity monitor | Hashes critical files and alerts on changes, showing what changed and when | Host-based detection |
| Dependency vulnerability checker | Scans requirements and package files against the OSV database | AppSec |
| Password auditor | Checks strength and breach exposure through the HIBP k-anonymity API, without sending the full password | Privacy-aware design |
