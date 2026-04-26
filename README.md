# ScoreSentinel 🛡️
### Automated AML Transaction Risk Scoring Engine

Built by a compliance professional, for compliance professionals.

---

## What is ScoreSentinel?

ScoreSentinel is an automated transaction monitoring engine 
that evaluates customer transactions against a weighted risk 
matrix and produces a composite risk score — triggering 
escalation workflows based on criticality thresholds.

No more manual Excel scoring. No more inconsistent analyst 
judgment. Just clean, auditable, automated risk decisions.

---

## The Problem It Solves

Most mid-size banks and fintechs score AML risk manually:
- An analyst opens Excel
- Checks a customer against multiple lists
- Assigns scores based on personal judgment
- Fills in a spreadsheet
- A manager reviews it days later

This is slow, inconsistent, and unauditable at scale.
ScoreSentinel fixes that.

---

## Risk Factors Covered

| Factor | Weight |
|--------|--------|
| Transaction Amount (> $10,000) | High |
| Transaction Frequency | Medium |
| Geography (FATF high-risk) | High |
| Customer Risk Rating (PEP) | High |
| Product/Service Type | Medium |
| Sanctions Exposure (OFAC) | Critical |
| Watchlist Exposure (IOCAL) | High |
| Corruption Perceptions Index | Medium |
| Structuring Patterns | Critical |

---
---

## Tech Stack
- Python (pandas) — scoring engine
- SQL — audit trail & storage
- GitHub — version control & documentation

---

## Status
🚧 Active development — Day 6 of 60

---

## About the Author
CAMS-Certified Financial Crime Analyst with 8+ years in AML,
sanctions, and KYC across global banking environments.

Currently @ Bank of America | High Risk Detection Team

🌐 [Chainsutra](https://chainsutra.in) — crypto compliance blog
💼 [LinkedIn](https://linkedin.com/in/atul-krishnan-cams-aa99b535)
