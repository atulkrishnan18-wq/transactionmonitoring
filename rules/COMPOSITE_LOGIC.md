# COMPOSITE_LOGIC.md — Composite Scoring & Normalisation Framework

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.2 | **Day:** 6 of 60 | **Author:** Atul Krishnan, CAMS
**Last Updated:** 29 April 2026

---

## Table of Contents
1. [Purpose & Regulatory Basis](#1-purpose--regulatory-basis)
2. [Four-Module Architecture](#2-four-module-architecture)
3. [Auto-Alert Triggers — Independent of CRS](#3-auto-alert-triggers--independent-of-crs)
4. [Composite Risk Score Calculation](#4-composite-risk-score-calculation)
5. [Risk Band & Alert Thresholds](#5-risk-band--alert-thresholds)
6. [Weight Justification](#6-weight-justification)
7. [Normalisation Rationale](#7-normalisation-rationale)
8. [False Positive Management](#8-false-positive-management)
9. [Worked Examples](#9-worked-examples)
10. [SR 11-7 Model Risk Checklist](#10-sr-11-7-model-risk-checklist)
11. [Assumptions & Limitations](#11-assumptions--limitations)
12. [Version History](#12-version-history)

---

## 1. Purpose & Regulatory Basis

This document defines how ScoreSentinel combines individual module scores into a single **Composite Risk Score (CRS)** on a normalised scale of 0–100. The CRS determines alert status for every transaction processed by the engine.

### Regulatory Basis

- **SR 11-7** — Model risk management: weights, thresholds, and normalisation methodology must be documented and justified
- **FATF Recommendation 1** — Risk-based approach: composite risk must reflect relative severity of each risk dimension
- **BSA/AML Examination Manual** — Transaction monitoring systems must produce explainable, calibrated, and defensible scores

> **SR 11-7 Compliance Statement:** ScoreSentinel uses a weighted percentage model. Every weight is documented with explicit justification. Every score is traceable to a documented rule. The model produces a 0–100 CRS that any compliance officer can explain to a regulator in plain English. No machine learning or black-box algorithms are used at any stage.

---

## 2. Four-Module Architecture

ScoreSentinel evaluates every transaction across four independent risk dimensions. Each module has a defined raw score range and a documented maximum used for normalisation.

| Module | Weight | Raw Score Range | **Module Maximum** | Baseline Document |
|---|---|---|---|---|
| Customer Risk | 30% | 0–175 | **175** | `CUSTOMER_RULES.md` |
| Structuring | 25% | 0–70 | **70** | `STRUCTURING_RULES.md` |
| Geography | 25% | 0–100 | **100** | `GEO_RULES.md` |
| Transaction Type | 20% | 0–55 | **55** | `TRANSACTION_RULES.md` |

> **Critical Design Note — Why Four Modules, Not Five:**
> Data integrity (missing beneficial owner, incomplete KYC fields) is handled within the **Customer Risk module** through the Ownership Transparency dimension defined in `CUSTOMER_RULES.md` Section 3.3. It is not a standalone scoring module. This design prevents double-counting and keeps the composite score architecture clean and SR 11-7 compliant. Any missing data penalty is applied directly to the Customer Risk raw score — it does not add a fifth module or exceed the 175 maximum.

> **Version Note:** Earlier drafts of this document (v1.0) incorrectly listed Structuring maximum as 115 and Transaction Type maximum as 100, and included a Data Integrity module as a fifth scoring layer. Both errors have been corrected in this version. The correct maximums are Structuring = 70 and Transaction Type = 55, consistent with `STRUCTURING_RULES.md` and `TRANSACTION_RULES.md` respectively.

---

## 3. Auto-Alert Triggers — Independent of CRS

The following conditions generate **immediate alerts that bypass the CRS entirely**. These are hard rules — not scored variables. A low CRS must never suppress these triggers.

| # | Trigger | Threshold | Rule Reference | Alert Type |
|---|---|---|---|---|
| 1 | Country involved is Tier 1A or Tier 1B | Any involvement | `GEO_RULES.md` | 🚨 Sanctions Alert |
| 2 | PEP Tier 1 customer confirmed | Any onboarding or transaction | `CUSTOMER_RULES.md` | 🚨 PEP Alert — EDD mandatory |
| 3 | Sanctions name match on OFAC SDN List | ≥ 85% fuzzy match | `GEO_RULES.md` | 🚨 Sanctions Alert |
| 4 | OFAC 50% Ownership Rule triggered | ≥ 50% ownership by sanctioned entity | `GEO_RULES.md` | 🚨 Sanctions Alert |
| **5** | **Structuring normalised score** | **≥ 75%** | **`STRUCTURING_RULES.md`** | **🚨 Structuring Alert** |

### 3.1 Why Structuring Has Its Own Independent Trigger

Criminals structure transactions **specifically to keep individual amounts below scoring thresholds.** A structuring pattern strong enough to score 75% or above on the normalised structuring module represents a high-conviction deliberate evasion signal. If this were only captured through the composite CRS, a low customer risk score or domestic geography could mathematically suppress the alert — allowing the pattern to pass undetected.

The independent structuring trigger ensures that deliberate evasion behaviour alerts regardless of what other modules score.

```
Example — Why This Matters:
  Customer Risk (clean individual)  : 5/175  = 2.9%  × 30% = 0.87
  Structuring (smurfing confirmed)  : 55/70  = 78.6% × 25% = 19.65
  Geography (domestic)              : 0/100  = 0%    × 25% = 0
  Transaction Type (cash)           : 35/55  = 63.6% × 20% = 12.72
  CRS = 33.24 — below 60 threshold

  WITHOUT independent trigger → No alert → Criminal passes through
  WITH independent trigger    → Structuring = 78.6% ≥ 75% → 🚨 Alert
```

### 3.2 Two Alert Types

| Alert Type | Trigger | Reviewer | Timeframe |
|---|---|---|---|
| 🚨 **Sanctions / PEP Alert** | Triggers 1–4 | Compliance Officer | Within 24 hours |
| ⚠️ **AML Risk Alert** | CRS ≥ 60 OR Trigger 5 | AML Analyst | Within 5 business days |

---

## 4. Composite Risk Score Calculation

### 4.1 Two-Step Formula

```
STEP 1 — Normalise each module score to 0–100:

  Customer Normalised   = (Customer Raw   / 175) × 100
  Structuring Normalised = (Structuring Raw / 70)  × 100
  Geography Normalised  = (Geography Raw  / 100) × 100
  TxType Normalised     = (TxType Raw     / 55)  × 100

STEP 2 — Apply weights and sum:

  CRS = (Customer Normalised   × 0.30)
      + (Structuring Normalised × 0.25)
      + (Geography Normalised  × 0.25)
      + (TxType Normalised     × 0.20)

Alert Threshold: CRS ≥ 60
```

### 4.2 Module Maximum Reference Table

| Module | Maximum | Source Document | Section |
|---|---|---|---|
| Customer Risk | 175 | `CUSTOMER_RULES.md` | Section 5.1 |
| Structuring | 70 | `STRUCTURING_RULES.md` | Section 3 |
| Geography | 100 | `GEO_RULES.md` | Section 3.2 |
| Transaction Type | 55 | `TRANSACTION_RULES.md` | Section 2 |

> **Validation Rule:** If any module raw score exceeds its documented maximum, the score must be capped at the maximum before normalisation. Scores above 100% after normalisation indicate a data or calculation error and must be investigated before the alert is processed.

---

## 5. Risk Band & Alert Thresholds

| CRS Range | Risk Band | Action | Customer Review Frequency |
|---|---|---|---|
| 0–20 | 🟢 Low Risk | Standard monitoring | Every 24 months |
| 21–40 | 🟡 Medium-Low | Standard monitoring + logging | Every 18 months |
| 41–59 | 🟠 Medium-High | Enhanced monitoring — analyst queue | Every 12 months |
| 60–79 | 🔴 High Risk | Alert — analyst review required | Every 6 months |
| 80–100 | 🔴🔴 Very High Risk | Alert — senior escalation required | Every 3 months |
| AUTO-ALERT | 🚨 Hard Stop | Immediate escalation — bypasses CRS | Immediate |

### 5.1 Universal Threshold — Why 60

A single alert threshold of 60 applies universally across all customer types and transaction categories. This threshold was selected because:

1. It cannot be reached without **at least two independent risk factors** being elevated simultaneously — preventing single-factor false positives
2. A high-risk transaction type alone (e.g. crypto at 55/55 = 100% normalised × 20% = 20) cannot reach 60 without additional risk from other modules
3. A newly onboarded customer alone (30/175 = 17.1% × 30% = 5.1) cannot reach 60 without transaction, geography, or structuring risk
4. The threshold produces a target false positive rate of < 15% based on calibration against the 10 validation scenarios in `TEST_SCENARIOS.md`

> **SR 11-7 Note — Dynamic Segmentation Deferred:** Threshold segmentation by customer type (e.g. lower threshold for retail vs. institutional) has not been implemented in Version 1.0. A universal threshold of 60 is used pending back-testing data that would justify differential calibration with SR 11-7 documented rationale. This is a deliberate, documented deferral — not an oversight.

---

## 6. Weight Justification

### 6.1 Customer Risk = 30% (Highest Weight)

- Who the customer **is** remains the strongest single predictor of ML risk in practice
- Shell companies, PEPs, and tax haven associations are the highest-conviction signals encountered in real-world EDD reviews
- FATF Recommendation 10 places CDD at the centre of AML programs — reflecting customer profile as the primary risk variable
- Consistent with operational experience: customer profile drives the majority of high-risk escalations in Tier 1 bank screening operations
- 30% weight ensures customer risk can independently contribute meaningfully to the CRS without dominating it

### 6.2 Structuring = 25%

- Structuring is the most direct indicator of **deliberate evasion behaviour** — it requires intent, not just circumstance
- Pattern-based detection across multiple transactions is the strongest behavioural signal in the engine
- FATF Typologies consistently identify structuring as the primary placement-stage technique globally
- Equal weight to geography reflects that behavioural risk and jurisdictional risk are independent dimensions of equal regulatory importance

### 6.3 Geography = 25%

- Jurisdiction risk — applied to both sender and receiver — directly reflects regulatory enforcement gaps and corruption exposure
- FATF Recommendation 19 explicitly requires enhanced scrutiny for high-risk jurisdictions
- Equal weight to structuring because geographic risk is an independent dimension not correlated with customer type or transaction mechanism
- Dual-side application (sender + receiver both scored) provides comprehensive coverage within a single 25% module weight

### 6.4 Transaction Type = 20% (Lowest Weight)

- The transaction mechanism provides important context but is the least predictive dimension in isolation
- A cryptocurrency transaction from a verified clean customer in a low-risk jurisdiction is lower risk than a cash deposit from a shell company
- Transaction type acts as a **risk amplifier** for other modules rather than a standalone driver
- 20% weight reflects this supporting role — meaningful but not dominant

---

## 7. Normalisation Rationale

### 7.1 Why Normalisation Is Required

Raw module scores operate on incompatible scales:

| Module | Raw Maximum | Without Normalisation |
|---|---|---|
| Customer Risk | 175 | Would dominate composite at any weight |
| Structuring | 70 | Would be underweighted relative to customer |
| Geography | 100 | Intermediate — distorts at extremes |
| Transaction Type | 55 | Would be systematically underweighted |

Without normalisation, a customer risk score of 175 combined with a structuring score of 70 would produce vastly different composite results than intended by the 30/25 weight ratio — because the raw scales are incompatible.

Normalising each module to 0–100 before applying weights ensures every module contributes **proportionally according to its assigned weight** regardless of raw scale.

### 7.2 Normalisation Is Mandatory Under SR 11-7

SR 11-7 requires that model weights reflect their **intended contribution** to the output. If weights are applied to unnormalised raw scores, the effective contribution of each module deviates from the documented weights — making the model's behaviour inconsistent with its documentation. This is a model risk failure.

---

## 8. False Positive Management

### 8.1 Target Metrics

| Metric | Target | Breach Action |
|---|---|---|
| Overall false positive rate | < 15% | Full threshold review |
| Alert-to-SAR conversion ratio | 5:1 to 20:1 | Recalibrate threshold |
| Sanctions false positive rate | < 30% | Review matching thresholds |
| Recalibration frequency | Every 6 months | Scheduled review |

### 8.2 Threshold Calibration Logic

```
If false positive rate > 25% for 2 consecutive months:
  → Review threshold — consider upward adjustment (+5)

If alert-to-SAR ratio < 5:1:
  → Threshold too tight — review downward (-5)

If alert-to-SAR ratio > 20:1:
  → Threshold too loose — review upward (+5)

All adjustments require:
  → SR 11-7 documented justification
  → Back-testing against historical scenarios
  → Compliance Officer approval
```

### 8.3 Asymmetric Risk Tolerance for Auto-Alerts

ScoreSentinel deliberately accepts a **higher false positive rate** on auto-alert triggers (Tier 1A/1B sanctions, PEP Tier 1, structuring ≥ 75%) because:

- The cost of a missed sanctions hit = criminal liability + OFAC penalty
- The cost of a sanctions false positive = analyst review time (30–60 minutes)
- The asymmetry is extreme — false negatives are materially more costly than false positives on these triggers

This asymmetric risk tolerance is a **documented design decision**, not an oversight.

---

## 9. Worked Examples

### Example 1 — Shell Company Wire to Cayman (CRS Alert)

| Module | Raw | Max | Normalised | Weight | Contribution |
|---|---|---|---|---|---|
| Customer Risk | 90 | 175 | 51.4% | 30% | 15.42 |
| Structuring | 0 | 70 | 0% | 25% | 0 |
| Geography | 55 | 100 | 55% | 25% | 13.75 |
| Transaction Type | 45 | 55 | 81.8% | 20% | 16.36 |
| **CRS** | | | | | **45.53 — 🟠 Medium-High** |

---

### Example 2 — Classic Smurfing (Independent Trigger)

| Module | Raw | Max | Normalised | Weight | Contribution |
|---|---|---|---|---|---|
| Customer Risk | 30 | 175 | 17.1% | 30% | 5.13 |
| Structuring | 55 | 70 | 78.6% | 25% | 19.65 |
| Geography | 0 | 100 | 0% | 25% | 0 |
| Transaction Type | 35 | 55 | 63.6% | 20% | 12.72 |
| **CRS** | | | | | **37.5 — Below threshold** |

**Structuring normalised = 78.6% ≥ 75% → 🚨 Independent Structuring Alert fires**

---

### Example 3 — Verified Individual Domestic Wire (No Alert)

| Module | Raw | Max | Normalised | Weight | Contribution |
|---|---|---|---|---|---|
| Customer Risk | 5 | 175 | 2.9% | 30% | 0.87 |
| Structuring | 0 | 70 | 0% | 25% | 0 |
| Geography | 0 | 100 | 0% | 25% | 0 |
| Transaction Type | 15 | 55 | 27.3% | 20% | 5.46 |
| **CRS** | | | | | **6.33 — 🟢 Low Risk** |

---

## 10. SR 11-7 Model Risk Checklist

| Requirement | Status | Location |
|---|---|---|
| Model purpose documented | ✅ Complete | Section 1 |
| Four-module architecture documented | ✅ Complete | Section 2 |
| Module maximums explicitly stated | ✅ Complete | Section 2 & 4.2 |
| Auto-alert triggers documented | ✅ Complete | Section 3 |
| Structuring independent trigger justified | ✅ Complete | Section 3.1 |
| CRS formula documented | ✅ Complete | Section 4.1 |
| Weight derivation justified | ✅ Complete | Section 6 |
| Normalisation rationale documented | ✅ Complete | Section 7 |
| Alert threshold justified | ✅ Complete | Section 5.1 |
| False positive targets defined | ✅ Complete | Section 8.1 |
| Asymmetric risk tolerance documented | ✅ Complete | Section 8.3 |
| Dynamic segmentation deferral documented | ✅ Complete | Section 5.1 |
| Worked examples provided | ✅ Complete | Section 9 |
| Independent validation planned | 🔄 Pending | Planned Day 45 |
| Back-testing planned | 🔄 Pending | Planned Day 30 |

---

## 11. Assumptions & Limitations

- Module maximums are fixed at the values in Section 2. If future rule additions increase a module's maximum, this document must be updated and all scenarios recalculated
- The 60 threshold is calibrated against 10 validation scenarios in `TEST_SCENARIOS.md` — back-testing against historical transaction data is required to confirm calibration at scale
- The 30/25/25/20 weights reflect documented rationale but have not been empirically validated against historical SAR outcomes — weight adjustment may be required after back-testing
- Normalisation assumes raw scores will not exceed module maximums — a validation rule is defined in Section 4.2 to catch any violations
- Geographic risk is scored on both sender and receiver sides — the combined maximum for geography is therefore 100 (50 sender + 50 receiver, capped at 100 to prevent double-counting)
- The structuring independent trigger threshold of 75% was selected based on operational calibration — this should be reviewed against actual false positive rates after 6 months of operation

---

## 12. Version History

| Version | Change | Date | Author |
|---|---|---|---|
| 1.0 | Initial draft — five-module architecture including Data Integrity as standalone module. Incorrect module maximums: Structuring = 115, TxType = 100. Dynamic threshold segmentation included without SR 11-7 justification | 26 April 2026 | ScoreSentinel Build (Gemini) |
| 1.1 | Corrected to four-module architecture. Removed Data Integrity as standalone module — moved to Customer Risk ownership transparency dimension. Removed dynamic segmentation — replaced with universal threshold of 60. Added SR 11-7 compliance note on deferred segmentation | 26 April 2026 | Atul Krishnan, CAMS |
| 1.2 | Corrected module maximums: Structuring 115→70, TxType 100→55. Added structuring independent trigger (≥75%) to Section 3 with full justification and worked example. Added assumptions and limitations section. Added module maximum reference table. Added validation rule for scores exceeding maximum. Full SR 11-7 checklist updated | 29 April 2026 | Atul Krishnan, CAMS |

---

*ScoreSentinel | COMPOSITE_LOGIC.md | Composite Scoring & Normalisation Framework | Authored by Atul Krishnan, CAMS | Version 1.2 | 29 April 2026*