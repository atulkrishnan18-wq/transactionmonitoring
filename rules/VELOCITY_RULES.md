# VELOCITY_RULES.md — Transaction Velocity & Behavioral Pattern Rules

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.0 | **Day:** 10 of 60 | **Author:** Atul Krishnan, CAMS
**Last Updated:** 30 April 2026

---

## 1. Purpose & Regulatory Basis

Velocity rules are designed to detect risk not in a single transaction, but in the **frequency and pattern** of activity over time. Rapid movement of funds is a primary indicator of layering and integration stages of money laundering. These rules supplement static amount thresholds by identifying anomalies in a customer's typical behavioral profile.

### Regulatory Basis
- **FATF Recommendation 10** — Requires ongoing monitoring of transactions to ensure they are consistent with the institution's knowledge of the customer.
- **FinCEN Advisory FIN-2010-A001** — Highlights "increased velocity of funds" as a key red flag for money laundering.
- **SR 11-7** — Mandates that behavioral thresholds must be empirically justified and regularly validated.

---

## 2. Velocity Patterns & Thresholds

ScoreSentinel categorizes transaction velocity into three distinct tiers based on frequency and time windows, with additional "Burst" detection for high-signal events.

### 2.1 Velocity Tiers

| Tier | Frequency Threshold | Risk Classification | Action |
|---|---|---|---|
| **Normal** | 1–2 transactions per week | Low Risk | Standard Monitoring |
| **Unusual** | 5+ transactions per week | Medium Risk | Flag for Pattern Analysis |
| **Suspicious** | 20+ transactions per day | High Risk | Immediate Alert / EDD Trigger |
| **The Burst** | 5+ transactions in < 30 mins | Very High Risk | Real-time Blocking / SAR Review |

---

## 3. High-Signal Patterns

Beyond simple counts, these structural patterns identify sophisticated laundering schemes.

| Pattern ID | Name | Threshold | Risk Indication |
|---|---|---|---|
| **VEL-STR-001** | **Fan-In (Mule)** | 5+ different senders to 1 receiver (24h) | Aggregating funds for consolidation/exit |
| **VEL-STR-002** | **Fan-Out (Layering)** | 1 sender to 5+ different receivers (24h) | Dispersing funds to mules for integration |
| **VEL-STR-003** | **Round Number Burst** | 80%+ round numbers in a velocity surge | Automated layering / Structured payoffs |
| **VEL-STR-004** | **Off-Hours Shift** | 10+ transactions during non-banking hours | Evasion of live compliance monitoring |

---

## 4. Behavioral Change Indicators

A "Behavioral Change" occurs when a customer's current activity deviates significantly from their established historical baseline.

| Indicator ID | Pattern Change | Risk Weight | Description |
|---|---|---|---|
| **BEH-001** | **Dormant-to-Active** | +40 | Account inactive for 90+ days suddenly processes 5+ transactions in 48 hours. |
| **BEH-002** | **Velocity Surge** | +30 | 300% increase in weekly transaction count compared to 3-month rolling average. |
| **BEH-003** | **New Corridor Activity** | +35 | Sudden high-velocity transactions to a jurisdiction with no previous history. |
| **BEH-004** | **Time-of-Day Anomaly** | +20 | High-volume transactions occurring outside of typical business hours for the segment. |
| **BEH-005** | **Rapid Round-Tripping** | +50 | Funds received and fully disbursed within a 2-hour window (Pass-through indicator). |

---

## 5. Velocity Scoring Logic (Integration)

Velocity scores are additive to the composite score.

- **Unusual Velocity (5+ weekly):** +15 to Composite Score
- **Suspicious Velocity (20+ daily):** +50 to Composite Score
- **"The Burst" (5+ in 30 mins):** +75 to Composite Score (Auto-Alert)
- **Fan-In/Fan-Out Detection:** +60 to Composite Score

---

## 6. Test Scenarios

These scenarios validate the velocity rules against expected investigative outcomes.

### Scenario 1: Retail Smurfing / The Burst
- **Activity:** 10 small P2P transfers received in 15 minutes.
- **Rule Triggered:** "The Burst" (5+ in 30 mins).
- **Result:** **VERY HIGH RISK** — Score +75.
- **Rationale:** Human behavior is rarely this rapid; indicates bot-driven smurfing or rapid consolidation.

### Scenario 2: Mule Network Consolidation (Fan-In)
- **Activity:** 8 different individuals send $1,000 to a single student account in 6 hours.
- **Rule Triggered:** Fan-In Pattern (VEL-STR-001) + Round Number Burst.
- **Result:** **HIGH RISK** — Score +60.
- **Rationale:** Textbook mule aggregation pattern for a central "exit" point.

### Scenario 3: Dormant Account Takeover
- **Activity:** Account dormant for 6 months; 10 transactions in 24 hours to high-risk GEO.
- **Rule Triggered:** Dormant-to-Active (BEH-001) + Unusual Velocity.
- **Result:** **HIGH RISK** — Score +40 + +15 = 55 (plus GEO risk additions).
- **Rationale:** Indicators of either account takeover or "mule" activation.

---

## 7. Governance & Validation

- **Recalibration:** Velocity thresholds are reviewed every 6 months to account for shifts in payment technology (e.g., faster payments adoption).
- **False Positive Target:** < 15% for velocity-triggered alerts (Veteran target).
- **Audit Trail:** Every velocity alert must capture the historical baseline and the temporal burst density used for comparison.

---
*ScoreSentinel | VELOCITY_RULES.md | Authored by Atul Krishnan, CAMS | Version 1.0 | 30 April 2026*
