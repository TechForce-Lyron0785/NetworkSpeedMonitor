# Product Requirements Document (PRD)
## Network Speed Monitor v1.0

### 1. Executive Summary
A lightweight Windows utility that measures true internet speed by bypassing VPN tunnels. Identifies worst daily/weekly time periods for network performance via a React dashboard.

### 2. Problem Statement
VPNs mask physical network performance. Users cannot tell if slowdowns come from ISP, Wi-Fi interference, or VPN. This tool monitors physical adapters directly.

### 3. Target Users
- Remote workers on corporate VPNs
- Gamers troubleshooting latency
- Network admins monitoring ISP performance
- Home users identifying Wi-Fi dead zones

### 4. Features

| Feature | Description |
|---------|-------------|
| VPN‑aware polling | Auto‑detects & filters virtual/VPN adapters (WMI + route analysis) |
| Randomized intervals | Polls every 3–5 minutes to avoid alignment with periodic events |
| Daily summary | 24‑hour graph with minute‑resolution data |
| Weekly trend view | 7 stacked daily graphs for pattern recognition |
| Worst‑time analysis | Identifies slowest 15‑min windows per day/week |
| Portable deployment | Single EXE + embedded React, runs from USB drive |
| Low resource usage | <30 MB RAM, <0.5% CPU idle |

### 5. Success Metrics (Acceptance Criteria)

| Metric | Target |
|--------|--------|
| Physical speed measurement error | <5% compared to VPN‑disconnected test |
| Uptime | 7+ days without crash or memory leak |
| Worst‑time identification | User identifies worst daily period within first 24 hours |
| Dashboard load time | <2 seconds (on target machine) |

### 6. Non‑Functional Requirements
- Windows 10/11 only (x64)
- Portable – no admin install required (except optional service install)
- Data stored locally in SQLite (no cloud)
- Must handle adapter hot‑plug (Wi‑Fi dongle removal/reinsertion)

### 7. Constraints
- Development timeline: 5–6 days
- Team: 5 roles (but solo developer)
- No external dependencies except standard libraries

### 8. Out of Scope (v1.0)
- Email/slack alerts
- Historical data export (CSV) – future
- Custom test server selection (always uses default speed test)