# Porchlight OS — Master File Overview & Manifest

**System**: Porchlight OS (Domestic / Residential Digital Twin Node)  
**Product Suite**: Twinscape / Timescape Digital Twin Family  
**Target Environment**: Local Docker Stack + VS Code with Claude Code  

---

## 1. Final Production File Index

Below is the complete inventory of the final production files created for your **Porchlight OS** repository. Use these files when copying your workspace into VS Code.

| File Name | VS Code Target Location | Category | Purpose & Description |
| :--- | :--- | :--- | :--- |
| **`claude-code-instructions-v3.md`** | `CLAUDE.md` *(root)* | Guide / Context | Master instructions for Claude Code in VS Code. Defines directory structure, Pydantic/AsyncIO standards, DR-AIS schema, and step-by-step build prompts. |
| **`porchlight-spec-v3.md`** | `porchlight-spec-v3.md` | Architecture | Full system specification detailing the Industrial Intelligence Stack, 6 container subsystems, fixed property overhead framework, and local privacy model. |
| **`porchlight-tasks-v3.md`** | `porchlight-tasks-v3.md` | Task Taxonomy | Deconstructed domestic task primitives, core targeting system formulas (PFOR, EUR, $/2k kcal, FSR, OER), occupant settlement formulas, and 5-Phase execution plan. |
| **`docker-compose-v2.yml`** | `docker-compose.yml` | Infrastructure | Container orchestration file for Home Assistant, Grocy, Firefly III, InfluxDB v2, Grafana, and the Porchlight Middleware Engine. |
| **`grocy-client-v2.py`** | `engine/app/clients/grocy.py` | Python Core | Pantry ERP API client and metrics calculator. Fetches stock levels, calculates $/2k kcal, flags expiring items, and emits DR-AIS decision logs. |
| **`firefly-rates-client-v2.py`** | `engine/app/services/rates_allocator.py` | Python Core | Ingests council rates, HOA levies, insurance, and standing supply fees. Computes PFOR, EUR, and multi-occupant pro-rata monthly settlements. |
| **`receipt-parser-v2.py`** | `engine/app/services/ocr_parser.py` | Python Core | OCR receipt parsing pipeline using regex and confidence scoring to extract line items and emit DR-AIS logs for human-in-the-loop review. |
| **`porchlight-dashboard.json`** | Grafana Import | Analytics | Importable JSON configuration for the **Porchlight Portal** dashboard in Grafana, featuring real-time PFOR, EUR, $/2k kcal, FSR, and settlement panels. |

---

## 2. Version Evolution & File Mapping

During our iterative design process, several files evolved across three major revisions. The table below maps earlier iterations to their final production equivalents:

```
[ Iteration 1: Household Machine ]    ──► [ Iteration 2: Fixed Costs Added ] ──► [ Iteration 3: Porchlight OS (Final) ]
  • household-machine-spec.md                • household-machine-spec-v2.md          • porchlight-spec-v3.md
  • household-machine-tasks.md               • household-machine-tasks-v2.md         • porchlight-tasks-v3.md
  • claude-code-instructions.md              • claude-code-instructions-v2.md        • claude-code-instructions-v3.md (CLAUDE.md)
  • docker-compose.yml                       • docker-compose-v2.yml                 • docker-compose-v2.yml
  • grocy_client.py                          • grocy-client-v2.py                    • grocy-client-v2.py
  • receipt_parser.py                        • firefly_rates_client.py               • firefly-rates-client-v2.py
                                             • receipt_parser.py                     • receipt-parser-v2.py
                                             • porchlight-dashboard.json             • porchlight-dashboard.json
```

> **Recommendation**: For your final VS Code project setup, use the **v3 specifications**, **`docker-compose-v2.yml`**, and the **v2 Python script files**.

---

## 3. System Architecture Quick Reference

```
                             [ PHYSICAL HOUSEHOLD ]
                                        │
 ┌─────────────────────────┬────────────┴────────────┬─────────────────────────┐
 ▼                         ▼                         ▼                         ▼
[ Smart Electric Panel ]  [ Smart Water Meter ]     [ Pantry / Grocy ERP ]    [ Bank / Rates Feeds ]
 │                         │                         │                         │
 └─────────────────────────┼─────────────────────────┘                         │
                           ▼                                                   ▼
                [ Home Assistant Core ] ◄─────────────────────────── [ Firefly III Ledger ]
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
    [ InfluxDB / Grafana ]    [ Porchlight Digital Twin Engine ]
    (Porchlight Analytics)         (Metrics, SOPs, Agents)
                                         │
                                         ▼
                             [ Action Surfaces & DR-AIS ]
                            (Grid-Shifting, Auto-Orders)
```

---

## 4. Key Targeting System Metrics Summary

* **Property Fixed Overhead Ratio (PFOR %)**:
  $$\text{PFOR} = \left( \frac{\text{Council Rates + HOA Levies + Insurance + Standing Supply Charges}}{\text{Total Monthly Household Spend}} \right) \times 100$$
* **Effective Utility Rate (EUR $/kWh)**:
  $$\text{EUR} = \frac{\text{Fixed Connection Charges + Variable Usage Charges}}{\text{Total Consumption Units (kWh)}}$$
* **Food Efficiency ($/2,000 kcal)**:
  $$\text{Cost per 2k kcal} = \left( \frac{\text{Total Food Spend}}{\text{Total Calories Purchased}} \right) \times 2000$$
* **Food Spoilage Ratio (FSR %)**: Target $< 2.0\%$.
* **Per-Occupant Monthly Settlement**:
  $$\text{Occupant Due} = \text{Direct Personal Purchases} + \left( \frac{\text{Fixed House Overhead}}{\text{Active Occupants}} \right) + \text{Sub-metered Utilities}$$

---

## 5. VS Code Deployment Steps

1. **Initialize Project Directory**:
   ```bash
   mkdir porchlight && cd porchlight
   ```
2. **Setup `CLAUDE.md`**:
   Copy `claude-code-instructions-v3.md` into `porchlight/CLAUDE.md`.
3. **Copy Final Production Files**:
   Place `porchlight-spec-v3.md`, `porchlight-tasks-v3.md`, `docker-compose-v2.yml`, `grocy-client-v2.py`, `firefly-rates-client-v2.py`, `receipt-parser-v2.py`, and `porchlight-dashboard.json` into your workspace.
4. **Launch Stack**:
   ```bash
   docker compose up -d
   ```
5. **Prompt Claude Code**:
   > *"Read `CLAUDE.md` and `porchlight-spec-v3.md`. Let me know when the containers are healthy and ready to test."*
