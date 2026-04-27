# COMPOSITE_LOGIC.md — Composite Scoring Logic

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.0 | **Day:** 6 of 60 | **Author:** Atul Krishnan, CAMS
**Last Updated:** 25 April 2026

---

## 1. Purpose & Regulatory Basis

This document defines how ScoreSentinel combines individual module scores into a single Composite Risk Score (CRS). The composite model is a weighted percentage model producing a final score of 0–100, where scores of 60 or above trigger an AML alert.

Regulatory basis:
- SR 11-7 — Model risk management: weights and thresholds must be documented and justified
- FATF Recommendation 1 — Risk-based approach: composite risk must reflect relative severity of each risk dimension
- BSA/AML Examination Manual — Transaction monitoring systems must produce explainable, calibrated scores

SR 11-7 Compliance Statement: ScoreSentinel uses a weighted percentage model. Every weight is documented with explicit justification. The model produces a 0–100 score that any compliance officer can explain to a regulator in plain English.

---

## 2. Scoring Architecture

### 2.1 Four Risk Modules

| Module | Document | Max Raw Score | Weight |
|---|---|---|---|
| Customer Risk | CUSTOMER_RULES.md | 175 | 30% |
| Structuring | STRUCTURING_RULES.md | 115 | 25% |
| Geography | GEO_RULES.md | 100 | 25% |
| Transaction Type | TRANSACTION_RULES.md | 100 | 20% |

*Note: Transaction Type max (100) includes Base Score (55) + Data Integrity Penalties (45).*

### 2.2 Two-Step Calculation

Step 1 — Normalise each module score to 0–100:
  Normalised Score = (Raw Score / Max Raw Score) × 100

Step 2 — Apply weights and sum:
  CRS = (Customer × 30%) + (Structuring × 25%) + (Geography × 25%) + (Transaction Type × 20%)

### 2.3 Alert Threshold

| CRS Range | Risk Band | Action |
|---|---|---|
| 0–20 | Low Risk | Standard monitoring |
| 21–40 | Medium-Low Risk | Standard monitoring + logging |
| 41–59 | Medium-High Risk | Enhanced monitoring |
| 60–79 | High Risk | Alert generated — analyst review |
| 80–100 | Very High Risk | Alert generated — senior escalation |
| AUTO-ALERT | Sanctions / PEP Tier 1 | Immediate escalation — bypasses CRS |

---

## 3. Auto-Alert Rules — Outside the Weighted Model

The following conditions trigger an immediate alert regardless of CRS:

- Customer or counterparty is in OFAC Tier 1A or 1B country — GEO_RULES.md
- Customer is confirmed PEP Tier 1 — CUSTOMER_RULES.md
- Sanctions name match at 85% or above — GEO_RULES.md
- OFAC 50% ownership rule triggered — GEO_RULES.md

Rationale: Sanctions and PEP Tier 1 exposure carry strict liability under OFAC regulations. No scoring model should be permitted to suppress an alert on these triggers. They operate as hard rules, not scored variables.

---

## 4. Weight Justification

### 4.1 Why Customer Risk = 30% (Highest Weight)

- Who the customer IS is the strongest single predictor of ML risk
- A shell company with unknown beneficial ownership in an offshore jurisdiction represents the highest-conviction ML signal regardless of transaction amount or type
- PEP exposure, tax haven association, and newly onboarded status are all customer-level attributes that dominate risk in real-world EDD reviews
- Consistent with G-SIB operational experience — customer profile drives the majority of high-risk escalations

---

## 10. Jurisdictional & Materiality Calibration

To ensure the model is "Business-Friendly" and operationally efficient, the following calibration layers are applied:

### 10.1 Jurisdictional Legal Supremacy
The Data Integrity Penalty (DIP) is dynamically adjusted based on the legal requirements of the transaction jurisdiction. If a specific data field is not legally mandated in a jurisdiction, the penalty for that field is suppressed (Penalty = 0). This prevents unnecessary friction in jurisdictions with lighter documentation requirements.

### 10.2 Materiality Filter
DIP is only applied to "Hard-Stop" fields (e.g., UBO, Source of Wealth) that carry direct regulatory liability. Missing secondary fields (e.g., phone numbers, middle names) are treated as operational gaps rather than risk indicators and do not trigger scoring penalties.

### 10.3 Segmented Risk Tolerance
Tolerance for data gaps is higher for **Institutional** segments where "Know Your Business" (KYB) has already been performed by a regulated partner institution. Retail segments carry a higher DIP to reflect the institution's direct regulatory obligation.
- FATF Recommendation 10 places CDD at the centre of AML programs — reflecting customer risk as the primary variable

### 4.2 Why Structuring = 25%

- Structuring is the most direct indicator of deliberate evasion behaviour — it requires intent, not just circumstance
- Pattern-based detection across multiple transactions is the strongest behavioural signal in the engine
- FATF Typologies consistently identify structuring as the primary placement-stage technique
- 25% weight reflects high signal value while preventing structuring alone from dominating the composite

### 4.3 Why Geography = 25%

- Jurisdiction risk — both sender and receiver — directly reflects regulatory enforcement gaps and corruption exposure
- Equal weight to structuring because geographic risk is an independent risk dimension not correlated with customer or transaction type
- Applies to both sides of every transaction — doubled coverage without doubled weight due to normalisation
- FATF Recommendation 19 explicitly requires enhanced scrutiny for high-risk jurisdictions

### 4.4 Why Transaction Type = 20% (Lowest Weight)

- The mechanism of a transaction is important but least predictive on its own
- A cryptocurrency transaction from a verified clean customer in a low-risk jurisdiction is lower risk than a cash deposit from a shell company
- Transaction type provides context for the other modules rather than standalone risk signal
- 20% weight reflects its role as a risk amplifier rather than a primary driver

---

## 5. Normalisation Rationale

Raw module scores have different maximum values:
- Customer Risk maximum = 175
- Structuring maximum = 115
- Geography maximum = 100
- Transaction Type maximum = 100 (including DIP)

Without normalisation, customer risk would dominate the composite regardless of weights — a customer score of 175 would always overwhelm a transaction type score of 55. Normalising each module to 0–100 before weighting ensures each module contributes proportionally according to its assigned weight.

This is a documented design decision required for SR 11-7 compliance — weights must reflect intended contribution, not raw scale differences.

---

## 6. Worked Examples

### Example 1 — Shell Company International Wire to Cayman Islands

Raw scores:
- Customer Risk: 105 (shell company + unknown BO + offshore)
- Structuring: 55 (near-CTR threshold pattern)
- Geography: 40 (Nigeria sender + Cayman receiver)
- Transaction Type: 70 (international wire + missing UBO penalty)

Normalised:
- Customer: 105/175 × 100 = 60.0
- Structuring: 55/115 × 100 = 47.8
- Geography: 40/100 × 100 = 40.0
- Transaction Type: 70/100 × 100 = 70.0

Weighted CRS:
- 60.0 × 30% = 18.00
- 47.8 × 25% = 11.95
- 40.0 × 25% = 10.00
- 70.0 × 20% = 14.00
- CRS = 53.95 — MEDIUM-HIGH — Enhanced Monitoring (Borderline Alert)

### Example 2 — Verified Individual Domestic Wire

Raw scores:
- Customer Risk: 5 (verified individual)
- Structuring: 0 (no pattern)
- Geography: 0 (domestic)
- Transaction Type: 15 (domestic wire)

Normalised:
- Customer: 5/175 × 100 = 2.9
- Structuring: 0/70 × 100 = 0
- Geography: 0/100 × 100 = 0
- Transaction Type: 15/55 × 100 = 27.3

Weighted CRS:
- 2.9 × 30% = 0.87
- 0 × 25% = 0
- 0 × 25% = 0
- 27.3 × 20% = 5.46
- CRS = 6.33 — LOW RISK — No Alert

### Example 3 — New Customer Crypto Transaction

Raw scores:
- Customer Risk: 30 (newly onboarded)
- Structuring: 0 (single transaction)
- Geography: 0 (domestic)
- Transaction Type: 55 (cryptocurrency)

Normalised:
- Customer: 30/175 × 100 = 17.1
- Structuring: 0
- Geography: 0
- Transaction Type: 55/55 × 100 = 100

Weighted CRS:
- 17.1 × 30% = 5.13
- 0 × 25% = 0
- 0 × 25% = 0
- 100 × 20% = 20.0
- CRS = 25.13 — MEDIUM-LOW — No Alert but Enhanced Monitoring

Note: Velocity rule VEL-015 may still fire independently if 3+ crypto transactions occur within 24 hours.

---

## 7. False Positive Management

Target false positive rate: less than 15%

The threshold of 60 is calibrated to ensure:
1. No high-risk transaction type alone triggers an alert for a clean customer
2. Any medium-risk activity requires at least one other elevated risk factor to alert
3. Single-factor noise is minimised while multi-factor signal is maximised

If false positive rate rises above 25% — threshold is reviewed for upward adjustment in increments of 5.
If alert-to-SAR ratio falls below 5:1 — threshold is reviewed for downward adjustment.
Recalibration schedule: every 6 months.

---

## 8. SR 11-7 Model Risk Checklist

| Requirement | Status | Location |
|---|---|---|
| Model purpose documented | Complete | Section 1 |
| Weight derivation justified | Complete | Section 4 |
| Normalisation methodology documented | Complete | Section 5 |
| Threshold justification provided | Complete | Section 7 |
| False positive targets defined | Complete | Section 7 |
| Auto-alert rules documented separately | Complete | Section 3 |
| Worked examples provided | Complete | Section 6 |
| Independent validation | Pending | Planned Day 45 |
| Back-testing | Pending | Planned Day 30 |

---

## 9. Version Control

| Version | Change | Date | Author |
|---|---|---|---|
| 1.0 | Initial release — weighted percentage model, 4 modules, normalisation framework | 25 April 2026 | Atul Krishnan, CAMS |
