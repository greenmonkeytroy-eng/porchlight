"""
Porchlight OS — Fixed House Cost Allocation Service (v3)
System: Porchlight Digital Twin Engine
Function: Orchestrates Firefly III fixed-cost ingestion and computes PFOR, EUR,
and per-occupant monthly settlement balances, emitting a DR-AIS Decision Record.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from app.clients.firefly import FireflyClient, FixedCosts
from app.metrics.energy_metrics import EnergyMetrics, calculate_eur
from app.metrics.property_metrics import (
    Occupant,
    OccupantSettlement,
    PropertyOverheadMetrics,
    calculate_occupant_settlement,
    calculate_pfor,
)
from app.services.drais_logger import DecisionRecord, emit_decision_record

logger = logging.getLogger("PorchlightRatesAllocator")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [Porchlight-Rates] - %(levelname)s - %(message)s")


@dataclass
class AllocationResult:
    fixed_costs: FixedCosts
    property_metrics: PropertyOverheadMetrics
    energy_metrics: EnergyMetrics
    settlements: list[OccupantSettlement]


class RatesAllocator:
    def __init__(self, firefly_client: FireflyClient | None = None) -> None:
        self.firefly_client = firefly_client or FireflyClient()

    async def allocate(
        self,
        total_monthly_spend: float,
        utility_variable_spend: float,
        kwh_consumed: float,
        occupants: list[Occupant],
    ) -> AllocationResult:
        """Calculates PFOR, EUR, and occupant settlements, then emits a DR-AIS record."""
        fixed_costs = await self.firefly_client.fetch_monthly_fixed_costs()
        property_metrics = calculate_pfor(fixed_costs, total_monthly_spend)
        energy_metrics = calculate_eur(fixed_costs, utility_variable_spend, kwh_consumed)
        settlements = calculate_occupant_settlement(fixed_costs, occupants)

        emit_decision_record(
            DecisionRecord(
                component="rates",
                action_type="PROPERTY_OVERHEAD_ALLOCATION",
                decision_logic="PRO_RATA_RESIDENCY_SPLIT",
                inputs={"fixed_house_costs": fixed_costs.model_dump(), "occupant_count": len(settlements)},
                output={
                    **property_metrics.model_dump(),
                    **energy_metrics.model_dump(),
                    "occupant_settlement_ledger": [s.model_dump() for s in settlements],
                },
            )
        )

        return AllocationResult(
            fixed_costs=fixed_costs,
            property_metrics=property_metrics,
            energy_metrics=energy_metrics,
            settlements=settlements,
        )


if __name__ == "__main__":
    import asyncio

    async def _demo() -> None:
        occupants = [
            Occupant(id="OCC_A", name="Occupant A", direct_spending=420.00, submetered_utility=95.00),
            Occupant(id="OCC_B", name="Occupant B", direct_spending=310.00, submetered_utility=85.00),
        ]

        # Example scenario: $2,800 total household monthly spend, $180 variable power, 600 kWh
        result = await RatesAllocator().allocate(
            total_monthly_spend=2800.00,
            utility_variable_spend=180.00,
            kwh_consumed=600.0,
            occupants=occupants,
        )

        print("\n=== Porchlight Property & Fixed House Overhead Ledger ===")
        print(f"Total Fixed House Overhead: ${result.property_metrics.total_fixed_house_overhead_usd}/mo")
        print(f"Property Fixed Overhead Ratio (PFOR): {result.property_metrics.pfor_percentage}%")
        print(f"Effective Utility Rate (EUR): ${result.energy_metrics.effective_utility_rate_per_kwh}/kWh\n")

        print("--- Per-Occupant Monthly Settlement ---")
        for s in result.settlements:
            print(
                f"• {s.name}: Personal Direct (${s.direct_personal_spend}) + "
                f"Fixed Share (${s.fixed_overhead_share}) + Power (${s.submetered_utility_spend}) "
                f"= Total Due: ${s.total_monthly_due_usd}"
            )

    asyncio.run(_demo())
