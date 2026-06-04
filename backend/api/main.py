"""FastAPI application for NetworkSpeedMonitor.

Stores network speed measurements and serves them to the dashboard.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.api import models, schemas
from backend.api.database import get_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="NetworkSpeedMonitor API",
    description="Stores and serves network speed measurements.",
    version="0.1.0",
    lifespan=lifespan,
)

# Allow the static frontend (served from any origin/file) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Simple liveness probe."""
    return {"status": "ok"}


@app.post("/measurements", response_model=schemas.Measurement, status_code=201)
def create_measurement(
    payload: schemas.MeasurementCreate, db: Session = Depends(get_db)
) -> models.Measurement:
    """Record a new speed measurement."""
    data = payload.model_dump(exclude_none=True)
    measurement = models.Measurement(**data)
    db.add(measurement)
    db.commit()
    db.refresh(measurement)
    return measurement


@app.get("/measurements", response_model=list[schemas.Measurement])
def list_measurements(
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> list[models.Measurement]:
    """Return the most recent measurements, oldest first (chart-friendly)."""
    rows = (
        db.query(models.Measurement)
        .order_by(models.Measurement.timestamp.desc())
        .limit(limit)
        .all()
    )
    return list(reversed(rows))


@app.get("/measurements/{measurement_id}", response_model=schemas.Measurement)
def get_measurement(
    measurement_id: int, db: Session = Depends(get_db)
) -> models.Measurement:
    """Return a single measurement by id."""
    measurement = db.get(models.Measurement, measurement_id)
    if measurement is None:
        raise HTTPException(status_code=404, detail="Measurement not found")
    return measurement


@app.get("/stats", response_model=schemas.Stats)
def get_stats(db: Session = Depends(get_db)) -> schemas.Stats:
    """Return aggregate statistics across all measurements."""
    count = db.query(func.count(models.Measurement.id)).scalar() or 0
    if count == 0:
        return schemas.Stats(count=0)

    avg_dl, avg_ul, avg_ping, max_dl, max_ul, min_ping = db.query(
        func.avg(models.Measurement.download_mbps),
        func.avg(models.Measurement.upload_mbps),
        func.avg(models.Measurement.ping_ms),
        func.max(models.Measurement.download_mbps),
        func.max(models.Measurement.upload_mbps),
        func.min(models.Measurement.ping_ms),
    ).one()

    latest = (
        db.query(models.Measurement)
        .order_by(models.Measurement.timestamp.desc())
        .first()
    )

    return schemas.Stats(
        count=count,
        avg_download_mbps=avg_dl,
        avg_upload_mbps=avg_ul,
        avg_ping_ms=avg_ping,
        max_download_mbps=max_dl,
        max_upload_mbps=max_ul,
        min_ping_ms=min_ping,
        latest=schemas.Measurement.model_validate(latest) if latest else None,
    )
