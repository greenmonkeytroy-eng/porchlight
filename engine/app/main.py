"""
Porchlight OS — Engine Entry Point Worker
System: Porchlight Digital Twin Engine
Function: Runs the Provisions and fixed-cost allocation cycles on an interval,
emits DR-AIS records, and writes the metrics the Grafana portal reads to InfluxDB.
"""

from __future__ import annotations

import asyncio
import logging
import tempfile
from pathlib import Path

import httpx

from app.clients.influx import InfluxClient
from app.clients.provisions import ProvisionsClient
from app.config import settings
from app.metrics.provisions_metrics import calculate_provisions_metrics
from app.services.drais_logger import DecisionRecord, emit_decision_record
from app.services.rates_allocator import RatesAllocator, load_household_profile

logging.basicConfig(level=settings.log_level, format="%(asctime)s - [Porchlight-Engine] - %(levelname)s - %(message)s")
logger = logging.getLogger("PorchlightEngine")

CYCLE_INTERVAL_SECONDS = 3600
# The container health check reads this; it must stay fresh within ~2 cycles.
HEARTBEAT_PATH = Path(tempfile.gettempdir()) / "porchlight-heartbeat"


async def _write_metric(
    influx: InfluxClient, measurement: str, fields: dict[str, float], tags: dict[str, str] | None = None
) -> None:
    try:
        await influx.write_point(measurement, fields=fields, tags=tags)
    except httpx.HTTPError as exc:
        logger.warning("InfluxDB write for %s failed (%s); dashboard will lag until it recovers.", measurement, exc)


async def run_provisions_cycle(influx: InfluxClient) -> None:
    inventory = await ProvisionsClient().fetch_provisions_inventory()
    metrics = calculate_provisions_metrics(inventory)

    emit_decision_record(
        DecisionRecord(
            component="provisions",
            action_type="PROVISIONS_INVENTORY_AND_REPLENISHMENT_EVALUATION",
            decision_logic="MULTI_CATEGORY_BUFFER_THRESHOLD_ANALYSIS",
            inputs={
                "tracked_items": metrics.total_items_tracked,
                "inventory_valuation_usd": metrics.total_inventory_valuation_usd,
            },
            output=metrics.model_dump(),
            human_override_available=metrics.reorder_alerts_count > 0,
        )
    )
    # food_spoilage_ratio_percent is deliberately not written: discarded-food value isn't tracked yet.
    await _write_metric(
        influx,
        "pantry_telemetry",
        {
            "cost_per_2000_kcal": metrics.food_specific_metrics.cost_per_2000_kcal_usd,
            "inventory_valuation_usd": metrics.total_inventory_valuation_usd,
            "reorder_alerts": metrics.reorder_alerts_count,
        },
    )
    logger.info("Provisions cycle complete: %s items, %s reorder alerts", metrics.total_items_tracked, metrics.reorder_alerts_count)


async def run_rates_cycle(influx: InfluxClient) -> None:
    profile = load_household_profile(settings.household_profile_path)
    result = await RatesAllocator().allocate(
        total_monthly_spend=profile.total_monthly_spend,
        utility_variable_spend=profile.utility_variable_spend,
        kwh_consumed=profile.kwh_consumed,
        occupants=profile.occupants,
    )

    await _write_metric(
        influx,
        "household_metrics",
        {
            "pfor_percent": result.property_metrics.pfor_percentage,
            "effective_utility_rate_kwh": result.energy_metrics.effective_utility_rate_per_kwh,
            "total_monthly_spend": profile.total_monthly_spend,
            "fixed_overhead_spend": result.property_metrics.total_fixed_house_overhead_usd,
        },
    )
    for s in result.settlements:
        await _write_metric(
            influx,
            "occupant_settlement",
            {"total_due_usd": s.total_monthly_due_usd, "fixed_overhead_share_usd": s.fixed_overhead_share},
            tags={"occupant_id": s.occupant_id, "name": s.name},
        )
    logger.info("Rates cycle complete: PFOR %s%%", result.property_metrics.pfor_percentage)


CYCLES = (run_provisions_cycle, run_rates_cycle)


async def run_all_cycles(influx: InfluxClient) -> None:
    """Runs every cycle; one cycle failing never stops the others or the worker."""
    for cycle in CYCLES:
        try:
            await cycle(influx)
        except Exception:
            logger.exception("%s failed; continuing with the next cycle.", cycle.__name__)
    HEARTBEAT_PATH.touch()


async def main() -> None:
    logger.info("Porchlight Engine starting (cycle interval: %ss)", CYCLE_INTERVAL_SECONDS)
    influx = InfluxClient()
    while True:
        await run_all_cycles(influx)
        await asyncio.sleep(CYCLE_INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
