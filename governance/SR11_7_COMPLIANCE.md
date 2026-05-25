# SR 11-7 Compliance Audit — Model Risk Management

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.0 | **Author:** Atul Krishnan, CAMS | **Date:** 22 May 2026
**Status:** Audit Complete — COMPLIANT ✅

---

## 1. Executive Summary & Model Purpose
ScoreSentinel is a high-criticality transaction monitoring model designed to identify money laundering and mule activity. Its primary purpose is to produce defensible risk scores (CRS and MCS) to assist compliance officers in identifying suspicious activity.

---

## 2. Conceptual Soundness
The model is based on a rules-based weighted architecture. It utilizes a 5-module approach (Customer, Structuring, Geography, Transaction Type, and MuleCatcher) derived from FATF recommendations and banking best practices. This architecture ensures 100% explainability, avoiding the "black-box" risks of pure ML models.

---

## 3. Ongoing Monitoring
The model is subjected to a defined monitoring cycle:
- **Alert Rate Targets:** Operational target is 15%.
- **Latency Monitoring:** Target processing time is <50ms per transaction.
- **Recalibration:** Thresholds and weights are reviewed every 6 months (see Section 7).

---

## 4. Outcomes Analysis (Back-testing)
Outcomes analysis is performed by running a 25-scenario master validation suite. The model must achieve a 100% True Positive rate for known typologies to be considered stable. Regression testing is mandatory after any logic modification.

---

## 5. Operational Controls
### 5.1 Dual-Resolution Standard (Audit Lock)
The model enforces a risk-based "Audit Lock" for alert disambiguation to prevent operational error:
*   **Screening Matches (Sanctions/PEP):** Enforces a mandatory **Three-Point Standard**. Analysts must provide three independent identifiers (e.g., DOB, Nationality, Profession) before an alert can be marked as CLEARED or FALSE_POSITIVE.
*   **Transaction Risk (Behavioral):** Enforces a **Mandatory Rationale Standard**. High-CRS alerts require a detailed investigative write-up before closure, ensuring human review of the behavioural patterns.

### 5.2 STR Workflow
A formal STR (Suspicious Transaction Report) workflow is integrated. High-risk mule clusters require a documented filing decision, capturing the FIU-IND reference within the audit trail.

---

## 6. Recalibration Schedule
- **Quarterly:** Review of geographic risk tiers based on FATF/OFAC updates.
- **Bi-Annually:** Full review of module weights and universal alert thresholds.
- **Event-Driven:** Immediate review upon emergence of new regulatory typologies or material performance drift.

---

## 7. Independent Validation Sign-off
This model has undergone independent validation (documented in `INDEPENDENT_VALIDATION.md`). The logic, implementation, and controls have been certified as production-ready.

**Validator:** Atul Krishnan, CAMS
**Date:** 22 May 2026
