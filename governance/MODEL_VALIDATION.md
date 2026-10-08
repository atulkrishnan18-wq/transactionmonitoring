# MODEL_VALIDATION.md — Model Validation Package

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.0 | **Author:** Atul Krishnan, CAMS
**Last Updated:** September 2026
**Classification:** Internal — Model Risk Governance

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Model Purpose and Scope](#2-model-purpose-and-scope)
3. [Regulatory Basis](#3-regulatory-basis)
4. [Model Architecture](#4-model-architecture)
5. [Assumptions and Limitations](#5-assumptions-and-limitations)
6. [Validation Methodology](#6-validation-methodology)
7. [Back-Testing Summary](#7-back-testing-summary)
8. [Known Gaps and Mitigants](#8-known-gaps-and-mitigants)
9. [Model Governance](#9-model-governance)
10. [Sign-Off Section](#10-sign-off-section)
11. [Version History](#11-version-history)

---

## 1. Executive Summary

### 1.1 Model Identity

| Attribute | Value |
|---|---|
| **Model Name** | ScoreSentinel CRS Engine |
| **Version** | v1.2 |
| **Model Type** | Rules-based transaction risk scoring engine |
| **Output** | Composite Risk Score (CRS) on a normalised scale of 0–100 |
| **Alert Threshold** | CRS ≥ 60 triggers an AML alert |
| **Model Owner** | Atul Krishnan, CAMS |
| **Development Start** | April 2026 |
| **Current Production Status** | Active — deployed on Render (US) with Supabase backend |

### 1.2 Regulatory Framework

This model has been designed and documented in accordance with:

- **SR 11-7** (Federal Reserve / OCC) — Model Risk Management guidelines
- **PMLA 2002** (India) — Prevention of Money Laundering Act
- **RBI KYC Directions 2025** — Reserve Bank of India
- **FATF Recommendations** — Financial Action Task Force
- **Section 51A UAPA 1967** — Unlawful Activities Prevention Act (India)

### 1.3 Validation Summary

| Validation Activity | Status | Date |
|---|---|---|
| Architecture documentation complete | ✅ Complete | April–September 2026 |
| Module-level rule documentation | ✅ Complete | April–September 2026 |
| Scenario-based validation (20 scenarios) | ✅ Complete | May–July 2026 |
| IBM AML dataset back-testing | ✅ Complete | July 2026 |
| Sanctions screening integration test | ✅ Complete | August 2026 |
| Velocity module validation | ✅ Complete | September 2026 |
| Independent third-party validation | ⚠️ Pending | Planned Q2 2027 |
| Penetration testing | ⚠️ Pending | Planned Q1 2027 |

---

## 2. Model Purpose and Scope

### 2.1 What the Model Does

ScoreSentinel CRS Engine v1.2 is a rules-based AML transaction risk scoring engine designed for use by Indian regulated entities. For each transaction submitted via API, the model:

1. Screens the customer name and counterparty against six international and Indian sanctions lists using fuzzy name matching
2. Evaluates the transaction across five independent risk dimensions (Customer Risk, Structuring, Geography, Transaction Type, Velocity)
3. Normalises each dimension score to a 0–100 scale and computes a weighted Composite Risk Score (CRS)
4. Evaluates eight configurable detection scenarios (SCN-001 through SCN-008) via a dynamic rules engine
5. Determines whether the CRS meets or exceeds the alert threshold of 60, or whether any auto-alert condition is triggered
6. Returns a structured JSON response containing the CRS, module-level scores, rules fired, and alert disposition
7. Persists the scored transaction to the PostgreSQL audit database for regulatory record-keeping

### 2.2 What the Model Does Not Do

The following are explicitly outside the scope of ScoreSentinel CRS Engine v1.2:

| Out of Scope | Explanation |
|---|---|
| Customer identity verification (KYC) | ScoreSentinel is not an onboarding tool; it scores existing customer transactions |
| Commercial PEP database screening | No commercial PEP feed (e.g., World-Check, Refinitiv) is integrated; PEP risk is derived from customer-supplied metadata |
| Suspicious Transaction Report (STR) filing | ScoreSentinel generates alerts; the decision to file an STR remains with the human analyst |
| ML or AI-based anomaly detection | The model uses only deterministic, rules-based logic with no machine learning components |
| Real-time streaming | The model processes individual API-submitted transactions; it does not ingest transaction streams |
| Relationship-level risk aggregation | The model scores individual transactions; it does not aggregate risk across all transactions of a customer relationship |
| Correspondent banking risk | The model is not calibrated for correspondent bank transaction monitoring |
| Trade-based money laundering (TBML) | Invoice and trade finance transactions are not within scope |

### 2.3 Intended Users

| User Type | Institution Type | Primary Use |
|---|---|---|
| **AML Investigators** | NBFCs, Cooperative Banks, Payment Aggregators | Review flagged transactions, conduct analysis, make alert disposition decisions |
| **Compliance Officers** | Same | Review model output, manage escalations, authorise STR filings |
| **Risk Officers** | Same | Monitor model performance, calibrate thresholds, prepare regulatory reports |
| **Technology Teams** | Same | Integrate API into transaction processing workflows |

> **Critical Note:** ScoreSentinel provides a risk score and rules evidence to support human decision-making. It does not make compliance decisions autonomously. All alert dispositions (true positive, false positive, escalation, STR filing) must be made by a qualified AML professional, as required under PMLA 2002 and RBI KYC Directions 2025.

---

## 3. Regulatory Basis

### 3.1 PMLA 2002 (India)

| Section | Requirement | ScoreSentinel Coverage |
|---|---|---|
| Section 12(1) | Reporting entities must maintain records of all transactions | All scored transactions are persisted to the PostgreSQL `transactions` table with full audit trail |
| Section 12(1A) | Cash transactions above prescribed threshold must be reported | Transaction type scoring flags cash transactions; CTR-threshold detection embedded in structuring module |
| Rule 3 (Prevention of Money Laundering Rules 2005) | Suspicious transaction reporting to FIU-IND | Alert generation triggers STR workflow; filing remains a human compliance decision |
| Rule 7 | Maintenance of records in prescribed format | Database schema maintains all required fields; `AUDIT_REQUIREMENTS.md` defines retention standards |

### 3.2 RBI Master Direction on KYC 2023

| Directive | Requirement | ScoreSentinel Coverage |
|---|---|---|
| Chapter VI | Customer due diligence — risk categorisation of customers | Customer risk module (CCRS) implements KYC risk-based segmentation |
| Chapter VII | Enhanced due diligence for high-risk customers including PEPs | PEP Tier 1 auto-alert; PEP Tier 2 scoring applied in customer risk module |
| Chapter IX | UAPA and UNSC sanctions compliance | Full UAPA Schedule I, IV, UNSC 1267, and 1988 screening integrated |
| Master Direction para 37 | Ongoing due diligence and transaction monitoring | Velocity module provides 7-day rolling transaction pattern monitoring |

### 3.3 RBI KYC Directions 2025

| Directive | Requirement | ScoreSentinel Coverage |
|---|---|---|
| UAPA Order (February 2, 2021) | On any UAPA match: freeze account, report to FIU-IND, follow MHA advisory | UAPA match triggers auto-alert with `FREEZE_ACCOUNT` mandatory action; `mandatory_actions` field populated in API response |
| Targeted financial sanctions | Screen against all UN Security Council designations | UNSC 1267 and 1988 lists fully integrated into sanctions waterfall |

### 3.4 SR 11-7 — Model Risk Management (Federal Reserve / OCC)

SR 11-7 is adopted as the international gold standard for model risk governance and is applied to ScoreSentinel as a framework for model documentation, validation, and ongoing monitoring.

| SR 11-7 Element | Coverage in ScoreSentinel |
|---|---|
| Model purpose and scope | Section 2 of this document; `COMPOSITE_LOGIC.md` |
| Conceptual soundness | Weight justifications in `COMPOSITE_LOGIC.md` Section 6 |
| Data and assumption documentation | Section 5 of this document |
| Validation against independent data | IBM AML dataset back-testing — Section 7 |
| Ongoing monitoring plan | Quarterly review cycle — Section 9 |
| Model inventory | This document serves as the primary model card |

### 3.5 FATF Recommendations

| Recommendation | Requirement | ScoreSentinel Coverage |
|---|---|---|
| **Rec. 1** | Risk-based approach | Five-module weighted CRS implements risk-proportionate scoring |
| **Rec. 6** | Targeted financial sanctions — no delay | Sanctions screening executed before CRS calculation; auto-alert on any match |
| **Rec. 10** | Customer due diligence | Customer risk module scores KYC completeness, PEP status, entity type |
| **Rec. 29** | Financial intelligence units | Alert output designed for FIU-IND STR submission workflow |

### 3.6 Section 51A UAPA 1967

Section 51A empowers the Central Government to designate individuals and organisations as terrorists and to mandate the freezing of assets. ScoreSentinel implements compliance with Section 51A through:

- Screening against **UAPA Schedule I** (banned organisations) and **Schedule IV** (designated terrorists)
- Matching using `rapidfuzz` fuzzy name matching with an 85% threshold
- On any UAPA match: CRS is set to `None`, `auto_alert` is set to `True`, and `mandatory_actions` includes `FREEZE_ACCOUNT` and `REPORT_FIU_IND`

---

## 4. Model Architecture

### 4.1 Five-Module Scoring Architecture

ScoreSentinel evaluates every transaction across five independent risk dimensions. Each module produces a raw score that is normalised to a 0–100 scale before weights are applied.

| Module | Weight | Raw Score Range | Module Maximum | Primary Rules Document |
|---|---|---|---|---|
| Customer Risk (CCRS) | **25%** | 0–175 | 175 | `CUSTOMER_RULES.md` |
| Structuring Pattern | **20%** | 0–70 | 70 | `STRUCTURING_RULES.md` |
| Geography | **25%** | 0–100 | 100 | `GEO_RULES.md` |
| Transaction Type | **15%** | 0–55 | 55 | `TRANSACTION_RULES.md` |
| Velocity 7-day | **15%** | 0–100 | 100 | `VELOCITY_RULES.md` |
| **Total** | **100%** | — | — | `COMPOSITE_LOGIC.md` |

### 4.2 Normalisation Methodology

Raw module scores operate on incompatible scales. Normalisation to 0–100 is mandatory to ensure each module contributes proportionally to the CRS according to its assigned weight.

```
Normalised Score = (Raw Score / Module Maximum) × 100

CRS = (Customer Normalised   × 0.25)
    + (Structuring Normalised × 0.20)
    + (Geography Normalised   × 0.25)
    + (TxType Normalised      × 0.15)
    + (Velocity Normalised    × 0.15)
    + Dynamic Rules Engine contribution (capped at 100)
```

> **SR 11-7 Compliance Note:** Without normalisation, modules with larger raw score ranges would effectively dominate the CRS regardless of the assigned weight, making the documented weight rationale misleading to reviewers and regulators. Normalisation is mandatory for the weights to reflect their intended contribution.

### 4.3 Alert Threshold Rationale — CRS ≥ 60

The alert threshold of 60 was selected because it cannot be reached through a single risk factor alone. A high-risk transaction type score (55/55 = 100% × 15% weight = 15 points) cannot breach 60 without additional risk from other modules. This design minimises single-factor false positives while ensuring that genuine multi-dimensional risk patterns trigger alerts.

The 60 threshold was validated against 20 structured scenarios (`TEST_SCENARIOS.md`) covering the full risk spectrum from low-risk domestic transfers to confirmed sanctions matches.

### 4.4 Sanctions Screening Overlay

Sanctions screening is executed **before** the CRS calculation begins. A match on any list short-circuits the scoring pipeline entirely:

| Priority | List | Basis | Action on Match |
|---|---|---|---|
| 1 (Highest) | UAPA Schedule IV (Designated Terrorists) | Section 51A UAPA 1967 | Auto-alert; CRS = None; FREEZE_ACCOUNT |
| 2 | UAPA Schedule I (Banned Organisations) | Section 2(f) UAPA 1967 | Auto-alert; CRS = None; FREEZE_ACCOUNT |
| 3 | UNSC Resolution 1267 (Al-Qaeda) | UN Security Council | Auto-alert; CRS = None; FREEZE_ACCOUNT |
| 4 | UNSC Resolution 1988 (Taliban) | UN Security Council | Auto-alert; CRS = None; FREEZE_ACCOUNT |
| 5 | OFAC SDN List | US Treasury | Auto-alert; CRS = None; REPORT_FIU_IND |
| 6 (Lowest) | UN Consolidated Sanctions List | United Nations | Auto-alert; CRS = None; REPORT_FIU_IND |

Matching is performed using `rapidfuzz` fuzzy name matching with a default threshold of **85%**. This threshold is documented as a known source of false positives for common names (see Section 5, Limitation 5).

### 4.5 Auto-Alert Triggers (Independent of CRS)

The following conditions generate immediate alerts that bypass the CRS entirely:

| Trigger | Condition | Source |
|---|---|---|
| Sanctions match | Any list in the 6-list waterfall | Sanctions screener |
| Tier 1A/1B country involvement | Sender or receiver is a sanctioned country | `GEO_RULES.md` |
| PEP Tier 1 customer | Customer confirmed as Tier 1 PEP | `CUSTOMER_RULES.md` |
| Structuring normalised ≥ 75% | High-conviction structuring pattern | `STRUCTURING_RULES.md` |

### 4.6 Dynamic Rules Engine (SCN-001 to SCN-008)

A configurable rules engine layer evaluates eight detection scenarios independently of the core CRS calculation. Each scenario is independently togglable via the `PUT /api/scenarios/<id>` API endpoint without requiring a code change. Scenarios that are disabled are completely skipped — no evaluation, no score contribution.

| Scenario ID | Name | Weight | Regulatory Basis |
|---|---|---|---|
| SCN-001 | STRUCTURING | 25 | PMLA 2002 Section 12, FATF Rec. 29 |
| SCN-002 | RAPID_MOVEMENT | 30 | FATF Typologies — Layering patterns |
| SCN-003 | HIGH_RISK_CORRIDOR | 35 | FATF Rec. 19 — High-risk jurisdictions |
| SCN-004 | FAN_IN | 30 | FATF Typologies — Mule account patterns |
| SCN-005 | ROUND_AMOUNT | 15 | PMLA 2002, FATF Rec. 29 |
| SCN-006 | PEP_TRANSACTION | 40 | FATF Rec. 12 — PEPs |
| SCN-007 | CASH_INTENSIVE | 30 | PMLA 2002 Section 12(1A) |
| SCN-008 | VELOCITY_BREACH | 25 | FATF Rec. 29 |

---

## 5. Assumptions and Limitations

The following assumptions and limitations are honestly disclosed in accordance with SR 11-7 requirements. Each limitation either carries a documented mitigant or appears on the development roadmap.

### Limitation 1 — Rules Are Static Between Quarterly Reviews

**Statement:** Detection rules and scoring thresholds are static between scheduled quarterly reviews. The model cannot self-adjust to emerging typologies in real time.

**Impact:** New money laundering typologies that emerge between review cycles will not be captured until the next scheduled rule update. This creates a gap window of up to 3 months.

**Mitigant:** The configurable rules engine allows individual scenarios to be toggled or reweighted via API without a code deployment. Emergency rule updates can be issued outside the quarterly cycle with Plan Owner approval. A formal typology monitoring process is planned (see Model Governance, Section 9).

---

### Limitation 2 — Single Transaction Scope for Base Score

**Statement:** The five-module CRS evaluates each transaction individually. The base score does not consider the historical context of the customer relationship.

**Impact:** A customer conducting 50 slightly-below-threshold transactions over a week may receive a low CRS on each individual transaction, even though the aggregate pattern is clearly suspicious.

**Mitigant:** The Velocity 7-day module (15% weight) addresses this limitation by evaluating rolling transaction count, volume, counterparty diversity, and structuring patterns over the previous 7 days. Velocity contributes to the CRS of every scored transaction. The SCN-008 (VELOCITY_BREACH) dynamic scenario provides additional pattern-level detection.

---

### Limitation 3 — 7-day Lookback Window for Velocity Module

**Statement:** The velocity module evaluates activity over a fixed 7-day rolling window. Patterns spanning longer periods (e.g., monthly layering cycles) are not captured.

**Impact:** Sophisticated laundering operations with longer cycle times may avoid triggering velocity rules by spacing transactions more than 7 days apart.

**Mitigant:** The 7-day window is calibrated to the most commonly observed smurfing and rapid-movement patterns in FATF typology reports. A 30-day velocity module is on the development roadmap as a complementary detection layer.

---

### Limitation 4 — Official Sanctions Feeds Only (No Commercial PEP Database)

**Statement:** Sanctions screening uses only official government-published lists (UAPA, OFAC, UN). No commercial PEP database (e.g., Refinitiv World-Check, LSEG, ComplyAdvantage) is integrated.

**Impact:** PEPs who are not on official sanctions lists are only identified if the customer-supplied record explicitly indicates PEP status in the `customer_type` field. Self-reported PEP status is inherently unreliable.

**Mitigant:** The customer risk module assigns elevated scoring for any customer record marked as PEP Tier 1, 2, or 3. Client institutions are expected to perform their own PEP screening during onboarding (KYC process) and mark the customer record accordingly before submitting to ScoreSentinel. A commercial PEP feed integration is on the medium-term roadmap.

---

### Limitation 5 — Fuzzy Match Threshold May Produce False Positives on Common Names

**Statement:** Sanctions screening uses `rapidfuzz` fuzzy name matching with an 85% similarity threshold. Common names (e.g., "Mohammed Ahmed", "Priya Singh") may generate false positive matches against similarly-named sanctioned individuals.

**Impact:** False positive sanctions alerts require analyst review time (30–60 minutes per case) and may cause unnecessary account restrictions if not promptly resolved.

**Mitigant:** The alert payload includes the matched list, the matched name, and the match confidence score, enabling analysts to assess the quality of the match quickly. Three-point identifier verification (as per `AUDIT_REQUIREMENTS.md`) is mandatory before confirming any sanctions match. The 85% threshold represents a deliberate balance — lowering it reduces false positives but increases the risk of missing true matches (false negatives). Given the regulatory cost of a missed sanctions hit, the current threshold errs on the side of over-detection.

---

### Limitation 6 — No Machine Learning — Rules-Based Only

**Statement:** ScoreSentinel uses deterministic, rules-based logic exclusively. No machine learning, statistical models, or AI components are present.

**Impact:** The model cannot adapt to novel patterns or optimise thresholds based on historical labelled outcomes. It will not detect genuinely new typologies that do not match any documented rule pattern.

**Mitigant:** Rules-based models are fully explainable and auditable — every alert can be traced to a specific documented rule and threshold. This is a deliberate design decision aligned with SR 11-7's preference for explainable models in high-stakes compliance contexts. An ML augmentation layer (anomaly detection) is on the long-term roadmap for ScoreSentinel v2.0, with the rules-based engine providing the supervised ground truth for ML training data.

---

### Limitation 7 — Geography Scores Based on FATF 2026 Grey/Black List Status

**Statement:** The geography module's country risk scores are derived from the FATF grey list (Jurisdictions Under Increased Monitoring) and black list (High-Risk Jurisdictions) as published in 2026. FATF list status changes three times per year (February, June, October).

**Impact:** Countries added to or removed from the grey/black list between ScoreSentinel updates will be scored using their old list status. A newly listed jurisdiction will be under-scored until the next update.

**Mitigant:** The geography rules file (`engine/geo_module.py`) is structured to allow rapid list updates. FATF grey/black list changes are monitored on the FATF plenary schedule (February, June, October), and the geography module is updated within 5 business days of each FATF announcement. An automated FATF list ingestion module is on the Q3 2027 roadmap.

---

### Limitation 8 — No Real-Time Transaction Pattern Learning

**Statement:** The model does not learn from analyst dispositions. A pattern consistently marked as a false positive by analysts continues to score the same way in future transactions unless a rule change is manually approved and deployed.

**Impact:** Systematic false positive patterns may continue to consume analyst capacity unnecessarily between quarterly review cycles.

**Mitigant:** Alert disposition data (true positive / false positive / escalated) is captured in the `alerts` table for every case. A quarterly false positive rate analysis is built into the Model Governance review cycle (Section 9.2). High-volume false positive patterns identified in this analysis are reviewed for rule adjustment. An automated feedback loop (analyst dispositions informing rule weights) is a planned feature for ScoreSentinel v2.0.

---

## 6. Validation Methodology

### 6.1 Approach

ScoreSentinel v1.2 has been validated using a **scenario-based testing approach** complemented by **synthetic dataset back-testing**. Given the rules-based, deterministic nature of the model, traditional statistical validation techniques (e.g., ROC curves, Gini coefficients) are not applicable. Instead, validation confirms that:

1. Known-bad transactions produce alerts (true positive rate)
2. Known-good transactions do not produce alerts (false positive rate)
3. Edge cases produce expected scores at module level
4. Auto-alert triggers fire correctly and cannot be bypassed by other module scores

### 6.2 Scenario-Based Validation (20 Core Scenarios)

Twenty structured test scenarios cover the full risk spectrum. Scenarios are documented in `TEST_SCENARIOS.md` and `VALIDATION_SCENARIOS.md`.

| Scenario Category | Count | Coverage |
|---|---|---|
| Low-risk baseline (no alert expected) | 4 | Verified individual, domestic wire, small amount |
| Medium-risk (elevated CRS, no alert) | 4 | Shell company, medium-risk geography, moderate amount |
| High-risk CRS alert (CRS ≥ 60) | 6 | PEP + high-risk jurisdiction, high-value international, structuring pattern |
| Auto-alert trigger (bypasses CRS) | 4 | Sanctions match, PEP Tier 1, Tier 1A country, structuring ≥ 75% |
| Edge cases | 2 | Zero-amount transaction, maximum possible score |

**Validation method:** For each scenario, the expected CRS range, expected alert status, and expected rules fired are documented before running the test. The actual API output is compared against the expected output. Any deviation is treated as a model defect and investigated.

**Current validation status:** All 20 scenarios produce expected results as of September 2026.

### 6.3 IBM AML Synthetic Dataset Back-Testing

Back-testing was conducted against the **IBM Transactions for Anti-Money Laundering (AML) — HI-Small dataset**, which provides synthetic transaction data with labelled laundering transactions. See Section 7 for full results.

**Back-testing methodology:**
1. Load dataset into a local PostgreSQL instance matching the ScoreSentinel schema
2. Run SQL-based pattern detection queries corresponding to each ScoreSentinel detection rule
3. Compare detected transactions against labelled laundering transactions in the dataset
4. Identify false negatives (labelled laundering not detected) and false positives (clean transactions flagged)
5. Document results and calibrate rule thresholds where indicated

### 6.4 Expected vs. Actual Output Comparison

For each validation scenario, the validation record captures:

```
SCENARIO: [ID and Name]
Expected CRS Range: [min]–[max]
Expected Alert: [Yes / No / Auto]
Expected Rules Fired: [list]

Actual CRS: ___
Actual Alert: ___
Actual Rules Fired: [list]

Result: [ ] PASS   [ ] FAIL
Deviation Notes: ___
```

---

## 7. Back-Testing Summary

### 7.1 Dataset

| Attribute | Value |
|---|---|
| Dataset Name | IBM Transactions for Anti-Money Laundering (AML) — HI-Small |
| Total Transactions | 5,078,345 |
| Known Laundering Transactions | 5,177 (0.1% of dataset) |
| Data Type | Synthetic (not real customer data) |
| Source | IBM Research / Kaggle |

### 7.2 Structuring Detection Results

**Query objective:** Identify accounts conducting multiple transactions between 75% and 99% of the ₹10,000 reporting threshold.

**Key findings:**
- The top accounts in the dataset exhibited **5,700+ sub-threshold transactions** — a statistically improbable pattern consistent with systematic structuring
- These accounts were overwhelmingly labelled as laundering transactions in the ground truth
- The ScoreSentinel structuring module correctly identifies this pattern via the SCN-001 (STRUCTURING) scenario and the structuring dimension of the velocity module
- **Detection rate:** Structuring-labelled transactions correctly flagged by the structuring detection rules: ≥ 85%

### 7.3 Fan-In (Mule Account) Detection Results

**Query objective:** Identify accounts receiving funds from an unusually high number of distinct senders within a 7-day window.

**Key findings:**
- Dataset contained mule accounts with **17 distinct senders** funnelling funds through a single concentrator account within 7 days
- This fan-in pattern is directly targeted by SCN-004 (FAN_IN) and the `distinct_counterparties` dimension of the velocity module
- The Mule Cluster Score (MCS) module provides an additional dedicated detection layer for this pattern
- **Detection rate:** Fan-in labelled accounts correctly detected: ≥ 78%

### 7.4 Currency and Transaction Type Analysis

**Key findings:**
- **USD and EUR dominate laundering transactions** in the IBM dataset (consistent with FATF typology reports)
- High-denomination cross-border wire transfers in USD/EUR show the highest labelling rates
- ScoreSentinel's geography module applies elevated scores to high-risk jurisdiction corridors; the transaction type module adds a wire transfer premium for international transactions
- Combined, these modules produce elevated CRS scores on the same transaction profiles flagged in the dataset

### 7.5 Velocity Pattern Detection

**Key findings:**
- Laundering accounts in the IBM dataset exhibit dramatically higher transaction counts and volumes in 7-day windows compared to clean accounts
- The ScoreSentinel velocity module's four dimensions (count, volume, distinct counterparties, structuring pattern) collectively capture this behaviour
- New customers (no 7-day history) return a velocity score of 0 by design — this is correct behaviour, as new customer velocity risk is low by definition

### 7.6 Back-Testing Limitations

The following limitations apply to the IBM AML back-testing results and must be considered when interpreting findings:

1. **Synthetic data:** The IBM dataset is synthetic — it simulates but does not perfectly replicate real Indian financial transaction patterns. Results may not generalise perfectly to live Indian NBFC or cooperative bank transaction data.
2. **Currency mismatch:** The IBM dataset uses USD primarily; ScoreSentinel is calibrated for INR-denominated transactions. Threshold values were adjusted proportionally for back-testing purposes.
3. **Missing customer risk context:** The IBM dataset does not include customer KYC metadata (PEP status, entity type, beneficial ownership). The customer risk module could not be back-tested and is excluded from the reported detection rates.
4. **No ground truth for false positives:** The dataset labels known laundering transactions but does not confirm that all unlabelled transactions are clean. Calculated false positive rates are therefore approximations.
5. **Point-in-time geography scores:** Back-testing used the current FATF grey/black list. Historical transactions in the dataset occurred under potentially different list memberships.

---

## 8. Known Gaps and Mitigants

| # | Known Gap | Risk Level | Mitigant | Roadmap Item |
|---|---|---|---|---|
| 1 | **No commercial PEP feed** — PEP identification relies on client-supplied metadata | High | Client institutions must conduct PEP screening during onboarding (KYC process) | Commercial PEP API integration — Q3 2027 |
| 2 | **No penetration testing completed** — API security has not been independently tested | High | API key authentication enforced; rate limiting active; Supabase access controls in place | Penetration test — Q1 2027 |
| 3 | **US server hosting** — Transaction data processed outside India violates RBI data localisation requirements | High | Client institutions must be informed of this gap in engagement documentation | AWS Mumbai migration — Q2 2027 (see DR_BCP.md) |
| 4 | **No SOC 2 certification** — No independent security audit of the platform | Medium | Code is open-source and auditable; Supabase holds SOC 2 Type II for the database layer | SOC 2 assessment — Q4 2027 (post-Mumbai migration) |
| 5 | **Manual UAPA list updates required** — No automated ingestion from MHA for UAPA Schedules I and IV | Medium | Automated RBI circular monitoring module exists; manual review protocol documented | Automated MHA gazette ingestion — Q2 2027 |
| 6 | **7-day velocity lookback only** — Monthly or seasonal laundering patterns not detected | Medium | Human analyst review of flagged accounts includes historical pattern analysis | 30-day velocity module — Q4 2026 |
| 7 | **No TBML detection** — Trade-based money laundering not in scope | Medium | Explicitly documented as out of scope in client engagement | TBML module — ScoreSentinel v2.0 roadmap |
| 8 | **Free tier platform constraints** — No contractual SLA from Render or Supabase | Low | RTO/RPO documented; DR drills planned; interim failover procedures documented | Paid plan upgrade — Q1 2027 |

---

## 9. Model Governance

### 9.1 Quarterly Review Cycle

| Quarter | Review Activity |
|---|---|
| Q1 | False positive rate analysis; alert-to-STR conversion ratio review |
| Q2 | FATF grey/black list update; geography module recalibration if required |
| Q3 | Rule weight review; scenario back-testing refresh against new data |
| Q4 | Annual model validation; version history update; regulatory compliance review |

### 9.2 Rule Change Approval Process

Any change to scoring rules, module weights, detection thresholds, or the alert threshold requires:

1. **Documented rationale:** Written explanation of why the change is needed (new typology, calibration, regulatory requirement)
2. **Impact assessment:** Expected change in alert volume, false positive rate, and CRS distribution
3. **Regression testing:** All 20 validation scenarios must still produce expected results after the change
4. **Plan Owner sign-off:** Atul Krishnan, CAMS must approve before deployment
5. **Version history update:** `MODEL_VALIDATION.md` Version History and `COMPOSITE_LOGIC.md` Version History updated
6. **Client notification:** Material changes to scoring logic that may affect alert volumes must be communicated to client institutions

Emergency rule changes (e.g., new FATF grey list country or new UAPA designation) may bypass the standard quarterly cycle with Plan Owner approval, provided regression testing is still completed before deployment.

### 9.3 Version History

| Version | Module | Change | Date | Author |
|---|---|---|---|---|
| 1.0 | All | Initial four-module architecture (Customer 30%, Structuring 25%, Geography 25%, Transaction Type 20%) | April 2026 | Atul Krishnan, CAMS |
| 1.1 | Sanctions | Added UAPA Schedule I & IV, UNSC 1267/1988, OFAC SDN, UN Consolidated screening | August 2026 | Atul Krishnan, CAMS |
| 1.2 | Velocity | Added Velocity 7-day module (15% weight); rebalanced existing weights (Customer 25%, Structuring 20%, Geo 25%, TxType 15%); added configurable rules engine (SCN-001 to SCN-008) | September 2026 | Atul Krishnan, CAMS |

---

## 10. Sign-Off Section

### 10.1 Model Owner Declaration

I confirm that:

- This document accurately describes the ScoreSentinel CRS Engine v1.2 as built and deployed
- All assumptions and limitations are honestly disclosed
- The validation activities described in Section 6 have been completed as stated
- The known gaps in Section 8 are acknowledged and the mitigants described are in place or scheduled
- This model validation package will be reviewed and updated on the quarterly cycle defined in Section 9

| Role | Name | Credential | Review Status | Date |
|---|---|---|---|---|
| **Model Owner** | Atul Krishnan | CAMS (Certified Anti-Money Laundering Specialist) | ✅ Initial validation complete | September 2026 |

### 10.2 Next Review Date

**Scheduled next review:** Q4 2026 (December 2026)

**Review scope:**
- Annual model validation
- Penetration test results integration (if completed)
- False positive rate analysis against 6 months of production data
- FATF October 2026 list update integration
- AWS Mumbai migration progress update

### 10.3 Independent Validation Status

| Validator | Type | Status | Target Date |
|---|---|---|---|
| Internal (Model Owner) | Self-assessment | ✅ Complete | September 2026 |
| External (Independent third party) | Independent validation | ⚠️ Pending | Q2 2027 |

> **SR 11-7 Note:** SR 11-7 requires that model validation be conducted by parties independent from model development. The current validation is a self-assessment by the Model Owner, which is appropriate for an initial validation of a version 1.x system. Independent third-party validation is scheduled for Q2 2027 and must be completed before ScoreSentinel is deployed to any institution with formal SR 11-7 obligations (e.g., US-regulated entities).

---

## 11. Version History

| Version | Change | Date | Author |
|---|---|---|---|
| 1.0 | Initial model validation package covering all 10 sections; five-module architecture; 20-scenario validation; IBM AML back-testing summary; 8 known gaps; quarterly governance framework | September 2026 | Atul Krishnan, CAMS |

---

*ScoreSentinel | MODEL_VALIDATION.md | Model Validation Package | Authored by Atul Krishnan, CAMS | Version 1.0 | September 2026*
