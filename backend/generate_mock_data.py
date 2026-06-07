"""
Generate mock network speed data for testing.
Fills data from 2026-05-01 to 2026-06-04.
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

# Database path
DB_PATH = os.path.join("data", "speedmon.db")


def generate_realistic_speed(hour):
    """
    Generate realistic speed based on time of day.
    Peak hours (6-9 AM, 6-11 PM) have slower speeds.
    """
    # Base speeds
    base_download = 100.0  # Mbps
    base_upload = 50.0  # Mbps
    base_latency = 15.0  # ms

    # Peak hours slowdown factor
    if (6 <= hour < 9) or (18 <= hour < 23):
        factor = random.uniform(0.3, 0.6)  # Slower during peak
    elif 9 <= hour < 17:
        factor = random.uniform(0.8, 1.0)  # Normal business hours
    else:
        factor = random.uniform(0.9, 1.1)  # Off-peak (fastest)

    download_speed = base_download * factor + random.uniform(-10, 10)
    upload_speed = base_upload * factor + random.uniform(-5, 5)
    latency = base_latency / factor + random.uniform(-5, 10)

    return {
        "download_speed": max(25.0, download_speed),  # Minimum 25 Mbps
        "upload_speed": max(15.0, upload_speed),  # Minimum 15 Mbps
        "latency": max(5.0, latency),  # Minimum 5 ms
    }


def main():
    """Generate mock data from 2026-05-01 to 2026-06-04."""
    print("Generating mock network speed data...")
    print("=" * 50)

    # Ensure database exists
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Date range
    start_date = datetime(2026, 5, 1)
    end_date = datetime(2026, 6, 4)

    current_date = start_date
    total_samples = 0

    while current_date <= end_date:
        print(f"Generating data for {current_date.strftime('%Y-%m-%d')}...")

        # Generate samples every 15 minutes
        for hour in range(24):
            for minute in range(0, 60, 15):
                timestamp = current_date.replace(hour=hour, minute=minute)

                # Generate realistic speed data
                speed_data = generate_realistic_speed(hour)

                # Insert sample
                cursor.execute(
                    """
                    INSERT INTO speed_samples
                    (timestamp, download_mbps, upload_mbps, latency_ms,
                     adapter_name, adapter_hardware_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        timestamp,
                        speed_data["download_speed"],
                        speed_data["upload_speed"],
                        int(speed_data["latency"]),
                        "Ethernet Adapter",
                        "HWID-1234",
                    ),
                )

                total_samples += 1

        current_date += timedelta(days=1)

    conn.commit()
    conn.close()

    print("=" * 50)
    print("Mock data generation complete!")
    print(f"Total samples inserted: {total_samples}")
    print(
        f"Date range: {start_date.strftime('%Y-%m-%d')}"
        f" to {end_date.strftime('%Y-%m-%d')}"
    )
    print(f"Database location: {DB_PATH}")


if __name__ == "__main__":
    main()
