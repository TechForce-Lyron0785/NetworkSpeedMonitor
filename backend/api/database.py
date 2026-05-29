# backend/api/database.py
import sqlite3
import os
import logging
from datetime import datetime

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "speedmon.db")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """Create database directory, tables, and indexes if they don't exist."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable WAL mode for concurrency (poller writes, API reads)
    cursor.execute("PRAGMA journal_mode=WAL")
    
    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS speed_samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            download_mbps REAL NOT NULL,
            upload_mbps REAL,
            latency_ms INTEGER,
            adapter_name TEXT,
            adapter_hardware_id TEXT
        )
    """)
    
    # Create index
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_timestamp ON speed_samples(timestamp)"
    )
    
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")


def insert_sample(
    download_mbps, upload_mbps, latency_ms, adapter_name,
    adapter_hardware_id=None
):
    """Insert one speed test result."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO speed_samples
        (timestamp, download_mbps, upload_mbps, latency_ms,
         adapter_name, adapter_hardware_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now(), download_mbps, upload_mbps,
        latency_ms, adapter_name, adapter_hardware_id
    ))
    conn.commit()
    rowid = cursor.lastrowid
    conn.close()
    return rowid


def get_last_sample_time():
    """Return datetime of most recent sample, or None."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(timestamp) FROM speed_samples")
    result = cursor.fetchone()[0]
    conn.close()
    return result


# Quick test if run directly
if __name__ == "__main__":
    init_db()
    print("Database ready. Last sample", get_last_sample_time())
