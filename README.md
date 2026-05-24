# ScoreSentinel 🛡️

## Automated AML Transaction Risk Scoring Engine + MuleCatcher™

**Author:** Atul Krishnan, CAMS
**Build:** 60-Day Independent Project | 1 Hour Per Day
**Status:** **PHASE 3 COMPLETE — LIVE & SEEDED (v1.2)**
**Last Updated:** 23 May 2026

---

### 🚀 Live Demo & Infrastructure
*   🛡️ **Live Dashboard:** [transactionmonitoring.vercel.app](https://transactionmonitoring.vercel.app)
*   ⚙️ **API Health:** [scoresentinel-api.onrender.com/api/health](https://scoresentinel-api.onrender.com/api/health)
*   📦 **Architecture:** Supabase (PostgreSQL) + Render (Python/Docker) + Vercel (React)

---

## 💎 What Is ScoreSentinel?

ScoreSentinel is a **CAMS-certified, risk-based AML engine** designed to solve the "black-box" problem in transaction monitoring. It produces a defensible **Composite Risk Score (CRS)** and specialized **Mule Cluster Intelligence (MCS)**, ensuring every alert is 100% explainable to regulators.

> *"ScoreSentinel is not just code; it is a regulatory framework in software form."*

### 🕸️ Project MuleCatcher™ (Overlay)
A proprietary intelligence layer targeting organized fraud rings. It identifies:
*   **Fan-In/Fan-Out:** Coordinated bursts to a single concentrator.
*   **Device Nexus:** Cross-account identification via shared hardware signatures.
*   **Dormant Activation:** Instant alerting on high-velocity shifts in stale accounts.

---

## 🧠 Proprietary Compliance Logic

### 1. The 3-Point Identifier Standard (Audit Lock)
Unlike standard case managers, ScoreSentinel enforces a **Hard Block** on case resolution. An analyst **cannot** close an alert as a "False Positive" or "Cleared" without documenting the **Three-Point Standard**:
*   **Identifiers:** Passport Number, Entity Registry ID, etc.
*   **Sources:** Government Database, Utility Bill, Site Visit.
*   **Why:** This ensures zero "rubber-stamping" and provides a bulletproof audit trail for regulators.

### 2. Composite Risk Scoring (CRS) Calibration
The engine uses a four-dimension weighted matrix:
*   👤 **Customer Risk (30%):** PEPs, UBO complexity, Entity type.
*   📈 **Structuring (25%):** Smurfing, micro-structuring, CTR thresholds.
*   🌍 **Geography (25%):** OFAC, FATF Grey lists, CPI Corridors.
*   💸 **TX Type (20%):** Crypto, Correspondent Banking, Cash Intensives.

**The "Scenario 9" Proof:** In validation, a high-risk shell company wire through a grey-list corridor returns a score of **59.04**. By keeping this below the alert threshold (60), the engine proves it is calibrated to avoid unnecessary noise while maintaining high sensitivity.

---

## 🖼️ Dashboard Preview

*(Screenshots coming soon! Replace placeholders with your own captures)*

| Alert Queue | Case Investigation | Mule Network Graph |
| :--- | :--- | :--- |
| ![Queue Placeholder](https://via.placeholder.com/400x200?text=Alert+Queue+Live+Data) | ![Case Placeholder](https://via.placeholder.com/400x200?text=3-Point+Audit+Enforcement) | ![Graph Placeholder](https://via.placeholder.com/400x200?text=MuleCatcher+Network+Graph) |

---

## 🛠️ Repository Structure

```
transactionmonitoring/
│
├── api/                            # Flask REST API (Render Hosted)
├── dashboard/                      # React Case Management (Vercel Hosted)
├── engine/                         # Python Scoring Modules (CAMS Logic)
├── rules/                          # AML & Mule detection logic docs
├── database/                       # PostgreSQL (Supabase Hosted)
├── tests/                          # Automated Suite (25+ Live Scenarios)
└── governance/                     # Model Risk Management (SR 11-7)
```

---

## ⚖️ Regulatory Alignment

| Framework | Implementation |
|---|---|
| **SR 11-7 Model Risk** | Documented weight derivation, FP targets, and recalibration schedule. |
| **FATF Rec 12 — PEPs** | Three-tier PEP structure with domestic/foreign de-escalation. |
| **UK MLR 2017** | Domestic PEP inclusion and 25% UBO threshold enforcement. |
| **OFAC Sanctions** | 50% Ownership Rule engine and SDN fuzzy matching. |
| **BSA/AML** | CTR threshold monitoring and SAR-ready investigation reports. |

---

## ✍️ About the Author

**Atul Krishnan, CAMS**
Senior Financial Crimes Professional | Bank of America HRDT
APAC Regional Screening | PEP | Sanctions | FinCrime SME

*ScoreSentinel is a professional demonstration of AML technology design, built by a compliance expert to bridge the gap between regulatory theory and technical execution.*

**GitHub:** github.com/atulkrishnan18-wq/transactionmonitoring
**Professional Portfolio:** chainsutra.in

---
*ScoreSentinel | Version 1.2 | Authored by Atul Krishnan, CAMS | 23 May 2026*
