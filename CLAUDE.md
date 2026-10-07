# Porchlight OS — Claude Code Assistant Guide (v4)

## Project Overview
**Porchlight** is a privacy-first, locally hosted **Digital Twin of Domestic Operations** operating within the **Twinscape / Timescape** product family, built on top of the **Industrial Intelligence Stack**. It connects Home Assistant, Porchlight Provisions (a Grocy-backed consumables ERP), Firefly III, InfluxDB, and Grafana via a custom Python middleware engine (`porchlight-engine`) to automate household logistics, track fixed/variable costs (rates, levies, insurance, provisions, utilities), and run multi-horizon predictive simulations (Timescape Horizon).

Household management is divided into **Above the Line (ATL)** — fixed capital & infrastructure (rates, levies, insurance, PowerMesh) — and **Below the Line (BTL)** — daily operational consumables (Porchlight Provisions, maintenance, occupant spend). See `porchlight-dashboard-ui-spec.md` for the spatial dashboard layout this drives.

## Architecture & Tech Stack
* **System Name**: Porchlight OS
* **Core Controller**: Home Assistant Core (`porchlight-homeassistant`)
* **Consumables ERP**: Porchlight Provisions, Grocy-backed (`porchlight-grocy`)
* **Financial Ledger**: Firefly III (`porchlight-firefly`)
* **Time-Series Store**: InfluxDB v2 (`porchlight-influxdb`)
* **Dashboards**: Grafana (`porchlight-grafana` / Porchlight Portal)
* **Middleware Engine**: Python 3.11+ AsyncIO (`porchlight-engine`)

---

## Directory Structure Standard

```
porchlight/
├── CLAUDE.md                          # This instruction file
├── README.md                          # Master file overview & quick start
├── porchlight-spec.md                 # System Architecture & Specification
├── porchlight-tasks.md                # Task Taxonomy & Implementation Roadmap
├── porchlight-dashboard-ui-spec.md    # Spatial Dashboard & UI Specification
├── porchlight-dashboard.json          # Importable Grafana Portal Dashboard
├── docker-compose.yml                 # Service container orchestration
├── .env.example                       # Environment variables template
├── engine/                            # Porchlight Middleware Engine
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # Entry point worker
│   │   ├── config.py                  # Pydantic settings
│   │   ├── clients/                   # API clients (I/O only)
│   │   │   ├── homeassistant.py
│   │   │   ├── provisions.py          # Porchlight Provisions (Grocy-backed) client
│   │   │   ├── firefly.py             # Firefly III fixed-cost client
│   │   │   └── influx.py
│   │   ├── metrics/                   # Pure targeting-system calculations
│   │   │   ├── provisions_metrics.py  # Provisions valuation, $/2k kcal, reorder alerts
│   │   │   ├── energy_metrics.py      # EUR
│   │   │   └── property_metrics.py    # PFOR & occupant settlement
│   │   └── services/                  # Orchestration & DR-AIS logging
│   │       ├── ocr_parser.py
│   │       ├── rates_allocator.py
│   │       └── drais_logger.py
│   └── tests/
└── logs/                              # DR-AIS Decision Record logs
```

---

## Development & Coding Standards

1. **Async & Type Hints**: All I/O-bound Python backend code in `porchlight-engine` must use strict type annotations and `asyncio` (`httpx` or `aiohttp`). Pure computation (metrics, parsing) does not need to be forced into `async`.
2. **Pydantic Validation**: All API responses, receipt OCR outputs, and DR-AIS decision records must be validated using Pydantic v2 models.
3. **UTC Datetime Standard**: Always use timezone-aware UTC objects (`datetime.datetime.now(datetime.UTC)`), never naive or `utcnow()`.
4. **Privacy First**: No telemetry or household logs may be transmitted outside the local Docker network.
5. **DR-AIS Decision Record Standard**: Every automated action or financial allocation must emit a JSON Decision Record:

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

Use the shared `engine/app/services/drais_logger.py` (`DecisionRecord` + `emit_decision_record`) to emit these — don't hand-roll another copy of this schema per service.

---

## Step-by-Step Claude Code Prompts

### Step 1: Docker Stack Verification
> *"Read `porchlight-spec.md` and `docker-compose.yml`. Verify that all container services (`porchlight-homeassistant`, `porchlight-grocy`, `porchlight-firefly`, `porchlight-influxdb`, `porchlight-grafana`, `porchlight-engine`) are configured properly with health checks."*

### Step 2: Engine Configuration & API Clients
> *"In `engine/app/config.py`, create a Pydantic Settings class for Porchlight loading environment variables for HA, Provisions, Firefly, and InfluxDB URLs and tokens."*

### Step 3: Provisions & Rates Service Testing
> *"Run `python -m app.clients.provisions` and `python -m app.services.rates_allocator` (from the `engine/` directory) to verify mock telemetry calculations and DR-AIS logging."*
