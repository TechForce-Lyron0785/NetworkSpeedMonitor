# NetworkSpeedMonitor — Technical Spec

## Architecture
```
+-----------+      POST /measurements      +-----------+      SQL      +---------+
|  Poller   |  -------------------------->  |    API    |  --------->   | SQLite  |
| (python)  |                              | (FastAPI) |  <---------    |   DB    |
+-----------+                              +-----------+      rows      +---------+
                                                 ^
                                                 | GET /measurements, /stats
                                                 |
                                           +-----------+
                                           | Frontend  |  (static HTML + Chart.js)
                                           +-----------+
```

Three decoupled components communicate over HTTP. The poller and frontend are
both just HTTP clients of the API, so either can be swapped or scaled
independently.

## Components

### Backend API (`backend/api`)
- **Framework:** FastAPI + Uvicorn.
- **Storage:** SQLAlchemy 2.0 ORM over SQLite (path via `NSM_DATABASE_URL`).
- **Model:** `Measurement(id, timestamp, download_mbps, upload_mbps, ping_ms, server)`.
- **Endpoints:**
  - `GET /health` → `{"status": "ok"}`
  - `POST /measurements` → create a measurement (201). Body validated by Pydantic
    (`download_mbps`, `upload_mbps`, `ping_ms` must be ≥ 0; optional `server`,
    `timestamp`).
  - `GET /measurements?limit=N` → most recent N, returned oldest-first for charts.
  - `GET /measurements/{id}` → single measurement (404 if missing).
  - `GET /stats` → count + avg/max/min aggregates + latest measurement.
- **CORS:** open (`*`) so the static dashboard can call the API from any origin.
- Tables are created on startup via the lifespan handler (`init_db`).

### Poller (`backend/poller`)
- `measure.py` — `measure(simulate: bool)` returns a `Sample`.
  - **Real mode:** HTTP-based measurement using `httpx` — times a download stream,
    a fixed-size upload POST, and a small request for ping. Targets configurable
    (default Cloudflare speed endpoints). Falls back to simulated on `httpx.HTTPError`.
  - **Simulated mode:** random plausible values; deterministic with a seeded RNG
    (used by tests/CI/demos).
- `poller.py` — CLI loop. `record()` POSTs a sample to the API.
  - Flags: `--api`, `--interval`, `--simulate`, `--once`.
  - Env: `NSM_API_URL`, `NSM_POLL_INTERVAL`.

### Frontend (`frontend`)
- Static `index.html` + `app.js` + `styles.css`; no build step.
- Chart.js (CDN) renders two line charts (download/upload, ping) plus stat cards.
- Configurable API URL field; auto-refreshes every 15s and on demand.

## Configuration
| Variable | Default | Used by |
| --- | --- | --- |
| `NSM_DATABASE_URL` | `sqlite:///./network_speed_monitor.db` | API |
| `NSM_API_HOST` / `NSM_API_PORT` | `0.0.0.0` / `8000` | `scripts/run_api.sh` |
| `NSM_API_URL` | `http://localhost:8000` | Poller |
| `NSM_POLL_INTERVAL` | `60` | Poller |
| `NSM_FRONTEND_PORT` | `8080` | `scripts/serve_frontend.sh` |

## Local development
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements-dev.txt

./scripts/run_api.sh                       # API on :8000
./scripts/run_poller.sh --once --simulate  # write one sample
./scripts/serve_frontend.sh                # dashboard on :8080
```

## Testing & quality
- `pytest` (`backend/tests`) covers API endpoints (via FastAPI `TestClient` with a
  temp SQLite DB and `dependency_overrides`) and the poller/measurement logic
  (network calls mocked).
- `ruff` for lint/format. Config in `backend/pyproject.toml`.
- CI (`.github/workflows/ci.yml`) runs ruff + pytest on push/PR.
