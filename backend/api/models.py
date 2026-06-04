"""ORM models for the NetworkSpeedMonitor API."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.api.database import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Measurement(Base):
    """A single network speed measurement sample."""

    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False, index=True
    )
    download_mbps: Mapped[float] = mapped_column(Float, nullable=False)
    upload_mbps: Mapped[float] = mapped_column(Float, nullable=False)
    ping_ms: Mapped[float] = mapped_column(Float, nullable=False)
    server: Mapped[str | None] = mapped_column(String(255), nullable=True)
