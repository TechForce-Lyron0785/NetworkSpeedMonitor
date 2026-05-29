# backend/poller/poller.py
import random
import time
import logging
import sys
import socket
import psutil

# Add parent directory to path to import database module
sys.path.append(".")
from backend.api.database import insert_sample, init_db  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("poller.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Poller")


class SpeedMonitorPoller:
    def __init__(self):
        self.running = True
        self.adapter_name = "Ethernet (Stub)"
        init_db()

    def get_physical_adapter(self):
        """Return the best active physical network adapter name."""
        virtual_markers = (
            "vpn", "virtual", "vmware", "virtualbox", "hyper-v", "vethernet",
            "loopback", "tunnel", "tap", "tun", "wireguard", "tailscale",
            "zerotier", "hamachi", "bluetooth", "npcap", "wintun"
        )
        preferred_markers = (
            "ethernet", "wi-fi", "wifi", "wireless", "wlan", "lan"
        )

        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()
        candidates = []

        for name, iface_stats in stats.items():
            lowered = name.lower()
            if (
                not iface_stats.isup or
                lowered.startswith("lo") or
                any(marker in lowered for marker in virtual_markers)
            ):
                continue

            has_ipv4 = any(
                addr.family == socket.AF_INET and
                not addr.address.startswith(("127.", "169.254."))
                for addr in addrs.get(name, ())
            )
            if not has_ipv4:
                continue

            score = 0
            if any(marker in lowered for marker in preferred_markers):
                score += 10
            if iface_stats.speed and iface_stats.speed > 0:
                score += min(iface_stats.speed, 10000) / 1000
            candidates.append((score, name))

        if not candidates:
            return None

        candidates.sort(reverse=True)
        self.adapter_name = candidates[0][1]
        return self.adapter_name

    def measure_speed(self, adapter_name):
        """Stub: return fake speed data between 10 and 100 Mbps."""
        # Simulate random speed measurement
        download = random.uniform(10.0, 100.0)
        upload = random.uniform(5.0, 50.0)
        latency = random.randint(10, 50)
        logger.info(
            f"Stub measurement: {download:.1f} Mbps down,"
            f" {upload:.1f} up, {latency} ms"
        )
        return {
            "download_mbps": download,
            "upload_mbps": upload,
            "latency_ms": latency
        }

    def run_once(self):
        """Single polling cycle."""
        adapter = self.get_physical_adapter()
        if not adapter:
            logger.warning("No physical adapter found. Skipping cycle.")
            return
        data = self.measure_speed(adapter)
        insert_sample(
            download_mbps=data["download_mbps"],
            upload_mbps=data["upload_mbps"],
            latency_ms=data["latency_ms"],
            adapter_name=adapter,
            adapter_hardware_id="stub"
        )
        logger.info("Sample saved to database.")

    def run_forever(self):
        """Main loop with random interval 3-5 minutes."""
        logger.info("Poller started (stub mode).")
        while self.running:
            self.run_once()
            interval = random.randint(180, 300)  # seconds
            logger.info(f"Sleeping for {interval} seconds...")
            time.sleep(interval)
        logger.info("Poller stopped.")

    def stop(self):
        self.running = False


if __name__ == "__main__":
    poller = SpeedMonitorPoller()
    try:
        poller.run_forever()
    except KeyboardInterrupt:
        poller.stop()
        logger.info("Exited by user.")
