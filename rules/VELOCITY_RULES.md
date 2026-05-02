# VELOCITY_RULES.md — Transaction Velocity & Behavioural Pattern Rules

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.1 | **Day:** 10 of 60 | **Author:** Atul Krishnan, CAMS
**Last Updated:** 30 April 2026

---

## Table of Contents
1. [Purpose & Regulatory Basis](#1-purpose--regulatory-basis)
2. [Architecture Integration](#2-architecture-integration)
3. [Velocity Tiers & Thresholds](#3-velocity-tiers--thresholds)
4. [High-Signal Structural Patterns](#4-high-signal-structural-patterns)
5. [Behavioural Change Indicators](#5-behavioural-change-indicators)
6. [Velocity Scoring Logic](#6-velocity-scoring-logic)
7. [Independent Velocity Alert Triggers](#7-independent-velocity-alert-triggers)
8. [Test Scenarios](#8-test-scenarios)
9. [Governance & Validation](#9-governance--validation)
10. [Version History](#10-version-history)

---

## 1. Purpose & Regulatory Basis

Velocity rules detect risk not in a single transaction but in the **frequency and pattern** of activity over time. Rapid movement of funds is a primary indicator of layering and integration stages of money laundering. These rules supplement static amount thresholds by identifying anomalies in a customer's typical behavioural profile.

A single $5,000 transfer is low risk. Twenty $5,000 transfers in one hour from a dormant account to five different jurisdictions is very high risk. The amount did not change — the pattern did. Velocity rules exist to catch the pattern.

### Regulatory Basis

- **FATF Recommendation 10** — Ongoing monitoring of transactions must ensure consistency with the institution's knowledge of the customer
- **FinCEN Advisory FIN-2010-A001** — Highlights increased velocity of funds as a key red flag for money laundering
- **BSA/AML Examination Manual** — Transaction monitoring systems must detect unusual patterns, not just unusual amounts
- **SR 11-7** — Behavioural thresholds must be empirically justified, documented, and regularly validated

---

## 2. Architecture Integration

### 2.1 How Velocity Scores Feed Into the Composite

> **Critical Design Rule:** Velocity scores are NOT added directly to the Composite Risk Score (CRS). The CRS is a normalised 0–100 score — adding raw points to it breaks normalisation and violates SR 11-7 model integrity requirements.

Velocity rules feed into the **Structuring module raw score (0–70)** which is then normalised and weighted at 25% in the CRS calculation.

```
CORRECT FLOW:

Velocity Rule Triggered
        ↓
Adds points to Structuring Module Raw Score (0–70)
        ↓
Structuring Raw Score normalised: (Raw / 70) × 100
        ↓
Normalised Structuring × 25% weight
        ↓
Contributes to CRS (0–100)
        ↓
If CRS ≥ 60 → AML Risk Alert
If Structuring normalised ≥ 75% → Independent Structuring Alert

INCORRECT (do not use):
Velocity score added directly to CRS → breaks normalisation
```

### 2.2 Relationship to Existing Velocity Rules

`TRANSACTION_RULES.md` defines VEL-001 to VEL-027 — transaction-type specific velocity rules. This document extends that framework with:

- **VEL-028 to VEL-031** — High-signal structural pattern rules (Fan-In, Fan-Out, Round Number Burst, Off-Hours)
- **BEH-001 to BEH-005** — Behavioural change indicators based on historical baseline deviation

All new rule IDs continue the existing VEL sequence to maintain audit trail consistency.

### 2.3 Structuring Module Maximum

The Structuring module maximum is **70 points**. Velocity and behavioural scores contribute to this maximum — they cannot push the raw structuring score above 70. If multiple rules fire simultaneously, scores are capped at 70 before normalisation.

```
Cap Rule:
  IF (base structuring score + velocity additions) > 70
  THEN structuring raw score = 70
  REASON: Prevents normalised score exceeding 100%
```

---

## 3. Velocity Tiers & Thresholds

ScoreSentinel categorises transaction velocity into four tiers based on frequency and time windows.

| Tier | Frequency Threshold | Risk Classification | Structuring Score Addition |
|---|---|---|---|
| **Normal** | 1–2 transactions per week | Low Risk | +0 |
| **Unusual** | 5+ transactions per week | Medium Risk | +15 |
| **Suspicious** | 20+ transactions per day | High Risk | +35 |
| **Burst** | 5+ transactions in < 30 minutes | Very High Risk | +55 — see Section 7 |

### 3.1 Threshold Justification

**Why 5+ per week = Unusual (+15)**
- Retail customers average 2–3 transactions per week in normal behaviour
- 5+ transactions represents a 150%+ deviation from typical retail baseline
- Score of +15 reflects elevated uncertainty — not confirmation of ML
- Combined with other risk factors, pushes composite toward alert threshold

**Why 20+ per day = Suspicious (+35)**
- 20 transactions in a single day represents extreme behavioural deviation for any retail or SMB customer
- Only legitimate high-volume customers (established merchants, payroll processors) should reach this level
- Score of +35 combined with customer risk alone (30+ for new customer) approaches alert threshold — requiring at least one more risk factor

**Why Burst (5+ in 30 minutes) = +55**
- Human transaction behaviour is rarely this rapid — indicates automation, bot-driven activity, or coordinated mule network
- 30-minute window chosen because it is below the typical fraud detection review cycle at most institutions — deliberate evasion of real-time monitoring
- Score of +55 pushes structuring normalised score to 78.6% (55/70) — exceeding the 75% independent trigger threshold
- This means Burst activity auto-alerts via the independent structuring trigger even if CRS is below 60

---

## 4. High-Signal Structural Patterns

These patterns identify sophisticated laundering schemes beyond simple transaction counts. All rules continue the VEL numbering sequence from TRANSACTION_RULES.md.

| Rule ID | Pattern | Threshold | Structuring Score Addition | ML Typology |
|---|---|---|---|---|
| **VEL-028** | **Fan-In (Consolidation)** | 5+ different senders → 1 receiver within 24 hours | +40 | Mule network aggregating funds before exit |
| **VEL-029** | **Fan-Out (Dispersion)** | 1 sender → 5+ different receivers within 24 hours | +40 | Layering — dispersing funds to mules for integration |
| **VEL-030** | **Round Number Burst** | 80%+ round number amounts in a velocity surge | +25 | Automated layering or structured payoffs |
| **VEL-031** | **Off-Hours Activity** | 10+ transactions during non-banking hours (22:00–06:00) | +20 | Evasion of live compliance monitoring |

### 4.1 Fan-In / Fan-Out Detailed Logic

```
VEL-028 — FAN-IN DETECTION:

IF within any 24-hour window:
  Unique sender count → single receiver ≥ 5
  AND aggregate amount > $5,000
THEN:
  → Add +40 to Structuring module raw score
  → Flag pattern as "Consolidation — potential mule receiver"
  → Trigger enhanced review of all sending accounts

VEL-029 — FAN-OUT DETECTION:

IF within any 24-hour window:
  Single sender → unique receiver count ≥ 5
  AND aggregate amount > $5,000
THEN:
  → Add +40 to Structuring module raw score
  → Flag pattern as "Dispersion — potential layering"
  → Trigger enhanced review of all receiving accounts
```

**Why Fan-In and Fan-Out Score +40:**
- Both patterns represent deliberate fund movement architecture — not random transaction behaviour
- +40 pushes structuring normalised score to 57% (40/70) — elevated but not yet at independent trigger threshold
- Combined with other velocity or structuring rules, these patterns will exceed the 75% independent trigger
- Scoring at 40 rather than 55+ preserves the ability for an analyst to review before auto-alerting on these alone — legitimate payroll disbursement could trigger Fan-Out without ML intent

---

## 5. Behavioural Change Indicators

Behavioural Change Indicators detect risk based on **deviation from established baseline** — not absolute transaction counts. A customer making 20 transactions per day is suspicious for a retail individual but normal for an established merchant.

All BEH scores add to the **Structuring module raw score** — they represent pattern-based risk in the same risk dimension as structuring.

| Indicator ID | Pattern Change | Structuring Score Addition | Description |
|---|---|---|---|
| **BEH-001** | **Dormant-to-Active** | +40 | Account inactive 90+ days suddenly processes 5+ transactions in 48 hours |
| **BEH-002** | **Velocity Surge** | +30 | 300%+ increase in weekly transaction count vs. 3-month rolling average |
| **BEH-003** | **New Corridor Activity** | +35 | Sudden high-velocity transactions to a jurisdiction with no previous transaction history |
| **BEH-004** | **Time-of-Day Anomaly** | +20 | High-volume transactions outside typical business hours for customer segment |
| **BEH-005** | **Rapid Round-Trip** | +50 | Funds received and fully disbursed within a 2-hour window — pass-through indicator |

### 5.1 Behavioural Indicator Justifications

**BEH-001 Dormant-to-Active (+40)**
- 90-day inactivity followed by sudden activity is a textbook account takeover or mule account activation pattern
- +40 pushes structuring normalised to 57% — requires one additional factor to auto-alert
- Threshold of 90 days chosen because legitimate account reactivation (returning from travel, seasonal business) typically involves gradual return to activity, not sudden bursts

**BEH-002 Velocity Surge (+30)**
- 300% increase threshold chosen to avoid flagging normal business growth (50–100% increase)
- 300% represents a step-change that cannot be explained by organic business development
- 3-month rolling average baseline prevents seasonal spikes from triggering alerts for established businesses

**BEH-003 New Corridor Activity (+35)**
- A customer suddenly transacting with a new jurisdiction at high velocity — with no prior history — is a strong layering indicator
- New corridor + high velocity = deliberate new channel opening, not gradual business expansion
- Integrates with GEO_RULES.md — if new corridor is also a high-risk jurisdiction, geo module adds further score

**BEH-004 Time-of-Day Anomaly (+20)**
- Lowest BEH score — time-of-day alone is a weak signal but meaningful in combination
- Non-banking hours activity avoids real-time compliance monitoring at many institutions
- +20 reflects supporting rather than primary risk signal

**BEH-005 Rapid Round-Trip (+50)**
- Funds in and fully out within 2 hours is the clearest pass-through / layering indicator in the engine
- Highest BEH score because the pattern has minimal legitimate explanation for most customer types
- Combined with any velocity rule, will exceed 75% independent structuring trigger
- Exception: established payment processors and clearinghouses — must be whitelisted if this pattern is their normal business

---

## 6. Velocity Scoring Logic

### 6.1 How Scores Stack

Multiple velocity and behavioural rules can fire on the same transaction or pattern. All additions feed into the Structuring module raw score, capped at 70.

```
STACKING EXAMPLE:

Customer triggers:
  Suspicious velocity (20+ per day)  : +35
  Fan-In pattern (VEL-028)            : +40
  Dormant-to-Active (BEH-001)         : +40
  ─────────────────────────────────────────
  Total before cap                    : 115
  Cap applied at Structuring maximum  : 70
  Structuring normalised              : 70/70 = 100%
  Independent trigger fires (≥ 75%)  : 🚨 Structuring Alert
```

### 6.2 Velocity Score Reference Table

| Rule | Score Addition | Module | Cap |
|---|---|---|---|
| Unusual velocity (5+ weekly) | +15 | Structuring | 70 max |
| Suspicious velocity (20+ daily) | +35 | Structuring | 70 max |
| Burst (5+ in 30 min) | +55 | Structuring | 70 max |
| VEL-028 Fan-In | +40 | Structuring | 70 max |
| VEL-029 Fan-Out | +40 | Structuring | 70 max |
| VEL-030 Round Number Burst | +25 | Structuring | 70 max |
| VEL-031 Off-Hours | +20 | Structuring | 70 max |
| BEH-001 Dormant-to-Active | +40 | Structuring | 70 max |
| BEH-002 Velocity Surge | +30 | Structuring | 70 max |
| BEH-003 New Corridor | +35 | Structuring | 70 max |
| BEH-004 Time-of-Day Anomaly | +20 | Structuring | 70 max |
| BEH-005 Rapid Round-Trip | +50 | Structuring | 70 max |

---

## 7. Independent Velocity Alert Triggers

The following velocity conditions trigger an **independent alert** regardless of CRS — consistent with the structuring independent trigger defined in `COMPOSITE_LOGIC.md` Section 3.

| Trigger | Condition | Rationale |
|---|---|---|
| **Burst activity** | 5+ transactions in < 30 minutes | Structuring score reaches 55/70 = 78.6% — exceeds 75% independent trigger |
| **Rapid Round-Trip** | Funds in and out within 2 hours | BEH-005 at +50 — combined with any base structuring score reaches 75% threshold |
| **Fan-In + Velocity** | VEL-028 + any velocity tier | +40 + 15 minimum = 55/70 = 78.6% — exceeds independent trigger |
| **Stacked pattern** | Any combination reaching 75%+ normalised | Cap at 70 → 100% normalised → auto-alert |

---

## 8. Test Scenarios

### Scenario 1 — Retail Burst Activity

```
Activity:   10 P2P transfers received in 15 minutes
Rule fired: Burst (VEL — 5+ in 30 minutes)
Score:      +55 to Structuring module
Normalised: 55/70 = 78.6% — exceeds 75% independent trigger
Result:     🚨 Independent Structuring Alert
Rationale:  Human behaviour is rarely this rapid — indicates 
            bot-driven smurfing or coordinated mule consolidation
```

---

### Scenario 2 — Mule Network Consolidation (Fan-In)

```
Activity:   8 different individuals send $1,000 to single 
            student account within 6 hours
Rules fired: VEL-028 Fan-In (+40) + VEL-030 Round Number (+25)
Score:      +65 to Structuring module (capped at 70)
Normalised: 70/70 = 100% — independent trigger fires
Result:     🚨 Independent Structuring Alert
Rationale:  Textbook mule aggregation — multiple senders, 
            round amounts, single receiver
```

---

### Scenario 3 — Dormant Account Activation

```
Activity:   Account dormant 6 months — 10 transactions in 
            24 hours to high-risk geography
Rules fired: BEH-001 Dormant-to-Active (+40) 
             + Suspicious velocity (+35)
Score:      +75 → capped at 70
Normalised: 70/70 = 100% — independent trigger fires
Geography:  Nigeria Tier 1C adds further to CRS
Result:     🚨 Independent Structuring Alert + elevated CRS
Rationale:  Account takeover or mule activation pattern — 
            dormancy followed by immediate high-risk corridor activity
```

---

### Scenario 4 — Legitimate Payroll (False Positive Prevention)

```
Activity:   Employer sends 50 identical $3,200 wires same day
Rules assessed: Fan-Out (VEL-029) — 1 sender, 50+ receivers
False positive risk: Fan-Out rule would add +40
Prevention:  CUSTOMER_RULES.md payroll exemption applies
             (see EDGE_CASES.md EC-007)
Result:      ✅ No alert — payroll exemption documented
Rationale:   Established business + pre-approved beneficiary 
             list + consistent with historical payroll dates
             = Fan-Out rule suppressed
```

---

## 9. Governance & Validation

### 9.1 Recalibration Schedule

| Trigger | Frequency | Action |
|---|---|---|
| Scheduled review | Every 6 months | Validate velocity thresholds against actual alert volumes |
| Payment technology change | As identified | Review burst thresholds — faster payments reduce natural velocity gaps |
| False positive rate breach | If FP > 20% for 2 months | Review Fan-In/Fan-Out thresholds — payroll and batch payments most likely cause |
| New ML typology identified | As published by FATF/FinCEN | Add new BEH or VEL rule with documented justification |

### 9.2 Baseline Management

```
BASELINE CALCULATION RULES:

Customer velocity baseline = 3-month rolling average
  - Recalculated weekly
  - Excludes known anomaly periods (e.g. tax season, 
    documented payroll dates)
  - New customers: no baseline for first 90 days
    → Apply BEH-001 standard thresholds during this period

Dormancy threshold = 90 days with zero transactions
  - Clock resets on any transaction
  - Does not apply to accounts with documented seasonal 
    business patterns
```

### 9.3 SR 11-7 Checklist

| Requirement | Status | Location |
|---|---|---|
| Purpose documented | ✅ Complete | Section 1 |
| Architecture integration documented | ✅ Complete | Section 2 |
| Module home for all scores defined | ✅ Complete | Section 2.1 |
| Cap rule documented | ✅ Complete | Section 2.3 |
| Threshold justifications provided | ✅ Complete | Sections 3.1, 4.1, 5.1 |
| Scoring logic documented | ✅ Complete | Section 6 |
| Independent triggers documented | ✅ Complete | Section 7 |
| Test scenarios provided | ✅ Complete | Section 8 |
| False positive scenario included | ✅ Complete | Section 8 Scenario 4 |
| Recalibration schedule defined | ✅ Complete | Section 9.1 |
| Baseline management documented | ✅ Complete | Section 9.2 |
| Independent validation | 🔄 Pending | Planned Day 45 |
| Back-testing | 🔄 Pending | Planned Day 30 |

---

## 10. Version History

| Version | Change | Date | Author |
|---|---|---|---|
| 1.0 | Initial draft — velocity tiers, Fan-In/Fan-Out, BEH indicators. Incorrect integration: velocity scores added directly to CRS. Rule IDs VEL-STR-001 to 004 conflicted with existing VEL sequence | 30 April 2026 | AK, CAMS |
| 1.1 | Corrected integration architecture — all velocity scores feed into Structuring module (0–70), not directly to CRS. Added cap rule at 70. Renamed VEL-STR rules to VEL-028 to VEL-031 to continue existing sequence. Added explicit module home for all BEH scores. Added SR 11-7 threshold justifications. Added false positive scenario. Added independent trigger section | 02 May 2026 | AK, CAMS |

---

*ScoreSentinel | VELOCITY_RULES.md | Transaction Velocity & Behavioural Pattern Rules | Authored by Atul Krishnan, CAMS | Version 1.1 | 30 April 2026*
