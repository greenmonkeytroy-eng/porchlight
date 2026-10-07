"""
Porchlight OS — Food & Pantry Targeting Metrics
System: Porchlight Digital Twin Engine
Function: Computes Cost per 2,000 kcal and expiring-stock benchmarks from pantry stock.
"""

from __future__ import annotations

import datetime

from pydantic import BaseModel

from app.clients.grocy import StockItem


class PantryMetrics(BaseModel):
    total_items: int
    inventory_value_usd: float
    total_calories_kcal: float
    cost_per_2000_kcal_usd: float
    expiring_soon_count: int
    expiring_items: list[str]


def calculate_pantry_metrics(stock: list[StockItem], expiry_horizon_days: int = 3) -> PantryMetrics:
    """Calculates total inventory valuation, total calories, and Cost per 2,000 kcal."""
    total_val = sum(item.amount * item.price_per_unit for item in stock)
    total_cal = sum(item.amount * item.calories_per_unit for item in stock)
    cost_per_2k = (total_val / total_cal * 2000) if total_cal > 0 else 0.0

    cutoff = (datetime.date.today() + datetime.timedelta(days=expiry_horizon_days)).isoformat()
    expiring_soon = [item.name for item in stock if item.best_before_date <= cutoff]

    return PantryMetrics(
        total_items=len(stock),
        inventory_value_usd=round(total_val, 2),
        total_calories_kcal=round(total_cal, 0),
        cost_per_2000_kcal_usd=round(cost_per_2k, 2),
        expiring_soon_count=len(expiring_soon),
        expiring_items=expiring_soon,
    )
