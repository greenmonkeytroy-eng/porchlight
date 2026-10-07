# Porchlight OS — Claude Code Assistant Guide (v3)

## Project Overview
**Porchlight** is a privacy-first, locally hosted **Digital Twin of Domestic Operations** built on top of the **Industrial Intelligence Stack**. It connects Home Assistant, Grocy, Firefly III, InfluxDB, and Grafana via a custom Python middleware engine (`porchlight-engine`) to automate household logistics, track fixed/variable costs (rates, levies, groceries, utilities), and drive domestic abundance.

## Architecture & Tech Stack
* **System Name**: Porchlight OS
* **Core Controller**: Home Assistant Core (`porchlight-homeassistant`)
* **Pantry ERP**: Grocy (`porchlight-grocy`)
* **Financial Ledger**: Firefly III (`porchlight-firefly`)
* **Time-Series Store**: InfluxDB v2 (`porchlight-influxdb`)
* **Dashboards**: Grafana (`porchlight-grafana` / Porchlight Portal)
* **Middleware Engine**: Python 3.11+ AsyncIO (`porchlight-engine`)

---

## Directory Structure Standard

```
porchlight/
├── CLAUDE.md                          # This instruction file
├── porchlight-spec-v3.md              # System Architecture & Specification
├── porchlight-tasks-v3.md             # Task Taxonomy & Implementation Roadmap
├── docker-compose.yml                 # Service container orchestration
├── .env.example                       # Environment variables template
├── engine/                            # Porchlight Middleware Engine
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # Entry point worker
│   │   ├── config.py                  # Pydantic settings
│   │   ├── clients/                   # API clients
│   │   │   ├── homeassistant.py
│   │   │   ├── grocy.py
│   │   │   ├── firefly.py
│   │   │   └── influx.py
│   │   ├── metrics/                   # Targeting systems (PFOR, EUR, $/2k kcal)
│   │   │   ├── food_metrics.py
│   │   │   ├── energy_metrics.py
│   │   │   └── property_metrics.py
│   │   └── services/                  # Business logic & DR-AIS logging
│   │       ├── ocr_parser.py
│   │       ├── rates_allocator.py
│   │       └── drais_logger.py
│   └── tests/
└── logs/                              # DR-AIS Decision Record logs
```

---

## Development & Coding Standards

1. **Async & Type Hints**: All Python backend code in `porchlight-engine` must use strict type annotations and `asyncio` (`httpx` or `aiohttp`).
2. **Pydantic Validation**: All API responses, receipt OCR outputs, and DR-AIS decision records must be validated using Pydantic v2 models.
3. **Privacy First**: No telemetry or household logs may be transmitted outside the local Docker network.
4. **DR-AIS Decision Record Standard**: Every automated action or financial allocation must emit a JSON Decision Record:

```json
{
  "system": "Porchlight OS",
  "drais_version": "1.0",
  "timestamp": "ISO-8601 UTC",
  "action_type": "PROPERTY_OVERHEAD_ALLOCATION",
  "inputs": { ... },
  "decision_logic": "PRO_RATA_RESIDENCY_SPLIT",
  "output": { ... },
  "human_override_available": true
}
```

---

## Step-by-Step Claude Code Prompts

### Step 1: Docker Stack Verification
> *"Read `porchlight-spec-v3.md` and `docker-compose.yml`. Verify that all container services (`porchlight-homeassistant`, `porchlight-grocy`, `porchlight-firefly`, `porchlight-influxdb`, `porchlight-grafana`, `porchlight-engine`) are configured properly with health checks."*

### Step 2: Engine Configuration & API Clients
> *"In `engine/app/config.py`, create a Pydantic Settings class for Porchlight loading environment variables for HA, Grocy, Firefly, and InfluxDB URLs and tokens."*

### Step 3: Fixed House Cost Allocator
> *"In `engine/app/services/rates_allocator.py`, build the Porchlight fixed house cost allocation service that calculates PFOR, EUR, and occupant monthly settlement balances."*
