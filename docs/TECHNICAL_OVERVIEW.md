# TECHNICAL_OVERVIEW.md — ScoreSentinel System Explained

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.0 | **Day:** 20 of 60 | **Author:** Atul Krishnan, CAMS
**Last Updated:** 11 May 2026
**Audience:** Non-technical readers — compliance officers, hiring managers, regulators

---

## What Is ScoreSentinel?

ScoreSentinel is an automated AML transaction risk scoring engine. It takes a financial transaction as input and returns a risk score between 0 and 100 — along with a clear explanation of why that score was produced.

A score of 60 or above generates an alert for analyst review. A score below 60 is monitored but does not require immediate action.

Every score is fully explainable. There is no black box. Any compliance officer can look at a ScoreSentinel output and explain exactly why a transaction scored what it did — down to the specific rules that fired.

---

## The Problem ScoreSentinel Solves

Traditional transaction monitoring has two failure modes:

**Too many alerts** — the system flags everything, analysts spend all day clearing noise, and genuine money laundering hides in the queue.

**Too few alerts** — the system misses sophisticated typologies because it only looks at one factor at a time (just amount, or just geography) rather than combining multiple risk signals.

ScoreSentinel solves both by combining four independent risk dimensions into a single weighted score — so a $500 wire to Iran alerts (sanctions exposure) but a $500 wire between two verified UK individuals does not (clean profile, domestic, low-risk type).

---

## How It Works — Plain English

### Step 1 — A Transaction Arrives

Any financial transaction can be scored — a cash deposit, an international wire, a cryptocurrency purchase, an insurance premium payment. The transaction includes basic information: the amount, the type, which countries are involved, and who the customer is.

### Step 2 — Four Independent Risk Checks Run

ScoreSentinel assesses the transaction across four dimensions simultaneously:

**Who is the customer?**
Is this a verified individual with a clean history? A newly incorporated shell company with unknown owners? A Politically Exposed Person with links to a foreign government? The customer profile contributes 30% of the final score — the single most important factor.

**Is there a suspicious pattern?**
Is this one normal transaction — or is it the fifth cash deposit just below the $10,000 reporting threshold in ten days? ScoreSentinel looks for structuring patterns, velocity anomalies, and behavioural changes. This contributes 25% of the final score.

**Where are the funds going?**
Is the sender in a FATF grey-listed country? Is the receiver in a known offshore secrecy jurisdiction? Is either country subject to OFAC sanctions? Geography contributes 25% — applied to both the sending and receiving country.

**What type of transaction is it?**
A cryptocurrency transaction carries more inherent risk than a loan repayment. A correspondent banking payment carries more risk than a domestic wire. The transaction mechanism contributes 20% of the final score.

### Step 3 — Scores Are Normalised and Combined

Each of the four checks produces a raw score on a different scale. To combine them fairly, each score is converted to a percentage (0–100%) before the weighted combination is applied. This ensures the customer risk check (which can reach 175 raw points) does not mathematically overwhelm the transaction type check (which reaches 55 raw points).

```
Final Score = (Customer % × 30%) + (Structuring % × 25%)
            + (Geography % × 25%) + (Transaction Type % × 20%)
```

### Step 4 — Hard Rules Fire First

Before the composite score is calculated, three types of transaction trigger an immediate alert regardless of score:

- Any transaction involving an OFAC-sanctioned country (Iran, Russia, North Korea, and others) — a $1 transfer to Iran is as illegal as a $1 million transfer
- Any transaction involving a confirmed Tier 1 Politically Exposed Person — heads of state, cabinet ministers, royalty
- Any structuring pattern scoring above 75% — deliberate fragmentation of transactions to avoid detection thresholds

These are not scoring decisions. They are absolute rules.

### Step 5 — The Result Is Returned and Stored

The system returns the composite score, the risk band, whether an alert was generated, and the specific rules that fired. Everything is written to a permanent audit log — who scored it, when, what rules fired, and what the analyst decided.

---

## What the Numbers Mean

| Score | Risk Band | What Happens |
|---|---|---|
| 0–20 | Low Risk | Standard automated monitoring |
| 21–40 | Medium-Low | Logged — no analyst action needed |
| 41–59 | Medium-High | Enhanced monitoring — analyst reviews at next cycle |
| 60–79 | High Risk | Alert generated — analyst reviews within 5 days |
| 80–100 | Very High Risk | Alert generated — senior escalation required |
| AUTO | Sanctions / PEP | Immediate escalation — bypasses score entirely |

---

## Real Example — Pakistani Trade Payment

A Nepali textile manufacturer sends $180,000 to a UK fabric supplier for a confirmed export order.

```
Customer check:     Non-resident business — score 35/175 = 20%
Structuring check:  Single consistent payment — score 0/70 = 0%
Geography check:    Nepal FATF grey list — score 45/100 = 45%
Transaction check:  International wire — score 45/55 = 82%

Final score = (20×30%) + (0×25%) + (45×25%) + (82×20%)
            = 6 + 0 + 11.25 + 16.4
            = 33.65 — MEDIUM-LOW
```

Nepal's FATF grey list status correctly adds risk weight. But the combination of an established business, a single transaction, and full trade documentation keeps the score below the alert threshold. The system flags it for enhanced monitoring — but does not block it or generate an analyst alert.

This is the correct outcome. A legitimate Nepali trade payment should not be blocked — but it should be monitored more closely than a domestic UK transfer.

---

## Real Example — Viktor Vekselberg / Renova Group

A transaction involves Renova Group — a Russian holding company whose controlling shareholder, Viktor Vekselberg, is on the OFAC SDN sanctions list.

```
Customer check:     Shell company + sanctioned BO — score 125/175 = 71%
Structuring check:  Single transaction — score 0/70 = 0%
Geography check:    Russia — OFAC sanctioned Tier 1B — score 100/100 = 100%
Transaction check:  International wire — score 45/55 = 82%

Final score = (71×30%) + (0×25%) + (100×25%) + (82×20%)
            = 21.3 + 0 + 25 + 16.4
            = 62.7 — HIGH RISK

PLUS: OFAC 50% ownership rule fires → AUTO-ALERT
PLUS: Russia Tier 1B → AUTO-ALERT
PLUS: Vekselberg name match → SANCTIONS ALERT
```

Three independent auto-alerts fire simultaneously. The transaction is blocked and escalated to the Compliance Officer immediately — regardless of the composite score.

---

## The Four Components That Power ScoreSentinel

### The Scoring Engine (Python)
The brain of the system. Written in Python — a free, open-source programming language used by banks, hedge funds, and technology companies globally. The engine implements every rule documented in the AML rule files. It is fast enough to score thousands of transactions per second.

### The API (Flask)
The door. Flask is a lightweight web framework that allows any external system to send transactions to ScoreSentinel and receive scores back. It receives transactions, passes them to the scoring engine, stores results, and returns the output. All communication goes through the API — nothing bypasses it.

### The Database (PostgreSQL)
The memory. PostgreSQL is a free, enterprise-grade database used by major financial institutions globally. It stores every transaction score, every alert, every analyst decision, and every audit log entry permanently. This is what a regulator sees when they ask for the audit trail.

### The Dashboard (React)
The face. React is a web application framework that powers the analyst interface. It shows the alert queue, transaction details, score breakdowns, and case management workflow. The dashboard was designed based on operational experience in a Tier 1 bank financial crime screening team — reflecting how analysts actually work, not how developers think they work.

---

## The Case Management Workflow

ScoreSentinel's dashboard reflects a real compliance operations workflow — not a generic alert list. Every case moves through four defined stages:

**Stage 1 — Pending Assessment**
The alert has been generated. No analyst has reviewed it yet.

**Stage 2 — Pending Action**
The analyst has reviewed and made a decision — but is waiting on something external. For example, waiting for the client's Relationship Manager to provide documents, or waiting for a response from the client.

**Stage 3 — Sent for Review**
The case has been escalated. It may go to Sales / Relationship Management (for client contact), GFC (Global Financial Crimes — for complex cases), Internal Review (for second reviewer sign-off), or the MLRO (for SAR filing decisions).

**Stage 4 — Resolved / Completed**
The case is closed. The outcome is recorded — false positive cleared, EDD completed, SAR filed, or enhanced monitoring applied.

Every stage transition is time-stamped. Every decision is documented. The audit trail is complete.

---

## Why Rules-Based and Not Machine Learning?

ScoreSentinel deliberately uses documented rules rather than machine learning algorithms. This is a design choice, not a technical limitation.

Machine learning models can be more sophisticated in detecting patterns — but they create three problems for AML compliance:

**Explainability.** A regulator asks: "Why did you flag this transaction?" A rules-based engine answers: "Because it was a cash deposit from a FATF grey-listed country by a newly onboarded customer — three independent risk factors." A machine learning model answers: "Because the algorithm weighted these 47 features in this combination." The first answer satisfies a regulator. The second requires additional validation work.

**Auditability.** SR 11-7 — the Federal Reserve's model risk management standard — requires that every model output be traceable to documented logic. Rules-based engines provide this by design. ML models require additional explainability tools.

**Manipulation risk.** A sophisticated money launderer who understands a rules-based threshold can attempt to engineer around it — but they know exactly what they are doing. A launderer attempting to engineer around an ML model's hidden weights is operating blind. However, the compliance team is also operating with less clarity — which creates regulatory risk.

ScoreSentinel's rules-based design means any analyst, any auditor, and any regulator can follow the reasoning from transaction to score to decision — without specialist data science knowledge.

---

## Regulatory Alignment

ScoreSentinel was designed against the following regulatory frameworks:

| Framework | What It Covers in ScoreSentinel |
|---|---|
| SR 11-7 | Every threshold justified, every weight documented, false positive targets set, recalibration scheduled |
| FATF Recommendations 1, 10, 12, 16, 19 | Risk-based approach, CDD, PEP screening, wire transfers, high-risk countries |
| UK MLR 2017 | Domestic PEP inclusion, 25% beneficial owner threshold, EDD requirements |
| OFAC Sanctions | SDN screening, 50% ownership rule, 40–50% enhanced monitoring zone |
| BSA/AML | CTR threshold, structuring detection, SAR workflow |
| FinCEN CDD Rule | Beneficial ownership identification, fallback BO rule |
| EU 4AMLD/6AMLD | Strictest audit standards applied as default |

---

## Deployment

ScoreSentinel is deployed on free, open-source infrastructure:

| Component | Platform | Cost |
|---|---|---|
| Scoring engine + API | Render.com | Free |
| Database | Render.com PostgreSQL | Free |
| Dashboard | Vercel.com | Free |
| Source code | GitHub | Free |

**Total infrastructure cost: £0**

The system is accessible via public URLs — any hiring manager, regulator, or interview panel can test it live without installation or credentials.

---

## Version History

| Version | Change | Date | Author |
|---|---|---|---|
| 1.0 | Initial release — Phase 1 complete. Plain English explanation of full system architecture, two worked examples, case management workflow, regulatory alignment table | 11 May 2026 | Atul Krishnan, CAMS |

---

*ScoreSentinel | TECHNICAL_OVERVIEW.md | System Explained for Non-Technical Readers | Authored by Atul Krishnan, CAMS | Version 1.0 | Day 20 of 60 | 11 May 2026*
