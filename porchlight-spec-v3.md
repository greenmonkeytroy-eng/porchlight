# Porchlight OS — System Architecture & Specification (v3)

## Executive Summary
**Porchlight** (or **Porchlight OS**) is a privacy-first, locally hosted **Digital Twin of Domestic Operations**. By applying the **Industrial Intelligence Stack** to household logistics, economics, and resource flows, Porchlight elevates home management from an informal, unmeasured craft (**L0: The Muddle**) to an automated, compute-bound utility (**L3/L4: Automated & Industrialized Abundance**).

Porchlight tracks resource throughputs (food, energy, water, money, fixed property overheads) per occupant and executes automated optimizations to lower living costs, eliminate waste, and minimize domestic cognitive overhead.

---

## 1. Theoretical Grounding: Industrial Intelligence Stack
Porchlight operationalizes the core mechanisms of the *Solve Everything* framework at the household scale:

* **Observability (The Eyes)**: Instrumented legibility across food stock, power draw, water consumption, cash flow, council rates, HOA levies, and insurance via local sensors and financial APIs.
* **Task Taxonomy (The Map)**: Granular deconstruction of food planning, cost allocation, utility scheduling, fixed overhead management, and preventive home maintenance.
* **Targeting System (The Harness)**: Quantitative target metrics (e.g., *Cost per 2,000 kcal*, *Property Fixed Overhead Ratio (PFOR)*, *Effective Utility Rate (EUR)*, *Food Spoilage Ratio*).
* **Action Surfaces (The Hands)**: Integrations with Home Assistant, smart electric panels, and grocery delivery APIs for autonomous execution.
* **Governance & DR-AIS**: Immutable, transparent Decision Records for AI Systems to ensure multi-occupant trust and budget safety.

---

## 2. High-Level Porchlight Architecture

```
                                  [ PHYSICAL HOUSEHOLD ]
                                             │
      ┌──────────────────────────────┬───────┴──────────────────────┬──────────────────────────────┐
      ▼                              ▼                              ▼                              ▼
[ Smart Panel / Plugs ]      [ Smart Water Meter ]       [ Pantry / Grocy ERP ]        [ Bank / Card / Rates Feeds ]
      │                              │                              │                              │
      └──────────────────────────────┼──────────────────────────────┘                              │
                                     ▼                                                             ▼
                          [ Home Assistant Core ] ◄───────────────────────────────────── [ Firefly III / Actual ]
                                     │
                        ┌────────────┴────────────┐
                        ▼                         ▼
               [ InfluxDB / Grafana ]    [ Porchlight Digital Twin Engine ]
               (Porchlight Analytics)         (Metrics, SOPs, Agents)
                                                  │
                                                  ▼
                                      [ Action Surfaces & DR-AIS ]
                                     (Grid-Shifting, Auto-Orders)
```

---

## 3. Core Subsystems & Components

### 3.1 Local Core Operating System: Home Assistant (`porchlight-homeassistant`)
* **Role**: Central message bus, device state tracker, and event automation engine.
* **Deployment**: Docker container or Dedicated OS (Raspberry Pi 4/5 or Home Server).
* **Key Protocols**: Zigbee, Z-Wave, ESPHome, MQTT, local REST/WebSocket APIs.

### 3.2 Pantry & Food ERP: Grocy (`porchlight-grocy`)
* **Role**: Itemized food inventory, barcode tracking, expiration management, and recipe modeling.
* **Integration**: REST API sync with Home Assistant and the Porchlight Engine.

### 3.3 Financial Ledger: Firefly III (`porchlight-firefly`)
* **Role**: Double-entry financial accounting, per-occupant cost tagging, rates/levies tracking, and recurring transaction auditing.
* **Ingestion**: Auto-sync via Plaid, SimpleFIN, or local CSV/receipt OCR parsers (Paperless-ngx / Porchlight OCR).

### 3.4 Telemetry & Analytics: InfluxDB + Grafana (`porchlight-influxdb` / `porchlight-grafana`)
* **Role**: High-frequency time-series store for energy, water, and environmental telemetry paired with the **Porchlight Portal** dashboard interface.

### 3.5 Porchlight Digital Twin Middleware Engine (`porchlight-engine`)
* **Role**: Calculates real-time metrics (PFOR, EUR, $/2k kcal), runs *in-silico* household simulations (budget/meal/energy projections), and executes agentic workflows.

---

## 4. House-Associated Fixed Costs Subsystem
Porchlight treats fixed property overheads as essential structural baselines:
1. **Municipal Council Rates & Land Tax**: Categorized as fixed structural overhead.
2. **Body Corporate / HOA Strata Levies**: Subdivided into administrative fund vs. capital sinking fund reserves.
3. **Building & Contents Insurance**: Tracked for annual renewal optimizations.
4. **Utility Standing Supply Charges**: Separated from volumetric usage to calculate true Effective Utility Rates.

---

## 5. Privacy & Data Sovereignty
1. **100% Local Execution**: All telemetry, financial logs, and sensor feeds remain on the local home network.
2. **Air-Gapped Core**: Core automations run without external cloud dependencies.
3. **Encrypted Credentials**: API tokens and financial credentials stored in encrypted environment vaults (`.env` / Docker secrets).
