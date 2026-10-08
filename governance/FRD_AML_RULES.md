# ScoreSentinel AML Engine — Functional Requirements Document

---

## Cover Page

| Field | Value |
|---|---|
| **Document Title** | ScoreSentinel AML Engine Functional Requirements Document |
| **Document ID** | FRD-AML-001 |
| **Version** | 1.2 |
| **Author** | Atul Krishnan, CAMS |
| **Status** | APPROVED |
| **Date** | September 2026 |
| **Classification** | Internal — Governance |
| **Parent Document** | `rules/AML_RULES.md` — Master Detection Framework v1.3 |

---

## Version History

| Version | Change Summary | Date | Author | Status |
|---|---|---|---|---|
| 1.0 | Initial FRD — four-module CRS architecture; universal alert threshold of 60; SR 11-7 compliance framework | April 2026 | Atul Krishnan, CAMS | Superseded |
| 1.1 | Added MuleCatcher™ overlay; UAPA/OFAC/UN sanctions screening requirements; configurable rules engine (SCN-001 to SCN-008) | August 2026 | Atul Krishnan, CAMS | Superseded |
| 1.2 | Added Velocity 7-day module; rebalanced module weights (Customer 25%, Structuring 20%, Geography 25%, TxType 15%, Velocity 15%); added FRD numbering schema (FR-xxx); reformatted as formal FRD with acceptance criteria and priority classifications | September 2026 | Atul Krishnan, CAMS | **APPROVED** |

---

## Table of Contents

1. [Document Purpose and Scope](#1-document-purpose-and-scope)
2. [Regulatory References](#2-regulatory-references)
3. [System Architecture Overview](#3-system-architecture-overview)
4. [Functional Requirements — Composite Risk Score Engine](#4-functional-requirements--composite-risk-score-engine)
5. [Functional Requirements — Customer Risk Module](#5-functional-requirements--customer-risk-module)
6. [Functional Requirements — Structuring Module](#6-functional-requirements--structuring-module)
7. [Functional Requirements — Geography Module](#7-functional-requirements--geography-module)
8. [Functional Requirements — Transaction Type Module](#8-functional-requirements--transaction-type-module)
9. [Functional Requirements — Velocity Module](#9-functional-requirements--velocity-module)
10. [Functional Requirements — Sanctions Screening](#10-functional-requirements--sanctions-screening)
11. [Functional Requirements — Configurable Rules Engine](#11-functional-requirements--configurable-rules-engine)
12. [Functional Requirements — Auto-Alert Triggers](#12-functional-requirements--auto-alert-triggers)
13. [Functional Requirements — Audit Trail and Logging](#13-functional-requirements--audit-trail-and-logging)
14. [Functional Requirements — API and Integration](#14-functional-requirements--api-and-integration)
15. [Non-Functional Requirements](#15-non-functional-requirements)
16. [Sign-Off Section](#16-sign-off-section)

---

## 1. Document Purpose and Scope

### 1.1 Purpose

This Functional Requirements Document (FRD) defines the complete set of functional and non-functional requirements for the ScoreSentinel AML Engine. It translates the detection logic documented in `rules/AML_RULES.md` and associated rule documents into numbered, testable requirements against which the engine can be validated, audited, and governed.

Every requirement in this document:
- Is assigned a unique requirement ID (FR-xxx)
- States a specific, testable condition
- Is linked to a regulatory basis
- Carries a priority classification (MUST / SHOULD / MAY)
- Includes acceptance criteria

### 1.2 Scope

This FRD covers all components of the ScoreSentinel CRS Engine v1.2:

| In Scope | Out of Scope |
|---|---|
| Composite Risk Score (CRS) calculation | Customer identity verification (KYC onboarding) |
| Five scoring modules (Customer, Structuring, Geography, Transaction Type, Velocity) | Suspicious Transaction Report (STR) filing |
| Sanctions screening (6 lists) | Commercial PEP database integration |
| Configurable rules engine (SCN-001 to SCN-008) | Trade-based money laundering (TBML) detection |
| Auto-alert triggers | Machine learning model training |
| Audit trail and logging | Correspondent banking risk |
| REST API scoring endpoint | Core banking system integration specifics |

### 1.3 Intended Audience

- AML Compliance Officers deploying ScoreSentinel at regulated entities
- Technology teams integrating the ScoreSentinel API
- Internal auditors and model risk reviewers
- Regulatory examiners (RBI, FIU-IND)

### 1.4 Requirement Priority Definitions

| Priority | Definition |
|---|---|
| **MUST** | Mandatory requirement. Non-compliance with this requirement means the system fails regulatory standards or core AML function. No exceptions. |
| **SHOULD** | Strongly recommended. Non-compliance is permissible only with documented justification and a remediation plan. |
| **MAY** | Optional enhancement. Provides additional functionality or accuracy but is not required for baseline compliance. |

---

## 2. Regulatory References

| Reference ID | Regulation / Standard | Issuing Authority | Applicability |
|---|---|---|---|
| REG-001 | Prevention of Money Laundering Act 2002 (PMLA) — Section 12 | Government of India | Transaction record-keeping and STR obligations |
| REG-002 | Prevention of Money Laundering (Maintenance of Records) Rules 2005 — Rule 3 | Government of India | Suspicious transaction reporting to FIU-IND |
| REG-003 | RBI Master Direction on Know Your Customer (KYC) 2023 | Reserve Bank of India | Customer due diligence, PEP, EDD requirements |
| REG-004 | RBI KYC Directions 2025 — Chapter IX | Reserve Bank of India | UAPA and UNSC sanctions compliance |
| REG-005 | Unlawful Activities Prevention Act 1967 — Section 51A | Government of India | Designated terrorist and banned organisation screening |
| REG-006 | UAPA Order dated February 2, 2021 | Ministry of Home Affairs, India | Mandatory actions on UAPA/UNSC match |
| REG-007 | SR 11-7 — Guidance on Model Risk Management | Federal Reserve / OCC (adopted as standard) | Model documentation, validation, and governance |
| REG-008 | FATF Recommendation 1 | Financial Action Task Force | Risk-based approach |
| REG-009 | FATF Recommendation 6 | Financial Action Task Force | Targeted financial sanctions — no delay |
| REG-010 | FATF Recommendation 10 | Financial Action Task Force | Customer due diligence |
| REG-011 | FATF Recommendation 29 | Financial Action Task Force | Financial intelligence units |
| REG-012 | US Treasury OFAC SDN List | US Treasury / OFAC | OFAC sanctions screening |
| REG-013 | UN Security Council Consolidated Sanctions List | United Nations | UN sanctions screening |
| REG-014 | FATF Mutual Evaluation — India 2024 | Financial Action Task Force | Jurisdiction-specific findings |

---

## 3. System Architecture Overview

```
┌──────────────────────────────────────────────────────┐
│              API LAYER (POST /api/score)              │
│  Input: customer, transaction, history               │
└─────────────────────────┬────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────┐
│        STEP 1: SANCTIONS SCREENING (Priority)        │
│  6-list waterfall: UAPA Sch4 → Sch1 → UNSC 1267      │
│  → UNSC 1988 → OFAC SDN → UN Consolidated           │
│  Match → CRS = None; auto_alert = True               │
└─────────────────────────┬────────────────────────────┘
                          │ No match: continue
                          ▼
┌──────────────────────────────────────────────────────┐
│         STEP 2: FIVE-MODULE CRS CALCULATION          │
│  Module 1: Customer Risk (CCRS)          Weight: 25% │
│  Module 2: Structuring Pattern                   20% │
│  Module 3: Geography Risk                        25% │
│  Module 4: Transaction Type                      15% │
│  Module 5: Velocity 7-day                        15% │
└─────────────────────────┬────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────┐
│       STEP 3: CONFIGURABLE RULES ENGINE              │
│  SCN-001 to SCN-008 — evaluate enabled scenarios     │
│  Contribution added to CRS (capped at 100)           │
└─────────────────────────┬────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────┐
│       STEP 4: ALERT DETERMINATION                    │
│  CRS ≥ 60 → AML Risk Alert                           │
│  Auto-alert trigger → Sanctions / PEP Alert          │
│  Structuring normalised ≥ 75% → Structuring Alert    │
└─────────────────────────┬────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────┐
│       STEP 5: PERSIST AND RESPOND                    │
│  Write to transactions table (INSERT-ONLY)           │
│  Write to alerts table if alert triggered            │
│  Return JSON scoring response                        │
└──────────────────────────────────────────────────────┘
```

---

## 4. Functional Requirements — Composite Risk Score Engine

### FR-001 — CRS Scale

| Field | Value |
|---|---|
| **Requirement ID** | FR-001 |
| **Description** | The system SHALL calculate a Composite Risk Score (CRS) for every transaction on a normalised scale of 0 to 100. |
| **Regulatory Basis** | REG-007 (SR 11-7) — Model output must be on a defined, documented scale |
| **Acceptance Criteria** | Every API scoring response contains a `crs` value in the range 0.00–100.00, or `null` in the event of a sanctions match. No CRS value outside this range is permitted. |
| **Priority** | **MUST** |

---

### FR-002 — Module Normalisation

| Field | Value |
|---|---|
| **Requirement ID** | FR-002 |
| **Description** | The system SHALL normalise each module's raw score to a 0–100 scale before applying weights, using the formula: `Normalised = (Raw Score / Module Maximum) × 100`. |
| **Regulatory Basis** | REG-007 (SR 11-7) — Weights must reflect intended contribution; raw scale differences must not distort the composite |
| **Acceptance Criteria** | (1) No normalised module score exceeds 100. (2) A raw score at the documented module maximum produces a normalised score of exactly 100. (3) A raw score of 0 produces a normalised score of 0. |
| **Priority** | **MUST** |

---

### FR-003 — Module Weights

| Field | Value |
|---|---|
| **Requirement ID** | FR-003 |
| **Description** | The system SHALL apply the following documented weights when computing the CRS: Customer Risk 25%, Structuring 20%, Geography 25%, Transaction Type 15%, Velocity 15%. The sum of all weights SHALL equal 100%. |
| **Regulatory Basis** | REG-007 (SR 11-7) — All weights must be documented with explicit justification |
| **Acceptance Criteria** | (1) CRS formula matches: `(Customer × 0.25) + (Structuring × 0.20) + (Geography × 0.25) + (TxType × 0.15) + (Velocity × 0.15) + rules_engine_contribution`, capped at 100. (2) Adjusting a single module input changes the CRS proportionally to its weight. |
| **Priority** | **MUST** |

---

### FR-004 — Module Maximums

| Field | Value |
|---|---|
| **Requirement ID** | FR-004 |
| **Description** | The system SHALL enforce the following module maximums for normalisation: Customer Risk = 175, Structuring = 70, Geography = 100, Transaction Type = 55, Velocity = 100. Any raw score exceeding its module maximum SHALL be capped at the maximum before normalisation. |
| **Regulatory Basis** | REG-007 (SR 11-7) — Documented limits required |
| **Acceptance Criteria** | A raw customer risk score of 200 (exceeding the 175 maximum) normalises to 100, not 114. API response module scores never exceed 100. |
| **Priority** | **MUST** |

---

### FR-005 — Alert Threshold

| Field | Value |
|---|---|
| **Requirement ID** | FR-005 |
| **Description** | The system SHALL generate an AML Risk Alert whenever the CRS meets or exceeds 60. The alert threshold of 60 SHALL be universal across all customer types and transaction categories. |
| **Regulatory Basis** | REG-001 (PMLA Section 12), REG-008 (FATF Rec. 1 — risk-based approach) |
| **Acceptance Criteria** | (1) CRS of 59.99 does not generate an alert. (2) CRS of 60.00 generates an alert. (3) The alert threshold cannot be overridden per customer type without a documented SR 11-7 model change approval. |
| **Priority** | **MUST** |

---

### FR-006 — CRS Null on Sanctions Match

| Field | Value |
|---|---|
| **Requirement ID** | FR-006 |
| **Description** | When a sanctions match is detected, the system SHALL set `crs` to `null` in the API response and SHALL NOT compute a CRS. The sanctions auto-alert SHALL be generated regardless of what the CRS would have been. |
| **Regulatory Basis** | REG-005 (Section 51A UAPA), REG-009 (FATF Rec. 6 — no delay on targeted sanctions) |
| **Acceptance Criteria** | (1) An API response for a UAPA-matched customer contains `"crs": null`. (2) The `alert` field is `true` and `mandatory_actions` is populated. (3) No module scores contribute to any CRS value when a sanctions match is present. |
| **Priority** | **MUST** |

---

### FR-007 — CRS Cap at 100

| Field | Value |
|---|---|
| **Requirement ID** | FR-007 |
| **Description** | The system SHALL cap the final CRS at 100 after all module contributions and the rules engine contribution are summed. No CRS value above 100 SHALL be returned. |
| **Regulatory Basis** | REG-007 (SR 11-7) — Output must be on the defined 0–100 scale |
| **Acceptance Criteria** | A transaction where the weighted module sum plus rules engine contribution exceeds 100 returns a CRS of exactly 100.00. |
| **Priority** | **MUST** |

---

## 5. Functional Requirements — Customer Risk Module

### FR-008 — Customer Type Risk Taxonomy

| Field | Value |
|---|---|
| **Requirement ID** | FR-008 |
| **Description** | The system SHALL assign a base Customer Composite Risk Score (CCRS) based on a documented customer type taxonomy. High-risk entity types (shell companies, cryptocurrency businesses, DNFBPs) SHALL receive materially higher base scores than low-risk types (verified salaried individuals, regulated financial institutions). |
| **Regulatory Basis** | REG-003 (RBI KYC 2023 — CDD), REG-010 (FATF Rec. 10 — CDD) |
| **Acceptance Criteria** | A customer of type `Shell Company` receives a higher CCRS than a customer of type `Verified Salaried Individual` on identical transactions. The taxonomy is documented in `CUSTOMER_RULES.md`. |
| **Priority** | **MUST** |

---

### FR-009 — PEP Tier Scoring

| Field | Value |
|---|---|
| **Requirement ID** | FR-009 |
| **Description** | The system SHALL apply elevated CCRS scores for customers identified as Politically Exposed Persons (PEPs). PEP Tier 1 (Heads of State, Cabinet Ministers) SHALL trigger an auto-alert independent of CRS. PEP Tier 2 and Tier 3 SHALL receive elevated but not auto-alerting scores. |
| **Regulatory Basis** | REG-003 (RBI KYC 2023 Chapter VII — PEP EDD), REG-010 (FATF Rec. 10 and 12) |
| **Acceptance Criteria** | (1) A customer with `pep_tier = "Tier 1"` generates an auto-alert on every transaction. (2) PEP Tier 2 and Tier 3 customers receive a CCRS increment documented in `CUSTOMER_RULES.md`. (3) A non-PEP customer does not receive any PEP score increment. |
| **Priority** | **MUST** |

---

### FR-010 — Beneficial Ownership Transparency

| Field | Value |
|---|---|
| **Requirement ID** | FR-010 |
| **Description** | The system SHALL apply a CCRS penalty for customers where beneficial ownership is unknown, unverified, or concealed through complex structures. Missing beneficial owner information SHALL be treated as a risk indicator, not a neutral data state. |
| **Regulatory Basis** | REG-003 (RBI KYC 2023 — beneficial ownership CDD), REG-010 (FATF Rec. 10) |
| **Acceptance Criteria** | A customer record with `beneficial_owner = null` or `bo_ownership_pct = null` receives a higher CCRS than an identical customer with complete beneficial ownership data. |
| **Priority** | **MUST** |

---

### FR-011 — Customer Type Normalised Score Bound

| Field | Value |
|---|---|
| **Requirement ID** | FR-011 |
| **Description** | The Customer Risk module raw score SHALL NOT exceed the documented maximum of 175. The normalised customer score SHALL be calculated as `(CCRS / 175) × 100`. |
| **Regulatory Basis** | REG-007 (SR 11-7) — Module maximums must be documented and enforced |
| **Acceptance Criteria** | No API response contains a customer module raw score above 175. A CCRS of 175 normalises to exactly 100. |
| **Priority** | **MUST** |

---

## 6. Functional Requirements — Structuring Module

### FR-012 — Near-Threshold Detection

| Field | Value |
|---|---|
| **Requirement ID** | FR-012 |
| **Description** | The system SHALL detect and score transactions that fall between 75% and 99% of the defined reporting threshold (default: ₹10,000 or equivalent). This range indicates potential deliberate avoidance of reporting obligations. |
| **Regulatory Basis** | REG-001 (PMLA Section 12(1A) — CTR obligations), REG-011 (FATF Rec. 29) |
| **Acceptance Criteria** | A transaction of ₹9,500 (95% of ₹10,000) receives a structuring score contribution. A transaction of ₹5,000 (50% of threshold) does not receive a structuring score contribution from this rule. |
| **Priority** | **MUST** |

---

### FR-013 — Smurfing Pattern Detection

| Field | Value |
|---|---|
| **Requirement ID** | FR-013 |
| **Description** | The system SHALL detect smurfing patterns — multiple sub-threshold transactions from the same customer within a short time window — and assign elevated structuring scores based on frequency and pattern. |
| **Regulatory Basis** | REG-001 (PMLA Section 12), REG-011 (FATF Rec. 29) |
| **Acceptance Criteria** | A customer history containing three or more near-threshold transactions within 7 days receives a higher structuring score than a customer with a single near-threshold transaction. |
| **Priority** | **MUST** |

---

### FR-014 — Structuring Independent Alert Trigger

| Field | Value |
|---|---|
| **Requirement ID** | FR-014 |
| **Description** | When the structuring normalised score meets or exceeds 75%, the system SHALL generate an independent Structuring Alert regardless of the overall CRS. A low CRS SHALL NOT suppress this alert. |
| **Regulatory Basis** | REG-001 (PMLA — deliberate evasion), REG-007 (SR 11-7 — auto-alerts must bypass composite) |
| **Acceptance Criteria** | A transaction with structuring normalised score of 75% and overall CRS of 35 (below the 60 alert threshold) still generates an alert. The `alert_generated` field is `true`. |
| **Priority** | **MUST** |

---

### FR-015 — Structuring Module Maximum

| Field | Value |
|---|---|
| **Requirement ID** | FR-015 |
| **Description** | The Structuring module raw score SHALL NOT exceed the documented maximum of 70. The normalised structuring score SHALL be calculated as `(structuring_raw / 70) × 100`. |
| **Regulatory Basis** | REG-007 (SR 11-7) |
| **Acceptance Criteria** | No API response contains a structuring module raw score above 70. |
| **Priority** | **MUST** |

---

## 7. Functional Requirements — Geography Module

### FR-016 — Sender and Receiver Country Scoring

| Field | Value |
|---|---|
| **Requirement ID** | FR-016 |
| **Description** | The system SHALL score both the sender country and receiver country independently for geographic risk. Both sides of a transaction contribute to the geography module score. |
| **Regulatory Basis** | REG-009 (FATF Rec. 6 — TF risks from both ends of transaction), REG-003 (RBI KYC 2023) |
| **Acceptance Criteria** | A transaction with a high-risk sender country and low-risk receiver country receives a geography score greater than a transaction with two low-risk countries. A transaction with two high-risk countries receives the highest geography score. |
| **Priority** | **MUST** |

---

### FR-017 — FATF Grey List and Black List Countries

| Field | Value |
|---|---|
| **Requirement ID** | FR-017 |
| **Description** | The system SHALL apply elevated geography scores to countries on the FATF Jurisdictions Under Increased Monitoring (grey list) and High-Risk Jurisdictions Subject to a Call for Action (black list). Black list countries SHALL receive a higher score than grey list countries. |
| **Regulatory Basis** | REG-009 (FATF Rec. 19 — higher-risk countries), REG-003 (RBI KYC 2023) |
| **Acceptance Criteria** | A transaction involving a FATF black list country receives a higher geography score than a transaction involving a FATF grey list country. A transaction involving neither receives the baseline score. |
| **Priority** | **MUST** |

---

### FR-018 — Sanctioned Country Auto-Alert (Tier 1A/1B)

| Field | Value |
|---|---|
| **Requirement ID** | FR-018 |
| **Description** | The system SHALL generate an immediate auto-alert when either the sender or receiver country is classified as Tier 1A (OFAC comprehensively sanctioned) or Tier 1B (UNSC-sanctioned). This alert SHALL bypass the CRS entirely. |
| **Regulatory Basis** | REG-009 (FATF Rec. 6), REG-005 (Section 51A UAPA), REG-012 (OFAC) |
| **Acceptance Criteria** | A transaction with sender_country = "IR" (Iran — Tier 1A) generates an auto-alert. The `crs` field is `null`. The alert is generated even if all other module scores are 0. |
| **Priority** | **MUST** |

---

### FR-019 — Geography Module Maximum

| Field | Value |
|---|---|
| **Requirement ID** | FR-019 |
| **Description** | The Geography module raw score SHALL NOT exceed the documented maximum of 100. The combined sender + receiver score SHALL be capped at 100. |
| **Regulatory Basis** | REG-007 (SR 11-7) |
| **Acceptance Criteria** | No API response contains a geography module raw score above 100. |
| **Priority** | **MUST** |

---

## 8. Functional Requirements — Transaction Type Module

### FR-020 — Transaction Type Risk Taxonomy

| Field | Value |
|---|---|
| **Requirement ID** | FR-020 |
| **Description** | The system SHALL assign risk scores to transactions based on their payment mechanism. The taxonomy SHALL include at minimum: Cash Deposit, Wire Transfer (Domestic), Wire Transfer (International), Cryptocurrency, Trade Finance, Correspondent Banking, and Money Service Business transfers. |
| **Regulatory Basis** | REG-001 (PMLA — cash transaction reporting), REG-010 (FATF Rec. 10) |
| **Acceptance Criteria** | Cryptocurrency transactions receive a higher transaction type score than domestic wire transfers. Cash deposits receive a higher score than cheque payments. The full taxonomy is documented in `TRANSACTION_RULES.md`. |
| **Priority** | **MUST** |

---

### FR-021 — Transaction Type Module Maximum

| Field | Value |
|---|---|
| **Requirement ID** | FR-021 |
| **Description** | The Transaction Type module raw score SHALL NOT exceed the documented maximum of 55. The normalised score SHALL be calculated as `(txtype_raw / 55) × 100`. |
| **Regulatory Basis** | REG-007 (SR 11-7) |
| **Acceptance Criteria** | No API response contains a transaction type module raw score above 55. |
| **Priority** | **MUST** |

---

## 9. Functional Requirements — Velocity Module

### FR-022 — 7-day Rolling Window

| Field | Value |
|---|---|
| **Requirement ID** | FR-022 |
| **Description** | The system SHALL evaluate customer transaction velocity over a rolling 7-day lookback window using historical records from the transactions database. |
| **Regulatory Basis** | REG-003 (RBI KYC 2023 para 37 — ongoing monitoring), REG-011 (FATF Rec. 29) |
| **Acceptance Criteria** | Velocity scores are computed from transactions with `timestamp_processed >= NOW() - INTERVAL '7 days'`. Transactions older than 7 days do not contribute to velocity scoring. |
| **Priority** | **MUST** |

---

### FR-023 — Four Velocity Dimensions

| Field | Value |
|---|---|
| **Requirement ID** | FR-023 |
| **Description** | The velocity score SHALL be calculated as an equally weighted average of four dimensions: (1) Transaction Count in 7 days, (2) Total Volume in 7 days, (3) Distinct Counterparties in 7 days, (4) Structuring Pattern count (transactions at 75–99% of threshold) in 7 days. Each dimension SHALL be scored on a 0–100 scale using documented thresholds. |
| **Regulatory Basis** | REG-001 (PMLA Section 12), REG-011 (FATF Rec. 29), REG-003 (RBI KYC 2023) |
| **Acceptance Criteria** | (1) `velocity_score = (count_score + volume_score + counterparty_score + structuring_score) / 4`. (2) All four dimension scores are present in the API response `module_scores.velocity.dimensions`. |
| **Priority** | **MUST** |

---

### FR-024 — New Customer Velocity Handling

| Field | Value |
|---|---|
| **Requirement ID** | FR-024 |
| **Description** | When no transaction history exists for a customer in the 7-day window, the system SHALL return a velocity score of 0 with all dimensions at 0. The system SHALL NOT raise an error or exception for customers with no transaction history. |
| **Regulatory Basis** | REG-007 (SR 11-7 — model must handle edge cases gracefully) |
| **Acceptance Criteria** | A first-ever transaction for a new customer returns `velocity_score: 0` and all dimension values of 0. The API response is valid JSON with HTTP 200. |
| **Priority** | **MUST** |

---

### FR-025 — Velocity Rules Fired

| Field | Value |
|---|---|
| **Requirement ID** | FR-025 |
| **Description** | The system SHALL append velocity rule IDs to the `rules_fired` array when dimension scores breach defined thresholds: `VEL-001-HIGH-FREQUENCY` (count score ≥ 70), `VEL-002-HIGH-VOLUME` (volume score ≥ 70), `VEL-003-MANY-COUNTERPARTIES` (counterparty score ≥ 70), `VEL-004-STRUCTURING-PATTERN` (structuring dimension score ≥ 60). |
| **Regulatory Basis** | REG-001 (PMLA), REG-007 (SR 11-7 — explainability; rules fired must be traceable) |
| **Acceptance Criteria** | A customer with 25 transactions in 7 days has `VEL-001-HIGH-FREQUENCY` in `rules_fired`. A customer with 2 transactions has no VEL-001 rule fired. |
| **Priority** | **MUST** |

---

## 10. Functional Requirements — Sanctions Screening

### FR-026 — Six-List Screening Waterfall

| Field | Value |
|---|---|
| **Requirement ID** | FR-026 |
| **Description** | The system SHALL screen every transaction against six sanctions lists in a defined priority waterfall before computing the CRS: (1) UAPA Schedule IV, (2) UAPA Schedule I, (3) UNSC Resolution 1267, (4) UNSC Resolution 1988, (5) OFAC SDN List, (6) UN Consolidated List. Screening SHALL stop at the first match and return the matched list. |
| **Regulatory Basis** | REG-005 (Section 51A UAPA), REG-004 (RBI KYC 2025 Chapter IX), REG-009 (FATF Rec. 6), REG-012 (OFAC), REG-013 (UN) |
| **Acceptance Criteria** | (1) A name matching UAPA Schedule IV returns `sanctions_list: "UAPA_SCHEDULE_IV"` and does not continue screening lower-priority lists. (2) A name matching only the OFAC list returns `sanctions_list: "OFAC_SDN"`. (3) A clean name returns no sanctions match. |
| **Priority** | **MUST** |

---

### FR-027 — Fuzzy Name Matching

| Field | Value |
|---|---|
| **Requirement ID** | FR-027 |
| **Description** | The system SHALL use fuzzy name matching with a default threshold of 85% similarity to screen customer names against all six sanctions lists. The matching algorithm SHALL use token sort ratio to handle name component order variations. |
| **Regulatory Basis** | REG-004 (RBI KYC 2025 — sanctions screening must account for name variations and transliterations) |
| **Acceptance Criteria** | (1) "Lakhbir Singh" matches "Lakhbir Singh @ Landa" at ≥ 85% similarity. (2) "John Smith" does not match "Mohammed Al-Rashid" (no false positive). (3) Name matching is case-insensitive. |
| **Priority** | **MUST** |

---

### FR-028 — UAPA Mandatory Actions on Match

| Field | Value |
|---|---|
| **Requirement ID** | FR-028 |
| **Description** | When a UAPA Schedule I, Schedule IV, UNSC 1267, or UNSC 1988 match is confirmed, the system SHALL populate the `mandatory_actions` field in the API response with: `FREEZE_ACCOUNT`, `REPORT_FIU_IND`, and `FOLLOW_MHA_ADVISORY`. |
| **Regulatory Basis** | REG-006 (UAPA Order February 2, 2021 — mandatory triple action on UAPA match) |
| **Acceptance Criteria** | API response for any UAPA/UNSC-matched transaction contains `"mandatory_actions": ["FREEZE_ACCOUNT", "REPORT_FIU_IND", "FOLLOW_MHA_ADVISORY"]`. All three actions are present; none may be omitted. |
| **Priority** | **MUST** |

---

### FR-029 — Sanctions List Currency

| Field | Value |
|---|---|
| **Requirement ID** | FR-029 |
| **Description** | The system SHALL maintain current versions of all six sanctions lists. OFAC SDN and UN Consolidated lists SHALL be ingested via automated scripts. UAPA and UNSC lists SHALL be updated within 5 business days of a new MHA gazette notification or UNSC designation. |
| **Regulatory Basis** | REG-004 (RBI KYC 2025 — screening lists must be current), REG-009 (FATF Rec. 6 — no delay) |
| **Acceptance Criteria** | Each sanctions JSON file contains a `last_updated` field. OFAC and UN files are updated on the schedule defined in `feeds/ofac/ofac_ingestion.py`. UAPA files are updated within 5 business days of a gazette notification. |
| **Priority** | **MUST** |

---

### FR-030 — Alias Screening

| Field | Value |
|---|---|
| **Requirement ID** | FR-030 |
| **Description** | The system SHALL screen customer names against all known aliases for each sanctioned individual or entity, not only the primary listed name. Aliases SHALL be maintained in the `aliases` array of each sanctions list entry. |
| **Regulatory Basis** | REG-004 (RBI KYC 2025), REG-009 (FATF Rec. 6 — must account for name variations) |
| **Acceptance Criteria** | A customer named "LeT" matches Lashkar-e-Taiba via alias screening. A customer named "Daesh" matches ISIS/ISIL via alias screening. |
| **Priority** | **MUST** |

---

## 11. Functional Requirements — Configurable Rules Engine

### FR-031 — Eight Detection Scenarios

| Field | Value |
|---|---|
| **Requirement ID** | FR-031 |
| **Description** | The system SHALL implement the following eight detection scenarios in the configurable rules engine, each independently evaluable: SCN-001 (STRUCTURING), SCN-002 (RAPID_MOVEMENT), SCN-003 (HIGH_RISK_CORRIDOR), SCN-004 (FAN_IN), SCN-005 (ROUND_AMOUNT), SCN-006 (PEP_TRANSACTION), SCN-007 (CASH_INTENSIVE), SCN-008 (VELOCITY_BREACH). |
| **Regulatory Basis** | REG-001 (PMLA), REG-003 (RBI KYC 2023), REG-008 (FATF Rec. 1 — risk-based), REG-011 (FATF Rec. 29) |
| **Acceptance Criteria** | All eight scenarios are present in `rules/rules_config.json`. Each scenario has a unique ID, name, weight, enabled flag, and trigger_conditions object. |
| **Priority** | **MUST** |

---

### FR-032 — Scenario Toggle Without Code Deployment

| Field | Value |
|---|---|
| **Requirement ID** | FR-032 |
| **Description** | The system SHALL allow any detection scenario to be enabled or disabled via the `PUT /api/scenarios/<scenario_id>` API endpoint without requiring a code change or application redeployment. A disabled scenario SHALL be completely skipped — no evaluation, no score contribution. |
| **Regulatory Basis** | REG-007 (SR 11-7 — model must support operational governance and rapid adjustment) |
| **Acceptance Criteria** | (1) Disabling SCN-005 via API causes subsequent transactions to return no SCN-005 rule fired and no score contribution from that scenario. (2) Re-enabling SCN-005 via API restores its evaluation immediately. (3) No Python code changes are required for this toggle. |
| **Priority** | **MUST** |

---

### FR-033 — Scenario Weight Adjustment

| Field | Value |
|---|---|
| **Requirement ID** | FR-033 |
| **Description** | The system SHALL allow the weight of any detection scenario to be updated via the `PUT /api/scenarios/<scenario_id>` API endpoint. Weight changes SHALL take effect immediately on subsequent scoring calls. |
| **Regulatory Basis** | REG-007 (SR 11-7 — model governance must allow calibration without full redeploy) |
| **Acceptance Criteria** | Updating SCN-001 weight from 25 to 35 via API causes the next structuring-matched transaction to contribute 35 points (not 25) to the CRS from that scenario. |
| **Priority** | **SHOULD** |

---

### FR-034 — Rules Engine API Protection

| Field | Value |
|---|---|
| **Requirement ID** | FR-034 |
| **Description** | The `PUT /api/scenarios/<scenario_id>` endpoint SHALL require a valid `X-DEMO-API-KEY` header. Requests without a valid key SHALL be rejected with HTTP 401. |
| **Regulatory Basis** | REG-007 (SR 11-7 — model changes must be access-controlled) |
| **Acceptance Criteria** | (1) A PUT request without `X-DEMO-API-KEY` receives HTTP 401. (2) A PUT request with an incorrect key receives HTTP 401. (3) A PUT request with the correct key is processed and returns HTTP 200. |
| **Priority** | **MUST** |

---

## 12. Functional Requirements — Auto-Alert Triggers

### FR-035 — Sanctions Auto-Alert

| Field | Value |
|---|---|
| **Requirement ID** | FR-035 |
| **Description** | The system SHALL generate an immediate auto-alert on any confirmed sanctions match, regardless of CRS. The alert SHALL be classified as a Sanctions Alert. |
| **Regulatory Basis** | REG-005 (Section 51A UAPA), REG-006 (UAPA Order Feb 2 2021), REG-009 (FATF Rec. 6) |
| **Acceptance Criteria** | (1) A UAPA-matched transaction returns `alert: true` and `alert_type` containing the matched list. (2) The `crs` field is `null`. (3) `mandatory_actions` is populated with three required actions. |
| **Priority** | **MUST** |

---

### FR-036 — PEP Tier 1 Auto-Alert

| Field | Value |
|---|---|
| **Requirement ID** | FR-036 |
| **Description** | The system SHALL generate an immediate auto-alert for any transaction involving a customer with `pep_tier = "Tier 1"`. This alert SHALL be classified as a PEP Alert. Enhanced Due Diligence (EDD) is mandatory. |
| **Regulatory Basis** | REG-003 (RBI KYC 2023 Chapter VII — PEP EDD), REG-010 (FATF Rec. 12) |
| **Acceptance Criteria** | A Tier 1 PEP customer transaction generates `alert: true` with alert type indicating PEP, regardless of transaction amount or geography. |
| **Priority** | **MUST** |

---

### FR-037 — Tier 1A/1B Country Auto-Alert

| Field | Value |
|---|---|
| **Requirement ID** | FR-037 |
| **Description** | The system SHALL generate an immediate auto-alert when the sender_country or receiver_country is classified as Tier 1A (OFAC comprehensively sanctioned) or Tier 1B (UNSC-sanctioned jurisdiction). |
| **Regulatory Basis** | REG-012 (OFAC), REG-013 (UN sanctions), REG-009 (FATF Rec. 6) |
| **Acceptance Criteria** | Transactions with sender or receiver country of IR (Iran), KP (North Korea), SY (Syria), or RU (Russia — where applicable) generate immediate auto-alerts. |
| **Priority** | **MUST** |

---

### FR-038 — Structuring Pattern Auto-Alert

| Field | Value |
|---|---|
| **Requirement ID** | FR-038 |
| **Description** | The system SHALL generate an AML Risk Alert when the structuring normalised score meets or exceeds 75%, independent of the overall CRS. |
| **Regulatory Basis** | REG-001 (PMLA Section 12 — deliberate evasion), REG-002 (Rule 3 — STR obligations) |
| **Acceptance Criteria** | A transaction where structuring normalised = 78.6% generates an alert even if CRS = 37. The `alert_generated` field is `true`. |
| **Priority** | **MUST** |

---

## 13. Functional Requirements — Audit Trail and Logging

### FR-039 — INSERT-ONLY Transaction Ledger

| Field | Value |
|---|---|
| **Requirement ID** | FR-039 |
| **Description** | The `transactions` table SHALL be INSERT-ONLY. No UPDATE or DELETE operations on scored transaction records SHALL be permitted at the application layer. All corrections or amendments SHALL be made via new INSERT entries. |
| **Regulatory Basis** | REG-001 (PMLA Section 12 — records must be maintained as-scored; retroactive modification is prohibited) |
| **Acceptance Criteria** | (1) The application layer has no `UPDATE transactions SET` or `DELETE FROM transactions` statements. (2) Any attempt to modify a scored transaction via API returns an error. |
| **Priority** | **MUST** |

---

### FR-040 — Mandatory Audit Fields

| Field | Value |
|---|---|
| **Requirement ID** | FR-040 |
| **Description** | Every scored transaction persisted to the database SHALL contain the following mandatory fields: `transaction_id`, `customer_id`, `timestamp_processed`, `transaction_amount`, `transaction_currency`, `transaction_type`, `sender_country`, `receiver_country`, `crs` (or null), `risk_band`, `rules_fired` (array), `alert_generated` (boolean). |
| **Regulatory Basis** | REG-001 (PMLA Section 12 — full transaction record), REG-007 (SR 11-7 — audit trail) |
| **Acceptance Criteria** | None of the mandatory fields are null in a scored transaction record, except `crs` which is null for sanctions matches. |
| **Priority** | **MUST** |

---

### FR-041 — Rules Fired Traceability

| Field | Value |
|---|---|
| **Requirement ID** | FR-041 |
| **Description** | The system SHALL populate the `rules_fired` field with the complete list of rule IDs that contributed to the scoring decision for every transaction. Every alert SHALL be traceable to at least one documented rule. |
| **Regulatory Basis** | REG-007 (SR 11-7 — explainability; all model outputs must be traceable to documented logic) |
| **Acceptance Criteria** | (1) Every alert-generating transaction contains at least one rule ID in `rules_fired`. (2) Every rule ID in `rules_fired` corresponds to a documented rule in the applicable rule document. (3) A low-risk transaction with no rules triggered has an empty `rules_fired` array, not null. |
| **Priority** | **MUST** |

---

### FR-042 — 5-Year Record Retention

| Field | Value |
|---|---|
| **Requirement ID** | FR-042 |
| **Description** | Transaction records in the database SHALL be retained for a minimum of 5 years from the date of the transaction, as required by PMLA 2002. No auto-deletion policy SHALL be applied within this period. |
| **Regulatory Basis** | REG-001 (PMLA Section 12(1) — 5-year retention), REG-003 (RBI KYC 2023) |
| **Acceptance Criteria** | No scheduled job, trigger, or API endpoint deletes transaction records from the database. The database operator confirms in writing that records will not be purged within 5 years. |
| **Priority** | **MUST** |

---

### FR-043 — Alert Case Management Fields

| Field | Value |
|---|---|
| **Requirement ID** | FR-043 |
| **Description** | The `alerts` table SHALL capture the following case management fields for every generated alert: `alert_id`, `transaction_id`, `customer_id`, `alert_type`, `stage`, `status`, `three_point_met` (boolean), three-point identifiers (six fields), `reviewer_id`, `review_timestamp`, `reviewer_rationale`. |
| **Regulatory Basis** | REG-001 (PMLA — STR documentation), REG-007 (SR 11-7 — audit trail), institutional three-point decision standard |
| **Acceptance Criteria** | Alert records in the database contain all mandatory case management fields. The `three_point_met` field is false by default and is set to true only when all three identifier fields are populated. |
| **Priority** | **MUST** |

---

## 14. Functional Requirements — API and Integration

### FR-044 — Scoring Endpoint Input Validation

| Field | Value |
|---|---|
| **Requirement ID** | FR-044 |
| **Description** | The `POST /api/score` endpoint SHALL validate all required input fields before scoring. Invalid requests SHALL be rejected with HTTP 400 and a descriptive error message. Required fields: `transaction_amount` (positive numeric), `transaction_currency` (3-character ISO code), `transaction_type` (non-empty string), `sender_country` (2-character ISO code), `receiver_country` (2-character ISO code). |
| **Regulatory Basis** | REG-007 (SR 11-7 — model must reject invalid inputs, not produce unreliable outputs) |
| **Acceptance Criteria** | (1) A request with missing `transaction_amount` returns HTTP 400. (2) A request with `transaction_currency` = "ABCD" (4 characters) returns HTTP 400. (3) A valid request returns HTTP 200. |
| **Priority** | **MUST** |

---

### FR-045 — Scoring Response Structure

| Field | Value |
|---|---|
| **Requirement ID** | FR-045 |
| **Description** | The `POST /api/score` response SHALL include at minimum: `crs`, `overall_crs`, `risk_band`, `alert`, `rules_fired`, `module_scores` (with sub-objects for all five modules plus rules_engine), `sanctions_match` (if applicable), `mandatory_actions` (if applicable). |
| **Regulatory Basis** | REG-007 (SR 11-7 — model output must be complete and traceable) |
| **Acceptance Criteria** | All listed fields are present in every API response. No required field is absent. Null fields are explicitly returned as `null`, not omitted. |
| **Priority** | **MUST** |

---

### FR-046 — API Rate Limiting

| Field | Value |
|---|---|
| **Requirement ID** | FR-046 |
| **Description** | The API SHALL implement rate limiting to prevent abuse. The scoring endpoint SHALL enforce a documented rate limit. Requests exceeding the limit SHALL receive HTTP 429 with a descriptive error. |
| **Regulatory Basis** | REG-007 (SR 11-7 — model must be protected from operational misuse) |
| **Acceptance Criteria** | Sending more than the documented rate limit of requests per minute to `POST /api/score` from a single source returns HTTP 429. |
| **Priority** | **SHOULD** |

---

### FR-047 — Health Check Endpoint

| Field | Value |
|---|---|
| **Requirement ID** | FR-047 |
| **Description** | The system SHALL expose a `GET /api/health` endpoint that returns the current operational status of the API and database connectivity. The response SHALL include a status field and a timestamp. |
| **Regulatory Basis** | DR_BCP.md — RTO monitoring requires a reliable health check mechanism |
| **Acceptance Criteria** | `GET /api/health` returns HTTP 200 with `{"status": "ok", "timestamp": "..."}` when the API and database are operational. Returns a non-200 response when the database is unreachable. |
| **Priority** | **MUST** |

---

### FR-048 — Velocity Analytics Endpoint

| Field | Value |
|---|---|
| **Requirement ID** | FR-048 |
| **Description** | The system SHALL expose a `GET /api/customers/{customer_id}/velocity` endpoint that returns the current 7-day velocity profile for a customer, including all four dimension scores, velocity rules fired, and a transaction history summary. |
| **Regulatory Basis** | REG-003 (RBI KYC 2023 para 37 — ongoing monitoring must be accessible to compliance teams) |
| **Acceptance Criteria** | Response contains `current_7_day_score`, `dimensions` (all four), `transaction_history_summary`, and `trend_vs_previous_period`. |
| **Priority** | **SHOULD** |

---

## 15. Non-Functional Requirements

### FR-049 — Explainability

| Field | Value |
|---|---|
| **Requirement ID** | FR-049 |
| **Description** | Every scoring decision produced by the system SHALL be fully explainable to a compliance officer or regulator without reference to source code. The `rules_fired` array and `module_scores` object SHALL provide sufficient information for a qualified professional to reconstruct the scoring logic. |
| **Regulatory Basis** | REG-007 (SR 11-7 — no black-box ML; full explainability required) |
| **Acceptance Criteria** | A compliance officer with no programming knowledge can use the `rules_fired` array and `module_scores` to explain any alert in plain English to a regulator. |
| **Priority** | **MUST** |

---

### FR-050 — Rules-Based Architecture (No Unsupervised ML)

| Field | Value |
|---|---|
| **Requirement ID** | FR-050 |
| **Description** | The system SHALL use only deterministic, rules-based logic for CRS calculation. No unsupervised machine learning model, neural network, or opaque algorithmic component SHALL contribute to the CRS or alert determination. |
| **Regulatory Basis** | REG-007 (SR 11-7 — model must be fully explainable; unsupervised ML is not permissible without additional validation framework) |
| **Acceptance Criteria** | A technical review of the codebase finds no calls to ML libraries (scikit-learn, TensorFlow, PyTorch, etc.) in the scoring pipeline. All scoring logic is traceable to documented rules. |
| **Priority** | **MUST** |

---

### FR-051 — Scoring Latency

| Field | Value |
|---|---|
| **Requirement ID** | FR-051 |
| **Description** | The system SHOULD return a scoring response within 3 seconds for 95% of requests under normal operating conditions. Sanctions screening SHALL complete within 1 second. |
| **Regulatory Basis** | Operational requirement — real-time transaction monitoring |
| **Acceptance Criteria** | Performance testing confirms p95 response time ≤ 3 seconds. Sanctions screening alone completes in ≤ 1 second. |
| **Priority** | **SHOULD** |

---

### FR-052 — Quarterly Rule Review

| Field | Value |
|---|---|
| **Requirement ID** | FR-052 |
| **Description** | All detection rules, scoring thresholds, and module weights SHALL be reviewed at minimum quarterly. Any change SHALL require documented justification, regression testing against the 20 core validation scenarios, and Model Owner sign-off before deployment. |
| **Regulatory Basis** | REG-007 (SR 11-7 — ongoing model monitoring), REG-003 (RBI KYC 2023 — ongoing monitoring) |
| **Acceptance Criteria** | (1) A quarterly review record exists for every completed quarter of operation. (2) Any rule change is preceded by a documented approval record. (3) Post-change regression test results are on file. |
| **Priority** | **MUST** |

---

## 16. Sign-Off Section

| Field | Name | Credential / Role | Signature | Date |
|---|---|---|---|---|
| **Prepared by** | | | | |
| **Reviewed by (Compliance)** | | | | |
| **Reviewed by (Technology)** | | | | |
| **Approved by (Model Owner)** | Atul Krishnan | CAMS | | September 2026 |
| **Approved by (Risk Committee)** | | | | |

### 16.1 Approval Notes

> This document has been prepared in accordance with SR 11-7 Model Risk Management guidelines and is intended to serve as the primary functional specification for the ScoreSentinel CRS Engine v1.2. Any material deviation from the requirements documented herein requires a formal change request with Model Owner approval, regression testing, and an updated version of this document.

### 16.2 Next Review Date

**Scheduled next review:** December 2026 (Q4 quarterly cycle)

---

*ScoreSentinel | FRD_AML_RULES.md | AML Engine Functional Requirements Document | Authored by Atul Krishnan, CAMS | Version 1.2 | September 2026 | Status: APPROVED*
