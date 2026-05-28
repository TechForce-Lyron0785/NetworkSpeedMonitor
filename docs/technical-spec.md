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