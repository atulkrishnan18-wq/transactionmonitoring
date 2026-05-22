# Rules Maintenance & Modification Guide

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.0 | **Author:** Atul Krishnan, CAMS | **Date:** 22 May 2026
**Purpose:** Technical and Governance procedures for engine updates.

---

## 1. Introduction

As financial crime typologies evolve, the ScoreSentinel engine requires periodic recalibration. To maintain **SR 11-7** compliance, any change to the model logic must follow the procedures outlined in this guide.

---

## 2. Modifying Scoring Weights

The Composite Risk Score (CRS) is calculated based on four weighted modules.

**File Location:** `scoring_engine.py`

### How to Modify:
Locate the `self.weights` dictionary in the `__init__` method:
```python
self.weights = {
    "customer": 0.30,
    "structuring": 0.25,
    "geo": 0.25,
    "transaction": 0.20
}
```
**Mandatory Rule:** The sum of all weights must exactly equal **1.00 (100%)**.

---

## 3. Adjusting Alert Thresholds

The universal threshold determines when a transaction triggers an alert.

**File Location:** `scoring_engine.py`

### How to Modify:
Locate `self.alert_threshold` in the `__init__` method:
```python
self.alert_threshold = 60
```
*   **Lowering:** Increases sensitivity (more alerts, higher False Positive rate).
*   **Raising:** Decreases sensitivity (fewer alerts, higher Miss Rate).

---

## 4. Updating Geographic Risk Tiers

Geographic tiers (1A, 1B, 2A, etc.) are based on OFAC, FATF, and CPI data.

**File Location:** `engine/geo_module.py`

### How to Add a Country:
Locate the tier lists in the `__init__` method and add the 2-letter ISO code:
```python
self.tier_1a_sanctions = ["IR", "KP", "SY", "CU", "RU"] # Example
```

---

## 5. Adding/Modifying Detection Rules

Each module contains specific rules (e.g., Round Number Avoidance, Fan-In Nexus).

**File Locations:**
*   `engine/customer_module.py`
*   `engine/structuring_module.py`
*   `engine/geo_module.py`
*   `engine/transaction_module.py`
*   `engine/mule_module.py`

### Procedure:
1.  **Define Rule:** Document the new rule in the relevant Markdown file in `rules/`.
2.  **Implementation:** Add the logic to the corresponding Python module.
3.  **Audit Trail:** Ensure the rule ID (e.g., `MUL-024`) is added to the `rules_fired` list in the module's return object.

---

## 6. Mandatory Regression Testing

**NEVER** deploy a logic change without regression testing.

### Steps:
1.  Modify the logic in the Python files.
2.  Run the master validation suite:
    ```powershell
    python tests/run_all_scenarios.py
    python tests/run_mule_scenarios.py
    ```
3.  Check `governance/BACKTESTING.md` to see if the detection rate for existing scenarios has changed.

---

## 7. Change Governance & Audit

Every modification to the scoring logic constitutes a **Model Version Update**.
1.  Increment the `engine_version` in `api/app.py`.
2.  Update the **Version History** in `ROADMAP.md`.
3.  Document the rationale for the change in a new audit note within the `governance/` folder.

---
*ScoreSentinel | docs/HOW_TO_MODIFY.md | Authored by Atul Krishnan, CAMS | 22 May 2026*
