"""Network speed measurement.

Provides a real HTTP-based measurement and a deterministic-ish simulated
measurement for environments without outbound network access (e.g. CI, demos).
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass

import httpx

# A small, widely-available file used to estimate download throughput.
DEFAULT_DOWNLOAD_URL = "https://speed.cloudflare.com/__down?bytes=10000000"
# Cloudflare's speed-test upload endpoint accepts arbitrary POST bodies.
DEFAULT_UPLOAD_URL = "https://speed.cloudflare.com/__up"
DEFAULT_PING_URL = "https://www.cloudflare.com/cdn-cgi/trace"
_UPLOAD_BYTES = 2_000_000


@dataclass
class Sample:
    """A single measurement result."""

    download_mbps: float
    upload_mbps: float
    ping_ms: float
    server: str

    def as_payload(self) -> dict[str, float | str]:
        return {
            "download_mbps": round(self.download_mbps, 3),
            "upload_mbps": round(self.upload_mbps, 3),
            "ping_ms": round(self.ping_ms, 3),
            "server": self.server,
        }


def _mbps(num_bytes: int, seconds: float) -> float:
    if seconds <= 0:
        return 0.0
    return (num_bytes * 8) / seconds / 1_000_000


def measure_simulated(rng: random.Random | None = None) -> Sample:
    """Return a plausible random measurement without using the network."""
    rng = rng or random.Random()
    return Sample(
        download_mbps=rng.uniform(50, 500),
        upload_mbps=rng.uniform(10, 100),
        ping_ms=rng.uniform(5, 60),
        server="simulated",
    )


def measure_real(
    *,
    download_url: str = DEFAULT_DOWNLOAD_URL,
    upload_url: str = DEFAULT_UPLOAD_URL,
    ping_url: str = DEFAULT_PING_URL,
    timeout: float = 30.0,
) -> Sample:
    """Perform a real HTTP-based speed measurement.

    Raises httpx.HTTPError on network failure so the caller can decide how to
    handle it (e.g. fall back to simulated mode).
    """
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        # Ping: time a tiny request.
        ping_start = time.perf_counter()
        client.get(ping_url)
        ping_ms = (time.perf_counter() - ping_start) * 1000

        # Download: stream the body and time it.
        dl_bytes = 0
        dl_start = time.perf_counter()
        with client.stream("GET", download_url) as resp:
            resp.raise_for_status()
            for chunk in resp.iter_bytes():
                dl_bytes += len(chunk)
        download_mbps = _mbps(dl_bytes, time.perf_counter() - dl_start)

        # Upload: POST a fixed-size payload and time it.
        payload = b"0" * _UPLOAD_BYTES
        ul_start = time.perf_counter()
        client.post(upload_url, content=payload)
        upload_mbps = _mbps(len(payload), time.perf_counter() - ul_start)

    return Sample(
        download_mbps=download_mbps,
        upload_mbps=upload_mbps,
        ping_ms=ping_ms,
        server=download_url,
    )


def measure(simulate: bool = False) -> Sample:
    """Measure speed, falling back to simulated values on network errors."""
    if simulate:
        return measure_simulated()
    try:
        return measure_real()
    except httpx.HTTPError:
        return measure_simulated()
