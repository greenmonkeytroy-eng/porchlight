# Porchlight OS — Dashboard UI & Spatial Architecture Specification (v2)

## Executive Overview
The **Porchlight Portal Dashboard UI** uses a **Central Hub & Spoke** layout anchored by the **House Icon**. This interface organizes household telemetry around an **Above the Line (ATL)** vs. **Below the Line (BTL)** spatial divide, providing instant visual legibility for both macro-financial health and daily operational throughput.

Positioned prominently in the header above the house is the **Timescape Time Horizon Activator**—a predictive simulation control that allows occupants to slide through time horizons (Real-Time, 1 Month, 1 Year, 5 Years, 10 Years, 30 Years) to project forward with predictive rates, property taxes, utility tariff escalations, asset decay curves, and sinking fund requirements.

---

## 🎨 Spatial Layout Blueprint

```text
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

## 🏛️ Zone Definitions & Panel Breakdown

### 1. Top Header: Timescape Time Horizon Activator & Baseline Meters (ATL)
Positioned at the top header directly above the house icon to serve as the master temporal lens and financial/energy baseline for the entire dashboard:

* **⏱️ Timescape Time Horizon Activator (Interactive Control Bar)**:
  * **Selector Options**: `[ Real-Time | 1 Month | 1 Year | 5 Years | 10 Years | 30 Years ]`
  * **Function**: Switches the entire dashboard view from real-time operational telemetry to forward-looking predictive simulations powered by the **Timescape Engine**.
  * **Predictive Projections Triggered**:
    * **Property Taxes & Council Rates**: Models statutory compounding rate increases over 1–30 years.
    * **Insurance & Strata Levies**: Simulates premium inflation and capital sinking fund reserve needs.
    * **Utility Tariff Escalations**: Projects rising standing supply connection fees and peak/off-peak kWh charges into future Effective Utility Rates (EUR).
    * **Asset Decay & Replacement Horizons**: Projects solar PV efficiency decay, battery cycle life, and HVAC replacement dates onto the timeline.

* **Property Fixed Overhead Ratio (PFOR %)**: Real-time gauge and forward projection showing the % of monthly income locked into fixed structural costs.
* **Monthly Fixed Baseline ($)**: Current or projected council rates, strata/HOA levies, building insurance, and standing connection fees.
* **Live & Predictive Utility Meters**:
  * **Electric Meter**: Instantaneous draw (kW) & cumulative off-peak ratio (OER %).
  * **Water Meter**: Current flow rate (L/min) & daily volume.
  * **Effective Utility Rate (EUR)**: True cost per kWh/kL inclusive of standing charges, projected into future tariff scenarios.

---

### 2. Central Anchor: The House Icon
* **Role**: Primary visual hub representing the physical home.
* **Status Halo**: Glows green (optimal), yellow (buffer warning), or red (maintenance/overhead spike).
* **Interactivity**: Clicking the House Icon resets all expanded side drawers and returns the Time Horizon Activator back to `Real-Time`.

---

### 3. Left Side Node: Above the Line (ATL) — Infrastructure, Asset & Risk Hub
Plugged into the **Left** side of the House (representing capital inputs, structural assets, and risk contracts).

* **Expandable Drawer Contents**:
  1. **PowerMesh Energy Assets**: Solar PV generation curve, home battery State of Charge (SoC %), EV battery level, grid feed-in tariff.
  2. **Timescape Horizon (Sinking Funds)**: 12-month to 30-year capital reserve trajectory for major property maintenance (roofing, plumbing, driveway).
  3. **Fixed Contracts, Rates & Insurance**:
     * Municipal Council Rates & Land Tax.
     * HOA / Body Corporate Strata Levies (Admin vs Capital fund).
     * 🛡️ Building & Contents Insurance coverage limits, deductibles, and pre-renewal market re-quote triggers.
  4. **Asset Health & Decay Models**: HVAC heat pump duty cycles, solar panel degradation, appliance lifespan forecasts.

---

### 4. Right Side Node: Below the Line (BTL) — Provisions & Operations Hub
Plugged into the **Right** side of the House (representing operational throughput and daily consumables).

* **Expandable Drawer Contents**:
  1. **Porchlight Provisions (Consumables Node)**:
     * **Food & Nutrition**: Cost per 2,000 kcal ($/2k kcal), caloric stock, 3-day spoilage risk list.
     * **Household & Cleaning**: Paper goods, sanitation burn-rates, days of supply remaining.
     * **Pet Care & Vitality**: Kibble stock, feeding cost per pet, prescription buffers.
     * **Personal Care & Wellness**: Toiletries and hygiene supplies.
     * **Building & Hardware**: HVAC air filters, water softener salt levels.
  2. **TaskForce & Maintenance Operations**: Robot vacuum fleet status, waste management schedule, filter change timers.

---

### 5. Below the House: Occupants & Lifestyle Layer (BTL Outcomes)
Positioned at the bottom footer to highlight human outcomes and personal variable spending:
* **Family Member / Occupant Avatars**:
  * Individual occupant nodes (Occupant A, Occupant B, etc.).
  * Displays direct personal spending, equal share of fixed house overhead, sub-metered power, and net end-of-month settlement due ($).
* **Subscriptions & Entertainment Audit**:
  * Active streaming, software, broadband, and membership recurring charges.
  * Overlap detection (e.g., duplicate streaming services or unused subscriptions).

---

## 🛠️ Grafana Grid Mapping (`porchlight-dashboard.json`)

| Panel Title | Zone | Grid Position (x, y, w, h) |
| :--- | :--- | :--- |
| **⏱️ Timescape Time Horizon Activator** | Above House (Top) | `x: 0, y: 0, w: 24, h: 2` |
| **PFOR & Fixed Overhead Summary** | Above House | `x: 0, y: 2, w: 8, h: 4` |
| **Live & Predictive Utility Meters** | Above House | `x: 8, y: 2, w: 8, h: 4` |
| **Effective Utility Rate (EUR)** | Above House | `x: 16, y: 2, w: 8, h: 4` |
| **ATL Infrastructure Node (PowerMesh, Insurance & Sinking Funds)** | Left Node | `x: 0, y: 6, w: 7, h: 10` |
| **Central House Anchor & System Status** | Center | `x: 7, y: 6, w: 10, h: 10` |
| **BTL Provisions Node (Consumables & Operations)** | Right Node | `x: 17, y: 6, w: 7, h: 10` |
| **Family Member Avatars & Settlement Ledger** | Below House | `x: 0, y: 16, w: 14, h: 6` |
| **Subscriptions & Entertainment Audit** | Below House | `x: 14, y: 16, w: 10, h: 6` |
