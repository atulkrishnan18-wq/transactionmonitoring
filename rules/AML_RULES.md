# AML_RULES.md — Master Detection Framework

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.2 | **Status:** Master Ruleset | **Author:** Atul Krishnan, CAMS
**Last Updated:** 3 May 2026

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Core Detection Logic](#2-core-detection-logic)
3. [High-Risk Triggers & Auto-Alerts](#3-high-risk-triggers--auto-alerts)
4. [Governance & Auditability](#4-governance--auditability)
5. [Master Index of Rulesets](#5-master-index-of-rulesets)
6. [Version History](#6-version-history)

---

## 1. Executive Summary

ScoreSentinel is a rules-based AML transaction risk scoring engine designed for full regulatory defensibility under **SR 11-7** model risk governance standards. It moves beyond binary detection by employing a **Weighted Composite Risk Score (CRS)** that evaluates every transaction across four independent risk dimensions.

ScoreSentinel is not a machine learning model. Every score is traceable to a documented rule with explicit justification. Any compliance officer can explain any score to a regulator in plain English.

### 1.1 The Four-Module Architecture

| Module | Core Logic | Weight | Baseline Document |
|---|---|---|---|
| **Customer Risk** | Entity type, ownership transparency, PEP status, beneficial owner | 30% | `CUSTOMER_RULES.md` |
| **Structuring** | Smurfing patterns, velocity, micro-structuring, near-threshold behaviour | 25% | `STRUCTURING_RULES.md` |
| **Geography** | Jurisdictional risk — sender and receiver — OFAC, FATF, CPI | 25% | `GEO_RULES.md` |
| **Transaction Type** | Mechanism-inherent risk — crypto, cash, wire, correspondent banking | 20% | `TRANSACTION_RULES.md` |

> **Design Note — Why Four Modules, Not Five:**
> Data integrity (missing beneficial owner, incomplete KYC fields) is handled within the Customer Risk module through the Ownership Transparency dimension defined in `CUSTOMER_RULES.md` Section 3.3. It is not a standalone scoring module. This prevents double-counting and keeps the composite score architecture clean and SR 11-7 compliant.

---

## 2. Core Detection Logic

### 2.1 The Composite Risk Score (CRS)

All transactions are scored on a normalised scale of **0–100**.

```
STEP 1 — Normalise each module score to 0–100:
  Normalised = (Raw Score / Module Maximum) × 100

STEP 2 — Apply weights:
  CRS = (Customer × 30%) + (Structuring × 25%)
      + (Geography × 25%) + (Transaction Type × 20%)

Module Maximums:
  Customer Risk     : 175
  Structuring       : 70
  Geography         : 100
  Transaction Type  : 55
```

### 2.2 Risk Band & Alert Thresholds

| CRS Range | Risk Band | Action | Review Frequency |
|---|---|---|---|
| 0–20 | 🟢 Low Risk | Standard monitoring | Every 24 months |
| 21–40 | 🟡 Medium-Low | Standard monitoring + logging | Every 18 months |
| 41–59 | 🟠 Medium-High | Enhanced monitoring — analyst queue | Every 12 months |
| 60–79 | 🔴 High Risk | Alert generated — analyst review required | Every 6 months |
| 80–100 | 🔴🔴 Very High Risk | Alert generated — senior escalation required | Every 3 months |
| AUTO-ALERT | 🚨 Sanctions / PEP Tier 1 | Immediate escalation — bypasses CRS entirely | Immediate |

> **Threshold Justification:** A single alert threshold of 60 applies universally across all customer types. This threshold cannot be reached without at least two independent risk factors being elevated simultaneously — preventing single-factor false positives while ensuring genuine multi-factor risk is captured. Full threshold justification is documented in `COMPOSITE_LOGIC.md` Section 7.

> **SR 11-7 Note:** Dynamic threshold segmentation by customer type has not been implemented in Version 1.0. A single universal threshold of 60 is used. Segmented thresholds may be introduced in a future version once back-testing data is available to justify differential calibration per customer segment with documented SR 11-7 rationale.

### 2.3 Normalisation Rationale

Raw module scores operate on different scales — Customer Risk maximum is 175, Transaction Type maximum is 55. Without normalisation, Customer Risk would dominate the composite regardless of assigned weights. Normalising each module to 0–100 before weighting ensures every module contributes proportionally according to its documented weight. This is a mandatory SR 11-7 requirement — weights must reflect intended contribution, not raw scale differences.

---

## 3. High-Risk Triggers & Auto-Alerts

The following conditions generate immediate alerts that **bypass the CRS entirely**. These are hard rules, not scored variables.

| # | Trigger | Rule Reference | Action |
|---|---|---|---|
| 1 | Country involved is Tier 1A or Tier 1B (OFAC sanctioned) | `GEO_RULES.md` | 🚨 Sanctions Alert — immediate escalation to Compliance Officer |
| 2 | PEP Tier 1 customer confirmed (Head of State, Cabinet Minister) | `CUSTOMER_RULES.md` | 🚨 PEP Alert — EDD mandatory, senior approval required |
| 3 | Sanctions name match ≥ 85% on OFAC SDN List | `GEO_RULES.md` | 🚨 Sanctions Alert — transaction held, escalation within 24 hours |
| 4 | OFAC 50% Ownership Rule triggered | `GEO_RULES.md` | 🚨 Sanctions Alert — entity treated as sanctioned |
| 5 | Structuring normalised score ≥ 75% | `COMPOSITE_LOGIC.md` | 🚨 Structuring Alert — deliberate evasion pattern confirmed |

### 3.1 Why Auto-Alerts Bypass CRS

Sanctions and deliberate structuring carry strict liability under OFAC regulations and BSA respectively. No scoring model should be permitted to suppress an alert on these triggers — a low CRS must never clear a sanctions hit or a confirmed structuring pattern. The CRS measures combined risk. Auto-alerts measure absolute violations.

### 3.2 Two Alert Types

| Alert Type | Trigger | Reviewer | Timeframe |
|---|---|---|---|
| 🚨 **Sanctions Alert** | Triggers 1–4 above | Compliance Officer | Within 24 hours |
| ⚠️ **AML Risk Alert** | CRS ≥ 60 or Trigger 5 | AML Analyst | Within 5 business days |

---

## 4. Governance & Auditability

### 4.1 SR 11-7 Compliance

ScoreSentinel is fully compliant with SR 11-7 model risk management guidance:

| SR 11-7 Requirement | How ScoreSentinel Meets It |
|---|---|
| **No Black-Box ML** | Every score is traceable to a documented rule — no algorithmic weights |
| **Explainability** | Any score can be explained in plain English to a regulator or auditor |
| **Threshold Justification** | Every threshold is documented with explicit rationale in each module document |
| **Weight Derivation** | All four module weights are documented with regulatory and operational rationale |
| **False Positive Management** | Target false positive rate < 15% — documented in `COMPOSITE_LOGIC.md` |
| **Ongoing Monitoring** | Semi-annual recalibration against actual SAR conversion rates |
| **Independent Validation** | Planned for Day 45 of the 60-day build |
| **Back-Testing** | Planned for Day 30 of the 60-day build |

### 4.2 Audit Trail Requirements

Every scoring decision is logged with the following mandatory fields:

```
AUDIT LOG — MANDATORY FIELDS PER TRANSACTION:

- Transaction ID
- Customer ID
- Timestamp
- Pre-scored metadata (amount, type, countries, customer type)
- Individual module raw scores (all four)
- Individual module normalised scores (all four)
- Weighted CRS
- Risk band assigned
- Auto-alert triggered (yes/no — which trigger)
- Rules fired (list of rule IDs)
- Disposition (Review / Escalate / Clear)
- Reviewer ID (if manually reviewed)
- Review timestamp
- Reviewer rationale (mandatory for all escalations and clearances)
```

### 4.3 Recalibration Schedule

| Trigger | Frequency | Action |
|---|---|---|
| Scheduled review | Every 6 months | Compare false positive rate to 15% target — adjust thresholds if needed |
| FATF list update | As published | Update GEO_RULES.md Tier 1C country list |
| OFAC SDN update | 3–4 times per month | Update sanctions list, rescreen active customer base |
| CPI annual publication | Every January | Review Tier 2A/2B country assignments |
| SAR conversion rate review | Every 6 months | If alert-to-SAR ratio falls outside 5:1–20:1 range, recalibrate |
| Regulatory guidance update | As issued | Full review of affected modules |

---

## 5. Master Index of Rulesets

| Document | Location | Purpose | Day Built |
|---|---|---|---|
| `AML_RULES.md` | `rules/` | This document — master framework and index | Day 1 / Day 7 |
| `STRUCTURING_RULES.md` | `rules/` | Smurfing, velocity, micro-structuring patterns | Day 2 |
| `GEO_RULES.md` | `rules/` | OFAC tiers, FATF grey/black list, CPI scoring | Day 3 |
| `CUSTOMER_RULES.md` | `rules/` | Customer type taxonomy, CCRS, PEP matching | Day 4 |
| `TRANSACTION_RULES.md` | `rules/` | 19 transaction types, velocity rules, sequencing rules | Day 5 |
| `COMPOSITE_LOGIC.md` | `scoring/` | Normalisation, weighting, CRS calculation, calibration | Day 6 |
| `TEST_SCENARIOS.md` | `scenarios/` | 10 validation scenarios — master test set | Day 8 |
| `EDGE_CASES.md` | `scenarios/` | False positive prevention — edge case library | Day 9 |
| `VELOCITY_RULES.md` | `rules/` | Standalone velocity and behavioural pattern rules | Day 10 |
| `PEP_RULES.md` | `rules/` | PEP tier definitions, matching logic, beneficial owner | Day 11 |
| `AUDIT_REQUIREMENTS.md` | `governance/` | Compliance audit trail requirements | Day 13 |
| `VELOCITY_RULES.md` | `rules/` | Transaction velocity, Fan-In/Fan-Out, behavioural change indicators | Day 10 |
| `PEP_RULES.md` | `rules/` | UK MLR 2017 PEP tiers, beneficial owner dual threshold, fuzzy match | Day 11 |
| `VALIDATION_SCENARIOS.md` | `scenarios/` | Extended 10-scenario set — Vekselberg, Wirecard, TBML, Insurance ML | Day 12 |
| `MODEL_GOVERNANCE.md` | `governance/` | SR 11-7 full compliance documentation | Day 43 |
| `BACKTESTING.md` | `governance/` | Back-testing methodology and results | Day 44 |

---

## 6. Version History

| Version | Change | Date | Author |
|---|---|---|---|
| 1.0 | Initial draft — five-module architecture, dynamic segmentation | 26 April 2026 | Atul Krishnan, CAMS |
| 1.2 | Updated master index — added VELOCITY_RULES.md, PEP_RULES.md, VALIDATION_SCENARIOS.md. Updated date. | 1 May 2026 | Atul Krishnan, CAMS |
| 1.1 | Corrected to four-module architecture. Removed unvalidated dynamic threshold segmentation — replaced with universal threshold of 60 with SR 11-7 justification. Clarified data integrity as customer module dimension, not standalone module. Added master index with day references. Added version history. | 03 May 2026 | Atul Krishnan, CAMS |

---

*ScoreSentinel | AML_RULES.md | Master Detection Framework | Authored by Atul Krishnan, CAMS | Version 1.1 | 03 May 2026*
