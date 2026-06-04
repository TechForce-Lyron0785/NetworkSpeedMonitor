# NetworkSpeedMonitor — Product Requirements

## Problem
Home and office internet connections degrade silently. Users want a lightweight,
self-hosted tool that continuously measures their connection (download, upload,
latency) and shows trends over time, so they can spot problems and have evidence
when contacting their ISP.

## Goals
- Continuously measure network speed at a configurable interval.
- Persist measurements so history survives restarts.
- Visualize speed and latency over time in a simple dashboard.
- Be easy to run locally with no heavy infrastructure.

## Non-goals (v1)
- User accounts / multi-tenancy.
- Alerting / notifications.
- Mobile apps.
- Distributed measurement from multiple probes.

## Users
- Home users diagnosing flaky internet.
- Small teams / homelab owners monitoring an office link.

## Core features
1. **Poller** — periodically runs a speed test (download, upload, ping) and stores
   the result. Supports a simulated mode for demos/CI without network access.
2. **API** — stores measurements and exposes them over REST.
3. **Dashboard** — line charts of download/upload and ping over time, plus
   latest-value and aggregate stat cards.

## Key metrics
- Download throughput (Mbps)
- Upload throughput (Mbps)
- Latency / ping (ms)

## Success criteria
- A user can start the API, run the poller, open the dashboard, and see live data
  within a few minutes.
- Measurements persist across restarts.

## Future ideas
- Threshold-based alerting (email/Slack/webhook).
- Scheduled exports / CSV download.
- Multiple named probes and per-probe comparison.
- Real speed-test provider integration (e.g. Ookla, Cloudflare) selectable via config.
