# ROADMAP.md — ScoreSentinel & MuleCatcher™ 60-Day Build Plan

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Overlay:** Project MuleCatcher™ (Mule Cluster Intelligence)
**Version:** 3.1 | **Author:** Atul Krishnan, CAMS | **Last Updated:** 19 May 2026

---

## Overview

| | AK | AI assistance (Days 21–60) |
|---|---|---|
| **Focus** | Design AML + Mule logic, validate builds, own every decision | Build Python engine, Database, API, Mule Layer, Dashboard |
| **Result** | Live AML + Anti-Mule system designed |  Understand every component |
| **By Day 60** |  Project completion | Full stack run with Dual-Scoring |

---

## Strategic Pivot: The MuleCatcher™ Upgrade
ScoreSentinel has been upgraded to include a specialized fifth module for **Mule Cluster Detection**. This targets the ₹11,00,00,00,000 (₹11,000 Crore) annual fraud loss in India via coordinated networks.

---

## Master Progress Tracker

| Day | Deliverable | Location | Status | Version |
|---|---|---|---|---|
| 1-20 | Phase 1: AML Logic Design | rules/, scenarios/ | ✅ Done | v1.2 |
| 21-25 | Phase 2A: Python Scoring Engine | engine/ | ✅ Done | v1.0 |
| 26-30 | Phase 2B: Database & API | database/, api/ | ✅ Done | v1.0 |
| 30 | MuleCatcher™ Intelligence Layer | engine/mule_module.py | ✅ Done | v1.0 |
| 31 | Full Suite Validation (25 Scenarios) | postman/ | ✅ Done | v1.0 |
| 32-35 | Phase 3: React Dashboard | dashboard/ | 🔄 In Progress | v1.0 |
| 36-40 | Phase 4: Integration & Testing | — | 📋 Upcoming | — |
| 41-45 | Phase 5: Model Governance (SR 11-7) | governance/ | 📋 Upcoming | — |
| 46-60 | Phase 6: Deployment & Portfolio | docs/ | 📋 Planned | — |

---

## Phase 2: Build & Validate (Days 21–31) — COMPLETE ✅

### Day 30 ✅ — MuleCatcher™ Cluster Intelligence
**Deliverable:** `rules/MULE_CLUSTER_RULES.md`, `engine/mule_module.py`
**What was built:** 
- **Module 5:** Coordinated Network Detection.
- **Rules:** Rapid Depletion (MUL-001), Fan-In Nexus (MUL-002), Dormant-to-Burst (MUL-003), Profile Contrast (MUL-005).
- **Dual-Scoring:** API now returns **CRS** (General AML) and **MCS** (Mule Cluster Score).

### Day 31 ✅ — Full Suite Postman Validation
**Deliverable:** `postman/ScoreSentinel_Full_Suite.postman_collection.json`
**Result:** 
- **100% Pass Rate:** All 25 scenarios (20 AML + 5 Mule Cluster) successfully scored and stored in PostgreSQL.
- **End-to-End Integrity:** Confirmed API connectivity, database persistence, and scoring logic accuracy.

---

## Phase 3: Visualise (Days 32–35) — IN PROGRESS 🔄
**Goal:** Build the React + Vite dashboard to manage alerts and investigate mule clusters.

| Day | What Gets Built | Status |
|---|---|---|
| 31 | **Alert Queue** — Stage workflow + MCS indicators | ✅ Done |
| 32 | **Case Detail** — Score breakdown + Mule Signals tab | ✅ Done |
| 33 | **Charts** — Alert volume, Risk by Country, FP Rate | ✅ Done |
| 34 | **Customer Profile** — History + Device Nexus | ⬜ Next |
| 35 | **Mule Cluster View** — Network mapping | ⬜ Pending |

---

## Phase 4: Integration & Testing (Days 36–40)

| Day | Task | Objective |
|---|---|---|
| 36 | End-to-End Connectivity | Connect Dashboard to live Flask API |
| 37 | Real-time Scoring Test | Submit 50 transactions via UI |
| 38 | Bulk Data Validation | Verify database integrity after stress test |
| 39 | Regression Testing | Re-run 25 master scenarios via UI |
| 40 | System Freeze v1.0 | Bug fixing and performance tuning |

---

## Phase 5: Model Governance (Days 41–45)

| Day | Objective | Deliverable |
|---|---|---|
| 41 | Model Risk Assessment | `governance/MODEL_GOVERNANCE.md` |
| 42 | SR 11-7 Compliance Audit | `governance/SR11_7_COMPLIANCE.md` |
| 43 | Backtesting Analysis | `governance/BACKTESTING.md` |
| 44 | Rules Maintenance Guide | `docs/HOW_TO_MODIFY.md` |
| 45 | Independent Model Validation | Final logic sign-off |

---

## Phase 6: Deployment & Launch (Days 46–60)

| Day | Objective | Status |
|---|---|---|
| 46-50 | **Live Deployment** | Render (API) + Vercel (UI) |
| 51-55 | **Portfolio Mastery** | GitHub README, Architecture Diagrams |
| 56-60 | **Launch** | Demo Video + LinkedIn Publication 🚀 |

---
*ScoreSentinel | ROADMAP.md | Version 3.1 | Authored by Atul Krishnan, CAMS | 19 May 2026*
