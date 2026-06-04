#!/usr/bin/env bash
# Run the NetworkSpeedMonitor poller.
# Pass extra args through, e.g. ./scripts/run_poller.sh --once --simulate
set -euo pipefail

cd "$(dirname "$0")/.."

exec python -m backend.poller.poller "$@"
