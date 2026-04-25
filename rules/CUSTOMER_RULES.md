# CUSTOMER_RULES.md — Customer Risk Categorization Rules

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.0 | **Day:** 4 of 60 | **Author:** Atul Krishnan, CAMS
**Last Updated:** 2025

---

## Table of Contents
1. [Purpose & Regulatory Basis](#1-purpose--regulatory-basis)
2. [Customer Type Classification](#2-customer-type-classification)
3. [Customer Risk Scoring Logic](#3-customer-risk-scoring-logic)
4. [PEP & Sanctions Matching Process](#4-pep--sanctions-matching-process)
5. [Composite Customer Risk Score](#5-composite-customer-risk-score)
6. [Threshold Justification & Weight Derivation](#6-threshold-justification--weight-derivation)
7. [False Positive Trade-Offs & Alert Volume Design](#7-false-positive-trade-offs--alert-volume-design)
8. [Model Risk Explainability](#8-model-risk-explainability)
9. [Governance Artifacts](#9-governance-artifacts)
10. [Worked Scoring Examples](#10-worked-scoring-examples)
11. [Success Criteria](#11-success-criteria)

---

## 1. Purpose & Regulatory Basis

This document defines the customer risk categorization rules for ScoreSentinel. Customer risk scoring is a mandatory component of any AML program — it determines the level of due diligence applied at onboarding and ongoing monitoring intensity throughout the customer lifecycle.

### Regulatory Basis

- **FATF Recommendation 10** — Customer Due Diligence: institutions must assess customer risk at onboarding and on an ongoing basis
- **FATF Recommendation 12** — Politically Exposed Persons: enhanced measures required for PEPs
- **FATF Recommendation 1** — Risk-Based Approach: customer risk must be documented, justified, and proportionate
- **FinCEN CDD Rule (31 CFR 1010.230)** — Requires identification of beneficial owners and risk categorization of legal entity customers
- **BSA/AML Examination Manual** — Customer Risk Rating methodology must be documented and defensible
- **SR 11-7** — Model risk management: scoring logic must be explainable, validated, and governed

> **Design Principle:** Customer risk scoring in ScoreSentinel is rules-based and fully transparent. Every score is traceable to a documented factor with explicit justification. No black-box ML is used. This ensures full SR 11-7 compliance and audit defensibility.

---

## 2. Customer Type Classification

Customer types are classified based on four real-world risk triggers observed in financial crime typologies and validated against FATF guidance, FinCEN advisories, and BofA HRDT operational experience:

1. **Shell company / opaque ownership structure** — beneficial ownership concealment
2. **Cash-intensive business** — elevated placement-stage ML risk
3. **Newly onboarded customer** — no transaction history baseline
4. **Tax haven association** — offshore/secrecy jurisdiction linkage

These four triggers form the backbone of ScoreSentinel's customer risk classification.

---

### 2.1 High-Risk Customer Types 🔴

| Customer Type | Definition | Primary Risk | Base Risk Score |
|---|---|---|---|
| **Shell Company** | Legal entity with no clear business purpose, complex layered ownership, or nominee directors | Beneficial ownership concealment, layering | 50 |
| **Politically Exposed Person (PEP)** | Current or former senior political figure, family member, or close associate | Bribery, corruption, misappropriation of public funds | 50 |
| **Cash-Intensive Business** | Business where primary revenue is received in cash — e.g. restaurants, car washes, convenience stores, money service businesses | Placement-stage money laundering | 45 |
| **Sanctions-Adjacent Entity** | Customer with direct or indirect linkage to a sanctioned individual, entity, or jurisdiction | OFAC exposure, sanctions evasion | 50 — AUTO-ALERT |
| **High-Risk Jurisdiction Customer** | Customer domiciled in or with primary business in a Tier 1A/1B/1C country per GEO_RULES.md | Geographic AML/CFT risk | 40–50 |
| **Tax Haven Associated Entity** | Customer incorporated in or with significant financial flows through Cayman, BVI, Panama, Seychelles, Vanuatu, or similar | Layering, beneficial ownership gaps, offshore concealment | 40 |
| **Correspondent Bank / NBFI** | Non-bank financial institution or foreign correspondent bank with elevated ML/TF exposure | Nested accounts, pass-through risk | 40 |
| **Crypto-Asset Business** | Virtual asset service provider or customer with significant crypto transaction history | Anonymity, mixing, unregulated exchange exposure | 40 |

---

### 2.2 Medium-Risk Customer Types 🟠

| Customer Type | Definition | Primary Risk | Base Risk Score |
|---|---|---|---|
| **Newly Onboarded Customer** | Customer with account open < 6 months and no established transaction baseline | Unknown behaviour pattern, first-transaction risk | 30 |
| **Non-Resident Customer** | Customer whose residential address is outside the operating jurisdiction | Cross-border exposure, identity verification complexity | 25 |
| **High-Net-Worth Individual (HNWI)** | Individual with declared assets or transaction volumes exceeding defined thresholds | Source of wealth complexity, PEP adjacency | 25 |
| **Small/Medium Business (SMB)** | Business customer without cash-intensive classification but operating in moderate-risk sector | Trade-based ML, invoice fraud | 20 |
| **Trust / Foundation** | Legal structure designed to hold assets for beneficiaries | Beneficial ownership opacity, estate planning misuse | 30 |
| **Charity / NGO** | Non-profit organisation | TF risk, fund diversion | 25 |

---

### 2.3 Low-Risk Customer Types 🟢

| Customer Type | Definition | Primary Risk | Base Risk Score |
|---|---|---|---|
| **Verified Salaried Individual** | Employed individual with documented salary source, stable transaction history, and verified identity | Low — predictable behaviour pattern | 5 |
| **Established Business (3+ years)** | Incorporated business with 3+ years of trading history, audited accounts, and consistent transaction behaviour | Low — known entity, established baseline | 10 |
| **Government Entity** | Public sector body or government-owned enterprise (excluding PEP-controlled entities) | Low — regulated, transparent | 5 |
| **Listed Company** | Publicly listed company subject to exchange disclosure requirements | Low — regulated, publicly accountable | 5 |

---

## 3. Customer Risk Scoring Logic

### 3.1 Scoring Architecture

Customer risk in ScoreSentinel is assessed across **five independent risk dimensions**. Each dimension is scored separately and combined into a **Composite Customer Risk Score (CCRS).**

```
COMPOSITE CUSTOMER RISK SCORE (CCRS) =
  Customer Type Score          (0–50)
+ Ownership Transparency Score (0–25)
+ Geographic Risk Score        (0–25) ← integrates with GEO_RULES.md
+ Account Behaviour Score      (0–25)
+ PEP / Sanctions Score        (0–50) ← auto-alert trigger
─────────────────────────────────────
Maximum Possible CCRS = 175
Alert Threshold = CCRS ≥ 60
```

---

### 3.2 Dimension 1 — Customer Type Score (0–50)

Derived directly from Section 2 classification. Assign the highest applicable score if a customer falls into multiple categories.

| Classification | Score |
|---|---|
| Shell company / Sanctions-adjacent / PEP | 50 |
| Cash-intensive / High-risk jurisdiction | 45 |
| Tax haven associated / Correspondent bank / Crypto | 40 |
| Newly onboarded / Trust / Charity | 30 |
| Non-resident / HNWI | 25 |
| SMB / Established business | 10–20 |
| Verified individual / Listed company / Government | 5 |

---

### 3.3 Dimension 2 — Ownership Transparency Score (0–25)

Assesses the clarity and verifiability of beneficial ownership — a direct response to the FinCEN CDD Rule and FATF Recommendation 24.

| Ownership Structure | Score |
|---|---|
| Beneficial owner unidentified or unverifiable | 25 |
| Layered ownership — 3+ levels, offshore intermediaries | 20 |
| Nominee directors or bearer shares present | 20 |
| Beneficial owner identified but not verified | 15 |
| Single corporate layer — owner identified and verified | 5 |
| Individual customer — direct ownership, verified | 0 |

---

### 3.4 Dimension 3 — Geographic Risk Score (0–25)

Pulls directly from **GEO_RULES.md** Tier classifications. Applies to customer domicile, incorporation jurisdiction, and primary business location.

| Tier (from GEO_RULES.md) | Score Applied |
|---|---|
| Tier 1A — OFAC + FATF Black List | 25 + AUTO-ALERT |
| Tier 1B — OFAC Sanctioned | 25 + AUTO-ALERT |
| Tier 1C — FATF Grey List | 20 |
| Tier 2A — CPI 0–29 (Highly Corrupt) | 15 |
| Tier 2B — CPI 30–49 (Corrupt) | 10 |
| Tier 3 — Offshore / Secrecy | 15 |
| Tier 4 — Standard | 0 |

> **Integration Note:** Geographic risk in customer scoring is capped at 25 to avoid double-counting with transaction-level geo scoring in GEO_RULES.md. The two modules are complementary, not duplicative.

---

### 3.5 Dimension 4 — Account Behaviour Score (0–25)

Assesses the customer's historical transaction behaviour relative to their stated profile. Applies at periodic review — not at initial onboarding.

| Behaviour Indicator | Score |
|---|---|
| Transaction pattern inconsistent with stated business purpose | 25 |
| Sudden spike in transaction volume (>300% of 90-day average) | 20 |
| Multiple jurisdictions inconsistent with business profile | 20 |
| Frequent large cash transactions without clear business reason | 20 |
| Newly onboarded — no baseline established yet | 15 |
| Transaction pattern broadly consistent with profile | 5 |
| Fully consistent, stable, long-established pattern | 0 |

---

### 3.6 Dimension 5 — PEP / Sanctions Score (0–50)

| Match Type | Score | Action |
|---|---|---|
| Confirmed PEP — Tier 1 (Head of State, Cabinet Minister) | 50 | AUTO-ALERT + EDD mandatory |
| Confirmed PEP — Tier 2 (Senior official, judge, military) | 40 | EDD mandatory |
| Confirmed PEP — Tier 3 (Family member, close associate) | 30 | Enhanced monitoring |
| Confirmed Sanctions Hit | 50 | AUTO-ALERT + block + OFAC report |
| Adverse Media — confirmed financial crime | 35 | EDD mandatory |
| Adverse Media — unconfirmed / single source | 15 | Enhanced monitoring |
| No PEP / Sanctions / Adverse Media match | 0 | Standard monitoring |

---

## 4. PEP & Sanctions Matching Process

### 4.1 When Screening Occurs

| Trigger | Frequency | Scope |
|---|---|---|
| New customer onboarding | Once — before account activation | Full screening — all 6 fields |
| Periodic review — High Risk | Every 6 months | Full rescreening |
| Periodic review — Medium Risk | Every 12 months | Full rescreening |
| Periodic review — Low Risk | Every 24 months | Full rescreening |
| SDN list update (OFAC) | Within 24 hours of publication | Rescreen entire active customer base |
| Triggered review | On adverse media alert or staff referral | Immediate full rescreening |

---

### 4.2 PEP Classification Tiers

```
PEP TIER STRUCTURE:

Tier 1 — Direct PEP
  Head of State, President, Prime Minister
  Cabinet Ministers, Senior Government Officials
  Senior Judiciary, Military Generals
  Senior Central Bank / State Enterprise Officials

Tier 2 — Senior PEP
  Members of Parliament / Legislature
  Senior Regional / Provincial Officials
  Senior Officials of International Organisations
  Board Members of State-Owned Enterprises

Tier 3 — PEP-Adjacent
  Immediate family members (spouse, children, parents)
  Known close associates with joint business interests
  Beneficial owners of PEP-controlled entities
```

> **Once a PEP, Always a PEP Rule:** An individual designated as a PEP retains elevated monitoring status for a minimum of **12 months** after leaving public office. Senior heads of state retain PEP status indefinitely in ScoreSentinel.

---

### 4.3 Adverse Media Classification

| Category | Examples | Score Impact |
|---|---|---|
| **Category A — Financial Crime** | ML, fraud, bribery, sanctions evasion, tax evasion | +35 |
| **Category B — Serious Crime** | Drug trafficking, human trafficking, organised crime | +35 |
| **Category C — Corruption** | Government corruption, embezzlement, abuse of power | +30 |
| **Category D — Regulatory** | Regulatory censure, licence revocation, enforcement action | +20 |
| **Category E — Reputational** | Civil litigation, unverified allegations, single-source reporting | +10 |

> **Source Quality Rule:** Category A–D findings from single unverified sources are treated as Category E until corroborated by a second independent source.

---

### 4.4 Fuzzy Name Matching — Same Logic as GEO_RULES.md

Consistent with sanctions screening defined in GEO_RULES.md Section 5.2:

| Match % | Action |
|---|---|
| 100% | Block + Auto-Alert |
| 85–99% | Hold + escalate for review |
| 70–84% | Flag for analyst review |
| < 70% | Clear |

---

## 5. Composite Customer Risk Score

### 5.1 CCRS Calculation

```
CCRS = Customer Type Score
     + Ownership Transparency Score
     + Geographic Risk Score
     + Account Behaviour Score
     + PEP / Sanctions Score
```

### 5.2 Risk Band Assignment

| CCRS Range | Risk Band | Due Diligence Level | Review Frequency |
|---|---|---|---|
| 0–20 | 🟢 Low Risk | Standard CDD | Every 24 months |
| 21–40 | 🟡 Medium-Low Risk | Standard CDD + monitoring | Every 18 months |
| 41–59 | 🟠 Medium-High Risk | Enhanced monitoring | Every 12 months |
| 60–89 | 🔴 High Risk | Enhanced Due Diligence (EDD) | Every 6 months |
| 90+ | 🔴🔴 Very High Risk | EDD + Senior approval required | Every 3 months |
| Any AUTO-ALERT | 🚨 Sanctions / PEP Tier 1 | Immediate escalation | Immediate |

---

### 5.3 Risk Band Escalation Rules

```
ESCALATION LOGIC:

IF PEP Tier 1 OR Sanctions Hit
  → AUTO-ALERT regardless of CCRS
  → Escalate to Compliance Officer immediately

IF CCRS ≥ 90
  → EDD mandatory
  → Senior Management approval required before onboarding
  → Quarterly review cycle

IF CCRS 60–89
  → EDD mandatory
  → Compliance sign-off required
  → 6-month review cycle

IF CCRS 41–59
  → Enhanced monitoring
  → Analyst review at each periodic cycle
  → 12-month review cycle

IF CCRS ≤ 40
  → Standard CDD
  → Automated monitoring sufficient
  → 18–24 month review cycle
```

---

## 6. Threshold Justification & Weight Derivation

> **SR 11-7 Requirement:** Every threshold and weight must be justified. An unjustified threshold is an assertion, not a model. This section provides the documented rationale required for regulatory review and model validation.

---

### 6.1 Why Alert Threshold = CCRS 60

- Maximum score for a clean, low-risk customer (verified individual, domestic, no PEP/sanctions) = approximately 10–15
- A medium-risk customer with one elevated factor (e.g. newly onboarded + non-resident) scores approximately 40–50
- CCRS 60 is chosen because it cannot be reached without **at least two independent risk factors** being elevated simultaneously
- This prevents single-factor false positives while ensuring genuine multi-factor risk is captured
- Consistent with alert threshold used in structuring and geo modules — preserves cross-module comparability

### 6.2 Why PEP Tier 1 = 50 Points

- PEP Tier 1 customers represent the highest corruption risk class under FATF Recommendation 12
- Score of 50 guarantees CCRS ≥ 60 even for an otherwise clean customer profile (50 + 10 base = 60)
- This reflects the regulatory expectation that **no PEP Tier 1 customer should be onboarded without an alert and EDD** regardless of other factors
- Auto-Alert provides secondary catch — even if CCRS arithmetic fails, the rule fires

### 6.3 Why Ownership Transparency = Maximum 25 Points

- Ownership opacity is a risk amplifier, not a standalone risk — it makes other risks harder to detect
- Capped at 25 to prevent ownership structure alone from triggering an alert on an otherwise clean customer
- An unidentified beneficial owner (25) + newly onboarded (30) = 55 — below alert threshold, requiring a third factor
- This calibration is intentional: unverified ownership alone warrants enhanced scrutiny, not immediate alert

### 6.4 Why Geographic Risk Capped at 25 in Customer Module

- Full geographic scoring (up to 50 points) is applied at the transaction level in GEO_RULES.md
- Applying the same full weight at customer level would double-count geographic risk in the composite score
- Customer-level geo score capped at 25 — representing the customer's inherent domicile risk
- Transaction-level geo score captures the specific routing risk of each payment
- Combined, both layers provide comprehensive geographic coverage without artificial inflation

### 6.5 Why Newly Onboarded = 30 Points (Not Higher)

- New customer status is a **temporary** risk factor — it resolves naturally as transaction history accumulates
- 30 points reflects elevated uncertainty, not elevated threat
- At 6 months, if transaction behaviour is consistent, account behaviour score drops to 5 — reducing CCRS by ~25 points automatically
- This self-correcting calibration rewards good behaviour over time without requiring manual intervention

---

## 7. False Positive Trade-Offs & Alert Volume Design

### 7.1 Target Metrics

| Metric | Target | Rationale |
|---|---|---|
| Customer Risk Alert False Positive Rate | < 20% | Slightly higher tolerance than transaction alerts — customer reviews are less time-sensitive |
| EDD-to-SAR Conversion Rate | 5:1 to 15:1 | For every 10 EDD reviews, 1–2 should result in SAR consideration |
| PEP False Positive Rate | < 35% | Higher tolerance — PEP misses carry regulatory liability |
| Sanctions False Positive Rate | < 30% | Consistent with GEO_RULES.md |
| Recalibration Frequency | Every 6 months | Accounts for FATF/OFAC updates and portfolio composition changes |

### 7.2 Documented Design Decisions

**Decision 1 — Newly Onboarded Customers**
> Assigning 30 points to new customers will generate alerts for new customers with one other elevated factor. This is intentional. The first 6 months of a customer relationship carry the highest uncertainty. The operational cost of reviewing these cases is accepted as a deliberate design choice.

**Decision 2 — PEP Auto-Alert**
> All PEP Tier 1 customers trigger an alert regardless of CCRS. This will generate false positives — legitimate politicians bank too. However, the regulatory cost of missing a PEP onboarding without EDD materially exceeds the cost of a false positive review. Asymmetric risk tolerance is documented here.

**Decision 3 — Beneficial Owner Unknown**
> Unidentified beneficial owners score 25 points but do not auto-alert alone. This is a deliberate calibration — an unknown beneficial owner is a data gap, not a confirmed risk. It should prompt enhanced scrutiny, not automatic rejection. Rejection without basis creates customer discrimination risk.

**Decision 4 — Adverse Media Single Source**
> Single-source unverified adverse media scores 10 points (Category E), not the full Category A score of 35. This prevents news aggregator noise from generating false alerts. Two independent sources are required to escalate to Category A scoring.

---

## 8. Model Risk Explainability

### 8.1 Rules-Based vs Black-Box ML

| Dimension | ScoreSentinel (Rules-Based) | Black-Box ML |
|---|---|---|
| Every score traceable | ✅ Yes — full audit trail | ❌ No — weights opaque |
| Regulator can follow logic | ✅ Yes — documented rules | ❌ No — requires XAI tools |
| SR 11-7 compliant | ✅ Yes — by design | ⚠️ Requires additional validation burden |
| Can explain to non-technical reviewer | ✅ Yes — plain English rules | ❌ No — probabilistic output |
| Bias risk | ✅ Low — explicit rules | ⚠️ High — training data bias |
| Model drift | ✅ None — rules don't drift | ⚠️ High — requires continuous monitoring |

### 8.2 SR 11-7 Explainability Statement

> ScoreSentinel's customer risk scoring model produces a fully traceable output for every customer. Given a CCRS of 75 for a customer, a model validator or regulator can reconstruct the exact score:
>
> - Customer Type (Shell Company) = 50
> - Ownership Transparency (Unidentified BO) = 25
> - Geographic Risk (Tier 3 Offshore) = 0 (below threshold)
> - Account Behaviour (Newly onboarded) = 0 (below threshold)
> - PEP / Sanctions = 0
> - **Total CCRS = 75 → High Risk → EDD Required**
>
> This level of traceability is the gold standard under SR 11-7 and is achievable only with a rules-based architecture.

### 8.3 Warning — When ML Should Not Be Used

ScoreSentinel explicitly warns against the following without full SR 11-7 model validation:

- Using ML clustering to define customer risk tiers without documented feature importance
- Using neural networks to generate risk scores without explainability layer (SHAP/LIME minimum)
- Replacing rules-based PEP matching with ML classification without validated precision/recall benchmarks
- Any model where a compliance officer cannot explain a score to a regulator in plain language

> **Rule:** If you cannot explain why a customer scored X in one sentence, the model is not compliant.

---

## 9. Governance Artifacts

### 9.1 Audit Log Requirements

Every customer risk score change must generate an audit log entry containing:

```
AUDIT LOG ENTRY — MINIMUM REQUIRED FIELDS:

- Customer ID
- Previous CCRS
- New CCRS
- Risk band change (if any)
- Trigger for review (scheduled / SDN update / adverse media / staff referral)
- Individual dimensions scored (all 5)
- Reviewer ID
- Review timestamp
- Decision (maintain / escalate / de-escalate / exit)
- Rationale (free text — mandatory for escalation or de-escalation)
- Approver ID (if CCRS ≥ 90)
- Next review date
```

### 9.2 Version Control

| Version | Change | Date | Author |
|---|---|---|---|
| 1.0 | Initial release — all customer type classifications, 5-dimension scoring, PEP/sanctions logic | Day 4 — 2025 | Atul Krishnan, CAMS |

### 9.3 Validation Requirements (SR 11-7)

| Validation Activity | Frequency | Owner |
|---|---|---|
| Threshold back-testing against historical customer portfolio | At launch + every 12 months | Model Risk / Compliance |
| False positive rate measurement | Every 6 months | AML Analytics |
| PEP/Sanctions match rate review | Every 6 months | Sanctions Team |
| Independent model validation | Every 12 months | Independent validator |
| Regulatory change impact assessment | On every FATF/OFAC/FinCEN update | Compliance |

### 9.4 SR 11-7 Model Risk Checklist

| Requirement | Status | Location |
|---|---|---|
| Model purpose documented | ✅ Complete | Section 1 |
| Customer type taxonomy defined | ✅ Complete | Section 2 |
| Scoring dimensions documented | ✅ Complete | Section 3 |
| Threshold justification provided | ✅ Complete | Section 6 |
| False positive trade-offs documented | ✅ Complete | Section 7 |
| Model explainability addressed | ✅ Complete | Section 8 |
| Audit log requirements defined | ✅ Complete | Section 9.1 |
| Validation schedule defined | ✅ Complete | Section 9.3 |
| Independent validation | 🔄 Pending | Planned — Day 45 |
| Back-testing against historical data | 🔄 Pending | Planned — Day 30 |

---

## 10. Worked Scoring Examples

### Example 1 — Verified Salaried Individual (Expected: Low Risk)

| Dimension | Factor | Score |
|---|---|---|
| Customer Type | Verified salaried individual | 5 |
| Ownership Transparency | Individual — direct, verified | 0 |
| Geographic Risk | UK domiciled — Tier 4 | 0 |
| Account Behaviour | 3-year stable history | 0 |
| PEP / Sanctions | No match | 0 |
| **CCRS** | | **5 — 🟢 Low Risk** |

---

### Example 2 — Newly Onboarded Non-Resident (Expected: Medium Risk)

| Dimension | Factor | Score |
|---|---|---|
| Customer Type | Newly onboarded customer | 30 |
| Ownership Transparency | Individual — verified | 0 |
| Geographic Risk | Nigeria domiciled — Tier 1C | 20 |
| Account Behaviour | No baseline yet | 15 |
| PEP / Sanctions | No match | 0 |
| **CCRS** | | **65 — 🔴 High Risk → EDD Required** |

> **Insight:** A newly onboarded customer from a FATF grey-listed country scores high enough for EDD without any suspicious behaviour. This is intentional — the combination of unknown behaviour + high-risk jurisdiction warrants enhanced scrutiny from day one.

---

### Example 3 — Shell Company with Tax Haven Association (Expected: Very High Risk)

| Dimension | Factor | Score |
|---|---|---|
| Customer Type | Shell company | 50 |
| Ownership Transparency | Beneficial owner unidentified | 25 |
| Geographic Risk | BVI incorporated — Tier 3 offshore | 15 |
| Account Behaviour | Newly onboarded — no baseline | 15 |
| PEP / Sanctions | No match | 0 |
| **CCRS** | | **105 — 🔴🔴 Very High Risk → EDD + Senior Approval** |

> **Insight:** This is the highest-risk customer profile ScoreSentinel will encounter in practice. Shell company + unknown beneficial owner + offshore jurisdiction = the classic layering vehicle. Senior management approval required before onboarding.

---

### Example 4 — PEP Tier 1 with Clean Profile (Expected: Auto-Alert)

| Dimension | Factor | Score |
|---|---|---|
| Customer Type | Verified individual | 5 |
| Ownership Transparency | Individual — verified | 0 |
| Geographic Risk | Domestic — Tier 4 | 0 |
| Account Behaviour | Stable history | 0 |
| PEP / Sanctions | Cabinet Minister — PEP Tier 1 | 50 |
| **CCRS** | | **55 + 🚨 AUTO-ALERT → EDD Mandatory** |

> **Insight:** This customer would not breach the CCRS threshold of 60 on score alone (55). The AUTO-ALERT rule catches it independently. This demonstrates why auto-alert rules must exist alongside score thresholds — scores alone are insufficient for PEP and sanctions risk.

---

### Example 5 — Established Listed Company (Expected: Low Risk)

| Dimension | Factor | Score |
|---|---|---|
| Customer Type | Listed company | 5 |
| Ownership Transparency | Publicly disclosed ownership | 0 |
| Geographic Risk | US domiciled — Tier 4 | 0 |
| Account Behaviour | 10-year stable history | 0 |
| PEP / Sanctions | No match | 0 |
| **CCRS** | | **5 — 🟢 Low Risk** |

---

## 11. Success Criteria

| Criterion | Met? |
|---|---|
| Customer type taxonomy is clear, justified, and covers real-world typologies | ✅ |
| Scoring dimensions are independent and non-duplicative | ✅ |
| Thresholds are explicitly justified with documented rationale | ✅ |
| Weights are transparent and normalized across modules | ✅ |
| False positive trade-offs are documented with target metrics | ✅ |
| PEP and sanctions matching process is defined end-to-end | ✅ |
| Model explainability is addressed — rules-based, no black-box ML | ✅ |
| SR 11-7 model risk governance checklist is complete | ✅ |
| Audit log requirements are defined | ✅ |
| Worked examples demonstrate scoring logic in practice | ✅ |
| Integration with GEO_RULES.md is explicit and non-duplicative | ✅ |

---
