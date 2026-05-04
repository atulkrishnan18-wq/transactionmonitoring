# STRUCTURING_SCENARIOS.md
# ScoreSentinel — Structuring Test Scenarios
# Author: Atul Krishnan | Day 2

---

## Scenario 1 — Classic Smurfing (HIGH RISK)
Customer: John D | Account: ACC001
- Day 1: $9,900 cash deposit
- Day 2: $9,800 cash deposit  
- Day 3: $9,500 cash deposit
Total: $29,200 in 3 days
Rule triggered: Rule 1 — Classic Smurfing
Expected score: HIGH

---

## Scenario 2 — Micro-Structuring (CRITICAL)
Customer: Sara M | Account: ACC002
- 25 deposits over 30 days
- Each between $1,000–$2,500
- Total: $47,500
- No business justification
Rule triggered: Rule 4 — Micro-Structuring
Expected score: CRITICAL → Immediate escalation

---

## Scenario 3 — Velocity Spike (MEDIUM RISK)
Customer: Ali K | Account: ACC003
- Normal pattern: 2 transactions/week
- Suddenly: 8 transactions in 48 hours
- Amounts: $500–$3,000 each
Rule triggered: Rule 2 — Velocity Structuring
Expected score: MEDIUM

---

## Scenario 4 — Round Number Avoidance (MEDIUM RISK)
Customer: Priya S | Account: ACC004
- Week 1: $9,999 deposit
- Week 3: $9,875 deposit
- Week 5: $9,950 deposit
Pattern: Always just under $10,000
Rule triggered: Rule 3 — Round Number Avoidance
Expected score: MEDIUM → Manual review

---

## Scenario 5 — Multiple Account Structuring (CRITICAL)
Customer: Marco T | Beneficial owner of 3 accounts
- Account A: $9,500 on Monday
- Account B: $9,400 on Monday
- Account C: $9,300 on Monday
Total: $28,200 in one day across accounts
Rule triggered: Rule 5 — Multiple Account Structuring
Expected score: CRITICAL → Immediate escalation

---

## Scenario 6 — False Positive Check (LOW RISK)
Customer: ABC Trading Co | Account: ACC006
- 15 transactions over 30 days
- Total: $85,000
- Declared business: Import/Export
- All wire transfers, no cash
- Consistent with historical pattern
Rule triggered: None
Expected score: LOW — legitimate business activity
