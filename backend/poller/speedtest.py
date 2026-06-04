"""
Measure internet speed through a specific physical adapter.
Uses Cloudflare speed test endpoints with source address binding.
"""
import time
import socket
import requests
from requests.adapters import HTTPAdapter
import logging
import psutil

logger = logging.getLogger(__name__)

# Cloudflare test endpoints
DOWNLOAD_URL = "https://speed.cloudflare.com/__down?bytes=10485760"  # 10 MB
UPLOAD_URL = "https://speed.cloudflare.com/__up"


class SourceAddressAdapter(HTTPAdapter):
    """Requests adapter that binds to a specific source IP address."""
    def __init__(self, source_address, **kwargs):
        self.source_address = (source_address, 0)
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['source_address'] = self.source_address
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs['source_address'] = self.source_address
        return super().proxy_manager_for(*args, **kwargs)


def get_adapter_ip(adapter_name: str) -> str:
    """
    Get the IPv4 address of a network adapter by name.
    Returns None if not found.
    """
    addrs = psutil.net_if_addrs()
    if adapter_name not in addrs:
        return None
    for addr in addrs[adapter_name]:
        if addr.family == socket.AF_INET:  # IPv4
            return addr.address
    return None


def measure_download(session, timeout=30) -> float:
    """Measure download speed in Mbps. Returns 0 on failure."""
    try:
        start = time.time()
        response = session.get(DOWNLOAD_URL, stream=True, timeout=timeout)
        total_bytes = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                total_bytes += len(chunk)
        elapsed = time.time() - start
        if elapsed > 0:
            mbps = (total_bytes * 8) / (elapsed * 1_000_000)
            return round(mbps, 2)
        return 0
    except Exception as e:
        logger.error(f"Download test failed: {e}")
        return 0


def measure_upload(session, timeout=30) -> float:
    """Measure upload speed in Mbps. Sends 10 MB of data."""
    try:
        # Generate 10 MB of random data
        data = b'X' * (10 * 1024 * 1024)  # 10 MB
        start = time.time()
        session.post(UPLOAD_URL, data=data, timeout=timeout)
        elapsed = time.time() - start
        if elapsed > 0:
            mbps = (10 * 8) / elapsed  # 10 MB * 8 bits / seconds
            return round(mbps, 2)
        return 0
    except Exception as e:
        logger.error(f"Upload test failed: {e}")
        return 0


def measure_latency(session) -> float:
    """Measure latency by sending a small GET request."""
    try:
        start = time.time()
        session.get("https://speed.cloudflare.com/__down?bytes=1", timeout=10)
        elapsed = (time.time() - start) * 1000  # ms
        return round(elapsed, 2)
    except Exception:
        return 999


def measure_speed(adapter_name: str) -> dict:
    """
    Perform download, upload, and latency tests through the physical adapter.
    Returns dict with keys: download_mbps, upload_mbps, latency_ms
    """
    ip = get_adapter_ip(adapter_name)
    if not ip:
        logger.error(f"Cannot get IP for adapter {adapter_name}")
        return {"download_mbps": 0, "upload_mbps": 0, "latency_ms": 999}

    logger.info(f"Binding to source IP: {ip}")
    session = requests.Session()
    adapter = SourceAddressAdapter(ip)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    # Run tests
    download = measure_download(session)
    upload = measure_upload(session)
    latency = measure_latency(session)

    logger.info(
        f"Results: {download} Mbps down, {upload} Mbps up, {latency} ms"
    )
    return {
        "download_mbps": download,
        "upload_mbps": upload,
        "latency_ms": latency
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Test with a known adapter name (from adapter.py)
    name = "Ethernet"  # change to your adapter
    result = measure_speed(name)
    print(result)
