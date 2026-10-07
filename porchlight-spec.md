# Porchlight OS — System Architecture & Specification (v4)

## Executive Summary
**Porchlight** (or **Porchlight OS**) is a privacy-first, locally hosted **Digital Twin of Domestic Operations** operating within the **Twinscape / Timescape** product family:
* **Twinscape Suite** *(Spatial & Observational Twin)*: Captures real-time physical state, IoT telemetry, consumables stock, and energy draw.
* **Timescape Suite** *(Temporal & Predictive Simulation Engine)*: Runs *in-silico* forward simulations across time horizons (1 month to 30 years) to project fixed property overheads, asset degradation curves, and life-stage financial trajectories.

Porchlight elevates home management from an informal, unmeasured craft (**L0: The Muddle**) to an automated, compute-bound utility (**L3/L4: Automated & Industrialized Abundance**).

---

## 1. Theoretical Grounding: Industrial Intelligence Stack & Spatial Architecture

### 1.1 The Industrial Intelligence Stack
Porchlight operationalizes the core mechanisms of the *Solve Everything* framework at the household scale:
* **Observability (The Eyes)**: Instrumented legibility across consumables stock, power draw, water flow, cash flow, council rates, HOA levies, and insurance via local sensors and financial APIs.
* **Task Taxonomy (The Map)**: Granular deconstruction of food/consumables management, cost allocation, utility scheduling, fixed overhead management, and preventive home maintenance.
* **Targeting System (The Harness)**: Quantitative target metrics (e.g., *Property Fixed Overhead Ratio (PFOR)*, *Effective Utility Rate (EUR)*, *Cost per 2,000 kcal*, *Food Spoilage Ratio (FSR)*).
* **Action Surfaces (The Hands)**: Integrations with Home Assistant, smart electric panels, and grocery delivery APIs for autonomous execution.
* **Governance & DR-AIS**: Immutable, transparent Decision Records for AI Systems to ensure multi-occupant trust and budget safety.

### 1.2 Above the Line (ATL) vs. Below the Line (BTL) Division
Porchlight divides household management into two fundamental tiers:
* **Above the Line (ATL) — Capital & Infrastructure (Left Node / Header)**: Fixed, strategic, and non-negotiable structural foundations (Council Rates, HOA Levies, Building/Contents Insurance, Solar/Battery Infrastructure, Timescape Capital Sinking Funds).
* **Below the Line (BTL) — Operations & Consumables (Right Node / Footer)**: Daily recurring, variable operational throughput (Porchlight Provisions: Food, Cleaning, Pet Care, Personal Care, Hardware; TaskForce Maintenance; Occupant Personal Spend).

---

## 2. High-Level Spatial Architecture (Central Hub & Spoke)

```
===================================================================================================
                                      [ TOP HEADER / ABOVE HOUSE ]
   ┌───────────────────────────────────────────────────────────────────────────────────────────┐
   │ ⏱️ TIMESCAPE TIME HORIZON ACTIVATOR: [ Real-Time | 1 Mo | 1 Yr | 5 Yrs | 10 Yrs | 30 Yrs ] │
   └───────────────────────────────────────────────────────────────────────────────────────────┘
   • Property Fixed Overhead Ratio (PFOR %) | Projected Fixed Baseline ($)
   • Live & Predictive Utility Meters: Power (kW/kWh) | Water (L/min) | Gas (MJ)
   • Effective Utility Rate (EUR $/kWh)
===================================================================================================

       [ LEFT NODE: ATL ]                 ┌───────────────────┐                 [ RIGHT NODE: BTL ]
   Capital & Infrastructure               │                   │              Consumables & Operations
 ┌───────────────────────────┐            │    ┌─────────┐    │            ┌───────────────────────────┐
 │ • PowerMesh / Solar / SoC │◄───────────┼────┤  HOUSE  ├────┼───────────►│ • Porchlight Provisions   │
 │ • Sinking Fund Runway     │ [EXPAND]   │    │  ICON   │    │ [EXPAND]   │   (Food, Cleaning, Pets)  │
 │ • Fixed Contracts & Rates │            │    └─────────┘    │            │ • TaskForce Maintenance   │
 │ • Insurance & Protection  │            │                   │            └───────────────────────────┘
 └───────────────────────────┘            └─────────┬─────────┘
                                                    │
===================================================================================================
                                    [ BOTTOM FOOTER / BELOW HOUSE ]
                       • Occupant Avatars (Family Members): Net Settlement Balances ($)
                       • Subscriptions & Entertainment: Monthly Service Audit & Flags
===================================================================================================
```

---

## 3. Core Subsystems & Components

### 3.1 Local Core Operating System: Home Assistant (`porchlight-homeassistant`)
* **Role**: Central message bus, device state tracker, and event automation engine.
* **Deployment**: Docker container with host networking or Dedicated OS (Raspberry Pi 4/5 or Home Server).

### 3.2 Consumables & Supply ERP: Porchlight Provisions (`porchlight-grocy`)
* **Role**: Itemized inventory management across 5 secondary categories:
  1. *Food & Nutrition* (Caloric yield, $/2k kcal, 3-day spoilage risks)
  2. *Household & Cleaning* (Sanitation, paper goods, burn-rate per duty cycle)
  3. *Pet Care & Vitality* (Kibble stock, daily feeding costs, medication buffers)
  4. *Personal Care & Wellness* (Hygiene & personal care goods)
  5. *Building & Hardware* (HVAC air filters, water softener salt, water filter cartridges)
* **Backend**: Powered by the Grocy ERP container (`porchlight-grocy`), fronted by the Porchlight Provisions middleware client (`engine/app/clients/provisions.py`).

### 3.3 Financial Ledger: Firefly III (`porchlight-firefly`)
* **Role**: Double-entry financial accounting, per-occupant cost tagging, rates/levies tracking, and recurring subscription auditing.

### 3.4 Telemetry & Analytics: InfluxDB + Grafana (`porchlight-influxdb` / `porchlight-grafana`)
* **Role**: High-frequency time-series store for energy, water, and environmental telemetry paired with the **Porchlight Portal** dashboard interface (`porchlight-dashboard.json`).

### 3.5 Porchlight Digital Twin Middleware Engine (`porchlight-engine`)
* **Role**: Executes Python AsyncIO microservices (`clients/provisions.py`, `clients/firefly.py`, `services/ocr_parser.py`), calculates real-time metrics (PFOR, EUR, $/2k kcal), runs Timescape predictive simulations, and emits DR-AIS Decision Records.

---

## 4. Privacy & Data Sovereignty
1. **100% Local Execution**: All telemetry, financial logs, and sensor feeds remain on the local home network.
2. **Air-Gapped Core**: Core automations run without external cloud dependencies.
3. **Encrypted Credentials**: API tokens and financial credentials stored in encrypted environment vaults (`.env` / Docker secrets).
