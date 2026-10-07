# Porchlight OS

**System**: Porchlight OS (Domestic / Residential Digital Twin Node)
**Product Suite**: Twinscape / Timescape Digital Twin Family
**Target Environment**: Local Docker Stack

Porchlight is a privacy-first, locally hosted Digital Twin of Domestic Operations. It connects Home Assistant, Porchlight Provisions (a Grocy-backed consumables ERP), Firefly III, InfluxDB, and Grafana via a Python middleware engine (`porchlight-engine`) to track fixed/variable household costs and consumables, and surface them through a spatial Grafana dashboard.

See `CLAUDE.md` for engine coding standards, `porchlight-spec.md` for the full architecture, `porchlight-tasks.md` for the task taxonomy and metric formulas, and `porchlight-dashboard-ui-spec.md` for the dashboard's spatial layout.

---

## Repository Layout

```
porchlight_OS/
├── CLAUDE.md                          # Assistant instructions for Claude Code
├── README.md                          # This file
├── porchlight-spec.md                 # System architecture & specification
├── porchlight-tasks.md                # Task taxonomy, formulas & roadmap
├── porchlight-dashboard-ui-spec.md    # Spatial dashboard & UI specification
├── porchlight-dashboard.json          # Importable Grafana portal dashboard
├── docker-compose.yml                 # Service container orchestration
├── .env.example                       # Environment variables template
└── engine/                            # Porchlight middleware engine
    ├── Dockerfile
    ├── requirements.txt
    └── app/
        ├── main.py                    # Entry point worker
        ├── config.py                  # Pydantic settings
        ├── clients/                   # Async API clients (Provisions, Firefly)
        ├── metrics/                   # Pure metric calculations (PFOR, EUR, provisions)
        └── services/                  # Orchestration & DR-AIS decision logging
```

---

## Architecture Quick Reference

```
                             [ PHYSICAL HOUSEHOLD ]
                                        │
 ┌─────────────────────────┬────────────┴────────────┬─────────────────────────┐
 ▼                         ▼                         ▼                         ▼
[ Smart Electric Panel ]  [ Smart Water Meter ]  [ Porchlight Provisions ]  [ Bank / Rates Feeds ]
 │                         │                         │                         │
 └─────────────────────────┼─────────────────────────┘                         │
                           ▼                                                   ▼
                [ Home Assistant Core ] ◄─────────────────────────── [ Firefly III Ledger ]
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
    [ InfluxDB / Grafana ]    [ Porchlight Digital Twin Engine ]
    (Porchlight Analytics)         (Metrics, DR-AIS, Agents)
                                         │
                                         ▼
                             [ Action Surfaces & DR-AIS ]
                            (Grid-Shifting, Auto-Orders)
```

The dashboard itself is organized as **Above the Line (ATL)** — fixed capital & infrastructure — vs. **Below the Line (BTL)** — daily consumables & operations — around a central house icon; see `porchlight-dashboard-ui-spec.md` for the full spatial breakdown.

---

## Key Targeting System Metrics

* **Property Fixed Overhead Ratio (PFOR %)**:
  $$\text{PFOR} = \left( \frac{\text{Council Rates + HOA Levies + Insurance + Standing Supply Charges}}{\text{Total Monthly Household Spend}} \right) \times 100$$
* **Effective Utility Rate (EUR $/kWh)**:
  $$\text{EUR} = \frac{\text{Fixed Connection Charges + Variable Usage Charges}}{\text{Total Consumption Units (kWh)}}$$
* **Food Efficiency ($/2,000 kcal)**:
  $$\text{Cost per 2k kcal} = \left( \frac{\text{Total Food Spend}}{\text{Total Calories Purchased}} \right) \times 2000$$
* **Food Spoilage Ratio (FSR %)**: Target $< 2.0\%$.
* **Per-Occupant Monthly Settlement**:
  $$\text{Occupant Due} = \text{Direct Personal Purchases} + \left( \frac{\text{Fixed House Overhead}}{\text{Active Occupants}} \right) + \text{Sub-metered Utilities}$$

Full formulas and task taxonomy: `porchlight-tasks.md`.

---

## Running Locally (without Docker)

The engine runs standalone for development — no container required:

```bash
cd engine
pip install -r requirements.txt
python -m app.clients.provisions      # Provisions scoreboard demo
python -m app.services.rates_allocator  # PFOR/EUR/settlement demo
python -m app.services.ocr_parser     # Receipt OCR demo
```

Settings load from environment variables or a local `.env` (see `.env.example`); every client falls back to mock data if the corresponding service (Grocy, Firefly) isn't reachable.

## Running via Docker

```bash
cp .env.example .env   # fill in real tokens/passwords
docker compose up -d
```

Then import `porchlight-dashboard.json` into Grafana at `http://localhost:3000` (**Dashboards → Import**).
