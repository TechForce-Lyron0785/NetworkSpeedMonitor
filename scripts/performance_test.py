import psutil
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("perf")


def monitor_poller(pid_file="poller.pid", duration_hours=24):
    # Assume poller is running; you'd manually run it
    logger.info(
        "Manual performance test: run poller in background, "
        "check memory every hour"
    )
    # For automated: find process by name
    process = None
    for proc in psutil.process_iter(['pid', 'name']):
        if (proc.info['name'] == 'python.exe' and
                'poller.py' in ' '.join(proc.cmdline())):
            process = proc
            break
    if not process:
        logger.error("Poller process not found")
        return
    logger.info(f"Monitoring poller PID {process.pid}")
    for i in range(duration_hours):
        mem_info = process.memory_info()
        cpu = process.cpu_percent(interval=1)
        logger.info(
            f"Hour {i+1}: RSS={mem_info.rss / 1024 / 1024:.2f} MB, "
            f"CPU={cpu}%"
        )
        time.sleep(3600)
    logger.info("Monitoring complete.")


if __name__ == "__main__":
    monitor_poller()
