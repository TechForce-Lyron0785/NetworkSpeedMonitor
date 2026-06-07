import requests
import time
from datetime import datetime

API_URL = "http://localhost:8000/health"
LOG_FILE = "monitor.log"


def log_status():
    try:
        resp = requests.get(API_URL, timeout=5)
        data = resp.json()
        with open(LOG_FILE, "a") as f:
            f.write(
                f"{datetime.now()} - OK - Last sample: {data['last_sample']}, "
                f"Total: {data['total_samples']}\n"
            )
    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"{datetime.now()} - ERROR - {e}\n")


if __name__ == "__main__":
    for _ in range(24):
        log_status()
        time.sleep(3600)