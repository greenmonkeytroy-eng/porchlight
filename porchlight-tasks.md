# Porchlight OS — Task Taxonomy & Implementation Roadmap (v4)

## 1. Granular Task Taxonomy

### 1.1 Porchlight Provisions (Consumables Operations — BTL Right Node)
* `TASK_CONSUMABLE_LOG_ENTRY`: Ingest item barcode, weight, purchase date, category, and shelf-life estimate into Porchlight Provisions.
* `TASK_FOOD_NUTRITION_CALC`: Compute total caloric and micronutrient yield, Cost per 2,000 kcal ($/2k kcal), and 3-day spoilage risk list.
* `TASK_CLEANING_BURN_RATE_CALC`: Measure paper goods and sanitation burn-rate per duty cycle (e.g., dishwasher loads/week).
* `TASK_PET_CARE_BUFFER_CHECK`: Track kibble and pet medication stock, flagging reorders when buffer falls below safety thresholds.
* `TASK_HARDWARE_FILTER_MONITOR`: Track HVAC air filter and water filter duty cycles, triggering replacement alerts.
* `TASK_AUTO_RESTOCK_CHECK`: Assemble unified shopping cart across all 5 consumable categories when buffer thresholds are breached.

### 1.2 Fixed Property Overhead & ATL Capital Management (Left Node)
* `TASK_RATES_LEVIES_INGEST`: Ingest municipal council rate notices, HOA/strata levies, and land tax bills into Firefly III.
* `TASK_INSURANCE_RENEWAL_AUDIT`: Track building & contents insurance policies, deductibles, and run 60-day market re-quote audits before auto-renewal.
* `TASK_FIXED_OVERHEAD_ALLOC`: Calculate each occupant's share of fixed house costs based on active residency days or room-share weighting.
* `TASK_TIMESCAPE_HORIZON_SIM`: Run 1-year to 30-year forward simulations projecting rate inflation, insurance escalations, and major CapEx sinking fund requirements (roofing, plumbing, driveway).

### 1.3 Energy, Utilities & PowerMesh (Above House / Left Node)
* `TASK_POWER_METER_READ`: Log watt-level draw per circuit / smart plug at 10-second intervals.
* `TASK_UTILITY_TARIFF_MODEL`: Parse electricity, water, and gas tariff structures (standing connection charges + peak/off-peak rates) to compute Effective Utility Rate (EUR $/kWh).
* `TASK_POWERMESH_ARBITRAGE`: Shift EV charging, battery SoC, and heavy appliance loads to off-peak grid hours or peak solar generation windows.

### 1.4 Occupant Settlements & Subscriptions (Bottom Footer)
* `TASK_TRANSACTION_INGEST`: Ingest bank/card transactions via API or receipt OCR (`services/ocr_parser.py`).
* `TASK_SUBSCRIPTION_AUDIT`: Identify recurring monthly billing (streaming, software, broadband) and flag unused/overlapping services.
* `TASK_SETTLEMENT_CALC`: Generate end-of-month occupant balance ledger (Direct Personal + Equal Share Fixed Overhead + Sub-metered Power).

---

## 2. Core Targeting System Metrics & Formulas

### Metric 1: Property Fixed Overhead Ratio (PFOR) [Header Meter]
$$\text{PFOR (\%)} = \left( \frac{\text{Council Rates + HOA Levies + Insurance + Standing Connection Charges}}{\text{Total Monthly Household Spend}} \right) \times 100$$

### Metric 2: Effective Utility Rate (EUR) [Header Meter]
$$\text{EUR (\$/kWh)} = \frac{\text{Fixed Standing Supply Charges (\$) + Variable Usage Charges (\$)}}{\text{Total Consumption Units (kWh)}}$$

### Metric 3: Cost per 2,000 kcal per Occupant ($/2k_kcal) [Provisions Meter]
$$\text{Cost per 2,000 kcal} = \left( \frac{\text{Total Food Spend (\\$)}}{\text{Total Calories Purchased (kcal)}} \right) \times 2000$$

### Metric 4: Food Spoilage Ratio (FSR) [Provisions Target < 2.0%]
$$\text{FSR (\%)} = \left( \frac{\text{Financial Value of Expired/Discarded Food (\\$)}}{\text{Total Food Spend (\\$)}} \right) \times 100$$

### Metric 5: Off-Peak Energy Utilization Ratio (OER) [Target > 80.0%]
$$\text{OER (\%)} = \left( \frac{\text{Kilowatt-Hours consumed during Off-Peak Hours}}{\text{Total Monthly Kilowatt-Hours consumed}} \right) \times 100$$

---

## 3. Occupant Settlement Calculation Formula
$$\text{Occupant Monthly Due} = \text{Direct Personal Purchases} + \left( \frac{\text{Fixed House Overhead (Rates + Levies + Insurance + Standing Fees)}}{\text{Active Occupant Count}} \right) + \text{Sub-metered Utilities}$$

---

## 4. Implementation Roadmap (Phases 1–5)

```
Phase 1: Porchlight Docker Stack (HA, Provisions/Grocy, Firefly, Influx, Grafana)
  └─► Phase 2: Ingestion Pipelines (Rates, Insurance, Receipts OCR, Meter Telemetry)
        └─► Phase 3: Porchlight Digital Twin Engine (provisions client, rates allocator, DR-AIS)
              └─► Phase 4: Spatial Portal & Timescape Horizon Activator (Grafana)
                    └─► Phase 5: Multi-Occupant Governance & Autonomous Action
```
