# backend/poller/poller.py
import os
import random
import signal
import sys
import time
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.poller.adapter import get_physical_adapter  # noqa: E402
from backend.poller.speedtest import measure_speed, get_adapter_ip  # noqa: E402
from backend.api.database import insert_sample, init_db  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("poller.log"), logging.StreamHandler()],
)
logger = logging.getLogger("Poller")


class SpeedMonitorPoller:
    def __init__(self):
        self.running = True
        init_db()
        # Register signal for Windows service stop
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)
        # On Windows, nssm sends CTRL_BREAK
        signal.signal(signal.SIGBREAK, self.shutdown)

    def shutdown(self, signum, frame):
        logger.info(f"Received signal {signum}. Shutting down...")
        self.running = False

    def run_once(self):
        """Single polling cycle."""
        adapter_name, adapter_hwid = get_physical_adapter()
        if not adapter_name:
            logger.warning("No physical adapter found. Skipping this cycle.")
            return

        ip = get_adapter_ip(adapter_name)
        if not ip:
            logger.warning(f"Adapter {adapter_name} has no IP. Skipping.")
            return

        logger.info(f"Testing on adapter: {adapter_name} ({ip})")
        data = measure_speed(adapter_name)

        if data["download_mbps"] > 0:
            insert_sample(
                download_mbps=data["download_mbps"],
                upload_mbps=data["upload_mbps"],
                latency_ms=data["latency_ms"],
                adapter_name=adapter_name,
                adapter_hardware_id=adapter_hwid,
            )
            logger.info("Sample saved.")
        else:
            logger.warning("Speed test failed (0 Mbps). Not saving.")

    def run_forever(self):
        logger.info("Poller started (real mode).")
        while self.running:
            self.run_once()
            interval = random.randint(180, 300)  # 3-5 minutes
            logger.info(f"Next poll in {interval} seconds.")
            time.sleep(interval)
        logger.info("Poller stopped.")


if __name__ == "__main__":
    poller = SpeedMonitorPoller()
    try:
        poller.run_forever()
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
        sys.exit(1)
