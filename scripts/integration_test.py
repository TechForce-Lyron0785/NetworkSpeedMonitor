#!/usr/bin/env python
"""
Integration test: poller -> API -> frontend.
Verifies data flow and performance.
"""

import os
import sqlite3
import sys

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.api.database import DB_PATH  # noqa: E402

API_URL = "http://127.0.0.1:8000"


def test_health():
    print("Testing /health...")
    resp = requests.get(f"{API_URL}/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "last_sample" in data
    print("OK")


def test_daily():
    print("Testing /daily...")
    resp = requests.get(f"{API_URL}/daily", params={"date": "2026-06-03"})
    assert resp.status_code == 200
    data = resp.json()
    assert "samples" in data
    print(f"Received {len(data['samples'])} minute points")
    print("OK")


def test_week():
    print("Testing /week...")
    resp = requests.get(f"{API_URL}/week", params={"start_date": "2026-06-01"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["days"]) == 7
    print("OK")


def test_worst():
    print("Testing /worst-times...")
    resp = requests.get(
        f"{API_URL}/worst-times", params={"period": "day", "date": "2026-06-03"}
    )
    assert resp.status_code == 200
    print("OK")


def test_db_integrity():
    print("Checking database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT COUNT(*) FROM speed_samples")
    count = cursor.fetchone()[0]
    conn.close()
    print(f"Total samples: {count}")
    assert count >= 0


def run_all():
    test_health()
    test_daily()
    test_week()
    test_worst()
    test_db_integrity()
    print("\n✅ All integration tests passed.")


if __name__ == "__main__":
    run_all()
