"""
Porchlight OS — Provisions API Client (v4)
System: Porchlight Digital Twin Engine
Function: Synchronizes Porchlight Provisions inventory (Food & Nutrition, Household &
Cleaning, Pet Care, Personal Care, Building & Hardware) from the Grocy-backed
provisions ERP, falling back to mock data when unreachable.
"""

from __future__ import annotations

import datetime
import logging

import httpx
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger("PorchlightProvisions")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [Porchlight-Provisions] - %(levelname)s - %(message)s")


class ProvisionItem(BaseModel):
    id: str
    name: str
    category: str
    sub_category: str
    quantity: float
    unit_price_usd: float
    min_buffer_qty: float = 0.0
    calories_per_unit: float | None = None
    best_before: str | None = None
    daily_burn_rate: float | None = None
    next_replacement_due: str | None = None


class ProvisionsClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        self.base_url = base_url or settings.grocy_url
        self.api_key = api_key or settings.grocy_api_key
        self.headers = {
            "GROCY-API-KEY": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def fetch_provisions_inventory(self) -> list[ProvisionItem]:
        """Fetch Porchlight Provisions inventory, falling back to mock data."""
        endpoint = f"{self.base_url}/api/objects/stock"
        logger.info("Connecting to Porchlight Provisions instance at %s...", self.base_url)

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(endpoint, headers=self.headers)
                response.raise_for_status()
                return [ProvisionItem.model_validate(item) for item in response.json()]
        except httpx.HTTPError as exc:
            logger.warning("Unable to connect to live Provisions API (%s). Using Porchlight mock inventory.", exc)
            return self._mock_inventory()

    @staticmethod
    def _mock_inventory() -> list[ProvisionItem]:
        today = datetime.date.today()
        return [
            # Food & Nutrition
            ProvisionItem(
                id="PROV_FOOD_1",
                name="Organic Whole Milk (2L)",
                category="Food & Nutrition",
                sub_category="Dairy & Refrigerated",
                quantity=2,
                unit_price_usd=3.50,
                calories_per_unit=1200,
                best_before=(today + datetime.timedelta(days=1)).isoformat(),
                min_buffer_qty=1,
            ),
            ProvisionItem(
                id="PROV_FOOD_2",
                name="Rolled Oats (1kg)",
                category="Food & Nutrition",
                sub_category="Pantry Staples",
                quantity=3,
                unit_price_usd=4.00,
                calories_per_unit=3800,
                best_before="2026-12-31",
                min_buffer_qty=1,
            ),
            # Household & Cleaning
            ProvisionItem(
                id="PROV_CLEAN_1",
                name="Dishwasher Detergent Pods (60pk)",
                category="Household & Cleaning",
                sub_category="Kitchen Sanitation",
                quantity=1,
                unit_price_usd=18.50,
                daily_burn_rate=0.033,
                min_buffer_qty=0.25,
            ),
            ProvisionItem(
                id="PROV_CLEAN_2",
                name="Recycled Paper Towels (12 Rolls)",
                category="Household & Cleaning",
                sub_category="Paper Goods",
                quantity=0.2,
                unit_price_usd=16.00,
                daily_burn_rate=0.05,
                min_buffer_qty=0.30,
            ),
            # Pet Care
            ProvisionItem(
                id="PROV_PET_1",
                name="Grain-Free Dog Kibble (10kg)",
                category="Pet Care",
                sub_category="Canine Food",
                quantity=1.5,
                unit_price_usd=45.00,
                daily_burn_rate=0.05,
                min_buffer_qty=0.5,
            ),
            # Building & Maintenance
            ProvisionItem(
                id="PROV_MAINT_1",
                name="MERV-13 HVAC Air Filter (2-pack)",
                category="Building & Maintenance",
                sub_category="HVAC / Air Quality",
                quantity=1,
                unit_price_usd=32.00,
                next_replacement_due=(today + datetime.timedelta(days=14)).isoformat(),
                min_buffer_qty=1,
            ),
        ]


if __name__ == "__main__":
    import asyncio

    from app.metrics.provisions_metrics import calculate_provisions_metrics
    from app.services.drais_logger import DecisionRecord, emit_decision_record

    async def _demo() -> None:
        client = ProvisionsClient()
        inventory = await client.fetch_provisions_inventory()
        metrics = calculate_provisions_metrics(inventory)

        print("\n=== Porchlight OS — Provisions Master Scoreboard ===")
        print(f"Total Stock Valuation:  ${metrics.total_inventory_valuation_usd}")
        print(f"Total Tracked Items:    {metrics.total_items_tracked}")
        print(f"Reorder Alerts Active:  {metrics.reorder_alerts_count}\n")

        print("--- Secondary Category Reporting ---")
        for cat, data in metrics.secondary_category_breakdown.items():
            print(f"- {cat}: ${data.valuation_usd} ({data.percentage_of_total_stock}% of stock) | {data.item_count} items")
            for sub_cat, sub_val in data.tertiary_subcategories.items():
                print(f"    - {sub_cat}: ${sub_val}")

        print("\n--- Food Specific Targeting Benchmark ---")
        print(f"Cost per 2,000 kcal:    ${metrics.food_specific_metrics.cost_per_2000_kcal_usd}")
        print(f"Expiring Items:         {metrics.food_specific_metrics.expiring_food_items}")

        print("\n--- Automatic Restock Buffer Flags ---")
        for r in metrics.items_needing_reorder:
            print(f"LOW STOCK: {r.name} ({r.category}) - Current: {r.current_stock} (Min Buffer: {r.min_buffer})")

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

    asyncio.run(_demo())
