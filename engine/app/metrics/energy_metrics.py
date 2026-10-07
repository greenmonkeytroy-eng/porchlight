"""
Porchlight OS — Energy & Utility Targeting Metrics
System: Porchlight Digital Twin Engine
Function: Computes the Effective Utility Rate (EUR), blending fixed standing
supply charges with variable usage charges.
"""

from __future__ import annotations

from pydantic import BaseModel

from app.clients.firefly import FixedCosts


class EnergyMetrics(BaseModel):
    effective_utility_rate_per_kwh: float


def calculate_eur(fixed_costs: FixedCosts, utility_variable_spend: float, kwh_consumed: float) -> EnergyMetrics:
    """Calculates the Effective Utility Rate (EUR $/kWh)."""
    total_elec_spend = fixed_costs.electricity_standing_supply_charge + utility_variable_spend
    rate = (total_elec_spend / kwh_consumed) if kwh_consumed > 0 else 0.0

    return EnergyMetrics(effective_utility_rate_per_kwh=round(rate, 4))
