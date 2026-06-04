"""Poller: periodically measures network speed and records it via the API.

Usage:
    python -m backend.poller.poller --interval 60 --api http://localhost:8000
    python -m backend.poller.poller --once --simulate
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time

import httpx

from backend.poller.measure import Sample, measure

logger = logging.getLogger("nsm.poller")


def record(sample: Sample, api_url: str, timeout: float = 10.0) -> bool:
    """POST a sample to the API. Returns True on success."""
    url = api_url.rstrip("/") + "/measurements"
    try:
        resp = httpx.post(url, json=sample.as_payload(), timeout=timeout)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error("Failed to record measurement: %s", exc)
        return False
    return True


def run(
    api_url: str,
    interval: float,
    simulate: bool,
    once: bool,
) -> None:
    """Run the polling loop."""
    while True:
        sample = measure(simulate=simulate)
        ok = record(sample, api_url)
        logger.info(
            "down=%.1f Mbps up=%.1f Mbps ping=%.1f ms recorded=%s",
            sample.download_mbps,
            sample.upload_mbps,
            sample.ping_ms,
            ok,
        )
        if once:
            return
        time.sleep(interval)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NetworkSpeedMonitor poller")
    parser.add_argument(
        "--api",
        default=os.environ.get("NSM_API_URL", "http://localhost:8000"),
        help="Base URL of the NetworkSpeedMonitor API",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=float(os.environ.get("NSM_POLL_INTERVAL", "60")),
        help="Seconds between measurements",
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Use simulated measurements instead of real network tests",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Take a single measurement and exit",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    args = build_parser().parse_args(argv)
    try:
        run(args.api, args.interval, args.simulate, args.once)
    except KeyboardInterrupt:
        logger.info("Stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
