# ScoreSentinel 🛡️

## Automated AML Transaction Risk Scoring Engine + MuleCatcher™

**Author:** Atul Krishnan, CAMS
**Build:** 60-Day Independent Project | 1 Hour Per Day
**Status:** Phase 4 Complete — Full Integration & Testing (v1.0)
**Last Updated:** 21 May 2026

---

## What Is ScoreSentinel?

ScoreSentinel is a **risk-based, rules-based AML transaction risk scoring engine** designed to automatically assess the money laundering risk of financial transactions. It produces a defensible, explainable **Composite Risk Score (CRS)** and a specialized **Mule Cluster Score (MCS)**.

Every score is traceable to a documented rule. Every threshold is justified. Every decision is auditable. No black-box ML.

### 🛡️ Project MuleCatcher™ (Overlay)
The system includes a specialized module for **Mule Cluster Detection**, targeting coordinated networks and organized fraud rings. It detects Fan-In/Fan-Out bursts, dormant-to-active transitions, and high device nexus counts.

---

## How It Works (The Dual-Scoring Engine)

```
        TRANSACTION INPUT
               ↓
┌──────────────┴──────────────┐
│ MODULE 1: CUSTOMER (30%)    │ ← PEPs, Shell Companies, UBO
│ MODULE 2: STRUCTURING (25%) │ ← Smurfing, Velocity
│ MODULE 3: GEOGRAPHY (25%)   │ ← OFAC, FATF, CPI
│ MODULE 4: TX TYPE (20%)     │ ← Crypto, Wire, Cash
└──────────────┬──────────────┘
               ↓
    COMPOSITE RISK SCORE (CRS) → 0-100 Normalised
               ↓
┌──────────────┴──────────────┐
│ MODULE 5: MULECATCHER™      │ ← Coordinated Clusters
└──────────────┬──────────────┘
               ↓
    MULE CLUSTER SCORE (MCS) → Organised Network Detection
```

---

## Repository Structure

```
transactionmonitoring/
│
├── api/                            # Flask REST API (v1.0)
├── dashboard/                      # React + Vite UI Dashboard
├── engine/                         # Python Scoring Modules (1-5)
├── rules/                          # Core AML & Mule detection logic
├── database/                       # PostgreSQL Schema & Migrations
├── tests/                          # Automated Scenario Suite (25+ cases)
├── scoring/                        # Composite logic & Normalisation
├── governance/                     # Model Risk Management (SR 11-7)
├── postman/                        # API Validation Collections
└── docs/                           # Technical Documentation
```

---

## Key Design Decisions

### Why Rules-Based, Not ML?

ScoreSentinel deliberately uses a rules-based architecture for three reasons:

1. **SR 11-7 compliance** — Every score must be explainable to a regulator in plain English. Rules-based engines provide this by design. ML models require additional XAI tooling and validation burden.

2. **Auditability** — Every alert includes a full breakdown of which rules fired and why. A compliance officer can reconstruct any decision from the audit log alone.

3. **Regulatory defensibility** — When an OCC or FCA examiner asks "why did you flag this transaction?" — the answer is a documented rule, not a probabilistic output.

### Why 85% Fuzzy Match?

The 85% threshold optimises between false positive rate (~12%) and false negative rate (~4–5%) simultaneously. Below 85%, false positives exceed the 15% operational target. Above 85%, miss rate increases materially on transliteration variations — the most documented sanctions evasion technique. Aligns with SWIFT, Refinitiv, and Actimize default settings.

### Why a Universal Alert Threshold of 60?

The CRS threshold of 60 cannot be reached without at least two independent risk factors being elevated simultaneously — preventing single-factor false positives while ensuring genuine multi-factor risk is captured. Full justification in `scoring/COMPOSITE_LOGIC.md` Section 5.1.

---

## Validation

ScoreSentinel has been validated against **20 scenarios** covering the full risk spectrum:

| Scenario | Typology | Result |
|---|---|---|
| Clean salary earner | Low risk baseline | ✅ No alert — CRS 6.33 |
| Shell company wire to Cayman | Offshore layering | ⚠️ Medium-High + EDD |
| Classic smurfing | Structuring | 🚨 Alert — independent trigger |
| Iran sanctions | Tier 1A auto-alert | 🚨 Auto-Alert |
| High-frequency crypto | Velocity + type risk | ⚠️ Medium-High + VEL-015 |
| PEP Tier 2 wire | PEP EDD | ⚠️ EDD mandatory |
| FATF corridor | Grey list geography | ⚠️ Medium-Low |
| Cash SMB micro-structuring | Structuring | 🚨 Alert — 100% trigger |
| SAR Generator | Multi-factor | ⚠️ 59.04 — calibration evidence |
| Missing UBO | Data quality | ⚠️ Data flag |
| Vekselberg / Sulzer | Sanctions + ownership engineering | 🚨 Triple Auto-Alert |
| Wirecard-style merchant ML | Card-not-present fraud | 🚨 Alert — structuring |
| Pakistani trade payment | False positive | ✅ Cleared — documented |
| UK Cabinet Minister | Domestic PEP Tier 1 | 🚨 Auto-Alert |
| Former PEP 18 months | De-escalation | ⚠️ EDD maintained |
| BVI shell unknown BO | Fallback BO | ⚠️ Data block |
| Fan-In mule network | Velocity | 🚨 Alert |
| Dormant account Nigeria | Account takeover | 🚨 Alert |
| TBML Letter of Credit | Trade-based ML | ⚠️ TBML flag |
| Insurance early surrender | Integration stage | ⚠️ Insurance ML escalation |

---

## Regulatory Coverage

| Framework | Coverage |
|---|---|
| SR 11-7 Model Risk | Threshold justification, weight derivation, normalisation, false positive targets, recalibration schedule, audit trail |
| FATF Rec 1 — RBA | Risk-based philosophy throughout all modules |
| FATF Rec 10 — CDD | Customer risk taxonomy, beneficial owner identification |
| FATF Rec 12 — PEPs | Three-tier PEP structure, UK MLR 2017, de-escalation framework |
| FATF Rec 16 — Wire Transfers | Travel Rule reference, domestic vs international scoring |
| FATF Rec 19 — High-Risk Countries | Tier 1A/1B/1C/2A/2B classification with CPI overlay |
| UK MLR 2017 | Domestic PEP inclusion, 25% BO threshold, EDD requirements |
| OFAC Sanctions | SDN screening, 50% ownership rule, 40–50% enhanced monitoring zone |
| BSA/AML | CTR threshold, structuring detection, SAR workflow |
| FinCEN CDD Rule | Beneficial ownership identification and fallback BO rule |

---

## Build Progress

| Phase | Days | Status |
|---|---|---|
| Phase 1 — AML Logic Design | Days 1–20 | ✅ Complete |
| Phase 2 — Python Engine Build | Days 21–45 | 🔄 In Progress — Engine Build Complete |
| Phase 3 — Deploy & Portfolio | Days 46–60 | 📋 Planned |

**Full 60-day roadmap:** See `ROADMAP.md`

---

## About the Author

**Atul Krishnan, CAMS**
Senior Financial Crimes Compliance Professional
Bank of America — High Risk Detection Team (HRDT)
APAC Regional Screening | PEP | Sanctions | EDD | FinCrime SME

*ScoreSentinel is an independent project demonstrating the application of CAMS-certified financial crime expertise to compliance technology design — without a coding background.*

**GitHub:** github.com/atulkrishnan18-wq/transactionmonitoring
**Publications:** chainsutra.in

---

*ScoreSentinel | Automated AML Transaction Risk Scoring Engine | Authored by Atul Krishnan, CAMS | Version 1.0 | 4 May 2026*
