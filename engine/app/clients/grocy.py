"""
Porchlight OS — Grocy Pantry API Client (v3)
System: Porchlight Digital Twin Engine
Function: Synchronizes Grocy pantry stock, falling back to mock pantry data when the
local Grocy instance is unreachable.
"""

from __future__ import annotations

import datetime
import logging

import httpx
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger("PorchlightGrocy")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [Porchlight-Grocy] - %(levelname)s - %(message)s")


class StockItem(BaseModel):
    product_id: int
    name: str
    amount: float
    price_per_unit: float
    calories_per_unit: float
    best_before_date: str


class GrocyClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        self.base_url = base_url or settings.grocy_url
        self.api_key = api_key or settings.grocy_api_key
        self.headers = {
            "GROCY-API-KEY": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def fetch_stock_overview(self) -> list[StockItem]:
        """Fetch current stock overview from the Grocy API, falling back to mock data."""
        endpoint = f"{self.base_url}/api/objects/stock"
        logger.info("Connecting to Porchlight Grocy instance at %s...", self.base_url)

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(endpoint, headers=self.headers)
                response.raise_for_status()
                return [StockItem.model_validate(item) for item in response.json()]
        except httpx.HTTPError as exc:
            logger.warning("Unable to connect to live Grocy API (%s). Using Porchlight mock pantry data.", exc)
            return self._mock_stock_overview()

    @staticmethod
    def _mock_stock_overview() -> list[StockItem]:
        today = datetime.date.today()
        return [
            StockItem(
                product_id=101,
                name="Organic Whole Milk (2L)",
                amount=2,
                price_per_unit=3.50,
                calories_per_unit=1200,
                best_before_date=(today + datetime.timedelta(days=1)).isoformat(),
            ),
            StockItem(
                product_id=102,
                name="Rolled Oats (1kg)",
                amount=3,
                price_per_unit=4.00,
                calories_per_unit=3800,
                best_before_date="2026-12-31",
            ),
            StockItem(
                product_id=103,
                name="Chicken Breast (1kg)",
                amount=1.5,
                price_per_unit=11.00,
                calories_per_unit=1650,
                best_before_date=(today + datetime.timedelta(days=2)).isoformat(),
            ),
            StockItem(
                product_id=104,
                name="Avocados (Mesh Bag)",
                amount=1,
                price_per_unit=5.00,
                calories_per_unit=800,
                best_before_date="2026-10-15",
            ),
        ]


if __name__ == "__main__":
    import asyncio

    from app.metrics.food_metrics import calculate_pantry_metrics
    from app.services.drais_logger import DecisionRecord, emit_decision_record

    async def _demo() -> None:
        client = GrocyClient()
        stock = await client.fetch_stock_overview()
        metrics = calculate_pantry_metrics(stock)

        print("\n--- Porchlight Pantry Scoreboard ---")
        print(f"Total Pantry Items:       {metrics.total_items}")
        print(f"Inventory Valuation:       ${metrics.inventory_value_usd}")
        print(f"Total Caloric Stock:       {metrics.total_calories_kcal} kcal")
        print(f"Targeting System ($/2k):   ${metrics.cost_per_2000_kcal_usd} / 2,000 kcal")
        print(f"Expiring Items (3 days):   {metrics.expiring_items}\n")

        emit_decision_record(
            DecisionRecord(
                component="grocy",
                action_type="PANTRY_NUTRITION_METRICS_EVALUATION",
                decision_logic="COST_PER_2000_KCAL_BENCHMARK",
                inputs={"active_pantry_items_count": metrics.total_items},
                output=metrics.model_dump(),
            )
        )

    asyncio.run(_demo())
