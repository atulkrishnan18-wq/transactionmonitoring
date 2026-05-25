# CASE_STUDY_CRYPTO_AML.md — ScoreSentinel: Bridging CAMS Expertise and Technical Execution

**Author:** Atul Krishnan, CAMS
**Platform:** ChainSutra.in (Crypto Compliance & Intelligence)
**Date:** 25 May 2026

---

## 🛡️ Executive Summary
In an era of ₹11,000 Crore annual fraud losses and rapidly evolving crypto-cleansing typologies, binary "hit/no-hit" AML systems are no longer sufficient. **ScoreSentinel** was built to demonstrate how CAMS-certified risk-based logic can be translated into a transparent, multi-cloud automated engine. 

This case study details the 60-day engineering journey of building a system that prioritizes **Model Explainability (SR 11-7)** and **Operational Integrity**.

---

## 🛑 The Problem: The "Black Box" of Automated AML
Traditional automated monitoring suffers from two critical flaws:
1.  **Black-Box Logic:** Many AI-driven systems provide a "Risk Score" without a regulatory audit trail, making them indefensible during an audit.
2.  **Mule Invisibility:** Organized fraud rings often operate via clusters of small transactions that individual scoring engines treat as "Low Risk."

---

## 💎 The Solution: ScoreSentinel + MuleCatcher™

### 1. The Composite Risk Score (CRS)
Instead of a single score, ScoreSentinel evaluates transactions across four weighted dimensions:
*   **Customer (30%):** UBO transparency and PEP status.
*   **Structuring (25%):** Targeting smurfing and micro-structuring.
*   **Geography (25%):** OFAC corridors and FATF grey-list tiers.
*   **TX Type (20%):** Inherent mechanism risk (Crypto, Cash, Correspondent).

### 2. The MuleCatcher™ Intelligence Overlay
Targeting organized crime, this module identifies **Fan-In networks** and **Device Nexus** signatures—detecting when 15 accounts are coordinated by a single hardware fingerprint.

---

## 🛠️ The Tech Stack: Multi-Cloud Architecture
To ensure high availability for global reviewers, ScoreSentinel uses a decoupled architecture:
*   **Database:** Supabase (PostgreSQL) — Tokyo/Singapore Region.
*   **Backend:** Render (Containerized Python/Flask).
*   **Frontend:** Vercel (React Case Management).

---

## ⚖️ Regulatory Defensibility: The "Audit Lock"
The most significant innovation in ScoreSentinel is the **Dual-Resolution Standard**. 
*   Analysts **cannot** close a Screening Match (Sanctions/PEP) without providing **Three Unique Identifiers** and their sources (e.g., Passport, Utility Bill, Gov DB).
*   Behavioral alerts require mandatory investigative rationale.

This ensures zero "rubber-stamping" and a bulletproof audit trail for regulators.

---

## 📈 Results: The Validation Proof
ScoreSentinel was validated against 25 complex scenarios, achieving a **100% True Positive rate** for known typologies, including:
*   **Scenario 9 (The Calibration Proof):** A shell company wire through a grey-list corridor returns a score of **59.04**—proving the engine avoids unnecessary noise while maintaining high sensitivity.
*   **Scenario MC-4:** Identifying a high-velocity **UPI/Crypto Smurfing Ring** that traditional systems would miss.

---

## 🏁 Conclusion: The Future of Compliance
ScoreSentinel proves that compliance professionals don't need to choose between automation and integrity. By embedding CAMS principles directly into the code, we create systems that are fast, scalable, and—above all—defensible.

**Explore the project:**
*   🛡️ **Live Dashboard:** [transactionmonitoring.vercel.app](https://transactionmonitoring.vercel.app)
*   📦 **GitHub:** [atulkrishnan18-wq/transactionmonitoring](https://github.com/atulkrishnan18-wq/transactionmonitoring)

---
*Atul Krishnan is a CAMS-certified Senior Financial Crimes Professional at Bank of America. This project is a personal build demonstrating the future of AML Technology.*
