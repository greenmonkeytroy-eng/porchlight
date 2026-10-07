"""
Porchlight OS — Engine Entry Point Worker
System: Porchlight Digital Twin Engine
Function: Runs the Porchlight Provisions metrics cycle on an interval and emits
DR-AIS records.
"""

from __future__ import annotations

import asyncio
import logging

from app.clients.provisions import ProvisionsClient
from app.config import settings
from app.metrics.provisions_metrics import calculate_provisions_metrics
from app.services.drais_logger import DecisionRecord, emit_decision_record

logging.basicConfig(level=settings.log_level, format="%(asctime)s - [Porchlight-Engine] - %(levelname)s - %(message)s")
logger = logging.getLogger("PorchlightEngine")

CYCLE_INTERVAL_SECONDS = 3600


async def run_provisions_cycle() -> None:
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
    logger.info("Provisions cycle complete: %s", metrics.model_dump())


async def main() -> None:
    logger.info("Porchlight Engine starting (cycle interval: %ss)", CYCLE_INTERVAL_SECONDS)
    while True:
        await run_provisions_cycle()
        await asyncio.sleep(CYCLE_INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
