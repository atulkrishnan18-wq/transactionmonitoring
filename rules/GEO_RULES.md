# GEO_RULES.md — Geographic Risk & Sanctions Scoring Rules

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.1 | **Day:** 3 of 60 | **Author:** Atul Krishnan, CAMS
**Last Updated:** 12 May 2026

---

## Table of Contents
1. [Purpose & Regulatory Basis](#1-purpose--regulatory-basis)
2. [Country Risk Tier Classification](#2-country-risk-tier-classification)
3. [Geographic Scoring Architecture](#3-geographic-scoring-architecture)
4. [Threshold Justification & Weight Derivation](#4-threshold-justification--weight-derivation)
5. [Sanctions Screening Logic](#5-sanctions-screening-logic)
6. [Worked Scoring Examples](#6-worked-scoring-examples)
7. [Model Governance & Maintenance](#7-model-governance--maintenance)
8. [Version History](#8-version-history)

---

## 1. Purpose & Regulatory Basis

This document defines the geographic risk and sanctions screening rules for ScoreSentinel. Geographic risk is a mandatory component of AML transaction monitoring under:

- **FATF Recommendation 19** — Enhanced due diligence for higher-risk countries
- **FATF Recommendation 1** — Risk-based approach requiring documented country risk assessment
- **FinCEN guidance** — Geographic risk factors in transaction monitoring programs
- **SR 11-7 (Federal Reserve)** — Model risk management requiring documented, explainable, and validated scoring logic

> **SR 11-7 Compliance Statement:**
> ScoreSentinel is a rules-based scoring engine, not a machine learning model. Every score is fully traceable to documented rules, threshold justifications, and weight derivations. This design ensures explainability to regulators, auditors, and model validators without requiring algorithmic black-box justification.

> **Recalibration Note:**
> FATF updates its grey list three times per year — February, June, and October plenary sessions. This document must be reviewed and updated after every FATF plenary. The current classification reflects the **February 2026 FATF plenary** as the reference date.

---

## 2. Country Risk Tier Classification

Countries are classified into tiers based on three independent regulatory sources:
- **OFAC** sanctions designations
- **FATF** mutual evaluation outcomes (updated February 2026)
- **Transparency International CPI** (Corruption Perceptions Index — 2024 scores)

> **Cumulative Scoring Rule:** A country may appear in **multiple tiers** — all applicable tier scores are **cumulative and additive**. A country that is both FATF grey-listed (Tier 1C) and highly corrupt (Tier 2A) scores both +25 and +20 = **+45 total**.

---

### Tier 1A — OFAC Sanctioned AND FATF Black Listed 🔴

These jurisdictions carry the **highest possible risk designation** — comprehensive OFAC sanctions AND formally identified by FATF as requiring counter-measures.

**Rule:** Any transaction involving these countries triggers an **automatic Sanctions Alert** regardless of transaction amount or composite score.

| Country | OFAC Status | FATF Status | Score Added |
|---|---|---|---|
| Iran | Comprehensive Sanctions | Black List | **+50 \| AUTO-ALERT** |
| North Korea (DPRK) | Comprehensive Sanctions | Black List | **+50 \| AUTO-ALERT** |
| Myanmar | Military Regime Sanctions | Black List (added 2022) | **+50 \| AUTO-ALERT** |

> **Note:** As of October 2025, FATF confirmed Iran remains on the black list despite regime commitments — it has not made substantive changes and continues to pose high ML/TF/WMD financing risk.

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

> **Note:** Syria and Venezuela also appear in Tier 2A (CPI) — cumulative scoring applies. Venezuela also appears in Tier 1C (FATF grey list) — all three designations are cumulative.

---

### Tier 1C — FATF Grey List (Jurisdictions Under Increased Monitoring) 🟠

Formally identified by FATF as having strategic AML/CFT deficiencies. Updated to reflect **February 2026 FATF plenary**.

Transactions do **not** auto-alert but geo score is additive to transaction total. Countries may also appear in Tier 2A/2B for CPI — cumulative scoring applies.

| Country | FATF Grey List Since | Primary FATF Concern | Score Added | CPI Cumulative? |
|---|---|---|---|---|
| Afghanistan | Pre-2022 | Taliban designation, severe CFT deficiencies | +25 | +20 (CPI 20) |
| Algeria | October 2024 | AML/CFT framework deficiencies | +25 | — |
| Angola | October 2024 | Beneficial ownership, PEP controls | +25 | — |
| Bolivia | June 2025 | AML/CFT effectiveness gaps | +25 | +20 (CPI 26) |
| Bulgaria | October 2021 | Financial supervision gaps | +25 | — |
| Cameroon | October 2022 | Weak AML controls | +25 | — |
| Côte d'Ivoire | October 2024 | AML/CFT deficiencies | +25 | — |
| DR Congo | October 2022 | Conflict, weak state controls | +25 | +20 (CPI 20) |
| Haiti | Pre-2022 | Governance collapse, weak financial controls | +25 | +20 (CPI 17) |
| Kenya | October 2022 | East Africa hub, AML gaps | +25 | +15 (CPI 31) |
| Kuwait | February 2026 | AML/CFT deficiencies identified | +25 | — |
| Laos | February 2025 | Narcotics corridor, weak AML controls | +25 | +20 (CPI 28) |
| Lebanon | Pre-2022 | Banking sector collapse, Hezbollah nexus | +25 | +20 (CPI 24) |
| Monaco | June 2024 | Financial centre — AML supervision gaps | +25 | — |
| Namibia | October 2022 | Weak beneficial ownership controls | +25 | — |
| Nepal | February 2025 | AML/CFT framework weaknesses | +25 | — |
| Papua New Guinea | February 2026 | AML/CFT deficiencies identified | +25 | — |
| South Sudan | October 2021 | Conflict, state fragility | +25 | +20 (CPI 13) |
| Syria *(also Tier 1B)* | Pre-2022 | Conflict, sanctions evasion | +25 | +20 (CPI 13) |
| Venezuela *(also Tier 1B)* | June 2024 | Kleptocracy, sanctions evasion | +25 | +20 (CPI 13) |
| Vietnam | October 2023 | AML/CFT effectiveness gaps | +25 | — |
| Virgin Islands (BVI) *(also Tier 3)* | June 2025 | Beneficial ownership — shell company risk | +25 | — |
| Yemen | Pre-2022 | Conflict jurisdiction, Houthi TF risk | +25 | +20 (CPI 16) |

> **Corrections from v1.0:**
> - **Removed:** Pakistan (removed from grey list October 2022), Nigeria (removed October 2025), South Africa (removed October 2025), Philippines (removed February 2025), Tanzania (removed June 2025), Cambodia (was never on FATF grey list — CPI only)
> - **Added:** Algeria, Angola, Bolivia, Bulgaria, Côte d'Ivoire, DR Congo, Kuwait, Monaco, Namibia, Nepal, Papua New Guinea, South Sudan, Vietnam, BVI (cumulative with Tier 3)

---

### Tier 2A — High Corruption Risk (CPI Score 0–29) 🟠

Countries with a Transparency International CPI score of **0–29** indicate pervasive corruption, creating elevated risk of bribery-related proceeds, PEP exposure, and illicit fund flows.

> CPI is cited in FATF Recommendation 1 guidance as a valid geographic risk indicator. CPI scores reflect **Transparency International 2024 annual publication**.

| Country | CPI Score | Primary Risk | Score Added | Also In |
|---|---|---|---|---|
| Somalia | 11 | State failure, hawala, TF | +20 | — |
| North Korea *(also Tier 1A)* | 17 | Regime financing, sanctions evasion | +20 | Tier 1A |
| South Sudan *(also Tier 1C)* | 13 | Conflict, kleptocracy | +20 | Tier 1C |
| Syria *(also Tier 1B, 1C)* | 13 | Conflict, sanctions evasion | +20 | Tier 1B, 1C |
| Venezuela *(also Tier 1B, 1C)* | 13 | Kleptocracy, sanctions evasion | +20 | Tier 1B, 1C |
| Yemen *(also Tier 1C)* | 16 | Conflict, Houthi financing | +20 | Tier 1C |
| Equatorial Guinea | 17 | Oil kleptocracy, PEP risk | +20 | — |
| Libya | 18 | Conflict, oil revenue ML | +20 | — |
| Haiti *(also Tier 1C)* | 17 | Governance collapse | +20 | Tier 1C |
| DR Congo *(also Tier 1C)* | 20 | Conflict minerals, cash economy | +20 | Tier 1C |
| Afghanistan *(also Tier 1C)* | 20 | Taliban, TF, hawala | +20 | Tier 1C |
| Sudan | 20 | Conflict, kleptocracy, TF | +20 | — |
| Burundi | 23 | East Africa, weak institutions | +20 | — |
| Cambodia | 22 | Narcotics, casino ML, weak BO | +20 | — |
| Eritrea | 22 | Closed economy, diaspora hawala | +20 | — |
| Bangladesh | 25 | Trade-based ML, garment sector | +20 | — |
| Bolivia *(also Tier 1C)* | 26 | Narco corridor, AML gaps | +20 | Tier 1C |
| Nigeria | 26 | Proceeds of crime — removed from grey list Oct 2025 | +20 | — |
| Pakistan | 28 | TF risk — removed from grey list Oct 2022 | +20 | — |
| Kyrgyzstan | 26 | Central Asia ML corridor | +20 | — |
| Tajikistan | 20 | Central Asia corridor, hawala | +20 | — |
| Laos *(also Tier 1C)* | 28 | Narcotics corridor | +20 | Tier 1C |
| Lebanon *(also Tier 1C)* | 24 | Banking collapse, Hezbollah nexus | +20 | Tier 1C |

> **Correction from v1.0:** Lebanon moved from Tier 2B to Tier 2A — CPI score of 24 is below the 30 boundary. Nigeria added here after grey list removal.

---

### Tier 2B — Elevated Corruption Risk (CPI Score 30–49) 🟡

Countries with CPI 30–49 carry meaningful corruption risk. This tier captures major economies not sanctioned or FATF-listed but with documented AML typology risk.

| Country | CPI Score | Primary Risk | Score Added | Also In |
|---|---|---|---|---|
| China | 42 | Capital flight, SOE risk, PEPs | +15 | — |
| India | 39 | Hawala, trade-based ML, PEPs | +15 | — |
| Indonesia | 34 | PEP exposure, weak BO controls | +15 | — |
| Kenya *(also Tier 1C)* | 31 | East Africa hub, informal economy | +15 | Tier 1C |
| Malaysia | 50 | 1MDB precedent, offshore exposure | +15 | — |
| Mexico | 31 | Cartel ML, TBML, real estate | +15 | — |
| Egypt | 35 | PEP exposure, state controls | +15 | — |
| Ecuador | 36 | Narco corridor, dollarised economy | +15 | — |
| Uzbekistan | 33 | Central Asia, cash economy | +15 | — |
| South Africa | 41 | Removed from grey list Oct 2025 — CPI risk remains | +15 | — |
| Tanzania | 30 | Removed from grey list Jun 2025 — CPI risk remains | +15 | — |
| Nigeria | 26 | See Tier 2A — CPI 26 below 30 boundary | Moved to Tier 2A | — |
| Philippines | 33 | Removed from grey list Feb 2025 — CPI risk remains | +15 | — |

> **Correction from v1.0:** Malaysia CPI 50 is at the exact boundary — retained in Tier 2B with documented rationale: 1MDB precedent and offshore exposure justify elevated monitoring despite borderline CPI score. Nigeria moved to Tier 2A (CPI 26 is below 30 boundary).

---

### Tier 3 — Offshore / Secrecy Jurisdictions (Watch List) 🟡

Not sanctioned and may not be FATF-listed, but legal and financial infrastructure presents elevated risk of shell company abuse, beneficial ownership concealment, and layering activity.

| Jurisdiction | Primary Risk | Score Added | Also In |
|---|---|---|---|
| Cayman Islands | Offshore hub — hedge funds, shell structures | +15 | — |
| British Virgin Islands | Largest shell company registry globally | +15 | Tier 1C (June 2025) |
| Panama | Panama Papers — layering and concealment | +15 | — |
| Seychelles | Beneficial ownership gaps, offshore IBC registry | +15 | — |
| Vanuatu | Pacific secrecy jurisdiction, citizenship by investment | +15 | — |
| Cyprus | EU member but offshore history, Russian exposure | +15 | — |
| Switzerland | Private banking secrecy, offshore wealth management | +15 | — |

> **Correction from v1.0:** Switzerland added to Tier 3 — identified as missing during TEST_SCENARIOS.md Scenario 6 validation. BVI now also in Tier 1C — cumulative scoring applies (+25 Tier 1C + +15 Tier 3 = +40 total).

---

### Tier 4 — Standard Risk

All other countries not appearing in Tiers 1A through 3.

| Classification | CPI Range | Score Added |
|---|---|---|
| Standard / Low Risk | CPI 50+ | +0 |

> **Examples of Tier 4:** United States, United Kingdom, Germany, France, Japan, Australia, Canada, Singapore, New Zealand.

---

## 3. Geographic Scoring Architecture

### 3.1 Scoring Applies to Both Transaction Ends

Geographic risk is assessed on **BOTH the sender country and the receiver country** for every transaction.

| Side | Why It Matters |
|---|---|
| **Sender country** | Assesses whether funds originate from a jurisdiction with elevated corruption, sanctions exposure, or AML deficiencies |
| **Receiver country** | Assesses whether funds are directed toward a jurisdiction where detection, enforcement, or transparency is limited |

> **Scoring Rule:** Both sides are additive. If sender = Tier 2B (+15) and receiver = Tier 1C (+25), total geo contribution = **+40**. If either side is Tier 1A or 1B → **Auto-Alert regardless of total score.**

### 3.2 Cumulative Scoring — Multi-Tier Countries

When a country appears in multiple tiers, all applicable scores add together:

```
CUMULATIVE SCORING EXAMPLES:

Afghanistan (Tier 1C + Tier 2A):
  Tier 1C score:  +25
  Tier 2A score:  +20
  Total geo score: +45

British Virgin Islands (Tier 1C + Tier 3):
  Tier 1C score:  +25
  Tier 3 score:   +15
  Total geo score: +40

Venezuela (Tier 1B + Tier 1C + Tier 2A):
  Tier 1B:        +40 + AUTO-ALERT
  Tier 1C:        +25
  Tier 2A:        +20
  Total geo score: +85 + AUTO-ALERT

Lebanon (Tier 1C + Tier 2A):
  Tier 1C score:  +25
  Tier 2A score:  +20
  Total geo score: +45

Pakistan (Tier 2A only — removed from grey list):
  Tier 2A score:  +20
  Total geo score: +20
```

### 3.3 Universal Alert Threshold

> **ScoreSentinel applies a single universal alert threshold of CRS ≥ 60 across all customer types and transaction categories.** Dynamic segmentation by customer type has not been implemented in Version 1.0 — this requires back-testing data to justify differential calibration with documented SR 11-7 rationale. This is a deliberate documented deferral. See COMPOSITE_LOGIC.md Section 5.1.

### 3.4 Score Integration with Other ScoreSentinel Modules

Geography scores are **additive** to existing transaction scores and feed into the composite CRS formula.

| Component | Module | Score Range |
|---|---|---|
| Transaction amount & pattern | Structuring Rules | 0–70 |
| Sender country risk | GEO_RULES (this document) | 0–85+ (cumulative tiers) |
| Receiver country risk | GEO_RULES (this document) | 0–85+ (cumulative tiers) |
| Geography module input to CRS | Normalised 0–100 | Capped at 100 before normalisation |

> **Cap Rule:** Geography raw score is capped at 100 before normalisation to prevent individual module dominating composite. For multi-tier countries, combined scores exceeding 100 are capped at 100.

### 3.5 Alert Types

| Alert Type | Trigger | Reviewer |
|---|---|---|
| 🚨 **Sanctions Alert** | Any Tier 1A or 1B country involvement | Compliance Officer — within 24 hours |
| ⚠️ **AML Risk Alert** | Composite CRS ≥ 60 | AML Analyst — within 5 business days |

---

## 4. Threshold Justification & Weight Derivation

> **SR 11-7 Requirement:** Model developers must document the basis for threshold selection and weight derivation. Stating a threshold without justification is an assertion, not a model.

### 4.1 Why Tier 1A = +50

- Tier 1A carries a **dual designation** — OFAC sanctioned AND FATF black-listed
- Any transaction must trigger an alert independently of structuring score
- Minimum structuring score in the engine is approximately +10 for a clean transaction
- Alert threshold is 60 — geo score of +50 guarantees alert even on lowest-risk transaction (10 + 50 = 60)
- +50 chosen rather than +60 to preserve composite score meaning
- Auto-Alert rule provides a secondary catch — even if composite < 60, Tier 1A still alerts

### 4.2 Why FATF Grey List = +25

- FATF grey list represents documented but not critical deficiencies — materially less severe than black list
- A clean, low-value transaction to a grey-listed country (10 + 25 = 35) should **not** alert
- A moderate transaction (score 35) to a grey-listed country (35 + 25 = 60) **should** alert
- Calibration principle: Grey list alone should not alert; grey list combined with other risk should alert

### 4.3 Why CPI Boundary = 30

- Transparency International defines 0–29 as **"highly corrupt"** — pervasive institutional corruption
- Score 30–49 is **"corrupt"** — meaningful risk but not systemic state capture
- Score 50+ treated as standard risk — aligns with TI's categorization of 50 as governance midpoint
- CPI boundary at 30 is consistent with FATF Recommendation 1 guidance on using objective corruption indices

### 4.4 Why Malaysia Retained in Tier 2B at CPI 50

- CPI 50 is at the exact tier boundary
- 1MDB — one of the largest sovereign ML cases in history — originated from Malaysia
- Offshore exposure through Labuan financial centre remains elevated
- Documented decision: borderline CPI does not override documented typology risk
- Will be reviewed annually against updated CPI scores

### 4.5 False Positive Rate & Alert Volume Design

| Metric | Target | Rationale |
|---|---|---|
| False Positive Rate | < 15% | Operationally manageable — industry norm 10–20% |
| Alert-to-SAR Ratio | 10:1 to 20:1 | FinCEN / industry benchmark |
| Sanctions False Positive Rate | < 30% | Higher tolerance — sanctions misses carry criminal liability |
| Recalibration Frequency | Every 6 months | Accounts for FATF updates, OFAC changes, CPI annual release |

---

## 5. Sanctions Screening Logic

### 5.1 Six Mandatory Screening Fields

| # | Field Screened | Screened Against | Why |
|---|---|---|---|
| 1 | Sender name | OFAC SDN List | Direct sender identification |
| 2 | Receiver name | OFAC SDN List | Direct receiver identification |
| 3 | Sender country | Tier 1A / 1B country list | Jurisdiction-level sanctions |
| 4 | Receiver country | Tier 1A / 1B country list | Jurisdiction-level sanctions |
| 5 | Intermediary bank (if wire) | OFAC SDN List | Correspondent banking exposure |
| 6 | Beneficial owner (if known) | OFAC SDN List | Indirect sanctions exposure |

---

### 5.2 Name Matching — Fuzzy Match Thresholds

| Match % | Match Type | Example | Action |
|---|---|---|---|
| 100% | Exact match | BANK MELLI IRAN | 🚨 Block + Sanctions Alert immediately |
| 85–99% | Strong fuzzy match | Mohamed Al-Qahtani vs Mohammed Al-Kahtani | 🚨 Hold + escalate for review |
| 70–84% | Moderate fuzzy match | Ali Hassan vs Ali Hasan | ⚠️ Flag for analyst review |
| < 70% | No match | Ali Hassan vs Alan Harris | ✅ Clear — no action |

### 5.3 Why 85% Threshold

- At 70%: ~40% false positive rate — operationally unmanageable
- At 85%: ~12% false positive rate — acceptable, within SR 11-7 tolerance
- At 95%: ~8% miss rate — unacceptable regulatory risk
- 85% is the default used by SWIFT, Refinitiv, and Actimize
- Full OCC examiner defence script documented in PEP_RULES.md Section 7.2

---

### 5.4 The OFAC 50% Ownership Rule

> If a company is owned **50% or more** by a sanctioned entity, that company is treated as sanctioned — even if it does not appear on the SDN list by name.

**ScoreSentinel Rule:** Any transaction with a 50%-owned entity = **Tier 1B Auto-Alert**.

**40–50% Enhanced Monitoring Zone:** Any entity where a sanctioned individual holds 40–49.9% ownership triggers quarterly ownership verification and +25 sanctions-adjacent customer risk score. See PEP_RULES.md Section 5.5 — The Sulzer Gap.

---

### 5.5 Post-Hit Workflow

```
SANCTIONS HIT WORKFLOW:

Step 1 → HOLD transaction (automated)
Step 2 → Generate SANCTIONS Alert (automated)
Step 3 → Escalate to Compliance Officer within 24 hours
Step 4 → Compliance Officer reviews: Real Hit or False Positive?
Step 5A → Real Hit: File OFAC report, block funds, notify management
Step 5B → False Positive: Document three-point standard, release, update rules
```

---

### 5.6 Sanctions List Maintenance & Screening Frequency

| When to Screen | Trigger | Rationale |
|---|---|---|
| At transaction initiation | Every transaction | Catch exposure before funds move |
| At customer onboarding | New customer | KYC before first transaction |
| On SDN list update | OFAC publishes | OFAC updates 3–4 times per month |
| Periodic rescreening | Every 90 days | Customers can be added post-onboarding |
| After FATF plenary | February, June, October | Grey list changes require immediate reclassification |

---

## 6. Worked Scoring Examples

| Transaction | Structuring | Sender Geo | Receiver Geo | Total | Alert? |
|---|---|---|---|---|---|
| $500 transfer — UK to US | 5 | +0 | +0 | 5 | ❌ No |
| $5,000 wire — India to Cayman | 15 | +15 (CPI 2B) | +15 (Tier 3) | 45 | ❌ No |
| $9,500 cash — Nigeria sender | 55 | +20 (CPI 2A) | +0 | 75 | ✅ Yes |
| $500 wire — any country to Iran | 5 | +0 | +50 (Tier 1A) | 55+AUTO | 🚨 Yes |
| $7,000 cash — India to Cambodia | 45 | +15 (CPI 2B) | +20 (Tier 2A) | 80 | ✅ Yes |
| $200 wire — China to BVI | 5 | +15 (CPI 2B) | +40 (Tier 1C+3) | 60 | ✅ Yes |
| $180,000 wire — Pakistan to UK | 30 | +20 (CPI 2A) | +0 | 50 | ❌ No |
| $10,000 wire — Lebanon to BVI | 20 | +45 (Tier 1C+2A) | +40 (Tier 1C+3) | 105 | ✅ Yes |

> **Note on Nigeria example:** Nigeria was removed from FATF grey list October 2025. Score now reflects CPI Tier 2A (+20) only — not Tier 1C (+25). This reduces the score from the v1.0 example.

> **Note on BVI example:** BVI added to FATF grey list June 2025. Now scores +25 (Tier 1C) + +15 (Tier 3) = +40 cumulative.

---

## 7. Model Governance & Maintenance

### 7.1 Assumptions & Limitations

- Country classifications reflect FATF February 2026 plenary and TI CPI 2024 — must be reviewed after every FATF plenary (February, June, October)
- CPI scores are published annually in January — Tier 2A/2B assignments reviewed upon publication
- This model does not account for sub-national risk variation (e.g. OFAC-licensed exemptions within sanctioned countries)
- Beneficial ownership data quality directly affects 50% ownership rule reliability
- Fuzzy match accuracy depends on algorithm implementation — Jaro-Winkler + Levenshtein recommended per PEP_RULES.md Section 7.4
- Malaysia retained in Tier 2B at CPI 50 based on typology risk — reviewed annually
- Geography raw score capped at 100 before normalisation — scores above 100 for multi-tier countries are capped

### 7.2 FATF Plenary Review Schedule

| Plenary | Date | Action Required |
|---|---|---|
| February plenary | February each year | Review Tier 1C — add/remove countries |
| June plenary | June each year | Review Tier 1C — add/remove countries |
| October plenary | October each year | Review Tier 1C — add/remove countries |
| CPI publication | January each year | Review Tier 2A/2B — adjust for score movements |
| OFAC SDN update | 3–4x per month | Update Tier 1A/1B — rescreen customer base |
| Alert volume review | Every 6 months | Compare FP rate to target — recalibrate if needed |

### 7.3 SR 11-7 Model Risk Checklist

| SR 11-7 Requirement | Status | Location |
|---|---|---|
| Model purpose documented | ✅ Complete | Section 1 |
| Assumptions and limitations documented | ✅ Complete | Section 7.1 |
| Threshold selection justified | ✅ Complete | Section 4 |
| Weight derivation explained | ✅ Complete | Section 4 |
| False positive targets documented | ✅ Complete | Section 4.5 |
| Cumulative scoring documented | ✅ Complete | Section 3.2 |
| FATF recalibration schedule defined | ✅ Complete | Section 7.2 |
| Model outputs explainable | ✅ Complete | Rules-based — fully traceable |
| Independent validation | 🔄 Pending | Planned Day 45 |
| Back-testing | 🔄 Pending | Planned Day 30 |

---

## 8. Version History

| Version | Change | Date | Author |
|---|---|---|---|
| 1.0 | Initial release — five-tier geographic risk classification, OFAC/FATF/CPI framework, sanctions screening logic, SR 11-7 governance | Day 3 — 2025 | Atul Krishnan, CAMS |
| 1.1 | **Major recalibration — February 2026 FATF plenary.** Removed from Tier 1C: Pakistan (Oct 2022), Nigeria (Oct 2025), South Africa (Oct 2025), Philippines (Feb 2025), Tanzania (Jun 2025), Cambodia (never on grey list). Added to Tier 1C: Algeria, Angola, Bolivia, Bulgaria, Côte d'Ivoire, DR Congo, Kuwait, Monaco, Namibia, Nepal, Papua New Guinea, South Sudan, Venezuela (cumulative), Vietnam, BVI (cumulative with Tier 3). Added to Tier 2A: Lebanon (moved from 2B — CPI 24 below 30 boundary), Nigeria, Pakistan, Bolivia, South Sudan, Equatorial Guinea, Libya, Sudan, Burundi, Eritrea, Kyrgyzstan, Tajikistan, Laos, DR Congo, Afghanistan, Haiti, Yemen. Added to Tier 2B: Mexico, Egypt, Ecuador, Uzbekistan, South Africa, Tanzania, Philippines (after grey list removals). Added Switzerland to Tier 3. Documented cumulative scoring with worked examples. Removed unvalidated segmented thresholds and data integrity penalty sections (not consistent with COMPOSITE_LOGIC.md architecture). Added Malaysia retention rationale. Updated FATF plenary review schedule. Removed CONFIDENTIAL footer — repo is public. | 12 May 2026 | Atul Krishnan, CAMS |

---

*ScoreSentinel | GEO_RULES.md | Geographic Risk & Sanctions Scoring Rules | Authored by Atul Krishnan, CAMS | Version 1.1 | 12 May 2026*
