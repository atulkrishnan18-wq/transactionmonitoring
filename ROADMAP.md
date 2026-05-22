# ROADMAP.md — ScoreSentinel & MuleCatcher 60-Day Build Plan

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Overlay:** Project MuleCatcher (Mule Cluster Intelligence)
**Version:** 3.2 | **Author:** Atul Krishnan, CAMS | **Last Updated:** 21 May 2026

---

## Overview

| | AK | AI assistance (Days 21–60) |
|---|---|---|
| **Focus** | Design AML + Mule logic, validate builds, own every decision | Build Python engine, Database, API, Mule Layer, Dashboard |
| **Result** | Live AML + Anti-Mule system designed |  Understand every component |
| **By Day 60** |  Project completion | Full stack run with Dual-Scoring |

---

## Strategic Pivot: The MuleCatcher Upgrade
ScoreSentinel has been upgraded to include a specialized fifth module for **Mule Cluster Detection**. This targets the ₹11,0,00,00,000 (₹11,000 Crore) annual fraud loss in India via coordinated networks.

---

## Master Progress Tracker

| Day | Deliverable | Location | Status | Version |
|---|---|---|---|---|
| 1-20 | Phase 1: AML Logic Design | rules/, scenarios/ | ✅ Done | v1.2 |
| 21-45 | Phase 2: Build & Validate | engine/, database/, api/, dashboard/, governance/ | ✅ Done | v1.0 |
| 46-60 | Phase 3: Deployment & Portfolio | docs/ | 📋 Planned | — |

---

## Phase 2: Build & Validate (Days 21–45) — COMPLETE ✅

### Day 21-31 ✅ — Engine & API Core
- **Deliverable:** `engine/`, `database/`, `api/`, `postman/`
- **Result:** 100% pass rate for all 25 validation scenarios.

### Day 32-35 ✅ — React Dashboard
- **Deliverable:** `dashboard/`
- **Result:** Functional UI for alert management and cluster investigation.

### Day 36-40 ✅ — Integration & Testing
- **Objective:** End-to-End Connectivity & Real-time Scoring.
- **Result:** Dashboard connected to live API; 50-transaction stress test complete; data integrity verified.

### Day 41-45 ✅ — Model Governance (SR 11-7)
- **Objective:** Compliance documentation and rule maintenance guides.
- **Deliverables:** `SR11_7_COMPLIANCE.md`, `BACKTESTING.md`, `HOW_TO_MODIFY.md`, `INDEPENDENT_VALIDATION.md`.
- **Status:** Final Model Sign-off received on Day 45.

---

## Phase 3: Deployment & Launch (Days 46–60) — IN PROGRESS 🔄

| Day | Objective | Status |
|---|---|---|
| 46 | **System Deep Dive** | ✅ Done |
| 47 | **Deployment Strategy** | ✅ Done |
| 48 | **Supabase Database Migration** | 📋 Planned |

---
### Day 47 ✅ — Deployment Strategy & Containerization
- **Deliverable:** `Dockerfile`, `requirements.txt`, `.env.template`.
- **Infrastructure:** Finalized Render.com (API) + Supabase (Postgres) stack.
- **Portability:** Containerized the engine to ensure identical behavior across local and cloud environments.

---
*ScoreSentinel | ROADMAP.md | Version 3.2 | Authored by Atul Krishnan, CAMS | 21 May 2026*
