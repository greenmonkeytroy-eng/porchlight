"""
Porchlight OS — Home Assistant Core Client
System: Porchlight Digital Twin Engine
Function: Reads entity states (smart meter/plug telemetry, sensors) from Home
Assistant's REST API, falling back to mock states when unreachable, and calls
services (automations, device actions).
"""

from __future__ import annotations

import logging
from typing import Any

import httpx
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger("PorchlightHomeAssistant")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [Porchlight-HA] - %(levelname)s - %(message)s")


class EntityState(BaseModel):
    entity_id: str
    state: str
    attributes: dict[str, Any] = {}
    last_changed: str | None = None


class HomeAssistantClient:
    def __init__(self, base_url: str | None = None, token: str | None = None) -> None:
        self.base_url = base_url or settings.homeassistant_url
        self.token = token or settings.homeassistant_token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def fetch_states(self) -> list[EntityState]:
        """Fetch all entity states, falling back to mock sensor data."""
        endpoint = f"{self.base_url}/api/states"
        logger.info("Connecting to Porchlight Home Assistant instance at %s...", self.base_url)

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(endpoint, headers=self.headers)
                response.raise_for_status()
                return [EntityState.model_validate(item) for item in response.json()]
        except httpx.HTTPError as exc:
            logger.warning("Unable to connect to live Home Assistant API (%s). Using Porchlight mock states.", exc)
            return self._mock_states()

    async def get_state(self, entity_id: str) -> EntityState | None:
        """Fetch a single entity's state, falling back to mock data by entity_id."""
        endpoint = f"{self.base_url}/api/states/{entity_id}"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(endpoint, headers=self.headers)
                response.raise_for_status()
                return EntityState.model_validate(response.json())
        except httpx.HTTPError as exc:
            logger.warning("Unable to connect to live Home Assistant API (%s). Using Porchlight mock states.", exc)
            return next((s for s in self._mock_states() if s.entity_id == entity_id), None)

    async def call_service(self, domain: str, service: str, data: dict[str, Any] | None = None) -> Any:
        """Calls a Home Assistant service. Raises on failure — a service call is a real action, never mocked."""
        endpoint = f"{self.base_url}/api/services/{domain}/{service}"

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(endpoint, headers=self.headers, json=data or {})
            response.raise_for_status()
            return response.json()

    @staticmethod
    def _mock_states() -> list[EntityState]:
        return [
            EntityState(
                entity_id="sensor.porchlight_power_draw",
                state="1.42",
                attributes={"unit_of_measurement": "kW", "friendly_name": "Porchlight Power Draw"},
            ),
            EntityState(
                entity_id="sensor.porchlight_water_flow",
                state="2.1",
                attributes={"unit_of_measurement": "L/min", "friendly_name": "Porchlight Water Flow"},
            ),
            EntityState(
                entity_id="binary_sensor.porchlight_front_door",
                state="off",
                attributes={"friendly_name": "Porchlight Front Door"},
            ),
        ]


if __name__ == "__main__":
    import asyncio

    async def _demo() -> None:
        client = HomeAssistantClient()
        states = await client.fetch_states()

        print("\n=== Porchlight Home Assistant States ===")
        for s in states:
            unit = s.attributes.get("unit_of_measurement", "")
            print(f"- {s.entity_id}: {s.state} {unit}")

    asyncio.run(_demo())
