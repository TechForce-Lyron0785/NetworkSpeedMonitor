# Technical Specification – Network Speed Monitor v1.0

## 1. Architecture Overview

┌────────────────────────────────────────────────┐
│ Windows Machine │
│ ┌──────────┐ ┌─────────┐ ┌──────────┐ │
│ │ Poller │───▶│ SQLite │◀───│ FastAPI │ │
│ │ (Python) │ │ │ │ (thread) │ │
│ └──────────┘ └─────────┘ └────┬─────┘ │
│ │ │
│ │ HTTP │
│ ▼ │
│ ┌─────────────┐ │
│ │ React + │ │
│ │ Recharts │ │
│ └─────────────┘ │
└────────────────────────────────────────────────┘


## 2. Database Schema (SQLite)
File: `data/speedmon.db`

```sql
-- Core table for raw samples
CREATE TABLE speed_samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    download_mbps REAL NOT NULL,
    upload_mbps REAL,
    latency_ms INTEGER,
    adapter_name TEXT,
    adapter_hardware_id TEXT
);

-- Index for fast date aggregation
CREATE INDEX idx_timestamp ON speed_samples(timestamp);

-- Optional: view for 15-min windows
CREATE VIEW v_15min_worst AS
SELECT 
    date(timestamp) as day,
    strftime('%H:%M', 
        datetime((strftime('%s', timestamp) / 900) * 900, 'unixepoch')
    ) as window_start,
    AVG(download_mbps) as avg_download,
    MIN(download_mbps) as min_download,
    COUNT(*) as sample_count
FROM speed_samples
GROUP BY day, window_start;

## 3. API Contracts (FastAPI)
BaseURL: http://localhost:8000

All endpoints return JSON. Error responses follow standard HTTP codes (400, 404, 500).

### 3.1 GET /daily?date=YYYY-MM-DD

{
  "date": "2026-05-28",
  "samples": [
    {"time": "00:01", "download": 94.2, "upload": 23.1},
    {"time": "00:06", "download": 87.5, "upload": 22.8}
  ],
  "worst_15min": {
    "window_start": "14:30",
    "avg_download": 12.3,
    "min_download": 8.1,
    "samples": 3
  }
}

### 3.2 GET /week?start_date=YYYY-MM-DD

{
  "week_start": "2026-05-25",
  "days": [
    {
      "date": "2026-05-25",
      "samples": [{"time": "00:01", "download": 94.2, "upload": 23.1}],
      "worst_15min": null
    },
    {
      "date": "2026-05-26",
      "samples": [{"time": "00:01", "download": 85.3, "upload": 20.4}],
      "worst_15min": null
    }
    // ... up to 7 days total
  ]
}

### 3.3 GET /worst-times?period=day&date=YYYY-MM-DD

{
  "period": "day",
  "worst_windows": [
    {"window": "14:30", "avg": 12.3, "min": 8.1, "samples": 3},
    {"window": "15:00", "avg": 15.2, "min": 10.0, "samples": 2}
  ]
}

### 3.4 GET /health

{
  "status": "ok",
  "last_sample": "2026-05-28T09:23:45",
  "total_samples": 287
}

## 4. Poller Internal Logic

Interval: random uniform 180–300 seconds.

Adapter detection:

WMI Win32_NetworkAdapter where NetEnabled=True, PhysicalAdapter=True, AdapterType IN (0,6,9,71).
Fallback: psutil.net_if_stats() + name filtering (reject keywords: vpn, virtual, tap, tun, openvpn, wireguard).
Speed test: Download 10 MB file from https://speed.cloudflare.com/__down?bytes=10485760, measure time. Upload test similar (POST to same endpoint). Use source address binding to force physical adapter.

Error handling: On failure, log error, wait, retry.

## 5. Frontend (React) Components
App: main container with date picker and refresh button.

DailyGraph: LineChart for a single day.

WeeklyStack: 7 vertically stacked DailyGraph components.

WorstTimePanel: displays worst 15-min windows.

HealthIndicator: shows poller status.

## 6.Deployment Artifacts
speedmon.exe (PyInstaller – onefile)

install.bat (uses nssm to install Windows service)

uninstall.bat

config.json (optional: poll interval, API port)

data/ folder for SQLite database

## 7. Development Environment Setup

git clone https://github.com/TechForce-Lyron0785/NetworkSpeedMonitor.git
cd NetworkSpeedMonitor
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# Frontend
cd frontend
npm install
npm run build   # builds static files to ../backend/api/static
# Run everything
python run.py   # starts poller + API