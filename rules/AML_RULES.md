# AML SCORING RULES - TRANSACTION MONITORING

Based on Risk Matrix dated 03/03/2026

## RISK FACTOR 1: TRANSACTION AMOUNT
Criteria: Transaction amount threshold
Individual Score: 5 (High)
Weight: 3 (High)
Weighted Score: 15

Thresholds:
- ≤ $10,000: Score 1
- $10,001 - $25,000: Score 2
- $25,001 - $50,000: Score 3
- $50,001 - $100,000: Score 4
- > $100,000: Score 5

Governance Notes: Threshold reviewed quarterly; escalation required if threshold changes
Last Updated: 22/02/2026
Reviewed By: Atul Krishnan

---

## RISK FACTOR 2: TRANSACTION FREQUENCY
Criteria: Number of transactions per day
Individual Score: 4 (Medium-High)
Weight: 2 (Medium)
Weighted Score: 8

Thresholds:
- 1-3 transactions/week: Score 1
- 4-10 transactions/week: Score 2
- 11-20 transactions/week: Score 3
- 21-50 transactions/day: Score 4 (Flag for review)
- > 50 transactions/day: Score 5 (Critical)

Governance Notes: Reviewed annually; internal monitoring rules
Last Updated: 23/02/2026
Reviewed By: Atul Krishnan

---

## RISK FACTOR 3: GEOGRAPHY
Criteria: High-risk country per FATF list
Individual Score: 6 (Critical)
Weight: 3 (High)
Weighted Score: 18

High-Risk Countries (Score 6):
- Yemen
- Syria
- North Korea
- Iran

Medium-Risk Countries (Score 3):
- Kenya
- Mexico
- Pakistan
- Egypt

Low-Risk Countries (Score 1):
- United States
- United Kingdom
- Australia
- Canada
- Singapore

Governance Notes: Reviewed quarterly against FATF high-risk country list
Last Updated: 24/02/2026
Reviewed By: Atul Krishnan

---

## RISK FACTOR 4: CUSTOMER RISK RATING
Criteria: PEP or Politically Exposed Person
Individual Score: 7 (Critical)
Weight: 3 (High)
Weighted Score: 21

Customer Categories:
- PEP (Politically Exposed Person): Score 7
- Family member of PEP: Score 6
- Close associate of PEP: Score 5
- High-risk business (shell company): Score 5
- New customer (< 30 days): Score 4
- Verified individual (> 2 years): Score 1

Governance Notes: Reviewed semi-annually; senior compliance sign-off required
Last Updated: 25/02/2026
Reviewed By: Atul Krishnan

---

## RISK FACTOR 5: PRODUCT/SERVICE TYPE
Criteria: High-risk products (e.g., correspondent banking)
Individual Score: 5 (High)
Weight: 2 (Medium)
Weighted Score: 10

Transaction Type Scoring:
- Correspondent Banking: Score 5
- Wire Transfer (International): Score 4
- Trade Finance: Score 3
- Wire Transfer (Domestic): Score 2
- Deposit/Withdrawal: Score 1
- Loan Repayment: Score 1

Governance Notes: Reviewed semi-annually; compliance validates product mapping
Last Updated: 26/02/2026
Reviewed By: Atul Krishnan

---

## RISK FACTOR 6: SANCTIONS EXPOSURE
Criteria: Match with sanctions list (OFAC, UN, etc.)
Individual Score: 10 (CRITICAL)
Weight: 4 (Critical)
Weighted Score: 40

Action:
- ANY match with OFAC list: IMMEDIATE ESCALATION
- Score: 10 (Do Not Proceed)
- Action: Block transaction + Report to management
- Escalation: Daily

Governance Notes: If composite score = Critical, immediate escalation required
Last Updated: 27/02/2026
Reviewed By: Atul Krishnan

---

## RISK FACTOR 7: WATCHLIST EXPOSURE
Criteria: Match with iOCAL watchlists
Individual Score: 7 (High)
Weight: 3 (High)
Weighted Score: 21

Action:
- Match with iOCAL: Score 7
- Action: Manual review + escalation
- Escalation: Within 24 hours

Governance Notes: Reviewed upon each watchlist update; compliance validates mapping
Last Updated: 28/02/2026
Reviewed By: Atul Krishnan

---

## RISK FACTOR 8: CORRUPTION PERCEPTION INDEX (High Corruption)
Criteria: Country ranked outside top 50 (higher corruption)
Individual Score: 6 (High)
Weight: 2 (Medium)
Weighted Score: 12

CPI Scoring:
- Ranked outside top 50 (higher corruption): Score 6
- Ranked within top 50 (lower corruption): Score 2

Governance Notes: Updated annually using Transparency International CPI
Last Updated: 01/03/2026
Reviewed By: Atul Krishnan

---

## RISK FACTOR 9: CORRUPTION PERCEPTION INDEX (Low Corruption)
Criteria: Country ranked within top 50 (lower corruption)
Individual Score: 2 (Low)
Weight: 1 (Low)
Weighted Score: 2

CPI Scoring:
- Ranked within top 50: Score 2
- Additional safeguard: Lower risk weight applied

Governance Notes: Reviewed annually
Last Updated: 02/03/2026
Reviewed By: Atul Krishnan

---

## COMPOSITE SCORE CALCULATION

Formula:
Composite Score = Sum of all (Individual Score × Weight)

Example Transaction (from your matrix):
- Amount ($10k+): 5 × 3 = 15
- Frequency (>10/day): 4 × 2 = 8
- Geography (High-risk): 6 × 3 = 18
- Customer (PEP): 7 × 3 = 21
- Product (Correspondent): 5 × 2 = 10
- Sanctions (Match): 10 × 4 = 40
- Watchlist (Match): 7 × 3 = 21
- CPI High: 6 × 2 = 12
- CPI Low: 2 × 1 = 2

TOTAL COMPOSITE SCORE: 147

## FINAL RISK CATEGORIES

Based on Composite Score:

LOW RISK: Composite Score < 30
- Action: Monitor routine
- Review: Quarterly

MEDIUM RISK: Composite Score 30-80
- Action: Enhanced due diligence
- Review: Monthly

HIGH RISK: Composite Score 80-147+
- Action: Immediate escalation + investigation
- Review: Daily + Management approval required

CRITICAL (Sanctions Match): Automatic escalation
- Action: Block transaction immediately
- Review: Report to compliance + OFAC

---

## SPECIAL RULES & EXCEPTIONS

### Structuring Detection:
Rule: If 5+ transactions same customer in 24-hour period
- Additional Score Multiplier: 2x
- Action: Flag for structuring investigation

### PEP + High-Risk Geography + Large Amount:
Combination triggers highest alert
- Automatic escalation required
- Manual review mandatory

### Velocity Anomaly:
If transaction velocity increases 10x normal
- Flag as suspicious
- Add +5 points to composite score

---

## AUDIT & GOVERNANCE

Last Reviewed: 03/03/2026
Reviewed By: Atul Krishnan
Next Review Due: 03/04/2026 (Quarterly)
Approval Authority: Compliance Manager

Threshold Changes Require:
- Documented business rationale
- Compliance approval
- Management sign-off
- Quarterly review cycle
