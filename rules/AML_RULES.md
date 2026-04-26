# AML_RULES.md — Master Detection Framework (ScoreSentinel)

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.0 | **Status:** Master Ruleset | **Author:** Atul Krishnan, CAMS
**Last Updated:** 26 April 2026

---

## 1. Executive Summary

ScoreSentinel is a G-SIB grade, rules-based transaction monitoring engine designed for full regulatory defensibility under **SR 11-7** standards. It moves beyond binary detection by employing a **Weighted Risk Matrix** that evaluates transactions across five independent risk dimensions.

### 1.1 The Five-Module Architecture

| Module | Core Logic | Weight | Baseline Document |
|---|---|---|---|
| **Customer Risk** | Entity type, ownership, and PEP status | 30% | `CUSTOMER_RULES.md` |
| **Structuring** | Smurfing and velocity patterns | 25% | `STRUCTURING_RULES.md` |
| **Geography** | Jurisdictional risk (Sender/Receiver) | 25% | `GEO_RULES.md` |
| **Transaction Type** | Mechanism-inherent risk (e.g., Crypto, Cash) | 20% | `TRANSACTION_RULES.md` |
| **Data Integrity** | Penalty for missing mandatory fields | (Additive) | `COMPOSITE_LOGIC.md` |

---

## 2. Core Detection Logic

### 2.1 The Composite Risk Score (CRS)
All transactions are scored on a normalized scale of **0–100**. 
- **Alert Threshold:** 60+ (triggers analyst review)
- **High Risk:** 80+ (triggers senior management escalation)

### 2.2 Dynamic Customer Segmentation (Tier 1 RBA)
To ensure business friendliness and operational efficiency, alert thresholds are dynamically calibrated by customer segment:
- **Institutional:** 75+ (High tolerance for volume)
- **Small Business:** 65+ (Moderate tolerance)
- **Retail / HNW:** 60+ (Standard sensitivity)

### 2.3 Jurisdictional Calibration
ScoreSentinel respects **Local Law Supremacy**. Data Integrity Penalties (DIP) are only applied to fields legally mandated in the transaction's specific jurisdiction, ensuring the model remains efficient across global borders.

---

## 3. High-Risk Triggers & Auto-Alerts

The following triggers bypass the scoring logic and generate **Immediate Sanctions/Compliance Alerts**:
1. **Tier 1A/1B Geo Involvement:** Any flow involving OFAC-sanctioned jurisdictions (e.g., Iran, North Korea, Russia).
2. **PEP Tier 1 Matching:** Onboarding or transaction involving Heads of State or Cabinet-level officials.
3. **85% Fuzzy Match:** Direct matches against consolidated sanctions lists.
4. **OFAC 50% Rule:** Entities owned 50% or more by sanctioned parties.

---

## 4. Governance & Auditability

### 4.1 SR 11-7 Compliance
- **No Black-Box ML:** Every score is explainable in plain English.
- **Traceability:** Every alert includes a full breakdown of the rules fired and their individual score contributions.
- **Calibration:** Rules are reviewed semi-annually against actual SAR conversion rates.

### 4.2 Audit Trail
Every scoring decision is logged with:
- Timestamp & User ID
- Pre-scored metadata
- Individual module scores
- Final disposition (Review/Escalate/Clear)

---

## 5. Master Index of Rulesets

| Document | Purpose |
|---|---|
| `STRUCTURING_RULES.md` | Patterns for avoiding reporting thresholds |
| `GEO_RULES.md` | Jurisdictional risk and sanctions logic |
| `CUSTOMER_RULES.md` | Risk profiling of individuals and entities |
| `TRANSACTION_RULES.md` | Risk by transaction mechanism and velocity |
| `COMPOSITE_LOGIC.md` | Normalization, weighting, and calibration logic |

---
*ScoreSentinel | Master Framework | Authored by Atul Krishnan, CAMS | Version 1.0*
