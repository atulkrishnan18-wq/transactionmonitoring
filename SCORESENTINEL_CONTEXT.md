# SCORESENTINEL_CONTEXT.md — Master Project Context Document

**Purpose:** Restore full project context instantly by pasting this into a new AI session.
**Last Updated:** 11 May 2026
**Current Day:** 20 of 60 — Phase 1 Complete

---

## 1. Who You Are

**Name:** Atul Krishnan, CAMS
**Role:** Senior Financial Crimes Compliance Professional
**Employer:** Bank of America — High Risk Detection Team (HRDT)
**Day Job:** Financial crime screening — PEP, sanctions, adverse media, EDD reviews.
**APAC Coverage:** Hong Kong, Japan, Indonesia, South Korea, Thailand.
**GitHub:** github.com/atulkrishnan18-wq/transactionmonitoring

---

## 2. What ScoreSentinel Is

ScoreSentinel is a **risk-based, rules-based AML transaction risk scoring engine**. It produces a Composite Risk Score (CRS) on a normalised 0–100 scale across four weighted modules.

**Key design decision:** Rules-based, NOT machine learning. Every score is traceable to a documented rule. SR 11-7 compliant by design.

**Alert threshold:** CRS ≥ 60
**Auto-alert triggers:** Tier 1A/1B sanctions, PEP Tier 1, Structuring ≥ 75% normalised

---

## 3. Repository Structure (Phase 1 Complete)

```
transactionmonitoring/
├── README.md                    ← v2.0
├── ROADMAP.md                   ← Updated Day 20
│
├── rules/
│   ├── AML_RULES.md             ← v1.2 — master framework
│   ├── STRUCTURING_RULES.md     ← v1.1 — structuring detection
│   ├── GEO_RULES.md             ← v1.1 — Feb 2026 FATF/CPI 2024 updated
│   ├── CUSTOMER_RULES.md        ← v1.1 — customer taxonomy + CCRS
│   ├── TRANSACTION_RULES.md     ← v1.2 — 19 types + velocity rules
│   ├── VELOCITY_RULES.md        ← v1.1 — Fan-In/Fan-Out/BEH rules
│   └── PEP_RULES.md             ← v1.1 — UK MLR 2017 + BO logic
│
├── scoring/
│   └── COMPOSITE_LOGIC.md       ← v1.2 — normalisation + weights
│
├── scenarios/
│   ├── TEST_SCENARIOS.md        ← v1.2 — 10 core scenarios
│   ├── EDGE_CASES.md            ← v1.0 — false positive library
│   └── VALIDATION_SCENARIOS.md  ← v1.0 — 10 extended scenarios
│
├── governance/
│   └── AUDIT_REQUIREMENTS.md    ← v1.0 — three-point standard
│
├── docs/
│   ├── TECHNICAL_OVERVIEW.md    ← v1.0 — System explained for non-tech
│   └── TECH_STACK_EXPLAINED.md  ← v1.0 — Architecture and Data Flow
│
└── gaps/
    └── GAPS_TO_ADDRESS.md       ← v2.0 — 18 resolved
```

---

## 4. Key Design Decisions

- **Geography Scoring (v1.1):** Tier 1A (Black List), Tier 1B (Sanctions), Tier 1C (Feb 2026 Grey List). Cumulative scoring documented for highest-risk countries (e.g., Syria/Venezuela = +85).
- **Fuzzy Match Threshold — 85%:** Optimized for operational efficiency and regulatory safety.
- **Audit Trail — Three-Point Standard:** Rationale, Review, Result. Enforced in UI/UX design.
- **Tech Stack:** Python (Engine), Flask (API), PostgreSQL (DB), React (Dashboard). Zero-cost deployment on Render + Vercel.

---

## 5. Phase 1 Achievements

- Full AML logic documented across 7 rule files.
- 20 validation scenarios defined and tested against logic.
- Governance framework established (SR 11-7, Audit Trail).
- Technical architecture specified and documented.
- System explained for non-technical stakeholders.

---

## 6. Phase 2 Preview — Build (Days 21–45)

Next steps involve implementing the Python scoring engine, setting up the PostgreSQL database schema, and building the Flask API endpoints.

---

*ScoreSentinel Context Document | Atul Krishnan, CAMS | Day 20 of 60 | 11 May 2026*
