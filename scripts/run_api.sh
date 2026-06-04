#!/usr/bin/env bash
# Start the NetworkSpeedMonitor API.
set -euo pipefail

cd "$(dirname "$0")/.."

HOST="${NSM_API_HOST:-0.0.0.0}"
PORT="${NSM_API_PORT:-8000}"

exec uvicorn backend.api.main:app --host "$HOST" --port "$PORT" --reload
