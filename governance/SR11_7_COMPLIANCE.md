# SR 11-7 Compliance Audit — Model Risk Management

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.0 | **Author:** Atul Krishnan, CAMS | **Date:** 22 May 2026
**Status:** Audit Complete — COMPLIANT ✅

---

## 1. Executive Summary

This document provides the formal audit of **ScoreSentinel v1.0** against the **Federal Reserve SR 11-7 (Supervisory Guidance on Model Risk Management)**. 

ScoreSentinel is classified as a **High-Criticality Transaction Monitoring Model**. To mitigate model risk, it utilizes a transparent, rules-based weighted architecture, ensuring 100% explainability and avoiding "black-box" risk.

---

## 2. Model Development, Implementation, and Use

### 2.1 Conceptual Soundness
*   **Requirement:** The model should be based on sound theoretical principles and industry best practices.
*   **ScoreSentinel Alignment:** 
    *   Logic is derived from **FATF Recommendations**, **UK MLR 2017**, and **OFAC 50% Rule**.
    *   Architecture uses a 5-module composite approach (Customer, Structuring, Geo, TxType, MuleCatcher) to ensure multi-factor risk capture.
    *   **Normalisation:** Uses a 0-100 linear scaling to ensure module scores are comparable before weighting.

### 2.2 Data Integrity & Uniqueness
*   **Requirement:** Data used for model development and scoring must be accurate and reliable.
*   **ScoreSentinel Alignment:** 
    *   Implemented high-resolution ID generation (`TXN-YYYYMMDD-HHMMSS-RANDOM4`) to prevent primary key collisions during high-throughput bursts.
    *   Strict schema enforcement in PostgreSQL with foreign key constraints between Transactions, Alerts, and Mule Clusters.

---

## 3. Model Validation (Three Pillars)

### 3.1 Pillar 1: Evaluation of Conceptual Soundness
*   **Review:** The weighting (30/25/25/20) was calibrated to prioritize Customer Risk and Structuring, which are historically the strongest indicators of intent in financial crime.
*   **Finding:** Logic is sound. Independent auto-alerts for sanctions bypass the weighted score to ensure zero-fail compliance.

### 3.2 Pillar 2: Ongoing Monitoring
*   **Requirement:** Models must be subjected to ongoing testing to ensure performance remains within expected bounds.
*   **ScoreSentinel Alignment:**
    *   **Recalibration Schedule:** Defined in `scoring/COMPOSITE_LOGIC.md` Section 8.
    *   **Performance Metrics:** Latency monitored per transaction (<50ms target) and alert-to-transaction ratio (22% in synthetic test data; 15% production target).

### 3.3 Pillar 3: Outcomes Analysis (Back-testing)
*   **Requirement:** Comparing model outputs against actual outcomes.
*   **ScoreSentinel Alignment:**
    *   Validated against **25 master scenarios** (100% pass rate).
    *   Regression testing performed on Day 39 confirms that performance optimizations (SQL Joins) did not alter scoring outcomes.

---

## 4. Governance and Control

### 4.1 The Three-Point Standard (Disambiguation)
*   **Control:** To prevent "lazy disposal," ScoreSentinel enforces a **Three-Point Standard** for clearing hits.
*   **Evidence Required:** DOB, Nationality, Geography, or Profession (as documented in `governance/AUDIT_REQUIREMENTS.md`).
*   **Enforcement:** API returns `400 Bad Request` if identifiers are missing during alert resolution.

### 4.2 STR Workflow & Auditability
*   **Control:** High-risk Mule Clusters (MCS ≥ 60) must have a documented STR decision.
*   **Audit Trail:** Capture of `str_filed` (boolean) and `str_reference` (FIU-IND ref) ensures regulators can trace the filing from the detected cluster.

### 4.3 Documentation & Version Control
*   **Control:** All rules and thresholds are documented in Markdown files within the repository.
*   **Immutability:** The `transactions` table is insert-only at the application layer to maintain an untampered audit trail.

---

## 5. Auditor’s Conclusion

ScoreSentinel v1.0 meets the rigorous standards of **SR 11-7** for model risk management. The model's reliance on transparent rules, weighted normalization, and a strictly enforced manual review standard (Three-Point Standard) provides a defensible framework for regulatory scrutiny.

**Audit Sign-off:**
*Atul Krishnan, CAMS*
*Senior FinCrime SME*
*22 May 2026*
