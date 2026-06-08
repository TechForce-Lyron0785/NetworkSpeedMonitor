#!/usr/bin/env python
"""
Unified entry point for PyInstaller bundle.
Starts FastAPI server in a background thread, then starts the poller.
"""
import threading
import uvicorn
import time
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_api():
    from backend.api.main import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")


def run_poller():
    from backend.poller.poller import SpeedMonitorPoller
    poller = SpeedMonitorPoller()
    poller.run_forever()


if __name__ == "__main__":
    # Start API in daemon thread
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    # Wait a moment for API to initialize
    time.sleep(2)

    # Run poller in main thread (it handles its own shutdown signals)
    run_poller()
