"""
Porchlight OS — InfluxDB v2 Telemetry Client
System: Porchlight Digital Twin Engine
Function: Writes high-frequency energy/water telemetry points and runs Flux
queries against the local InfluxDB v2 store.

Telemetry is real sensor data, not a demo scoreboard like pantry stock or fixed
costs — there is no sensible "mock reading" to fall back to, so writes and
queries raise on failure instead of silently returning fabricated data.
"""

from __future__ import annotations

import csv
import datetime
import io
import logging

import httpx

from app.config import settings

logger = logging.getLogger("PorchlightInflux")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [Porchlight-Influx] - %(levelname)s - %(message)s")


def build_line_protocol(
    measurement: str,
    fields: dict[str, float],
    tags: dict[str, str] | None = None,
    time: datetime.datetime | None = None,
) -> str:
    """Builds a single InfluxDB line-protocol point."""
    if not fields:
        raise ValueError("A point requires at least one field")

    tag_part = "".join(f",{k}={v}" for k, v in (tags or {}).items())
    field_part = ",".join(f"{k}={v}" for k, v in fields.items())
    timestamp_ns = int((time or datetime.datetime.now(datetime.UTC)).timestamp() * 1_000_000_000)

    return f"{measurement}{tag_part} {field_part} {timestamp_ns}"


class InfluxClient:
    def __init__(
        self,
        base_url: str | None = None,
        org: str | None = None,
        bucket: str | None = None,
        token: str | None = None,
    ) -> None:
        self.base_url = base_url or settings.influx_url
        self.org = org or settings.influx_org
        self.bucket = bucket or settings.influx_bucket
        self.token = token or settings.influx_token
        self.headers = {"Authorization": f"Token {self.token}"}

    async def write_point(
        self,
        measurement: str,
        fields: dict[str, float],
        tags: dict[str, str] | None = None,
        time: datetime.datetime | None = None,
    ) -> None:
        """Writes a single telemetry point. Raises on failure — callers must know if a write didn't land."""
        line = build_line_protocol(measurement, fields, tags, time)
        endpoint = f"{self.base_url}/api/v2/write"
        params = {"org": self.org, "bucket": self.bucket, "precision": "ns"}

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                endpoint,
                params=params,
                headers={**self.headers, "Content-Type": "text/plain; charset=utf-8"},
                content=line,
            )
            response.raise_for_status()
        logger.info("Wrote point to %s: %s", measurement, line)

    async def query_flux(self, flux: str) -> list[dict[str, str]]:
        """Runs a Flux query and returns each result row as a dict. Raises on failure."""
        endpoint = f"{self.base_url}/api/v2/query"
        params = {"org": self.org}

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                endpoint,
                params=params,
                headers={
                    **self.headers,
                    "Content-Type": "application/vnd.flux",
                    "Accept": "application/csv",
                },
                content=flux,
            )
            response.raise_for_status()

        return _parse_annotated_csv(response.text)


def _parse_annotated_csv(csv_text: str) -> list[dict[str, str]]:
    """Parses InfluxDB v2's annotated CSV query response into plain row dicts."""
    data_lines = [line for line in csv_text.splitlines() if line and not line.startswith("#")]
    if not data_lines:
        return []
    reader = csv.DictReader(io.StringIO("\n".join(data_lines)))
    return list(reader)


if __name__ == "__main__":
    import asyncio

    async def _demo() -> None:
        client = InfluxClient()
        try:
            await client.write_point("power_draw", fields={"kw": 1.42}, tags={"circuit": "main"})
            rows = await client.query_flux(
                f'from(bucket:"{client.bucket}") |> range(start: -5m) |> filter(fn: (r) => r._measurement == "power_draw")'
            )
            print(f"\n=== Porchlight InfluxDB Telemetry Demo ===\nRows returned: {len(rows)}")
        except httpx.HTTPError as exc:
            logger.warning("Unable to reach Porchlight InfluxDB at %s (%s).", client.base_url, exc)

    asyncio.run(_demo())
