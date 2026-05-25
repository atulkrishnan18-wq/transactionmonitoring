# AML_LOGIC_EXPLAINED.md — The CAMS-Certified Core

**Author:** Atul Krishnan, CAMS
**Version:** 1.0 | **Status:** Expert Narrative | **Date:** 24 May 2026

---

## 🛡️ The Philosophy: "Risk-Based, Not Binary"

Traditional AML systems often operate on binary "hit/no-hit" logic. ScoreSentinel adopts a **Weighted Composite Risk Score (CRS)** approach, aligning with FATF Recommendation 1 and SR 11-7 standards. This document explains the expert rationale behind the 100+ rules built into the engine.

---

## 💎 1. The Four Pillars of Individual Risk

The CRS is calculated by combining four independent risk dimensions, ensuring that no single factor (like a "high-risk country") triggers an alert without supporting evidence.

### Pillar A: Customer Risk (30%)
*   **Expert Logic:** We prioritize "Transparency Over Type."
*   **The Difference:** A Shell Company is risky, but a Shell Company with **undisclosed UBOs** is a red flag.
*   **The "Sulzer" Gap:** We include a "40-50% Ownership Zone." This identifies actors who engineer ownership just below the 50% OFAC threshold to evade sanctions.

### Pillar B: Structuring & Velocity (25%)
*   **Expert Logic:** "Intent over Amount."
*   **The Logic:** We target **"Smurfing"** patterns — 10 small transactions of $9,500 are treated more severely than a single $100,000 transaction.
*   **Dormant Activation:** Sudden bursts in stale accounts trigger an immediate 40-point structuring penalty, targeting Account Takeovers (ATO).

### Pillar C: Geography (25%)
*   **Expert Logic:** "FATF Tiering."
*   **The Logic:** We don't just use a "Blacklist." We use a 5-tier corridor system (OFAC 1A/1B, FATF Grey-List 1C, Emerging Markets 2A/2B).
*   **Corridor Premium:** If both sender and receiver are in Tier 3 (Offshore), a 25% "Tax Haven Premium" is added to the score.

### Pillar D: Transaction Type (20%)
*   **Expert Logic:** "Inherent Mechanism Risk."
*   **The Logic:** Crypto transfers and Correspondent Banking wires carry a higher baseline risk than Domestic SALARY credits.

---

## 🧠 2. Scoring Decisions & Threshold Rationale

### Why is the Alert Threshold 60?
In a professional environment, a high **False Positive Rate (FPR)** leads to "Analyst Fatigue."
*   **The Calibration:** A CRS of 60 is mathematically impossible to reach unless **at least TWO** pillars are high-risk.
*   **The Proof:** A Shell Company (Pillar A) in a High-Risk Country (Pillar C) scores **~59.04**. This is high-risk but "Monitor Only." Once they perform a structured transaction (Pillar B), they hit **80+** and trigger an immediate alert.

### Why do Sanctions Bypass the Score?
Sanctions are **Absolute Liabilities**.
*   **Rationale:** You cannot "average out" an OFAC match with a low-risk customer profile. If there is a match ≥ 85% on the SDN list, the system generates an **AUTO-ALERT**, bypassing the CRS entirely to ensure non-discretionary reporting.

---

## 🕸️ 3. MuleCatcher™: Network Intelligence

While the CRS looks at *one* person, MuleCatcher™ looks at the **Network**.

### The "Fan-In" Pattern (MUL-028)
*   **Scenario:** 15 accounts receiving ₹5,000 via UPI and sending ₹75,000 to one central "Concentrator" within 1 hour.
*   **Rationale:** This targets the ₹11,000 Crore fraud problem in India. Traditional systems generate 15 separate alerts; ScoreSentinel generates **ONE Cluster Case**, showing the analyst the full web of mules.

---

## ⚖️ 4. The 3-Point Standard (Regulatory Defensibility)

The most unique feature of ScoreSentinel is the **Resolution Block**.
*   **The Requirement:** Analysts MUST provide 3 unique Identifiers (e.g., Passport, Utility Bill, Gov DB) to close a case.
*   **Expert Rationale:** This enforces **Operational Discipline**. It ensures that if a regulator audits the bank 5 years later, the "False Positive" decision is backed by forensic evidence, not just an analyst's "hunch."

---
*ScoreSentinel | AML Logic Documentation | Prepared by Atul Krishnan, CAMS | Day 54 of 60*
