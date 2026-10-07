"""
Porchlight OS — Shared DR-AIS Decision Record Logger
System: Porchlight Digital Twin Engine
Function: Validates and emits the common DR-AIS Decision Record schema used by every
Porchlight service (pantry metrics, rates allocation, receipt OCR, ...).
"""

from __future__ import annotations

import datetime
import logging
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger("PorchlightDRAIS")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [Porchlight-DRAIS] - %(levelname)s - %(message)s")


class DecisionRecord(BaseModel):
    system: str = "Porchlight OS"
    drais_version: str = "1.0"
    component: str
    action_type: str
    decision_logic: str
    inputs: dict[str, Any]
    output: dict[str, Any]
    human_override_available: bool = True
    privacy_scope: str = "LOCAL_NETWORK_ONLY"
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC).isoformat())


def emit_decision_record(record: DecisionRecord, log_dir: str = "logs") -> Path:
    """Writes an immutable DR-AIS Decision Record JSON file for Porchlight governance."""
    os.makedirs(log_dir, exist_ok=True)
    filename = Path(log_dir) / f"dr_ais_{record.component}_{datetime.date.today().strftime('%Y%m%d')}.json"
    filename.write_text(record.model_dump_json(indent=2))
    logger.info("DR-AIS Decision Record written to %s", filename)
    return filename
