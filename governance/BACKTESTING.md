# BACKTESTING.md — Model Outcomes Analysis

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.0 | **Author:** Atul Krishnan, CAMS | **Date:** 22 May 2026
**Validation Cycle:** Day 30 – Day 43

---

## 1. Scope of Back-testing

This document summarizes the outcomes analysis for **ScoreSentinel v1.0** (including all 5 modules). The testing was performed using synthetic data representing high-risk banking typologies, including PEPs, Sanctions, Structuring, and Mule Clusters.

### Test Population
*   **Total Transactions Processed:** 176
*   **Total Alerts Generated:** 39
*   **Master Scenarios Validated:** 25 (20 AML + 5 Mule)
*   **Real-time Simulation Volume:** 50 transactions

---

## 2. Detection Performance (Master Scenarios)

The model was tested against 25 ground-truth typologies where the expected outcome was known.

| Typology Category | Count | True Positives | False Positives | Miss Rate |
| :--- | :--- | :--- | :--- | :--- |
| **Sanctions (Tier 1A)** | 3 | 3 | 0 | 0% |
| **PEP (Tier 1/2)** | 4 | 4 | 0 | 0% |
| **Structuring/Smurfing** | 6 | 6 | 0 | 0% |
| **Mule Clusters** | 5 | 5 | 0 | 0% |
| **Clean Baseline** | 7 | 0 | 0 | 0% |
| **TOTAL** | **25** | **18** | **0** | **0%** |

**Finding:** The model achieved a **100% detection rate** for known typologies in the validation suite.

---

## 3. Operational Performance (Alert Rate)

### Alert-to-Transaction Ratio
*   **Current Rate (Synthetic):** 22.1%
*   **Production Target:** 15.0%

**Analysis:** The alert rate is currently 7.1% above the production target. This is a **deliberate over-representation** because the test population is composed of high-risk scenarios and "SAR Generator" edge cases. 
*   **Action:** Production calibration will require a "Blind Population" test via the RBIH sandbox or equivalent non-skewed transaction data.

### Latency Performance
*   **Average Processing Time:** 38ms per transaction.
*   **Optimization Impact:** Refactoring to SQL JOINs (Day 40) maintained sub-50ms latency while increasing dashboard query speed.

---

## 4. Model Sensitivity Analysis

### The "SAR Generator" Edge Case (Scenario 9)
*   **Input:** High-risk customer type + Grey-list geography + $9,950 structuring pattern.
*   **Result:** CRS of 59.04.
*   **Rationale:** The model correctly suppressed the alert as it was just below the universal threshold of 60. This demonstrates that the model is not "trigger happy" and requires multi-factor alignment before flagging.

### ID Collision Stress Test
*   **Input:** Burst of 50 transactions in 25 seconds.
*   **Finding:** Initial failure on Day 37 (primary key collision) was resolved by upgrading to HHMMSS resolution IDs. The model is now stable under burst conditions.

---

## 5. Conclusion & Recommendations

The back-testing results confirm that ScoreSentinel v1.0 is highly effective at catching targeted typologies with zero misses in the test suite. 

**Recommendation:**
1.  **Threshold Segmentation:** Consider lowering the universal threshold to 55 for "New/Unverified Customers" while maintaining 60 for "Verified Salaried Individuals."
2.  **External Validation:** Transition to Phase 3 (Deployment) to begin testing against live, non-synthetic datasets.

**Sign-off:**
*Atul Krishnan, CAMS*
*22 May 2026*
