"""
Porchlight OS — Engine Entry Point Worker
System: Porchlight Digital Twin Engine
Function: Runs the pantry metrics cycle on an interval and emits DR-AIS records.
"""

from __future__ import annotations

import asyncio
import logging

from app.clients.grocy import GrocyClient
from app.config import settings
from app.metrics.food_metrics import calculate_pantry_metrics
from app.services.drais_logger import DecisionRecord, emit_decision_record

logging.basicConfig(level=settings.log_level, format="%(asctime)s - [Porchlight-Engine] - %(levelname)s - %(message)s")
logger = logging.getLogger("PorchlightEngine")

CYCLE_INTERVAL_SECONDS = 3600


async def run_pantry_cycle() -> None:
    stock = await GrocyClient().fetch_stock_overview()
    metrics = calculate_pantry_metrics(stock)

    emit_decision_record(
        DecisionRecord(
            component="grocy",
            action_type="PANTRY_NUTRITION_METRICS_EVALUATION",
            decision_logic="COST_PER_2000_KCAL_BENCHMARK",
            inputs={"active_pantry_items_count": metrics.total_items},
            output=metrics.model_dump(),
        )
    )
    logger.info("Pantry cycle complete: %s", metrics.model_dump())


async def main() -> None:
    logger.info("Porchlight Engine starting (cycle interval: %ss)", CYCLE_INTERVAL_SECONDS)
    while True:
        await run_pantry_cycle()
        await asyncio.sleep(CYCLE_INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
