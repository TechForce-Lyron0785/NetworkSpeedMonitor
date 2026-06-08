"""
Measure internet speed through a specific physical adapter.
Uses Cloudflare speed test endpoints with source address binding.
"""

import time
import socket
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
import psutil
import ssl
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings for VMware environments
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)

# Multiple test endpoints for fallback
TEST_ENDPOINTS = [
    {
        "name": "Cloudflare",
        "download": "https://speed.cloudflare.com/__down?bytes=10485760",
        "upload": "https://speed.cloudflare.com/__up",
        "ping": "https://speed.cloudflare.com/__down?bytes=1"
    },
    {
        "name": "Fast.com", 
        "download": "http://ipv4.download.thinkbroadband.com/10MB.zip",
        "upload": "http://httpbin.org/post",
        "ping": "http://httpbin.org/get"
    },
    {
        "name": "SpeedOf.Me",
        "download": "http://www.speedof.me/empty.jpg?r=5",
        "upload": "http://httpbin.org/post",
        "ping": "http://www.speedof.me/"
    }
]


class SourceAddressAdapter(HTTPAdapter):
    """Requests adapter that binds to a specific source IP address with SSL handling."""

    def __init__(self, source_address, **kwargs):
        self.source_address = (source_address, 0)
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs["source_address"] = self.source_address
        # Add SSL context for VMware compatibility
        kwargs["ssl_context"] = ssl.create_default_context()
        kwargs["ssl_context"].check_hostname = False
        kwargs["ssl_context"].verify_mode = ssl.CERT_NONE
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs["source_address"] = self.source_address
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


def create_session(source_ip: str) -> requests.Session:
    """Create a requests session with VMware-compatible settings."""
    session = requests.Session()
    
    # Configure retries
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = SourceAddressAdapter(source_ip, max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set headers to appear as a regular browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': '*/*',
        'Connection': 'keep-alive'
    })
    
    # Disable SSL verification for VMware environments
    session.verify = False
    
    return session


def measure_download(session, endpoint, timeout=30) -> float:
    """Measure download speed in Mbps. Returns 0 on failure."""
    try:
        start = time.time()
        response = session.get(endpoint["download"], stream=True, timeout=timeout)
        response.raise_for_status()
        
        total_bytes = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                total_bytes += len(chunk)
        
        elapsed = time.time() - start
        if elapsed > 0 and total_bytes > 0:
            mbps = (total_bytes * 8) / (elapsed * 1_000_000)
            return round(mbps, 2)
        return 0
    except Exception as e:
        logger.error(f"Download test failed for {endpoint['name']}: {e}")
        return 0


def measure_upload(session, endpoint, timeout=30) -> float:
    """Measure upload speed in Mbps. Sends data to endpoint."""
    try:
        # Generate 1 MB of data for VM compatibility
        data = b"X" * (1 * 1024 * 1024)  # 1 MB
        start = time.time()
        response = session.post(endpoint["upload"], data=data, timeout=timeout)
        elapsed = time.time() - start
        
        if elapsed > 0:
            mbps = (1 * 8) / elapsed  # 1 MB * 8 bits / seconds
            return round(mbps, 2)
        return 0
    except Exception as e:
        logger.error(f"Upload test failed for {endpoint['name']}: {e}")
        return 0


def measure_latency(session, endpoint) -> float:
    """Measure latency by sending a small GET request."""
    try:
        start = time.time()
        response = session.get(endpoint["ping"], timeout=10)
        elapsed = (time.time() - start) * 1000  # ms
        return round(elapsed, 2)
    except Exception:
        return 999


def measure_speed(adapter_name: str) -> dict:
    """
    Perform download, upload, and latency tests through the physical adapter.
    Uses fallback endpoints for VMware compatibility.
    Returns dict with keys: download_mbps, upload_mbps, latency_ms
    """
    ip = get_adapter_ip(adapter_name)
    if not ip:
        logger.error(f"Cannot get IP for adapter {adapter_name}")
        return {"download_mbps": 0, "upload_mbps": 0, "latency_ms": 999}

    logger.info(f"Binding to source IP: {ip}")
    
    # Try each endpoint until one works
    for endpoint in TEST_ENDPOINTS:
        logger.info(f"Testing with {endpoint['name']}...")
        try:
            session = create_session(ip)
            
            # Test connectivity first
            test_response = session.get(endpoint["ping"], timeout=5)
            if test_response.status_code != 200:
                continue
                
            # Run actual tests
            download = measure_download(session, endpoint)
            upload = measure_upload(session, endpoint) 
            latency = measure_latency(session, endpoint)
            
            # If we got reasonable results, return them
            if download > 0:
                logger.info(f"Results via {endpoint['name']}: {download} Mbps down, {upload} Mbps up, {latency} ms")
                return {"download_mbps": download, "upload_mbps": upload, "latency_ms": latency}
            
        except Exception as e:
            logger.warning(f"Failed to test with {endpoint['name']}: {e}")
            continue
    
    # If all endpoints failed, return zeros
    logger.error("All speed test endpoints failed")
    return {"download_mbps": 0, "upload_mbps": 0, "latency_ms": 999}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Test with a known adapter name (from adapter.py)
    name = "Ethernet"  # change to your adapter
    result = measure_speed(name)
    print(result)
