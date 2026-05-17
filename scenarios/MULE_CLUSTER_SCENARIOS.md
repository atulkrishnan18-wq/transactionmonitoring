# MULE_CLUSTER_SCENARIOS.md — Coordinated Network Testing

**ScoreSentinel: Project MuleCatcher Validation**
**Version:** 1.0 | **Focus:** RBI Money Mule Typologies

---

## Scenario 26: The "Jan Dhan" Rapid Drain (MUL-001)
*   **Target:** Low-income accounts used as pass-throughs.
*   **Pattern:** ₹50,000 credit followed by 99% debit within 45 minutes.
*   **Expected Result:** MPS: 35+ | Alert: Potential pass-through mule.

## Scenario 27: The Student "Fan-In" Nexus (MUL-002 + MUL-005)
*   **Target:** Educational clusters (Hostels/Colleges).
*   **Pattern:** 6 unique senders send ₹5,000 each to a "Student" profile. Total turnover ₹30,000 in 6 hours.
*   **Expected Result:** MPS: 40+ | Alert: Multi-sender recruitment pattern.

## Scenario 28: The Dormant Account "Buy-Out" (MUL-003)
*   **Target:** Stolen/Purchased inactive accounts.
*   **Pattern:** Account inactive for 180 days suddenly receives ₹2,50,000 via UPI.
*   **Expected Result:** MPS: 20+ (Combined with CRS) | Alert: High-risk behavioural shift.

## Scenario 29: The Micro-Test "Probe" (MUL-006)
*   **Target:** Fraudsters testing if an account is flagged.
*   **Pattern:** ₹1.00 credit test, followed by ₹85,000 transfer within 10 minutes.
*   **Expected Result:** MPS: 10+ | Alert: Coordinated probe-and-burst signal.

## Scenario 30: The High-Confidence Cluster (MuleCatcher™ Final Boss)
*   **Target:** Coordinated Professional Mule Herding.
*   **Pattern:** 
    *   Occupation: "Farmer"
    *   Recent micro-test (₹5.00)
    *   7 unique senders (Fan-In)
    *   98% funds drained within 1 hour.
*   **Expected Result:** **MPS: 80+ | CRITICAL ALERT | Immediate Block.**

---
*ScoreSentinel | MULE_CLUSTER_SCENARIOS.md | Version 1.0*
