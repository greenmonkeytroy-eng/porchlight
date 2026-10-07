"""
Porchlight OS — Property Fixed Overhead & Occupant Settlement Metrics
System: Porchlight Digital Twin Engine
Function: Computes the Property Fixed Overhead Ratio (PFOR) and per-occupant
pro-rata monthly settlement balances.
"""

from __future__ import annotations

from pydantic import BaseModel

from app.clients.firefly import FixedCosts


class PropertyOverheadMetrics(BaseModel):
    total_fixed_house_overhead_usd: float
    pfor_percentage: float


class Occupant(BaseModel):
    id: str
    name: str
    direct_spending: float
    submetered_utility: float


class OccupantSettlement(BaseModel):
    occupant_id: str
    name: str
    direct_personal_spend: float
    fixed_overhead_share: float
    submetered_utility_spend: float
    total_monthly_due_usd: float


def calculate_pfor(fixed_costs: FixedCosts, total_monthly_spend: float) -> PropertyOverheadMetrics:
    """Calculates the Property Fixed Overhead Ratio (PFOR)."""
    total_fixed_overhead = fixed_costs.total
    pfor_percent = (total_fixed_overhead / total_monthly_spend * 100) if total_monthly_spend > 0 else 0.0

    return PropertyOverheadMetrics(
        total_fixed_house_overhead_usd=round(total_fixed_overhead, 2),
        pfor_percentage=round(pfor_percent, 2),
    )


def calculate_occupant_settlement(
    fixed_costs: FixedCosts, occupants: list[Occupant]
) -> list[OccupantSettlement]:
    """Distributes fixed house overhead pro-rata and calculates net monthly balances."""
    per_person_fixed_share = fixed_costs.total / len(occupants) if occupants else 0.0

    return [
        OccupantSettlement(
            occupant_id=occ.id,
            name=occ.name,
            direct_personal_spend=occ.direct_spending,
            fixed_overhead_share=round(per_person_fixed_share, 2),
            submetered_utility_spend=occ.submetered_utility,
            total_monthly_due_usd=round(occ.direct_spending + per_person_fixed_share + occ.submetered_utility, 2),
        )
        for occ in occupants
    ]
