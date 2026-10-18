"""
Porchlight OS — Engine Settings
System: Porchlight Digital Twin Engine
Function: Loads HA, Grocy, Firefly, and InfluxDB connection settings from the
environment (or a .env file), so the engine runs the same with or without Docker.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENGINE_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = ENGINE_DIR.parent


class PorchlightSettings(BaseSettings):
    # Repo-root .env first (local runs from engine/), then cwd .env; real env vars always win.
    model_config = SettingsConfigDict(
        env_file=(REPO_DIR / ".env", ".env"), env_file_encoding="utf-8", extra="ignore"
    )

    timezone: str = "America/Los_Angeles"
    log_level: str = "INFO"

    homeassistant_url: str = "http://localhost:8123"
    homeassistant_token: str = ""

    grocy_url: str = "http://localhost:9283"
    grocy_api_key: str = "mock_porchlight_key"

    firefly_url: str = "http://localhost:8080"
    firefly_api_key: str = "mock_porchlight_key"

    influx_url: str = "http://localhost:8086"
    influx_org: str = "porchlight-home"
    influx_bucket: str = "telemetry"
    influx_token: str = ""

    confidence_threshold: float = 0.70
    pfor_alert_threshold: float = 40.0

    household_profile_path: Path = ENGINE_DIR / "household.json"


settings = PorchlightSettings()
