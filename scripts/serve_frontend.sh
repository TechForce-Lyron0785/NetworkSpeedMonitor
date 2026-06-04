#!/usr/bin/env bash
# Serve the static frontend dashboard.
set -euo pipefail

cd "$(dirname "$0")/../frontend"

PORT="${NSM_FRONTEND_PORT:-8080}"

exec python -m http.server "$PORT"
