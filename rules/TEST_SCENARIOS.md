# TEST_SCENARIOS.md — Validation Scenarios

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.0 | **Day:** 8 of 60 | **Author:** Atul Krishnan, CAMS
**Last Updated:** 27 April 2026

---

## 1. Purpose of Testing

To ensure the weighted scoring logic defined in `COMPOSITE_LOGIC.md` and `AML_RULES.md` produces accurate, defensible, and explainable risk scores. These 10 scenarios cover the full spectrum of risk—from low-risk retail behavior to high-conviction money laundering patterns.

---

## 2. The Scenarios

### Scenario 1: The Clean Salary Earner
*   **Customer:** Verified Individual, salaried (5/175).
*   **Transaction:** Domestic Salary Credit, $4,500 (0/55).
*   **Geography:** Domestic (0/100).
*   **Structuring:** None (0/70).
*   **Calculation:** 
    *   Weighted: (2.8% * 0.3) + (0% * 0.25) + (0% * 0.25) + (0% * 0.2) = **0.84%**
*   **Disposition:** **LOW RISK** (No Alert)

### Scenario 2: The Shell Company International Wire
*   **Customer:** Shell Company with unknown UBO (50/175).
*   **Transaction:** International Wire, $45,000 (45/55).
*   **Geography:** Cayman Islands Receiver (40/100).
*   **Structuring:** Single high-value transaction (0/70).
*   **Calculation:** 
    *   Weighted: (28.5% * 0.3) + (0% * 0.25) + (40% * 0.25) + (81.8% * 0.2) = **34.9%**
*   **Disposition:** **MEDIUM-LOW** (Enhanced Monitoring)

### Scenario 3: Classic "Smurfing" (Structuring)
*   **Customer:** Retail Individual, newly onboarded (30/175).
*   **Transaction:** 4 Cash Deposits of $9,500 within 5 days.
*   **Geography:** Domestic (0/100).
*   **Structuring:** Rule 1 Triggered - High (50/70).
*   **Calculation:** 
    *   Weighted: (17.1% * 0.3) + (71.4% * 0.25) + (0% * 0.25) + (54.5% * 0.2) = **33.9%**
    *   *Note: While CRS is lower, the Structuring Module independently flags for review.*
*   **Disposition:** **HIGH RISK** (Alert Generated via Rule Trigger)

### Scenario 4: The Sanctions "Auto-Alert"
*   **Customer:** SMB Entity (20/175).
*   **Transaction:** Export Payment, $12,000 (15/55).
*   **Geography:** **Iran** Involvement (Tier 1A).
*   **Disposition:** **AUTO-ALERT** (Hard-Stop: Sanctions)

### Scenario 5: High-Frequency Crypto Activity
*   **Customer:** Crypto-Asset Business (40/175).
*   **Transaction:** 5 Crypto transfers in 24 hours (55/55).
*   **Geography:** Domestic (0/100).
*   **Structuring:** Velocity spike triggered (40/70).
*   **Calculation:** 
    *   Weighted: (22.8% * 0.3) + (57.1% * 0.25) + (0% * 0.25) + (100% * 0.2) = **41.1%**
*   **Disposition:** **MEDIUM-HIGH** (System Alert for Pattern)

### Scenario 6: The PEP Luxury Purchase
*   **Customer:** Tier 2 PEP (35/175).
*   **Transaction:** High-value International Wire, $250,000 (45/55).
*   **Geography:** Switzerland (High-risk for secrecy) (20/100).
*   **Structuring:** None (0/70).
*   **Calculation:** 
    *   Weighted: (20% * 0.3) + (0% * 0.25) + (20% * 0.25) + (81.8% * 0.2) = **27.3%**
*   **Disposition:** **MEDIUM-LOW** (Standard EDD review due to PEP status)

### Scenario 7: FATF Grey List Corridor
*   **Customer:** Established Business, 5 years (10/175).
*   **Transaction:** Correspondent Banking (50/55).
*   **Geography:** Nigeria to South Africa (Tier 1C) (25/100).
*   **Structuring:** None (0/70).
*   **Calculation:** 
    *   Weighted: (5.7% * 0.3) + (0% * 0.25) + (25% * 0.25) + (90.9% * 0.2) = **26.1%**
*   **Disposition:** **MEDIUM-LOW**

### Scenario 8: Cash-Intensive SMB Micro-Structuring
*   **Customer:** Restaurant (Cash-Intensive) (45/175).
*   **Transaction:** 15 Cash deposits of $2,000 in 30 days.
*   **Structuring:** Rule 4 (Micro-structuring) - Critical (70/70).
*   **Geography:** Domestic (0/100).
*   **Transaction:** Cash (30/55).
*   **Calculation:** 
    *   Weighted: (25.7% * 0.3) + (100% * 0.25) + (0% * 0.25) + (54.5% * 0.2) = **43.6%**
*   **Disposition:** **MEDIUM-HIGH** (Review for Structuring Pattern)

### Scenario 9: High-Risk Combination (The "SAR Generator")
*   **Customer:** Shell Company (50/175).
*   **Transaction:** International Wire (45/55).
*   **Geography:** Nigeria (Tier 1C) to BVI (Tax Haven) (25+40=65/100).
*   **Structuring:** Smurfing detected (50/70).
*   **Calculation:** 
    *   Weighted: (28.5% * 0.3) + (71.4% * 0.25) + (65% * 0.25) + (81.8% * 0.2) = **59.0%**
*   **Disposition:** **HIGH RISK** (Borderline Alert + Multi-factor trigger)

### Scenario 10: Missing Data Penalty (DIP)
*   **Customer:** HNW Individual (25/175).
*   **Transaction:** Int'l Wire with **Missing UBO** (45 + 25 penalty = 70/55*).
*   **Geography:** Domestic (0/100).
*   **Structuring:** None (0/70).
*   **Calculation:** 
    *   Weighted: (14.2% * 0.3) + (0% * 0.25) + (0% * 0.25) + (127%* * 0.2) = **29.7%**
*   **Disposition:** **MEDIUM-LOW** (System flag for missing data)

---
*Note: Scenarios designed for manual logic validation before Python implementation.*
