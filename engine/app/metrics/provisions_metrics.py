"""
Porchlight OS — Provisions Targeting Metrics
System: Porchlight Digital Twin Engine
Function: Computes multi-category inventory valuation, reorder/buffer alerts, and
food-specific benchmarks (Cost per 2,000 kcal, spoilage risk) across Porchlight
Provisions (Food & Nutrition, Household & Cleaning, Pet Care, Personal Care,
Building & Hardware).
"""

from __future__ import annotations

import datetime

from pydantic import BaseModel

from app.clients.provisions import ProvisionItem

FOOD_CATEGORY = "Food & Nutrition"


class ReorderAlert(BaseModel):
    name: str
    category: str
    current_stock: float
    min_buffer: float


class FoodMetrics(BaseModel):
    food_valuation_usd: float
    total_calories_kcal: float
    cost_per_2000_kcal_usd: float
    expiring_food_items: list[str]


class CategoryBreakdown(BaseModel):
    valuation_usd: float
    item_count: int
    percentage_of_total_stock: float
    tertiary_subcategories: dict[str, float]


class ProvisionsMetrics(BaseModel):
    primary_node: str = "Porchlight Provisions"
    total_inventory_valuation_usd: float
    total_items_tracked: int
    reorder_alerts_count: int
    items_needing_reorder: list[ReorderAlert]
    food_specific_metrics: FoodMetrics
    secondary_category_breakdown: dict[str, CategoryBreakdown]


def calculate_provisions_metrics(inventory: list[ProvisionItem], expiry_horizon_days: int = 3) -> ProvisionsMetrics:
    """Generates primary, secondary, and tertiary analytics across Porchlight Provisions."""
    total_valuation = sum(item.quantity * item.unit_price_usd for item in inventory)
    cutoff = (datetime.date.today() + datetime.timedelta(days=expiry_horizon_days)).isoformat()

    categories: dict[str, dict] = {}
    items_to_reorder: list[ReorderAlert] = []
    expiring_food: list[str] = []
    food_calories = 0.0
    food_spend = 0.0

    for item in inventory:
        item_val = item.quantity * item.unit_price_usd
        bucket = categories.setdefault(
            item.category, {"total_valuation_usd": 0.0, "item_count": 0, "sub_categories": {}}
        )
        bucket["total_valuation_usd"] += item_val
        bucket["item_count"] += 1
        bucket["sub_categories"][item.sub_category] = bucket["sub_categories"].get(item.sub_category, 0.0) + item_val

        if item.quantity <= item.min_buffer_qty:
            items_to_reorder.append(
                ReorderAlert(
                    name=item.name,
                    category=item.category,
                    current_stock=item.quantity,
                    min_buffer=item.min_buffer_qty,
                )
            )

        if item.category == FOOD_CATEGORY:
            food_calories += item.quantity * (item.calories_per_unit or 0)
            food_spend += item_val
            if item.best_before and item.best_before <= cutoff:
                expiring_food.append(item.name)

    cost_per_2k_kcal = (food_spend / food_calories * 2000) if food_calories > 0 else 0.0

    return ProvisionsMetrics(
        total_inventory_valuation_usd=round(total_valuation, 2),
        total_items_tracked=len(inventory),
        reorder_alerts_count=len(items_to_reorder),
        items_needing_reorder=items_to_reorder,
        food_specific_metrics=FoodMetrics(
            food_valuation_usd=round(food_spend, 2),
            total_calories_kcal=food_calories,
            cost_per_2000_kcal_usd=round(cost_per_2k_kcal, 2),
            expiring_food_items=expiring_food,
        ),
        secondary_category_breakdown={
            cat: CategoryBreakdown(
                valuation_usd=round(data["total_valuation_usd"], 2),
                item_count=data["item_count"],
                percentage_of_total_stock=round((data["total_valuation_usd"] / total_valuation * 100), 1)
                if total_valuation > 0
                else 0.0,
                tertiary_subcategories={k: round(v, 2) for k, v in data["sub_categories"].items()},
            )
            for cat, data in categories.items()
        },
    )
