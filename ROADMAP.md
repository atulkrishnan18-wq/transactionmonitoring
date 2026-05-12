# ROADMAP.md — ScoreSentinel 60-Day Build Plan

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 2.0 | **Author:** Atul Krishnan, CAMS | **Last Updated:** 8 May 2026

---

## Overview

| | AK | AI assistance (Days 21–60) |
|---|---|---|
| **Focus** | Design AML logic, validate builds, own every decision | Build Python engine, Flask API, React dashboard |
| **Result** | Live AML system designed |  understand every component |
| **By Day 60** |  project completion | full stack run |

---

## Three Phases

| Phase | Days | Focus | Status |
|---|---|---|---|
| **Phase 1** | Days 1–20 | AML Logic Design — rules, thresholds, testing, tech literacy | ✅ Complete |
| **Phase 2** | Days 21–45 | Build — Python engine, database, API, dashboard | 📋 Upcoming |
| **Phase 3** | Days 46–60 | Own It — mastery, deployment, portfolio, launch | 📋 Planned |

---

## Master Progress Tracker

| Day | Deliverable | Location | Status | Version |
|---|---|---|---|---|
| 1 | AML_RULES.md | rules/ | ✅ Done | v1.2 |
| 2 | STRUCTURING_RULES.md | rules/ | ✅ Done | v1.1 |
| 2 | STRUCTURING_SCENARIOS.md | scenarios/ | ✅ Done | v1.0 |
| 3 | GEO_RULES.md | rules/ | ✅ Done | v1.1 |
| 4 | CUSTOMER_RULES.md | rules/ | ✅ Done | v1.1 |
| 5 | TRANSACTION_RULES.md | rules/ | ✅ Done | v1.2 |
| 6 | COMPOSITE_LOGIC.md | scoring/ | ✅ Done | v1.2 |
| 7 | AML_RULES.md updated | rules/ | ✅ Done | v1.2 |
| 8 | TEST_SCENARIOS.md | scenarios/ | ✅ Done | v1.2 |
| 9 | EDGE_CASES.md | scenarios/ | ✅ Done | v1.0 |
| 10 | VELOCITY_RULES.md | rules/ | ✅ Done | v1.1 |
| 11 | PEP_RULES.md | rules/ | ✅ Done | v1.1 |
| 12 | VALIDATION_SCENARIOS.md | scenarios/ | ✅ Done | v1.0 |
| 13 | AUDIT_REQUIREMENTS.md | governance/ | ✅ Done | v1.0 |
| 14 | Folder structure + README + GAPS | root/gaps/ | ✅ Done | — |
| 15 | Python concepts — functions, dictionaries | Learning | ✅ Done | — |
| 16 | Database concepts — 3 tables, SQL queries | Learning | ✅ Done | — |
| 17 | API concepts — 3 endpoints, request-response | Learning | ✅ Done | — |
| 18 | Dashboard specification — 4 screens, case workflow | Learning | ✅ Done | — |
| 19 | Full tech stack overview | docs/ | ✅ Done | — |
| 20 | TECHNICAL_OVERVIEW.md + final Phase 1 commit | docs/ | ✅ Done | — |

---

# PHASE 1 — AML LOGIC DESIGN (Days 1–20)

---

## WEEK 1 — Rule Documentation ✅ Complete

### Day 1 ✅ — Project Kickoff
**Deliverable:** `rules/AML_RULES.md` v1.2
**What was built:** Master AML framework — four-module architecture, alert thresholds, auto-alert triggers, master index of all rule documents

---

### Day 2 ✅ — Structuring Detection Rules
**Deliverable:** `rules/STRUCTURING_RULES.md` v1.1
**What was built:** Structuring detection rules — smurfing patterns, CTR threshold logic, near-threshold behaviour, micro-structuring. Added governance section v1.1.

---

### Day 3 ✅ — Geography & Sanctions
**Deliverable:** `rules/GEO_RULES.md` v1.0
**What was built:** Five-tier geographic risk classification:
- Tier 1A: OFAC + FATF Black List (Iran, DPRK, Myanmar) → +50, AUTO-ALERT
- Tier 1B: OFAC sanctioned (Syria, Cuba, Russia, Belarus, Venezuela) → +40, AUTO-ALERT
- Tier 1C: FATF Grey List → +25
- Tier 2A: CPI 0–29 highly corrupt → +20
- Tier 2B: CPI 30–49 corrupt → +15
- Tier 3: Offshore/secrecy jurisdictions → +15
- Both sender and receiver scored
- SR 11-7 threshold justification documented

**Key decisions:** CPI included after CAMS QA challenge. FATF black list corrected from 1 country to 3 (Iran, DPRK, Myanmar).

---

### Day 4 ✅ — Customer Risk Categorization
**Deliverable:** `rules/CUSTOMER_RULES.md` v1.1
**What was built:** Five-dimension Composite Customer Risk Score (CCRS) — Customer Type (0–50), Ownership Transparency (0–25), Geographic Risk (0–25), Account Behaviour (0–25), PEP/Sanctions (0–50). Maximum CCRS = 175. Added OFAC 50% cross-reference v1.1.

---

### Day 5 ✅ — Transaction Type Analysis
**Deliverable:** `rules/TRANSACTION_RULES.md` v1.2
**What was built:** 19 transaction types scored from Cryptocurrency (55) to Insurance Premium (10). 27 velocity rules (VEL-001 to VEL-027). 6 sequencing rules (SEQ-001 to SEQ-006). Third-party loan repayment rules (VEL-025/026/027). Merchant ML refund rate threshold, TBML over-invoicing indicator, three-indicator insurance ML escalation rule added v1.2.

---

### Day 6 ✅ — Composite Scoring Logic
**Deliverable:** `scoring/COMPOSITE_LOGIC.md` v1.2
**What was built:** Weighted percentage model — Customer 30%, Structuring 25%, Geography 25%, Transaction Type 20%. Normalisation methodology. Alert threshold 60 justified. Structuring ≥75% independent trigger added v1.2. Module maximums corrected (Structuring 70, TxType 55) v1.2.

---

### Day 7 ✅ — Rule Review & Refinement
**What was done:** Internal consistency review. Cross-module alignment checked. AML_RULES.md updated to v1.2 with correct master index.

---

## WEEK 2 — Testing, Validation & Governance ✅ Complete

### Day 8 ✅ — Real Transaction Scenarios
**Deliverable:** `scenarios/TEST_SCENARIOS.md` v1.2
**What was built:** 10 core validation scenarios covering full risk spectrum. Gemini v1.0 reviewed and corrected to v1.1 then v1.2 — 5 errors fixed including wrong module scores, mislabelled dispositions, and broken penalty logic.

---

### Day 9 ✅ — False Positive Testing
**Deliverable:** `scenarios/EDGE_CASES.md` v1.0
**What was built:** 7 edge cases — 4 screening false positives from operational HRDT experience:
- EC-001: Adverse media wrong person — two-identifier corroboration rule
- EC-002: Former PEP left office — de-escalation framework
- EC-003: SDN name collision — three-step disambiguation protocol
- EC-004: Common name PEP match — high-collision name protocol
- EC-005 to EC-007: Transaction false positives (cash business, student tuition, payroll)

---

### Day 10 ✅ — Velocity & Pattern Rules
**Deliverable:** `rules/VELOCITY_RULES.md` v1.1
**What was built:** Velocity tiers (Normal/Unusual/Suspicious/Burst). High-signal patterns VEL-028 to VEL-031 (Fan-In, Fan-Out, Round Number, Off-Hours). Behavioural change indicators BEH-001 to BEH-005. All velocity scores feed into Structuring module — NOT directly to CRS (corrected from Gemini v1.0 error).

---

### Day 11 ✅ — Beneficial Owner & PEP Matching
**Deliverable:** `rules/PEP_RULES.md` v1.1
**What was built:** UK MLR 2017 PEP framework. Three-tier taxonomy (Tier 1: 8 categories, Tier 2: 14 categories, Tier 3: family/associates). Dual BO threshold — 25% UK MLR triggers EDD, 50% OFAC triggers sanctions auto-alert. Fallback BO rule. 85% fuzzy match with full OCC examiner defence script. Jaro-Winkler + Levenshtein combined algorithm. 40–50% enhanced monitoring zone (Sulzer Gap) added v1.1. ScoreSentinel 2.0 APAC overlay roadmap documented.

---

### Day 12 ✅ — Rules Validation (20 Scenarios)
**Deliverable:** `scenarios/VALIDATION_SCENARIOS.md` v1.0
**What was built:** 10 extended scenarios (Scenarios 11–20):
- Scenario 11: Vekselberg/Renova/Sulzer — sanctions evasion via ownership engineering
- Scenario 12: Wirecard-style merchant ML — card-not-present fraud
- Scenario 13: Pakistani trade payment false positive — cleared with documentation
- Scenario 14: UK Cabinet Minister — domestic PEP Tier 1 auto-alert
- Scenario 15: Former PEP 18 months — de-escalation applied
- Scenario 16: BVI shell unknown BO — fallback BO block
- Scenario 17: Fan-In mule network — VEL-028 trigger
- Scenario 18: Dormant account Nigeria — BEH-001 trigger
- Scenario 19: TBML Letter of Credit — trade-based ML
- Scenario 20: Insurance early surrender — three-indicator escalation

---

### Day 13 ✅ — Audit Trail & Logging
**Deliverable:** `governance/AUDIT_REQUIREMENTS.md` v1.0
**What was built:** Three-point decision standard (from HRDT operational experience). Contemporaneous documentation requirement. Mandatory second reviewer for MNN and PEP cases. QA random sampling framework (10% standard, 100% MNN/PEP). Jurisdiction-specific requirements — UK FCA, EU 4AMLD/6AMLD, Hong Kong HKMA, Malaysia BNM. 6-year retention standard (highest common denominator).

---

### Day 14 ✅ — Final Review & GitHub Commit
**What was done:**
- Folder structure reorganised — rules/, scoring/, scenarios/, governance/, gaps/
- 18 gaps resolved and documented in GAPS_TO_ADDRESS.md v2.0
- README.md updated with full project description, 20-scenario table, regulatory coverage
- TRANSACTION_RULES.md updated to v1.2 — four critical gaps closed
- PEP_RULES.md updated to v1.1 — Sulzer Gap added
- AML_RULES.md updated to v1.2 — master index complete
- Phase 1 Week 2 complete commit

---

## WEEK 3 — Tech Literacy 🔄 In Progress

### Day 15 ✅ — How Python Executes Your Logic
**Key concepts learned:**
- Rules = Python functions (input → process → output)
- Excel rows = Python dictionaries
- Four modules run sequentially
- Sanctions auto-alert fires in Module 3 (Geography) — engine skips Module 4
- Audit log writes automatically after every transaction

---

### Day 16 ✅ — Understanding Databases
**Key concepts learned:**
- Three tables: transactions, customers, alerts
- Transactions table = audit log from AUDIT_REQUIREMENTS.md
- Four key SQL queries: high-risk alerts, customer history, pending sanctions, false positive rate
- Database stores everything you defined in markdown — nothing new invented

---

### Day 17 ✅ — APIs & System Architecture
**Key concepts learned:**
- Three endpoints: POST /api/score, GET /api/transactions, PUT /api/alerts/:id
- Full transaction flow: arrive → Flask → Python engine → PostgreSQL → React dashboard
- PUT /api/alerts requires three-point standard, reviewer ID, contemporaneous timestamp
- All endpoints implement rules already designed — Gemini translates documents to code

---

### Day 18 ✅ — Dashboard Specification
**Key concepts learned:**
- Four screens: Alert Queue, Case Detail, Charts & Analytics, Customer Profile
- Case workflow from operational HRDT experience:
  1. Pending Assessment
  2. Pending Action
  3. Sent for Review (Sales / GFC / Internal / MLRO)
  4. Resolved / Completed
- Case fields: Alert ID, Customer ID, Client RP, World-Check ID, Internal Summary, Associated Jurisdictions, Score
- Three-point standard enforced in UI — cannot submit disposition without three points
- Additional database fields identified: client_rp, worldcheck_id, internal_summary, stage, sent_to, waiting_for

---

### Day 19 ✅ — Full Tech Stack Overview
**Objective:** Understand complete system architecture
**Tasks:**
1. Understand all four components together — Python, PostgreSQL, Flask, React
2. Create data flow diagram
3. Document in TECH_STACK_EXPLAINED.md
4. Confirm zero-cost deployment plan — Render + Vercel

**Deliverable:** `docs/TECH_STACK_EXPLAINED.md`

---

### Day 20 ✅ — Tech Review & Phase 1 Final Commit
**Objective:** Consolidate all Phase 1 learning, prepare for Phase 2
**Tasks:**
1. Create TECHNICAL_OVERVIEW.md — plain English explanation of all components
2. Update SCORESENTINEL_CONTEXT.md — save full project context
3. Review all open gaps — close what can be closed
4. Final Phase 1 commit: "Phase 1 Complete — AML Logic Design Days 1–20"

**Deliverable:** `docs/TECHNICAL_OVERVIEW.md`

---

# PHASE 2 — BUILD (Days 21–45)

---

## Days 21–25 — Python Scoring Engine

**What gets built:** The engine that calculates risk scores from your rules

**Your daily role:**
- Validate code matches your documented rules
- Test against your 20 scenarios
- Confirm CRS calculations are correct
- No coding required — review and validate only

| Day | What Gets Built | Your Validation Task |
|---|---|---|
| 21 | Engine structure + customer module | ✅ Done |
| 22 | Structuring + geography modules | Run 5 structuring scenarios — confirm scores |
| 23 | Transaction type + velocity modules | Validate all 19 transaction types + VEL rules |
| 24 | Composite score + independent triggers | Confirm CRS formula matches COMPOSITE_LOGIC.md |
| 25 | All 20 scenarios pass | Run every scenario — confirm output matches expected |

**Deliverable:** Working Python scoring engine

---

## Days 26–30 — Database & API

**What gets built:** PostgreSQL database + Flask REST API

| Day | What Gets Built | Your Validation Task |
|---|---|---|
| 26 | Database schema — all tables including dashboard fields | Confirm all AUDIT_REQUIREMENTS.md fields are columns |
| 27 | Flask API — POST /api/score endpoint | Test with 5 transactions — confirm scores returned |
| 28 | GET /api/transactions + customer history | Test customer profile queries |
| 29 | PUT /api/alerts — three-point enforcement | Confirm system rejects requests missing any of 3 points |
| 30 | Full API test + back-testing methodology | Run all 20 scenarios via API — document results |

**Deliverable:** Working API — can score transactions and manage alerts

---

## Days 31–35 — React Dashboard

**What gets built:** Visual interface based on Day 18 specification

| Day | What Gets Built | Your Validation Task |
|---|---|---|
| 31 | Alert Queue — four stages, Client RP, World-Check ID | Confirm stage workflow matches HRDT experience |
| 32 | Case Detail View — score breakdown, Internal Summary tab | Confirm three-point standard enforced |
| 33 | Charts — alert volume, risk by country, FP rate | Confirm metrics match COMPOSITE_LOGIC.md targets |
| 34 | Customer Profile — transaction history, screening history | Confirm all fields present |
| 35 | Associated Jurisdictions + stage progression UI | Full dashboard walkthrough |

**Deliverable:** Working dashboard — all four screens functional

---

## Days 36–40 — Integration & Testing

| Day | What Gets Built | Your Role |
|---|---|---|
| 36 | Connect engine + API + dashboard end-to-end | Submit transaction through dashboard — watch it score |
| 37 | Bug fixing from Day 36 | Document any issues found |
| 38 | Performance — bulk transaction handling | Submit 50 transactions — confirm dashboard responsive |
| 39 | Full 20-scenario end-to-end test | Run every scenario live — compare to expected |
| 40 | System stable v1.0 | Final sign-off — confirm ready for documentation |

---

## Days 41–45 — Refinement & Model Governance

| Day | What Gets Built | Your Role |
|---|---|---|
| 41 | User acceptance testing | Use system as you would in HRDT role — 30 minutes |
| 42 | Architecture documentation | Review accuracy of system diagrams |
| 43 | MODEL_GOVERNANCE.md — SR 11-7 full compliance | Confirm all governance artifacts in place |
| 44 | BACKTESTING.md — validate rules against data | Review methodology against regulatory expectations |
| 45 | Independent model validation — review all rules | Final validation of complete engine |

---

# PHASE 3 — OWN IT (Days 46–60)

---

## Days 46–50 — Mastery & Deployment

| Day | Objective | Deliverable |
|---|---|---|
| 46 | System deep dive — understand every file | Architecture notes |
| 47 | Rules management — modify thresholds independently | HOW_TO_MODIFY.md |
| 48 | Database queries — retrieve and export data | QUERIES.md |
| 49 | Troubleshooting — read errors, fix common issues | TROUBLESHOOT.md |
| 50 | **Deploy live** — Render + Vercel — get public URLs | Live ScoreSentinel URL |

---

## Days 51–55 — Portfolio & Presentation

| Day | Objective | Deliverable |
|---|---|---|
| 51 | Portfolio preparation — README, screenshots | Professional GitHub |
| 52 | Interview preparation Part 1 — story, demo script | INTERVIEW_PREP.md |
| 53 | Architecture documentation — system diagrams | Architecture diagrams |
| 54 | AML logic documentation — explain every decision | AML_LOGIC_EXPLAINED.md |
| 55 | Live demo practice — record demo video | Demo video |

---

## Days 56–60 — Launch

| Day | Objective | Deliverable |
|---|---|---|
| 56 | Blog post / case study — publish on LinkedIn | Published article |
| 57 | Interview preparation Part 2 — tough questions | Practice recording |
| 58 | Project showcase — presentation slides | 5-slide deck |
| 59 | Final review — GitHub QA, fix everything | Final commit |
| 60 | **LAUNCH DAY** — go live, share on LinkedIn | Live ScoreSentinel 🚀 |

---

# Final Repository Structure at Day 60

```
transactionmonitoring/
│
├── README.md
├── ROADMAP.md
│
├── rules/
│   ├── AML_RULES.md
│   ├── STRUCTURING_RULES.md
│   ├── GEO_RULES.md
│   ├── CUSTOMER_RULES.md
│   ├── TRANSACTION_RULES.md
│   ├── VELOCITY_RULES.md
│   ├── PEP_RULES.md
│   └── ESCALATION_RULES.md          ← Day 20
│
├── scoring/
│   ├── COMPOSITE_LOGIC.md
│   └── NORMALISATION_FRAMEWORK.md   ← Day 20
│
├── scenarios/
│   ├── TEST_SCENARIOS.md
│   ├── EDGE_CASES.md
│   ├── VALIDATION_SCENARIOS.md
│   └── COMBINED_SCENARIOS.md        ← Day 20
│
├── governance/
│   ├── AUDIT_REQUIREMENTS.md
│   ├── MODEL_GOVERNANCE.md          ← Day 43
│   ├── BACKTESTING.md               ← Day 44
│   └── SR11_7_COMPLIANCE.md         ← Day 43
│
├── gaps/
│   └── GAPS_TO_ADDRESS.md
│
├── engine/                           ← Days 21–25
│   ├── scoring_engine.py
│   ├── customer_module.py
│   ├── geo_module.py
│   ├── structuring_module.py
│   ├── transaction_module.py
│   ├── composite.py
│   └── velocity.py
│
├── api/                              ← Days 26–30
│   └── app.py
│
├── database/                         ← Day 26
│   └── schema.sql
│
├── dashboard/                        ← Days 31–35
│   └── [React components]
│
└── docs/
    ├── TECH_STACK_EXPLAINED.md       ← Day 19
    ├── TECHNICAL_OVERVIEW.md         ← Day 20
    ├── ARCHITECTURE.md               ← Day 42
    ├── HOW_TO_MODIFY.md              ← Day 47
    ├── QUERIES.md                    ← Day 48
    ├── TROUBLESHOOT.md               ← Day 49
    ├── INTERVIEW_PREP.md             ← Day 52
    └── AML_LOGIC_EXPLAINED.md        ← Day 54
```

---

# What You Will Have by Day 60

## Technical Deliverables
- ✅ Live AML transaction monitoring system — public URL
- ✅ Rules-based scoring engine with YOUR rules
- ✅ PostgreSQL database with full audit trail
- ✅ Flask REST API — three endpoints
- ✅ React dashboard — four screens, HRDT-style case workflow
- ✅ SR 11-7 compliant documentation throughout

## Deliverables
- ✅ GitHub repo — clean, professional, 60+ commits
- ✅ Professional README with live URL
- ✅ Architecture diagrams
- ✅ AML logic documentation
- ✅ Demo video
- ✅ Case study blog post on LinkedIn / chainsutra.in
- ✅ Live system URL — anyone can visit and test it

## secomdary Deliverables
- ✅ Explain every rule and its rationale
- ✅ Defend 85% fuzzy match to OCC examiner
- ✅ Walk through Vekselberg/Sulzer case
- ✅ Explain SR 11-7 compliance by design
- ✅ Demonstrate false positive trade-off thinking
- ✅ Show live working system

---

# Daily Time Commitment

| Phase | Days | Time/Day | Focus |
|---|---|---|---|
| Phase 1 | 1–20 | 60 min | AML logic design |
| Phase 2 | 21–45 | 60 min | Review and validate builds |
| Phase 3 | 46–60 | 60 min | Own, master, deploy, present |

**Total: 60 hours over 60 days — zero cost**

---

# ScoreSentinel 2.0 — Future Roadmap

Upon completion of the 60-day build, the following enhancements are planned:

| Enhancement | Description |
|---|---|
| APAC PEP Overlays | Japan ASF, Indonesia OJK/PPATK/SIPENDAR, HK, South Korea, Thailand |
| EU Overlay | 4AMLD/6AMLD — domestic PEPs, enhanced definitions |
| US Overlay | FinCEN — foreign PEP only framework |
| GCC Overlay | Sovereign Wealth Fund BO rules, Royal family classifications |
| Dynamic Threshold Segmentation | Different alert thresholds by customer segment — pending back-testing data |
| Real-time OFAC API | Live SDN list integration |
| Companies House API | Automated UK beneficial ownership verification |
| ML Name Matching | Jaro-Winkler + ML layer — pending SR 11-7 independent validation |

---

*ScoreSentinel | ROADMAP.md | Version 2.0 | Authored by Atul Krishnan, CAMS | 8 May 2026*
