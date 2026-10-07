# Porchlight OS — Task Taxonomy & Implementation Roadmap (v3)

## 1. Granular Task Taxonomy

### 1.1 Food & Nutrition Operations
* `TASK_FOOD_LOG_ENTRY`: Ingest item barcode, weight, purchase date, and expiration estimate into Grocy.
* `TASK_FOOD_CONSUMPTION_TAG`: Tag consumed food item to a specific occupant or shared household pool.
* `TASK_NUTRITION_CALC`: Compute total caloric and micronutrient yield per food purchase.
* `TASK_MEAL_PLAN_GEN`: Generate weekly meal plan prioritizing items within 3 days of expiration.
* `TASK_AUTO_REORDER_CHECK`: Check inventory levels against buffer thresholds and assemble shopping cart.

### 1.2 Per-Occupant Financial & Fixed House Accounting
* `TASK_TRANSACTION_INGEST`: Ingest bank/card transaction via API or receipt OCR.
* `TASK_RATES_LEVIES_INGEST`: Ingest council rate notices, HOA/strata levies, property taxes, and insurance bills into Firefly III.
* `TASK_FIXED_OVERHEAD_ALLOC`: Calculate each occupant's share of fixed house costs based on active residency days or room-share weighting.
* `TASK_COST_ATTRIBUTE`: Assign variable transaction to Occupant ID (Direct) or Shared Overhead (Pro-rata).
* `TASK_SUBSCRIPTION_AUDIT`: Identify recurring monthly billing and flag unused/overlapping services.
* `TASK_SETTLEMENT_CALC`: Generate end-of-month occupant balance ledger (Who owes what).

### 1.3 Energy & Utility Management
* `TASK_POWER_METER_READ`: Log watt-level draw per circuit / smart plug at 10-second intervals.
* `TASK_UTILITY_TARIFF_MODEL`: Parse electricity, water, and gas tariff structures (standing connection charges + peak/off-peak rates).
* `TASK_LOAD_SHIFT_SCHEDULE`: Shift dishwasher/laundry/EV charging to off-peak grid hours or peak solar hours.
* `TASK_WATER_ANOMALY_DETECT`: Monitor continuous flow thresholds to catch leaks or abnormal usage.

---

## 2. Porchlight Targeting Systems & Core Metrics Formulas

### Metric 1: Property Fixed Overhead Ratio (PFOR)
$$\text{PFOR (\%)} = \left( \frac{\text{Council Rates + HOA Levies + Insurance + Standing Connection Charges}}{\text{Total Monthly Household Spend}} \right) \times 100$$
*Target*: Track and stabilize structural housing baseline.

### Metric 2: Effective Utility Rate (EUR)
$$\text{EUR (\$/unit)} = \frac{\text{Fixed Connection Charges (\$) + Variable Usage Charges (\$)}}{\text{Total Consumption Units (kWh / kL / MJ)}}$$

### Metric 3: Cost per 2,000 kcal per Occupant ($/2k_kcal)
$$\text{Cost per 2,000 kcal} = \left( \frac{\text{Total Food Spend (\\$)}}{\text{Total Calories Purchased (kcal)}} \right) \times 2000$$

### Metric 4: Food Spoilage Ratio (FSR)
$$\text{FSR (\%)} = \left( \frac{\text{Financial Value of Expired/Discarded Food (\\$)}}{\text{Total Food Spend (\\$)}} \right) \times 100$$
*Target*: $< 2.0\%$

### Metric 5: Off-Peak Energy Utilization Ratio (OER)
$$\text{OER (\%)} = \left( \frac{\text{Kilowatt-Hours consumed during Off-Peak Hours}}{\text{Total Monthly Kilowatt-Hours consumed}} \right) \times 100$$
*Target*: $> 80.0\%$

---

## 3. Occupant Settlement Calculation
To ensure multi-occupant clarity, Porchlight calculates monthly settlements using:

$$\text{Occupant Monthly Total} = \text{Direct Personal Purchases} + \left( \frac{\text{Fixed House Overhead (Rates + Levies + Insurance + Standing Fees)}}{\text{Active Occupant Count}} \right) + \text{Sub-metered Variable Utilities}$$

---

## 4. Implementation Roadmap (Phases 1–5)

```
Phase 1: Porchlight Docker Stack (HA, Influx, Grocy, Firefly, Grafana)
  └─► Phase 2: Sensor Mesh & Fixed Overhead Ingestion (Rates, Utility Meters, Receipts)
        └─► Phase 3: Porchlight Engine Middleware (Python Metrics, PFOR/EUR, SOPs)
              └─► Phase 4: Autonomous Action Surfaces (Auto-Restock, Grid Load-Shifting)
                    └─► Phase 5: Multi-Occupant Governance & DR-AIS Logging
```
