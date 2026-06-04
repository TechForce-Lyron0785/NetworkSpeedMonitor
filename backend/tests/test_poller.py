"""Tests for the poller and measurement logic."""

from __future__ import annotations

import random

import httpx

from backend.poller import measure as measure_mod
from backend.poller.measure import Sample, measure, measure_simulated
from backend.poller.poller import record


def test_measure_simulated_is_in_range():
    sample = measure_simulated(random.Random(42))
    assert 0 < sample.download_mbps
    assert 0 < sample.upload_mbps
    assert 0 < sample.ping_ms
    assert sample.server == "simulated"


def test_measure_simulated_is_deterministic_with_seed():
    a = measure_simulated(random.Random(1))
    b = measure_simulated(random.Random(1))
    assert a == b


def test_sample_as_payload_rounds():
    sample = Sample(1.23456, 2.34567, 3.45678, "x")
    payload = sample.as_payload()
    assert payload["download_mbps"] == 1.235
    assert payload["server"] == "x"


def test_measure_falls_back_to_simulated_on_network_error(monkeypatch):
    def boom(**kwargs):
        raise httpx.ConnectError("no network")

    monkeypatch.setattr(measure_mod, "measure_real", boom)
    sample = measure(simulate=False)
    assert sample.server == "simulated"


def test_record_success(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["json"] = json
        return FakeResponse()

    monkeypatch.setattr(httpx, "post", fake_post)
    sample = Sample(100.0, 10.0, 5.0, "simulated")
    assert record(sample, "http://api.test") is True
    assert captured["url"] == "http://api.test/measurements"
    assert captured["json"]["download_mbps"] == 100.0


def test_record_handles_failure(monkeypatch):
    def fake_post(url, json, timeout):
        raise httpx.ConnectError("down")

    monkeypatch.setattr(httpx, "post", fake_post)
    sample = Sample(1.0, 1.0, 1.0, "simulated")
    assert record(sample, "http://api.test") is False
