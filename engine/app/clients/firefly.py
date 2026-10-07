"""
Porchlight OS — Firefly III Fixed Costs Client (v3)
System: Porchlight Digital Twin Engine
Function: Ingests recurring house-associated fixed costs (council rates, HOA/strata
levies, insurance, standing utility fees) from Firefly III.
"""

from __future__ import annotations

from pydantic import BaseModel

from app.config import settings


class FixedCosts(BaseModel):
    council_rates_monthly: float
    strata_hoa_levy_monthly: float
    building_insurance_monthly: float
    electricity_standing_supply_charge: float
    water_standing_connection_charge: float
    internet_broadband_fixed: float

    @property
    def total(self) -> float:
        return sum(self.model_dump().values())


class FireflyClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        self.base_url = base_url or settings.firefly_url
        self.api_key = api_key or settings.firefly_api_key

    async def fetch_monthly_fixed_costs(self) -> FixedCosts:
        """Ingests recurring house-associated fixed costs.

        Firefly III category ingestion is not wired up yet; this returns the
        Porchlight mock baseline until TASK_RATES_LEVIES_INGEST is implemented.
        """
        return self._mock_fixed_costs()

    @staticmethod
    def _mock_fixed_costs() -> FixedCosts:
        return FixedCosts(
            council_rates_monthly=220.00,
            strata_hoa_levy_monthly=350.00,
            building_insurance_monthly=140.00,
            electricity_standing_supply_charge=45.00,
            water_standing_connection_charge=35.00,
            internet_broadband_fixed=80.00,
        )
