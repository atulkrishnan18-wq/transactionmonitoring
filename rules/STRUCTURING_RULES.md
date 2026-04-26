# STRUCTURING_RULES.md
# ScoreSentinel — Structuring Detection Rules
# Author: Atul Krishnan | Day 2

---

## What is Structuring?
Deliberately breaking large transactions into smaller ones 
to avoid the $10,000 CTR reporting threshold under the 
Bank Secrecy Act (FinCEN).

---

## Rule 1 — Classic Smurfing
**Pattern:** Multiple transactions just below $10,000

Trigger conditions:
- 3 or more transactions between $8,000–$9,999
- Within a 7-day window
- By the same customer

Risk Score: HIGH (weight = 3)

Example:
$9,900 + $9,800 + $9,500 within 5 days = FLAG

---

## Rule 2 — Velocity Structuring
**Pattern:** Sudden spike in transaction frequency

Trigger conditions:
- Customer average is ≤ 2 transactions/week
- Suddenly performs 5+ transactions within 72 hours
- Regardless of amount

Risk Score: MEDIUM (weight = 2)

Example:
Normally quiet account → 7 transactions in 3 days = FLAG

---

## Rule 3 — Round Number Avoidance
**Pattern:** Transactions suspiciously close to $10,000

Trigger conditions:
- Any transaction between $9,500–$9,999
- More than once in a 30-day window
- Same customer

Risk Score: MEDIUM (weight = 2)

Example:
$9,999 on Day 1 + $9,875 on Day 14 = FLAG

---

## Rule 4 — Micro-Structuring (Most Dangerous)
**Pattern:** Many small deposits adding up to large total

Trigger conditions:
- 10+ transactions all under $3,000 each
- Total sum exceeds $30,000 within 30 days
- Same customer, no business justification

Risk Score: CRITICAL (weight = 4)

Example:
30 × $1,000–$2,000 deposits = $45,000 total = IMMEDIATE FLAG

---

## Rule 5 — Multiple Account Structuring
**Pattern:** Same beneficial owner, different accounts

Trigger conditions:
- 2+ accounts linked to same customer/entity
- Each account receives $8,000–$9,999
- On the same day or within 48 hours

Risk Score: CRITICAL (weight = 4)

Example:
Account A: $9,500 + Account B: $9,500 same day = FLAG

---

---

## Segmented Structuring Thresholds (Tier 1 RBA)

Structuring detection is more effective when thresholds are calibrated by `Customer Segment`.

| Segment | Rule 1 (Smurfing) Threshold | Rule 4 (Micro) Threshold | Rationale |
|---|---|---|---|
| **Institutional** | $50,000+ | $500,000+ aggregate | High volume is normal |
| **Retail** | $8,000+ | $10,000+ aggregate | Individual limit focus |
| **SMB** | $25,000+ | $100,000+ aggregate | Cash intensity context |

---

## Data Integrity Penalty (Structuring Context)

Missing metadata during a structuring pattern is a high-conviction indicator of intent to evade.

| Missing Metadata | Penalty Score |
|---|---|
| Missing "Source of Funds" on $8k+ cash | +20 |
| Missing "Relationship to Counterparty" | +15 |
| Generic "Business Payment" description | +10 |

---

## Composite Structuring Score

| Rule Triggered        | Score |
|-----------------------|-------|
| Rule 1 — Smurfing     | 15    |
| Rule 2 — Velocity     | 10    |
| Rule 3 — Round number | 10    |
| Rule 4 — Micro        | 40    |
| Rule 5 — Multi-acct   | 40    |

If ANY Rule 4 or Rule 5 triggers → Immediate escalation
regardless of composite score.

---

## What ScoreSentinel Will Do
- Group all transactions by Customer ID
- Apply a rolling 30-day window
- Check all 5 rules simultaneously
- Output a structuring risk flag per customer
- Store result in SQL with timestamp for audit

---

## Governance Notes
- Rules reviewed quarterly
- Thresholds adjustable without code changes
- All flags require human review before SAR filing
- False positive rate target: < 15%
