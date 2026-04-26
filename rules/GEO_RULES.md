# GEO_RULES.md — Geographic Risk & Sanctions Scoring Rules

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.0 | **Day:** 3 of 60 | **Author:** Atul Krishnan, CAMS
**Last Updated:** 2025

---

## Table of Contents
1. [Purpose & Regulatory Basis](#1-purpose--regulatory-basis)
2. [Country Risk Tier Classification](#2-country-risk-tier-classification)
3. [Geographic Scoring Architecture](#3-geographic-scoring-architecture)
4. [Threshold Justification & Weight Derivation](#4-threshold-justification--weight-derivation)
5. [Sanctions Screening Logic](#5-sanctions-screening-logic)
6. [Worked Scoring Examples](#6-worked-scoring-examples)
7. [Model Governance & Maintenance](#7-model-governance--maintenance)

---

## 1. Purpose & Regulatory Basis

This document defines the geographic risk and sanctions screening rules for ScoreSentinel. Geographic risk is a mandatory component of AML transaction monitoring under:

- **FATF Recommendation 19** — Enhanced due diligence for higher-risk countries
- **FATF Recommendation 1** — Risk-based approach requiring documented country risk assessment
- **FinCEN guidance** — Geographic risk factors in transaction monitoring programs
- **SR 11-7 (Federal Reserve)** — Model risk management requiring documented, explainable, and validated scoring logic

> **SR 11-7 Compliance Statement**
> ScoreSentinel is a rules-based scoring engine, not a machine learning model. Every score is fully traceable to documented rules, threshold justifications, and weight derivations. This design ensures explainability to regulators, auditors, and model validators without requiring algorithmic black-box justification.

---

## 2. Country Risk Tier Classification

Countries are classified into tiers based on three independent regulatory sources:
- **OFAC** sanctions designations
- **FATF** mutual evaluation outcomes
- **Transparency International CPI** (Corruption Perceptions Index)

> A country may appear in **multiple tiers** — all applicable tier scores are **cumulative**.

---

### Tier 1A — OFAC Sanctioned AND FATF Black Listed 🔴

These jurisdictions carry the **highest possible risk designation** — comprehensive OFAC sanctions AND formally identified by FATF as requiring counter-measures.

**Rule:** Any transaction involving these countries triggers an **automatic Sanctions Alert** regardless of transaction amount or composite score.

| Country | OFAC Status | FATF Status | Score Added |
|---|---|---|---|
| Iran | Comprehensive Sanctions | Black List | **+50 \| AUTO-ALERT** |
| North Korea (DPRK) | Comprehensive Sanctions | Black List | **+50 \| AUTO-ALERT** |
| Myanmar | Military Regime Sanctions | Black List (added 2022) | **+50 \| AUTO-ALERT** |

---

### Tier 1B — OFAC Sanctioned (Comprehensive or Sectoral) 🔴

These jurisdictions are subject to OFAC sanctions but are not currently FATF black-listed.

**Rule:** Any transaction involving these countries triggers an **automatic Sanctions Alert** regardless of score.

| Country | Primary Sanctions Basis | Score Added |
|---|---|---|
| Syria | Comprehensive OFAC sanctions — Assad regime | **+40 \| AUTO-ALERT** |
| Cuba | Comprehensive OFAC embargo | **+40 \| AUTO-ALERT** |
| Russia | Sectoral sanctions post-2022 — financial, energy, defence | **+40 \| AUTO-ALERT** |
| Belarus | OFAC / EU sanctions — Lukashenko regime | **+40 \| AUTO-ALERT** |
| Venezuela | OFAC — senior officials and key sectors | **+40 \| AUTO-ALERT** |

---

### Tier 1C — FATF Grey List (Jurisdictions Under Increased Monitoring) 🟠

Formally identified by FATF as having strategic AML/CFT deficiencies. Transactions do **not** auto-alert but geo score is additive to transaction total.

| Country | Primary FATF Concern | Score Added |
|---|---|---|
| Afghanistan | Taliban designation, severe CFT deficiencies | +25 |
| Haiti | Governance collapse, weak financial controls | +25 |
| Nigeria | Grey listed 2023 — proceeds of crime, TF risk | +25 |
| South Africa | Grey listed 2023 — beneficial ownership gaps | +25 |
| Yemen | Conflict jurisdiction, Houthi TF risk | +25 |
| Pakistan | Historically grey-listed, elevated TF risk | +25 |
| Laos | Narcotics corridor, weak AML controls | +25 |
| Cambodia | Grey list + CPI 22 — double designation | +25 |
| Philippines | Grey list — casino risk, remittance exposure | +25 |
| Tanzania | Grey list — weak financial intelligence capacity | +25 |

---

### Tier 2A — High Corruption Risk (CPI Score 0–29) 🟠

Countries with a Transparency International CPI score of **0–29** indicate pervasive corruption, creating elevated risk of bribery-related proceeds, PEP exposure, and illicit fund flows.

> CPI is cited in FATF Recommendation 1 guidance as a valid geographic risk indicator.

| Country | CPI Score | Primary Risk | Score Added |
|---|---|---|---|
| Somalia | 11 | State failure, hawala, TF | +20 |
| Venezuela *(also Tier 1B)* | 13 | Kleptocracy, sanctions evasion | +20 |
| Syria *(also Tier 1B)* | 13 | Conflict, sanctions evasion | +20 |
| Bangladesh | 25 | Trade-based ML, garment sector | +20 |
| DR Congo | 20 | Conflict minerals, cash economy | +20 |

---

### Tier 2B — Elevated Corruption Risk (CPI Score 30–49) 🟡

Countries with CPI 30–49 carry meaningful corruption risk. This tier captures major economies not sanctioned or FATF-listed but with documented AML typology risk.

| Country | CPI Score | Primary Risk | Score Added |
|---|---|---|---|
| China | 42 | Capital flight, state-owned entity risk, PEPs | +15 |
| India | 39 | Hawala, trade-based ML, PEPs | +15 |
| Indonesia | 34 | PEP exposure, weak beneficial ownership | +15 |
| Kenya | 31 | East Africa hub, informal economy | +15 |
| Malaysia | 50 | 1MDB precedent, offshore exposure | +15 |
| Lebanon | 24 | Banking collapse, Hezbollah nexus | +15 |

---

### Tier 3 — Offshore / Secrecy Jurisdictions (Watch List) 🟡

Not sanctioned and may not be FATF-listed, but legal and financial infrastructure presents elevated risk of shell company abuse, beneficial ownership concealment, and layering activity.

| Jurisdiction | Primary Risk | Score Added |
|---|---|---|
| Cayman Islands | Offshore hub — hedge funds, shell structures | +15 |
| British Virgin Islands | Largest shell company registry globally | +15 |
| Panama | Panama Papers — layering and concealment | +15 |
| Seychelles | Beneficial ownership gaps, offshore IBC registry | +15 |
| Vanuatu | Pacific secrecy jurisdiction, citizenship by investment | +15 |
| Cyprus | EU member but offshore history, Russian exposure | +15 |

---

### Tier 4 — Standard Risk

All other countries not appearing in Tiers 1A through 3.

| Classification | CPI Range | Score Added |
|---|---|---|
| Standard / Low Risk | CPI 50+ | +0 |

---

## 3. Geographic Scoring Architecture

### 3.1 Scoring Applies to Both Transaction Ends

Geographic risk is assessed on **BOTH the sender country and the receiver country** for every transaction.

| Side | Why It Matters |
|---|---|
| **Sender country** | Assesses whether funds originate from a jurisdiction with elevated corruption, sanctions exposure, or AML deficiencies |
| **Receiver country** | Assesses whether funds are directed toward a jurisdiction where detection, enforcement, or transparency is limited |

> **Scoring Rule:** Both sides are additive. If sender = Tier 2B (+15) and receiver = Tier 1C (+25), total geo contribution = **+40**. If either side is Tier 1A or 1B → **Auto-Alert regardless of total score.**

### 3.2 Segmented Thresholds (Tier 1 RBA)

Thresholds for geographic risk are adjusted based on the `Customer Segment` to ensure that standard institutional payments between major hubs are not flagged unnecessarily, while high-risk individual flows are prioritized.

| Segment | Geo Risk Alert Threshold | Rationale |
|---|---|---|
| Institutional | 85+ | High-volume cross-border flows are standard |
| HNW | 70+ | Complex international structures |
| Retail | 60+ | Low-volume, domestic-centric profile |

### 3.3 Data Integrity Penalty (Geo-Context)

Missing data in cross-border flows is a primary layering indicator.

| Missing Field (Geo) | Penalty Score |
|---|---|
| Missing SWIFT/BIC code | +15 |
| Missing Receiver Bank Address | +10 |
| Missing "Purpose of Payment" on Tier 1C flow | +20 |

---

### 3.4 Score Integration with Existing ScoreSentinel Modules

Geography scores are **additive** to existing transaction scores.

| Component | Module | Score Range |
|---|---|---|
| Transaction amount & pattern | Structuring Rules (Day 1–2) | 0–70 |
| Sender country risk | GEO_RULES (this document) | 0–50 |
| Receiver country risk | GEO_RULES (this document) | 0–50 |
| **COMPOSITE TOTAL** | **All modules combined** | **0–170+** |

### 3.3 Alert Types

| Alert Type | Trigger | Reviewer |
|---|---|---|
| 🚨 **Sanctions Alert** | Any Tier 1A or 1B country involvement | Compliance Officer — urgent |
| ⚠️ **AML Risk Alert** | Composite score ≥ 60 | AML Analyst |

---

## 4. Threshold Justification & Weight Derivation

> **SR 11-7 Requirement:** Model developers must document the basis for threshold selection and weight derivation. Stating a threshold without justification is an assertion, not a model.

---

### 4.1 Why Tier 1A = +50

- Tier 1A carries a **dual designation** — OFAC sanctioned AND FATF black-listed
- Any transaction must trigger an alert independently of structuring score
- Minimum structuring score in the engine is approximately +10 for a clean transaction
- Alert threshold is 60. Therefore geo score must be ≥ 50 to guarantee alert even on lowest-risk transaction (10 + 50 = 60)
- +50 chosen rather than +60 to preserve composite score meaning
- Auto-Alert rule provides a secondary catch — even if composite < 60, Tier 1A still alerts

### 4.2 Why FATF Grey List = +25

- FATF grey list represents documented but not critical deficiencies — materially less severe than black list
- A clean, low-value transaction to a grey-listed country (10 + 25 = 35) should **not** alert
- A moderate transaction (score 35) to a grey-listed country (35 + 25 = 60) **should** alert
- Calibration principle: Grey list alone should not alert; grey list combined with other risk should alert

### 4.3 Why CPI Boundary = Score 30

- Transparency International defines 0–29 as **"highly corrupt"** — pervasive institutional corruption with systemic AML implications
- Score 30–49 is **"corrupt"** — meaningful risk but not systemic state capture
- Score 50+ treated as standard risk — aligns with TI's own categorization of 50 as the governance midpoint
- CPI boundary at 30 is consistent with FATF Recommendation 1 guidance on using objective corruption indices

### 4.4 False Positive Rate & Alert Volume Design

| Metric | Target | Rationale |
|---|---|---|
| False Positive Rate | < 15% | Operationally manageable — industry norm 10–20% |
| Alert-to-SAR Ratio | 10:1 to 20:1 | FinCEN / industry benchmark for calibrated TM programs |
| Sanctions False Positive Rate | < 30% | Higher tolerance acceptable — sanctions misses carry criminal liability |
| Recalibration Frequency | Every 6 months | Accounts for FATF updates, OFAC changes, CPI annual release |

> **Documented Design Decision:** ScoreSentinel deliberately accepts a higher false positive rate on Tier 1A/1B transactions (auto-alert regardless of score) because the cost of a missed sanctions hit (criminal liability, OFAC penalty) materially exceeds the cost of a false positive (analyst review time). This asymmetric risk tolerance is a documented design choice, not an oversight.

---

## 5. Sanctions Screening Logic

### 5.1 Six Mandatory Screening Fields

Every transaction must be screened across all six fields before processing.

| # | Field Screened | Screened Against | Why |
|---|---|---|---|
| 1 | Sender name | OFAC SDN List | Direct sender identification |
| 2 | Receiver name | OFAC SDN List | Direct receiver identification |
| 3 | Sender country | Tier 1A / 1B country list | Jurisdiction-level sanctions |
| 4 | Receiver country | Tier 1A / 1B country list | Jurisdiction-level sanctions |
| 5 | Intermediary bank (if wire) | OFAC SDN List | Correspondent banking exposure |
| 6 | Beneficial owner (if known) | OFAC SDN List | Indirect sanctions exposure |

> Screening only the account name is insufficient — sanctions evaders routinely use clean intermediaries.

---

### 5.2 Name Matching — Fuzzy Match Thresholds

| Match % | Match Type | Example | Action |
|---|---|---|---|
| 100% | Exact match | BANK MELLI IRAN | 🚨 Block + Sanctions Alert immediately |
| 85–99% | Strong fuzzy match | Mohamed Al-Qahtani vs Mohammed Al Qahtani | 🚨 Hold transaction + escalate for review |
| 70–84% | Moderate fuzzy match | Ali Hassan vs Ali Hasan | ⚠️ Flag for analyst review — do not block |
| < 70% | No match | Ali Hassan vs Alan Harris | ✅ Clear — no action required |

### 5.3 Why 85% Threshold — Justified Rationale

- At **70% threshold:** Estimated false positive rate ~40% — operationally unmanageable
- At **85% threshold:** Estimated false positive rate ~12% — acceptable, within SR 11-7 operational tolerance
- At **95% threshold:** Estimated miss rate ~8% — regulatorily unacceptable, genuine sanctions evasion risk
- 85% selected as the optimization point — consistent with SWIFT, Refinitiv, and major TM vendor default settings
- Threshold will be reviewed every 6 months against actual false positive outcomes

---

### 5.4 The OFAC 50% Ownership Rule

> If a company is owned **50% or more** by a sanctioned entity, that company is treated as sanctioned by OFAC — even if it does not appear on the SDN list by name.

**ScoreSentinel Rule:** Any transaction with a 50%-owned entity = **Tier 1B Auto-Alert**. Beneficial ownership data must be obtained at onboarding to enable this check.

---

### 5.5 Post-Hit Workflow

```
SANCTIONS HIT WORKFLOW:

Step 1 → HOLD transaction (not processed — automated)
Step 2 → Generate SANCTIONS Alert — distinct from AML Risk Alert (automated)
Step 3 → Escalate to Compliance Officer within 24 hours (AML Analyst)
Step 4 → Compliance Officer reviews: Real Hit or False Positive?
Step 5A → Real Hit: File OFAC report, block funds, notify management and legal
Step 5B → False Positive: Document reasoning, release transaction, update matching rules
```

> **Critical:** Even false positives must be **fully documented**. OFAC examiners review false positive clearance process as rigorously as actual hits. Undocumented clearances = compliance failure regardless of outcome.

---

### 5.6 Sanctions List Maintenance & Screening Frequency

| When to Screen | Trigger | Rationale |
|---|---|---|
| At transaction initiation | Every transaction | Catch exposure before funds move |
| At customer onboarding | New customer | Know Your Customer before first transaction |
| On SDN list update | OFAC publishes update | OFAC updates SDN list 3–4 times per month |
| Periodic rescreening | Every 90 days | Existing customers can be added to SDN list post-onboarding |

---

## 6. Worked Scoring Examples

| Transaction | Structuring Score | Sender Geo | Receiver Geo | Total | Alert? |
|---|---|---|---|---|---|
| $500 transfer — UK to US | 5 | +0 | +0 | 5 | ❌ No |
| $5,000 wire — India to Cayman Islands | 15 | +15 (CPI) | +15 (offshore) | 45 | ❌ No |
| $9,500 cash — Nigeria sender | 55 | +25 (FATF grey) | +0 | 80 | ⚠️ Yes |
| $500 wire — any country to Iran | 5 | +0 | +50 (Tier 1A) | 55 + AUTO | 🚨 Yes |
| $7,000 cash — India to Cambodia | 45 | +15 (CPI 39) | +45 (grey+CPI) | 105 | 🚨 Yes |
| $200 wire — China to BVI | 5 | +15 (CPI 42) | +15 (offshore) | 35 | ❌ No |

---

## 7. Model Governance & Maintenance

### 7.1 Assumptions & Limitations

- Country classifications are based on FATF and OFAC designations current at time of writing — lists change and must be reviewed per Section 5.6 schedule
- CPI scores are published annually by Transparency International — tier assignments must be reviewed each year upon CPI publication
- This model does not account for sub-national risk variation (e.g. OFAC-licensed exemptions within sanctioned countries)
- Beneficial ownership data quality directly affects reliability of 50% ownership rule — KYC data gaps are a known limitation
- Fuzzy match accuracy depends on the matching algorithm implemented — threshold guidance assumes Levenshtein or Jaro-Winkler implementation

---

### 7.2 Version Control & Review Schedule

| Review Trigger | Frequency | Action Required |
|---|---|---|
| FATF list update | As published | Review Tier 1C — add/remove countries, update scores |
| OFAC SDN update | 3–4x per month | Update Tier 1A/1B list, rescreen existing customer base |
| CPI annual publication | Annually (January) | Review Tier 2A/2B — adjust for score movements |
| Alert volume review | Every 6 months | Compare actual false positive rate to target — recalibrate if needed |
| Regulatory change | As issued | Review all rules against new FinCEN/OFAC/FATF guidance |

---

### 7.3 SR 11-7 Model Risk Checklist

| SR 11-7 Requirement | Status | Document |
|---|---|---|
| Model purpose and use case documented | ✅ Complete | Section 1 |
| Assumptions and limitations documented | ✅ Complete | Section 7.1 |
| Threshold selection justified | ✅ Complete | Section 4 |
| Weight derivation explained | ✅ Complete | Section 4 |
| False positive rate targeted and documented | ✅ Complete | Section 4.4 |
| Model outputs explainable to non-technical reviewer | ✅ Complete | Rules-based — fully traceable |
| Ongoing monitoring and recalibration schedule | ✅ Complete | Section 7.2 |
| Independent model validation | 🔄 Pending | Planned — Day 45 |
| Back-testing against historical transactions | 🔄 Pending | Planned — Day 30 |

---

*ScoreSentinel | GEO_RULES.md | Authored by Atul Krishnan, CAMS | Version 1.0 | Day 3 of 60-Day Build | CONFIDENTIAL — INTERNAL USE ONLY*
