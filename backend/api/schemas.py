"""Pydantic schemas for the NetworkSpeedMonitor API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MeasurementCreate(BaseModel):
    """Payload for creating a measurement."""

    download_mbps: float = Field(..., ge=0, description="Download speed in Mbps")
    upload_mbps: float = Field(..., ge=0, description="Upload speed in Mbps")
    ping_ms: float = Field(..., ge=0, description="Latency in milliseconds")
    server: str | None = Field(default=None, description="Server/target used")
    timestamp: datetime | None = Field(
        default=None, description="Measurement time (defaults to now, UTC)"
    )


class Measurement(BaseModel):
    """A measurement as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    download_mbps: float
    upload_mbps: float
    ping_ms: float
    server: str | None = None


class Stats(BaseModel):
    """Aggregate statistics over stored measurements."""

    count: int
    avg_download_mbps: float | None = None
    avg_upload_mbps: float | None = None
    avg_ping_ms: float | None = None
    max_download_mbps: float | None = None
    max_upload_mbps: float | None = None
    min_ping_ms: float | None = None
    latest: Measurement | None = None
