# ROADMAP.md — ScoreSentinel & MuleCatcher™ 60-Day Build Plan

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Overlay:** Project MuleCatcher™ (Mule Cluster Intelligence)
**Version:** 3.0 | **Author:** Atul Krishnan, CAMS | **Last Updated:** 17 May 2026

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
| 32-40 | Phase 3: React Dashboard | dashboard/ | 📋 Upcoming | — |

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
- **Environment Ready:** Standardized Postman environment (`base_url`) deployed.

---

## Phase 3: Visualise & Govern (Days 32–45)
**Goal:** Build the React + Vite dashboard to manage alerts and document Model Risk Governance (SR 11-7).

| Day | What Gets Built | Your Validation Task |
|---|---|---|
| 31 | Alert Queue — include Mule Level indicator | Confirm MPS scores visible in queue |
| 32 | Case Detail View — score breakdown, **Mule Signals** tab | Confirm MUL rules listed in rationale |
| 33 | Charts — alert volume, **Mule Cluster Stats**, FP rate | Confirm metrics match COMPOSITE_LOGIC.md targets |
| 34 | Customer Profile — transaction history, **Device Nexus** | Confirm all fields present |
| 35 | Associated Jurisdictions + stage progression UI | Full dashboard walkthrough |

**Deliverable:** Working dashboard — all four screens functional with MuleCatcher™ integration

---
*ScoreSentinel | ROADMAP.md | Version 3.0 | Authored by Atul Krishnan, CAMS | 17 May 2026*
