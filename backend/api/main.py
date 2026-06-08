import sqlite3
import sys
from datetime import datetime, timedelta
from fastapi import FastAPI, Query, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os

try:
    from backend.api.database import init_db
except ImportError:
    from database import init_db

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "speedmon.db")

app = FastAPI(title="Network Speed Monitor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:8000"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    origin = request.headers.get("origin")
    allowed_origins = {"http://127.0.0.1:5173", "http://localhost:5173"}
    if request.method == "OPTIONS":
        headers = {}
        if origin in allowed_origins:
            headers = {
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
            }
        return Response(status_code=200, headers=headers)

    response = await call_next(request)
    if origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


# Pydantic models
class SpeedPoint(BaseModel):
    time: str
    download: float
    upload: Optional[float] = None


class DailyResponse(BaseModel):
    date: str
    samples: List[SpeedPoint]
    worst_15min: Optional[dict] = None


class WeeklyResponse(BaseModel):
    week_start: str
    days: List[DailyResponse]


class WorstWindow(BaseModel):
    window_start: str
    avg_download: float
    min_download: float
    sample_count: int


# Helper: get database connection
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.on_event("startup")
def startup_event():
    init_db()


def get_minute_aggregates(date_str: str):
    """Return minute-resolution data for a single day."""
    conn = get_db()
    # Parse as local date and convert to local datetime bounds
    start_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    start = datetime.combine(start_date, datetime.min.time())
    end = start + timedelta(days=1)
    query = """
        SELECT
            strftime('%H:%M', datetime(timestamp, 'localtime')) as minute,
            AVG(download_mbps) as avg_download,
            AVG(upload_mbps) as avg_upload
        FROM speed_samples
        WHERE date(datetime(timestamp, 'localtime')) = ?
        GROUP BY minute
        ORDER BY minute
    """
    cursor = conn.execute(query, (date_str,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "time": row["minute"],
            "download": round(row["avg_download"], 1),
            "upload": round(row["avg_upload"] or 0, 1),
        }
        for row in rows
    ]


def get_15min_worst(date_str: str, limit=5):
    """Return worst 15-min windows for a day."""
    conn = get_db()
    query = """
        SELECT
            strftime('%H:%M',
                datetime(
                    (strftime('%s',
                        datetime(timestamp, 'localtime'),
                        'utc') / 900) * 900,
                    'unixepoch',
                    'localtime'
                )
            ) as window_start,
            AVG(download_mbps) as avg_down,
            MIN(download_mbps) as min_down,
            COUNT(*) as samples
        FROM speed_samples
        WHERE date(datetime(timestamp, 'localtime')) = ?
        GROUP BY window_start
        ORDER BY avg_down ASC
        LIMIT ?
    """
    cursor = conn.execute(query, (date_str, limit))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "window_start": row["window_start"],
            "avg_download": round(row["avg_down"], 1),
            "min_download": round(row["min_down"], 1),
            "samples": row["samples"],
        }
        for row in rows
    ]


@app.get("/daily", response_model=DailyResponse)
async def get_daily(date: str = Query(..., description="YYYY-MM-DD")):
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(400, "Invalid date format. Use YYYY-MM-DD")
    samples = get_minute_aggregates(date)
    worst_windows = get_15min_worst(date, limit=1)
    worst = worst_windows[0] if worst_windows else None
    return DailyResponse(date=date, samples=samples, worst_15min=worst)


@app.get("/week", response_model=WeeklyResponse)
async def get_week(start_date: str = Query(..., description="Monday YYYY-MM-DD")):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(400, "Invalid date format")
    days = []
    for i in range(7):
        day = start + timedelta(days=i)
        date_str = day.strftime("%Y-%m-%d")
        samples = get_minute_aggregates(date_str)
        days.append(DailyResponse(date=date_str, samples=samples, worst_15min=None))
    return WeeklyResponse(week_start=start_date, days=days)


@app.get("/worst-times")
async def get_worst_times(
    period: str = Query("day", regex="^(day|week)$"), date: Optional[str] = None
):
    if period == "day":
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        windows = get_15min_worst(date, limit=5)
        return {"period": "day", "date": date, "worst_windows": windows}
    else:
        # Week: return worst per day (simplified)
        conn = get_db()
        # Get last 7 days
        end = datetime.now()
        start = end - timedelta(days=7)
        query = """
            SELECT
                date(datetime(timestamp, 'localtime')) as day,
                strftime('%H:%M', datetime(
                    (strftime('%s',
                        datetime(timestamp, 'localtime'),
                        'utc') / 900) * 900,
                    'unixepoch',
                    'localtime'
                )) as window_start,
                AVG(download_mbps) as avg_down
            FROM speed_samples
            WHERE datetime(timestamp, 'localtime') >= ?
                AND datetime(timestamp, 'localtime') < ?
            GROUP BY day, window_start
            ORDER BY avg_down ASC
            LIMIT 10
        """
        cursor = conn.execute(query, (start, end))
        rows = cursor.fetchall()
        conn.close()
        return {"period": "week", "worst_windows": [dict(row) for row in rows]}


@app.get("/health")
async def health():
    conn = get_db()
    cursor = conn.execute(
        "SELECT strftime('%Y-%m-%d %H:%M:%f', MAX(timestamp), 'localtime')"
        " as last, COUNT(*) as total"
        " FROM speed_samples"
    )
    row = cursor.fetchone()
    conn.close()
    return {"status": "ok", "last_sample": row["last"], "total_samples": row["total"]}


# Mount static files at the end so API routes are registered first
if getattr(sys, "frozen", False):
    static_dir = os.path.join(sys._MEIPASS, "static")
else:
    static_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "frontend", "dist"
    )

if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)