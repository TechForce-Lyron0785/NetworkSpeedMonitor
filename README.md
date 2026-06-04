# NetworkSpeedMonitor

A lightweight, self-hosted tool that continuously measures your internet
connection (download, upload, latency) and visualizes the trends over time.

It has three decoupled parts:

- **API** (`backend/api`) — FastAPI service that stores measurements in SQLite.
- **Poller** (`backend/poller`) — periodically runs a speed test and records it
  via the API. Supports a `--simulate` mode that needs no network.
- **Dashboard** (`frontend`) — static HTML + Chart.js page showing speed/ping
  charts and latest/aggregate stats.

See [docs/prd.md](docs/prd.md) and [docs/technical-spec.md](docs/technical-spec.md)
for details.

## Quick start

```bash
# 1. Install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements-dev.txt

# 2. Start the API (http://localhost:8000, docs at /docs)
./scripts/run_api.sh

# 3. In another terminal, take measurements
./scripts/run_poller.sh --once --simulate          # one simulated sample
./scripts/run_poller.sh --interval 60              # real test every 60s

# 4. Serve the dashboard (http://localhost:8080)
./scripts/serve_frontend.sh
```

Open the dashboard, confirm the **API URL** field points at your API
(`http://localhost:8000`), and click **Refresh**.

## API

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Liveness probe |
| POST | `/measurements` | Record a measurement |
| GET | `/measurements?limit=N` | Recent measurements (oldest first) |
| GET | `/measurements/{id}` | Single measurement |
| GET | `/stats` | Count + avg/max/min aggregates + latest |

Interactive API docs are available at `http://localhost:8000/docs`.

## Configuration

| Variable | Default | Used by |
| --- | --- | --- |
| `NSM_DATABASE_URL` | `sqlite:///./network_speed_monitor.db` | API |
| `NSM_API_HOST` / `NSM_API_PORT` | `0.0.0.0` / `8000` | API script |
| `NSM_API_URL` | `http://localhost:8000` | Poller |
| `NSM_POLL_INTERVAL` | `60` | Poller |
| `NSM_FRONTEND_PORT` | `8080` | Frontend script |

## Development

```bash
source .venv/bin/activate
cd backend
ruff check .     # lint
pytest -q        # tests
```
