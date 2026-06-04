"""Tests for the NetworkSpeedMonitor API."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.api import models
from backend.api.database import Base, get_db
from backend.api.main import app


@pytest.fixture()
def client(tmp_path):
    """Provide a TestClient backed by a fresh temporary SQLite database."""
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_models_registered():
    assert models.Measurement.__tablename__ == "measurements"


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_create_and_list_measurement(client):
    payload = {"download_mbps": 100.5, "upload_mbps": 20.1, "ping_ms": 12.3}
    resp = client.post("/measurements", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] > 0
    assert body["download_mbps"] == 100.5
    assert body["timestamp"]

    resp = client.get("/measurements")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["upload_mbps"] == 20.1


def test_list_is_chronological(client):
    for dl in (10, 20, 30):
        client.post(
            "/measurements",
            json={"download_mbps": dl, "upload_mbps": 5, "ping_ms": 9},
        )
    items = client.get("/measurements").json()
    downloads = [m["download_mbps"] for m in items]
    assert downloads == [10, 20, 30]  # oldest first


def test_get_measurement_404(client):
    assert client.get("/measurements/999").status_code == 404


def test_validation_rejects_negative(client):
    resp = client.post(
        "/measurements",
        json={"download_mbps": -1, "upload_mbps": 5, "ping_ms": 9},
    )
    assert resp.status_code == 422


def test_stats_empty(client):
    stats = client.get("/stats").json()
    assert stats["count"] == 0
    assert stats["latest"] is None


def test_stats_aggregates(client):
    samples = [
        {"download_mbps": 100, "upload_mbps": 10, "ping_ms": 20},
        {"download_mbps": 200, "upload_mbps": 30, "ping_ms": 10},
    ]
    for s in samples:
        client.post("/measurements", json=s)

    stats = client.get("/stats").json()
    assert stats["count"] == 2
    assert stats["avg_download_mbps"] == 150
    assert stats["max_download_mbps"] == 200
    assert stats["min_ping_ms"] == 10
    assert stats["latest"]["download_mbps"] == 200
