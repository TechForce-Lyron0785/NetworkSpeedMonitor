from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import random

app = FastAPI(title="Network Speed Monitor API")

# Allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
)

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


# Mock data generator
def generate_mock_daily(date_str: str):
    samples = []
    for hour in range(24):
        for minute in [0, 15, 30, 45]:
            download = random.uniform(20, 95)
            upload = download * 0.3
            samples.append(SpeedPoint(
                time=f"{hour:02d}:{minute:02d}",
                download=round(download, 1),
                upload=round(upload, 1)
            ))
    return samples


@app.get("/daily", response_model=DailyResponse)
async def get_daily(date: str = Query(..., description="YYYY-MM-DD")):
    """Stub: returns mock minute data."""
    samples = generate_mock_daily(date)
    return DailyResponse(date=date, samples=samples, worst_15min=None)


@app.get("/week", response_model=WeeklyResponse)
async def get_week(start_date: str = Query(..., description="YYYY-MM-DD")):
    week_start = datetime.strptime(start_date, "%Y-%m-%d")
    days = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        date_str = day.strftime("%Y-%m-%d")
        samples = generate_mock_daily(date_str)
        days.append(DailyResponse(date=date_str, samples=samples))
    return WeeklyResponse(week_start=start_date, days=days)


@app.get("/worst-times")
async def get_worst_times(period: str = "day", date: Optional[str] = None):
    return {"period": period, "worst_windows": []}


@app.get("/health")
async def health():
    return {"status": "ok", "last_sample": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)