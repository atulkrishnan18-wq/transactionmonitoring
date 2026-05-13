# ScoreSentinel 🛡️

## Automated AML Transaction Risk Scoring Engine

**Author:** Atul Krishnan, CAMS
**Build:** 60-Day Independent Project | 1 Hour Per Day
**Status:** Phase 2 In Progress — Python Scoring Engine Complete (Days 21–25)
**Last Updated:** 13 May 2026

---

## What Is ScoreSentinel?

ScoreSentinel is a **risk-based, rules-based AML transaction risk scoring engine** designed to automatically assess the money laundering risk of financial transactions across four independent dimensions — producing a defensible, explainable Composite Risk Score (CRS) on a normalised 0–100 scale.

Every score is traceable to a documented rule. Every threshold is justified. Every decision is auditable. No black-box ML.

Built by a CAMS-certified financial crime compliance professional applying 6+ years of Tier 1 bank AML experience (Bank of America HRDT) to design a system aligned with:

- **SR 11-7** Model Risk Governance
- **FATF Recommendations** 1, 10, 12, 16, 19
- **UK MLR 2017** PEP and beneficial owner framework
- **OFAC** sanctions screening and 50% ownership rule
- **BSA/AML** structuring detection and CTR threshold logic
- **FinCEN CDD Rule** beneficial ownership requirements

---

## How It Works

```
TRANSACTION INPUT
      ↓
┌─────────────────────────────────────────┐
│  Module 1: Customer Risk (30%)          │
│  Shell companies, PEPs, BO opacity      │
├─────────────────────────────────────────┤
│  Module 2: Structuring (25%)            │
│  Smurfing, velocity, micro-structuring  │
├─────────────────────────────────────────┤
│  Module 3: Geography (25%)              │
│  OFAC, FATF, CPI — sender + receiver    │
├─────────────────────────────────────────┤
│  Module 4: Transaction Type (20%)       │
│  Crypto, wire, cash, correspondent      │
└─────────────────────────────────────────┘
      ↓
NORMALISE each module to 0–100
      ↓
APPLY weights → Composite Risk Score (CRS)
      ↓
CHECK independent triggers (sanctions, PEP, structuring)
      ↓
GENERATE alert + audit log
```

**Alert Threshold:** CRS ≥ 60
**Auto-Alert Triggers:** Tier 1A/1B sanctions, PEP Tier 1, Structuring ≥ 75%

---

## Repository Structure

```
transactionmonitoring/
│
├── README.md
│
├── rules/                          # Core AML detection rules
│   ├── AML_RULES.md               # Master framework & index
│   ├── STRUCTURING_RULES.md       # Smurfing & structuring detection
│   ├── GEO_RULES.md               # Geographic risk — OFAC/FATF/CPI
│   ├── CUSTOMER_RULES.md          # Customer risk taxonomy & CCRS
│   ├── TRANSACTION_RULES.md       # 19 transaction types + velocity
│   ├── VELOCITY_RULES.md          # Fan-In/Fan-Out, behavioural patterns
│   └── PEP_RULES.md               # UK MLR 2017 PEP tiers + BO logic
│
├── scoring/                        # Composite scoring methodology
│   └── COMPOSITE_LOGIC.md         # Normalisation, weights, CRS formula
│
├── scenarios/                      # Validation & test cases
│   ├── TEST_SCENARIOS.md          # 10 core validation scenarios
│   ├── EDGE_CASES.md              # False positive prevention library
│   └── VALIDATION_SCENARIOS.md    # 10 extended scenarios (Scenarios 11–20)
│
├── governance/                     # Model risk & compliance
│   └── AUDIT_REQUIREMENTS.md      # Three-point standard, audit trail
│
└── gaps/                           # Intellectual honesty
    └── GAPS_TO_ADDRESS.md         # 18 resolved gaps, 6 open, 2.0 roadmap
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
