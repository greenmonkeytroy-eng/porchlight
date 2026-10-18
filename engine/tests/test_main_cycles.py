import json
import re

import pytest

from app import main
from app.config import REPO_DIR, settings

DASHBOARD_PATH = REPO_DIR / "porchlight-dashboard.json"
# Written nowhere yet on purpose: discarded-food value isn't tracked, so the panel honestly shows "No data".
KNOWN_UNWRITTEN = {("pantry_telemetry", "food_spoilage_ratio_percent")}


class FakeInflux:
    def __init__(self):
        self.points: list[tuple[str, dict, dict | None]] = []

    async def write_point(self, measurement, fields, tags=None, time=None):
        self.points.append((measurement, fields, tags))


@pytest.fixture
def isolated_worker(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # DR-AIS records land in tmp_path/logs
    monkeypatch.setattr(main, "HEARTBEAT_PATH", tmp_path / "heartbeat")
    monkeypatch.setattr(settings, "grocy_url", "http://127.0.0.1:1")
    monkeypatch.setattr(settings, "household_profile_path", tmp_path / "missing.json")
    return tmp_path


def _dashboard_queries() -> list[str]:
    dashboard = json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))
    return [t["query"] for p in dashboard["panels"] for t in p.get("targets", [])]


async def test_engine_writes_every_measurement_the_dashboard_queries(isolated_worker):
    influx = FakeInflux()
    await main.run_all_cycles(influx)

    written = {(m, f) for m, fields, _ in influx.points for f in fields}
    queried = set()
    for q in _dashboard_queries():
        measurement = re.search(r'_measurement"\] == "([^"]+)"', q).group(1)
        for field in re.findall(r'_field"\] == "([^"]+)"', q):
            queried.add((measurement, field))

    assert queried - written == KNOWN_UNWRITTEN


def test_dashboard_queries_the_bucket_the_stack_creates():
    buckets = {re.search(r'from\(bucket: "([^"]+)"\)', q).group(1) for q in _dashboard_queries()}

    assert buckets == {settings.influx_bucket}


async def test_occupant_settlements_are_tagged_per_occupant(isolated_worker):
    influx = FakeInflux()
    await main.run_rates_cycle(influx)

    occupants = [tags["name"] for m, _, tags in influx.points if m == "occupant_settlement"]
    assert occupants == ["Occupant A", "Occupant B"]


async def test_one_failing_cycle_does_not_stop_the_others_and_heartbeat_still_updates(isolated_worker, monkeypatch):
    async def boom(_influx):
        raise RuntimeError("simulated cycle failure")

    monkeypatch.setattr(main, "CYCLES", (boom, main.run_rates_cycle))
    influx = FakeInflux()

    await main.run_all_cycles(influx)

    assert any(m == "household_metrics" for m, _, _ in influx.points)
    assert main.HEARTBEAT_PATH.exists()
