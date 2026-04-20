# TEST SCENARIOS

Based on your Risk Matrix, these are the test cases to validate the scoring engine.

## Scenario 1: Low Risk Transaction
Customer: CUST126
Amount: $5,000
Geography: United States
Customer Type: Verified Individual (>2 years)
Transaction Type: Domestic Wire Transfer
Frequency: 1 transaction/week
PEP Status: No
Sanctions: No match
Watchlist: No match

Expected Scoring:
- Amount ($5k): Score 1 × Weight 3 = 3
- Frequency (1/week): Score 1 × Weight 2 = 2
- Geography (US): Score 1 × Weight 3 = 3
- Customer (Verified): Score 1 × Weight 3 = 3
- Product (Domestic Wire): Score 2 × Weight 2 = 4
- Sanctions: No match = 0 × Weight 4 = 0
- Watchlist: No match = 0 × Weight 3 = 0
- CPI (US - top 50): Score 2 × Weight 1 = 2

TOTAL COMPOSITE SCORE: 17 = LOW RISK ✓
Action: Monitor routine, Quarterly review

---

## Scenario 2: Medium Risk Transaction
Customer: CUST089
Amount: $45,000
Geography: Mexico
Customer Type: New Customer (<30 days)
Transaction Type: International Wire Transfer
Frequency: 3 transactions/week
PEP Status: No
Sanctions: No match
Watchlist: No match

Expected Scoring:
- Amount ($45k): Score 3 × Weight 3 = 9
- Frequency (3/week): Score 2 × Weight 2 = 4
- Geography (Mexico - Medium Risk): Score 3 × Weight 3 = 9
- Customer (New): Score 4 × Weight 3 = 12
- Product (Int'l Wire): Score 4 × Weight 2 = 8
- Sanctions: No match = 0 × Weight 4 = 0
- Watchlist: No match = 0 × Weight 3 = 0
- CPI (Mexico - outside top 50): Score 6 × Weight 2 = 12

TOTAL COMPOSITE SCORE: 54 = MEDIUM RISK ✓
Action: Enhanced due diligence, Monthly review

---

## Scenario 3: High Risk - Multiple Factors
Customer: CUST091
Amount: $250,000
Geography: Kenya
Customer Type: New Customer (<30 days)
Transaction Type: Correspondent Banking
Frequency: 7 transactions in 24 hours
PEP Status: No
Sanctions: No match
Watchlist: No match

Expected Scoring:
- Amount ($250k): Score 5 × Weight 3 = 15
- Frequency (7/day): Score 4 × Weight 2 = 8
- Geography (Kenya - Medium/High): Score 3 × Weight 3 = 9
- Customer (New): Score 4 × Weight 3 = 12
- Product (Correspondent): Score 5 × Weight 2 = 10
- Sanctions: No match = 0 × Weight 4 = 0
- Watchlist: No match = 0 × Weight 3 = 0
- CPI (Kenya - outside top 50): Score 6 × Weight 2 = 12

TOTAL COMPOSITE SCORE: 66 = MEDIUM-HIGH RISK (approaching HIGH)
Structuring Detection: 7 transactions in 24hrs = Flag + 2x multiplier
ADJUSTED SCORE: 66 × 2 = 132 = HIGH RISK ✓
Action: Immediate escalation + investigation

---

## Scenario 4: CRITICAL - PEP + Sanctions Match
Customer: CUST078 (VIP Client - under investigation)
Amount: $500,000
Geography: Yemen
Customer Type: PEP (Politically Exposed Person)
Transaction Type: Correspondent Banking
Frequency: 1 transaction
PEP Status: YES - Flagged
Sanctions: MATCH with OFAC list
Watchlist: MATCH with iOCAL

Expected Scoring:
- Amount ($500k): Score 5 × Weight 3 = 15
- Frequency (1 transaction): Score 1 × Weight 2 = 2
- Geography (Yemen - High Risk): Score 6 × Weight 3 = 18
- Customer (PEP): Score 7 × Weight 3 = 21
- Product (Correspondent): Score 5 × Weight 2 = 10
- Sanctions: MATCH = 10 × Weight 4 = 40 ⚠️ CRITICAL
- Watchlist: MATCH = 7 × Weight 3 = 21
- CPI (Yemen - outside top 50): Score 6 × Weight 2 = 12

TOTAL COMPOSITE SCORE: 139 = CRITICAL RISK ✓✓✓
Sanctions Match = AUTOMATIC ESCALATION
Action: BLOCK transaction immediately + Report to OFAC + Management escalation

---

## Scenario 5: Structuring Detection
Customer: CUST087
Amount: 5 transactions of $15,000 each
Geography: United States
Customer Type: Verified Individual
Transaction Type: Domestic Wire Transfer
Frequency: All within 24-hour period
PEP Status: No
Sanctions: No match
Watchlist: No match

Expected Scoring (Per transaction):
- Amount ($15k): Score 2 × Weight 3 = 6
- Frequency (1): Score 1 × Weight 2 = 2
- Geography (US): Score 1 × Weight 3 = 3
- Customer (Verified): Score 1 × Weight 3 = 3
- Product (Domestic): Score 2 × Weight 2 = 4
- Others: 0

Base Score per transaction: 18

Structuring Detection Applied:
- Rule: 5+ transactions in 24 hours = Structuring flag
- Multiplier: 2x
- Applied Score: 18 × 2 = 36 = MEDIUM RISK ✓

Pattern detected: STRUCTURING
Action: Flag customer, Enhanced monitoring, Manual review required

---

## Scenario 6: Velocity Anomaly
Customer: CUST156
Normal Pattern: 2-3 transactions/week over 6 months
Sudden Change: 20 transactions in one day
Amount per transaction: $8,000 each
Total: $160,000 in one day

Expected Scoring:
Base calculation for one transaction: 15-20 points
Velocity anomaly detected: 10x increase from normal
Additional penalty: +5 points

Combined Score: 35+ = HIGH RISK ✓
Action: Flag for investigation, Check for structuring or layering

---

## Scenario 7: False Positive Check - Legitimate Business
Customer: CUST205 (Registered Exporter)
Amount: $120,000
Geography: Singapore
Customer Type: Verified Business (5+ years)
Transaction Type: Trade Finance
Frequency: 8 transactions/week (normal for exporter)
PEP Status: No
Sanctions: No match
Watchlist: No match

Expected Scoring:
- Amount ($120k): Score 5 × Weight 3 = 15
- Frequency (8/week): Score 2 × Weight 2 = 4 (normal for business)
- Geography (Singapore - Low Risk): Score 1 × Weight 3 = 3
- Customer (Verified Business): Score 1 × Weight 3 = 3
- Product (Trade Finance): Score 3 × Weight 2 = 6
- Sanctions: No match = 0
- Watchlist: No match = 0
- CPI (Singapore - top 50): Score 2 × Weight 1 = 2

TOTAL COMPOSITE SCORE: 33 = MEDIUM RISK
Assessment: FALSE POSITIVE - Business is legitimate
Reason: High frequency is NORMAL for exporter; geography low-risk; verified customer
Action: Monitor routine, No escalation needed

---

## Scenario 8: Beneficial Owner Risk
Customer: CUST301 (Shell Company)
Amount: $75,000
Geography: British Virgin Islands (Offshore)
Customer Type: High-risk entity (shell company registration)
Beneficial Owner: Unknown/Hidden
Transaction Type: Wire Transfer (International)
PEP Status: Beneficial owner flagged as PEP
Sanctions: No direct match (but BO may be sanctioned)
Watchlist: No match

Expected Scoring:
- Amount ($75k): Score 4 × Weight 3 = 12
- Frequency (1): Score 1 × Weight 2 = 2
- Geography (BVI - Offshore): Score 4 × Weight 3 = 12
- Customer (Shell Company): Score 5 × Weight 3 = 15
- Beneficial Owner (PEP): Additional +7 = 7
- Product (Int'l Wire): Score 4 × Weight 2 = 8
- Sanctions: Potential = Add +5
- Watchlist: No match = 0
- CPI (BVI - outside top 50): Score 6 × Weight 2 = 12

TOTAL COMPOSITE SCORE: 68+ = MEDIUM-HIGH RISK ✓
Action: Enhanced due diligence, Verify beneficial owner, Check OFAC list for BO

---

## Scenario 9: Geographic Compliance
Customer: CUST410
Amount: $30,000
Geography: Iran
Transaction Type: Import/Export related
PEP Status: No
Sanctions: No direct match (yet)
Watchlist: No match

Expected Scoring:
- Amount ($30k): Score 2 × Weight 3 = 6
- Geography (Iran - FATF high-risk): Score 6 × Weight 3 = 18
- Customer (New): Score 4 × Weight 3 = 12
- Product (Int'l): Score 4 × Weight 2 = 8
- CPI (Iran): Score 6 × Weight 2 = 12

TOTAL COMPOSITE SCORE: 56 = MEDIUM RISK (due to geography)
Governance Note: Iran on FATF list = Extra scrutiny required
Action: Enhanced due diligence, Verify legitimate business purpose

---

## Scenario 10: Composite Score Edge Case (Just Below Thresholds)
Customer: CUST520
Amount: $22,000
Geography: Poland (EU - Low Risk)
Customer Type: Verified Individual (3 years)
Transaction Type: Wire Transfer (International)
Frequency: 2/week
PEP Status: No
Sanctions: No match
Watchlist: No match

Expected Scoring:
- Amount ($22k): Score 2 × Weight 3 = 6
- Frequency (2/week): Score 1 × Weight 2 = 2
- Geography (Poland - Low): Score 1 × Weight 3 = 3
- Customer (Verified): Score 1 × Weight 3 = 3
- Product (Int'l Wire): Score 4 × Weight 2 = 8
- Sanctions: No = 0
- Watchlist: No = 0
- CPI (Poland - top 50): Score 2 × Weight 1 = 2

TOTAL COMPOSITE SCORE: 24 = LOW RISK ✓
Just below medium threshold (30)
Action: Monitor routine, Quarterly review
Note: This shows system sensitivity is appropriate

---

## Test Validation Checklist

All 10 scenarios should pass:
- [ ] Scenario 1: LOW RISK (Score 17)
- [ ] Scenario 2: MEDIUM RISK (Score 54)
- [ ] Scenario 3: HIGH RISK with Structuring (Score 132)
- [ ] Scenario 4: CRITICAL - Sanctions Match (Score 139, BLOCK)
- [ ] Scenario 5: Structuring Detection (Score 36)
- [ ] Scenario 6: Velocity Anomaly (Score 35+)
- [ ] Scenario 7: FALSE POSITIVE Check (Score 33, No escalation)
- [ ] Scenario 8: Beneficial Owner Risk (Score 68+)
- [ ] Scenario 9: Geographic Compliance (Score 56)
- [ ] Scenario 10: Edge Case (Score 24)

Success Criteria:
✓ All scenarios score within expected ranges
✓ CRITICAL transactions (Sanctions) auto-block
✓ HIGH RISK transactions escalate automatically
✓ False positives are correctly identified
✓ System handles combinations properly
