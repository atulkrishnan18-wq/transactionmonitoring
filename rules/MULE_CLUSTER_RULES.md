# MULE_CLUSTER_RULES.md — Mule Account Network Detection

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.0 | **Module:** 5 of 5 | **Author:** Atul Krishnan, CAMS
**Last Updated:** 18 May 2026

---

## Table of Contents
1. [Purpose & The Mule Problem](#1-purpose--the-mule-problem)
2. [How ScoreSentinel Addresses The Gap](#2-how-scoresentinel-addresses-the-gap)
3. [Mule Account Taxonomy](#3-mule-account-taxonomy)
4. [Five Detection Dimensions](#4-five-detection-dimensions)
5. [Mule Cluster Score (MCS)](#5-mule-cluster-score-mcs)
6. [UPI-Specific Detection Rules](#6-upi-specific-detection-rules)
7. [Indian Financial Crime Context](#7-indian-financial-crime-context)
8. [Five Mule Cluster Scenarios](#8-five-mule-cluster-scenarios)
9. [False Positive Management](#9-false-positive-management)
10. [Integration with ScoreSentinel Engine](#10-integration-with-scoresentinel-engine)
11. [RBI Regulatory Alignment](#11-rbi-regulatory-alignment)
12. [Positioning vs RBI Mule Hunter AI](#12-positioning-vs-rbi-mule-hunter-ai)
13. [SR 11-7 Model Risk Checklist](#13-sr-11-7-model-risk-checklist)
14. [Future Roadmap — ScoreSentinel Network](#14-future-roadmap--scoresentinel-network)
15. [Version History](#15-version-history)

---

## 1. Purpose & The Mule Problem

### 1.1 Scale of the Problem in India

Mule account networks are the primary infrastructure of digital financial fraud in India:

- **₹11,333 crore** lost to digital fraud in FY 2023-24 — RBI Annual Report 2024
- **67%** of all UPI fraud involves mule account pass-through — FIU-IND Typology Report 2024
- **4.5 lakh** mule accounts identified and frozen by Indian banks in 2023-24
- Average mule network lifespan before detection: **72 hours**
- Average funds in transit through a mule network before exit: **less than 4 hours**

> The fundamental problem is not identifying individual mule accounts. Indian banks, NPCI, and law enforcement have become reasonably effective at that. The problem is identifying **coordinated mule networks** — clusters of accounts working together — before the funds exit the financial system.

### 1.2 Why Existing Systems Fail

```
EXISTING TRANSACTION MONITORING:

Sees:    Individual account A sending ₹9,500
Flags:   Account A — suspicious
Misses:  Accounts B, C, D, E also sending 
         ₹9,500 to the same recipient
         simultaneously

Result:  5 individual alerts — analyst 
         reviews each one separately
         By the time all 5 are reviewed,
         the concentrator has already 
         sent the consolidated ₹47,500 
         abroad

SCORESENTINEL MODULE 5:

Sees:    Accounts A, B, C, D, E all 
         sending similar amounts to 
         Account F within 30 minutes
Flags:   MULE CLUSTER ALERT — entire 
         network of 6 accounts
Action:  All 6 accounts flagged 
         simultaneously — single case
         for analyst review
```

---

## 2. How ScoreSentinel Addresses The Gap

### 2.1 The Unique Positioning

ScoreSentinel Module 5 is the **only rules-based, SR 11-7 compliant mule cluster detection module** designed specifically for the Indian financial crime context.

| | RBI Mule Hunter AI | ScoreSentinel Module 5 |
|---|---|---|
| Detection approach | ML-based retrospective | Rules-based real-time |
| Explainability | Black box | Every rule documented |
| Detection timing | After funds moved | While funds are moving |
| Alert unit | Individual account | Entire cluster |
| SR 11-7 compliance | Requires XAI layer | Compliant by design |
| False positive documentation | Not public | Fully documented |
| Cost | Enterprise | Zero |

> **Complementary positioning:** RBI Mule Hunter AI identifies accounts already used as mules from historical patterns. ScoreSentinel Module 5 catches coordinated networks in real time as they operate. Both are needed — they solve different parts of the same problem.

### 2.2 The Cluster vs Account Distinction

```
ACCOUNT-LEVEL DETECTION (existing):
  One alert per suspicious account
  Analyst reviews accounts in isolation
  Network relationship invisible
  Average: 5 alerts for 5 mule accounts

CLUSTER-LEVEL DETECTION (Module 5):
  One cluster alert for entire network
  Analyst sees all accounts together
  Network map generated automatically
  Average: 1 cluster alert for 5 accounts
           + concentrator + exit point
           = complete picture
```

---

## 3. Mule Account Taxonomy

ScoreSentinel Module 5 recognises five mule account types commonly observed in Indian financial crime:

### 3.1 Type 1 — The Concentrator
**Profile:** Receives funds from multiple mule accounts, holds briefly, sends consolidated amount to exit point.

```
Characteristics:
- High Fan-In score (5+ inbound in 24hrs)
- Rapid outbound — funds out within 2 hours
- No legitimate business purpose
- Often newly opened account
- Round number inflows, single large outflow
Indian Context: Often a Jan Dhan account 
or newly opened zero-balance account
```

### 3.2 Type 2 — The Pass-Through Mule
**Profile:** Receives funds and immediately forwards — account used as a single relay point.

```
Characteristics:
- Receive → send within 30 minutes
- Balance never accumulates
- No ATM withdrawals — purely digital
- BEH-005 Rapid Round-Trip fires
Indian Context: Compromised UPI-linked 
account — victim unaware account is being 
used — SIM swap or credential theft
```

### 3.3 Type 3 — The Salary Mule
**Profile:** Receives what appears to be a salary credit, immediately transfers 85-95% out.

```
Characteristics:
- Regular monthly credit — salary-like amount
- Immediate transfer of most balance
- Small retention — plausible living expenses
- Pattern repeats monthly
Indian Context: Recruited mule — individual 
knowingly rents account for monthly payment
Often students, unemployed individuals
```

### 3.4 Type 4 — The Dormant Activated Mule
**Profile:** Account inactive for months, suddenly receives and sends large amounts, returns to dormancy.

```
Characteristics:
- 90+ days inactivity before activation
- BEH-001 Dormant-to-Active fires
- Large amounts inconsistent with history
- Returns to dormancy after single use
Indian Context: Stolen KYC used to open 
dormant accounts — activated on demand
Common in Jamtara and cyber crime hubs
```

### 3.5 Type 5 — The Layered Network Mule
**Profile:** Part of a multi-tier structure — receives from Tier 1, sends to Tier 2, creating distance from original fraud.

```
Characteristics:
- Clear Tier 1 → Tier 2 → Tier 3 pattern
- Each tier adds one degree of separation
- Amounts reduce at each tier — fees extracted
- Geographic spread across states
Indian Context: Organised cyber crime 
networks — Jamtara, Mewat, Nuh corridors
Professional money laundering operations
```

---

## 4. Five Detection Dimensions

Module 5 scores every account cluster across five independent dimensions. All five contribute to the Mule Cluster Score (MCS).

### Dimension 1 — Concentration Score (0–30)

Measures how many accounts are feeding into a single concentrator account.

| Pattern | Score | Rule ID |
|---|---|---|
| 2–4 senders → 1 receiver in 24hrs | +10 | MUL-001 |
| 5–9 senders → 1 receiver in 24hrs | +20 | MUL-002 |
| 10+ senders → 1 receiver in 24hrs | +30 | MUL-003 |
| Same senders repeat next day | +15 additional | MUL-004 |

**Rationale:** Legitimate concentration (payroll, collections) involves a known business entity paying outward. Inward concentration from multiple individuals to one account has very few legitimate explanations.

---

### Dimension 2 — Velocity Correlation Score (0–25)

Measures whether multiple accounts are activating or transacting in a coordinated time window — suggesting centralised control.

| Pattern | Score | Rule ID |
|---|---|---|
| 3+ dormant accounts activating within 48hrs | +20 | MUL-005 |
| 5+ accounts transacting within same 30-min window | +25 | MUL-006 |
| Same transaction pattern repeating across accounts | +15 | MUL-007 |
| Accounts in different cities showing identical timing | +20 | MUL-008 |
| **Common Device Nexus (>3 accounts sharing same Device ID/IP)** | **+25** | **MUL-023** |

**Rationale:** Legitimate customers transact independently. Coordinated timing across multiple accounts — especially dormant accounts — indicates centralised instruction. Criminal mule networks are directed by a controller who instructs accounts to transact simultaneously. Shared hardware or network identifiers are high-confidence indicators of central control.

---

### Dimension 3 — Amount Pattern Score (0–20)

Detects structuring patterns across multiple accounts — amounts designed to avoid detection thresholds.

| Pattern | Score | Rule ID |
|---|---|---|
| 3+ accounts sending identical amounts | +15 | MUL-009 |
| 5+ accounts sending amounts within 10% of each other | +20 | MUL-010 |
| Amounts just below ₹10,000 reporting attention threshold | +15 | MUL-011 |
| Amounts just below ₹50,000 UPI daily limit | +15 | MUL-012 |
| Round amounts (₹5,000 / ₹10,000 / ₹25,000) in burst | +10 | MUL-013 |
| **Micro-Test Signal (₹1-₹10 test followed by large burst)** | **+15** | **MUL-022** |

**Rationale:** Natural transaction amounts vary. When multiple accounts send suspiciously similar amounts — especially just below reporting thresholds — the pattern reflects coordinated instruction from a single controller. Micro-test transactions are used by fraudsters to verify account activity before moving larger stolen sums.

---

### Dimension 4 — Pass-Through Speed Score (0–15)

Measures how quickly funds move through the account — the faster the pass-through, the more likely the account is being used as a relay.

| Pattern | Score | Rule ID |
|---|---|---|
| Funds received and sent within 30 minutes | +15 | MUL-014 |
| Funds received and sent within 2 hours | +10 | MUL-015 |
| Funds received and sent within 24 hours | +5 | MUL-016 |
| Balance retention below 5% after outbound | +10 | MUL-017 |

**Rationale:** Legitimate account holders retain funds for personal use. A mule account has no reason to retain funds — its purpose is relay. Near-zero balance retention combined with rapid outbound is the clearest behavioural signature of a pass-through mule.

---

### Dimension 5 — Network Depth Score (0–10)

Detects multi-tier layering structures — the more tiers, the more sophisticated and organised the network.

| Pattern | Score | Rule ID |
|---|---|---|
| Two-tier detected (sender → concentrator → exit) | +5 | MUL-018 |
| Three-tier detected (sender → relay → concentrator → exit) | +8 | MUL-019 |
| Four+ tier detected | +10 | MUL-020 |
| Circular flow detected (funds return to origin) | +10 | MUL-021 |

**Rationale:** Single-tier mule operations are opportunistic — recruited individuals acting alone. Multi-tier networks indicate organised criminal infrastructure. The number of tiers is a proxy for the sophistication and scale of the operation.

---

## 5. Mule Cluster Score (MCS)

### 5.1 MCS Formula

Unlike the CRS which scores a single transaction, the MCS scores a **cluster of accounts** simultaneously:

```
MCS = Concentration Score (0–30)
    + Velocity Correlation Score (0–25)
    + Amount Pattern Score (0–20)
    + Pass-Through Speed Score (0–15)
    + Network Depth Score (0–10)
─────────────────────────────────────
Maximum MCS = 100
Alert Threshold = MCS ≥ 60
```

### 5.2 MCS Risk Bands

| MCS Range | Risk Band | Action |
|---|---|---|
| 0–20 | 🟢 Low — Normal activity | Standard monitoring |
| 21–40 | 🟡 Medium — Elevated pattern | Flag for review |
| 41–59 | 🟠 High — Probable mule activity | Enhanced monitoring — analyst review |
| 60–79 | 🔴 Mule Cluster Alert | Freeze accounts pending review — report to FIU-IND |
| 80–100 | 🔴🔴 Organised Network Alert | Immediate freeze — report to FIU-IND and local LEA |

### 5.3 MCS Independent Triggers

The following patterns trigger immediate cluster alert regardless of MCS:

| Trigger | Rule | Action |
|---|---|---|
| 10+ accounts sending to 1 receiver within 1 hour | MUL-003 | Immediate freeze — organised network |
| Circular flow detected — funds return to origin | MUL-021 | Immediate freeze — money laundering ring |
| 5+ dormant accounts activating same 24-hour window | MUL-005 + MUL-006 | Immediate alert — coordinated activation |
| Pass-through within 30 mins + Concentration 5+ | MUL-014 + MUL-002 | Immediate alert — active relay network |
| **Common Device Nexus with Rapid Outbound** | **MUL-023 + MUL-014** | **Immediate freeze — active bot/controlled network** |

### 5.4 Dual Output — CRS and MCS

ScoreSentinel now produces two scores for every transaction:

```
TRANSACTION SCORED:

CRS: 45.2 — MEDIUM-HIGH
     (individual transaction risk)

MCS: 72.0 — MULE CLUSTER ALERT
     (network risk — this account is part
      of a coordinated mule cluster)

COMBINED DISPOSITION:
  CRS alone: Enhanced monitoring
  MCS alert: Freeze all cluster accounts
             File STR with FIU-IND
             Report to NPCI if UPI involved
```

---

## 6. UPI-Specific Detection Rules

UPI is the primary infrastructure for mule fund movement in India. Module 5 includes UPI-specific rules not covered in TRANSACTION_RULES.md.

| Rule ID | Pattern | Threshold | Score | Action |
|---|---|---|---|---|
| UPI-001 | Multiple UPI sends from one account in 1 hour | 10+ transactions | +15 | Velocity alert |
| UPI-002 | UPI amounts clustered just below ₹10,000 | 5+ transactions | +20 | Structuring alert |
| UPI-003 | Same UPI VPA receiving from 5+ different VPAs | Within 2 hours | +25 | Concentration alert |
| UPI-004 | UPI account registered less than 30 days | Any large transaction | +15 | New account risk |
| UPI-005 | UPI transaction at unusual hours | 11pm–5am burst | +10 | Off-hours alert |
| UPI-006 | Rapid UPI receive-then-IMPS/NEFT out | Within 1 hour | +20 | Pass-through alert |
| UPI-007 | Multiple VPAs linked to same mobile number | 3+ VPAs | +20 | Multi-VPA mule |

> **UPI Context:** UPI's real-time settlement and near-zero friction makes it the preferred infrastructure for mule networks in India. Funds can enter via UPI, be aggregated across accounts, and exit via IMPS or NEFT to a bank account in under 4 hours — faster than any manual review process.

---

## 7. Indian Financial Crime Context

### 7.1 Known Mule Network Typologies in India

**The Jamtara Model**
```
Phishing call → victim shares OTP
Funds transferred to Tier 1 mule account
Tier 1 → multiple Tier 2 accounts (Fan-Out)
Tier 2 accounts → single concentrator
Concentrator → cryptocurrency exchange
→ Funds exit financial system
Timeline: Under 4 hours
```

**The Cyber Crime Hub Model (Mewat, Nuh)**
```
Organised gang recruits mule account holders
Pays ₹5,000–10,000 per account per month
Accounts activated on demand via WhatsApp
Funds move in coordinated bursts
Multiple states involved simultaneously
```

**The Pig Butchering Model**
```
Romance/investment scam victim sends funds
Funds hit mule account immediately
Rapid pass-through to concentrator
Exit via hawala or crypto
International dimension — funds leave India
```

**The Jan Dhan Mule Model**
```
Fraudsters obtain Jan Dhan account credentials
Low KYC requirements — easy to open
Used as pass-through — owner may be unaware
Account frozen — owner victim not perpetrator
ScoreSentinel must distinguish between
knowing mule and unknowing victim
```

### 7.2 False Positive Risk — Legitimate Indian Financial Patterns

Several legitimate Indian financial behaviours resemble mule patterns and must be excluded:

| Legitimate Pattern | Resembles | Exclusion Rule |
|---|---|---|
| Chit fund collections | Fan-In concentration | Registered chit fund company + consistent monthly pattern |
| Festival gifting (Diwali, Eid) | Burst transactions | Seasonal calendar + known sender relationships |
| Rotating Savings Groups (RoSCA) | Coordinated activation | Group registration + recurring fixed amounts |
| Family remittances | Multiple senders one receiver | Family relationship documented |
| Salary disbursement by employer | Fan-Out from one account | Employer verified + consistent monthly amounts |
| Agricultural produce payments | Irregular large credits | Seasonal pattern + agri sector customer type |

---

## 8. Five Mule Cluster Scenarios

### Scenario MC-1 — Classic Concentrator Network
**Expected Outcome: MCS 80+ — Organised Network Alert**

```
8 accounts each receive ₹9,500 from 
different sources within 2 hours

All 8 send to Account X within 30 minutes
of receiving

Account X immediately sends ₹74,000 
(consolidated minus small fee) via IMPS

Dimension scores:
  Concentration:      30 (8 senders → 1)
  Velocity:           25 (coordinated 30-min window)
  Amount Pattern:     20 (identical ₹9,500 amounts)
  Pass-Through Speed: 15 (under 30 minutes)
  Network Depth:       5 (two-tier)

MCS = 95 — 🔴🔴 Organised Network Alert
```

---

### Scenario MC-2 — Salary Mule Network
**Expected Outcome: MCS 55 — High — Probable Mule**

```
10 accounts each receive ₹15,000-18,000 
on the same day (salary-like)

9 of 10 transfer 90%+ of balance within 
24 hours to same recipient

One account retains full balance — 
likely legitimate salary recipient

Dimension scores:
  Concentration:      20 (9 senders → 1)
  Velocity:           15 (same day but not burst)
  Amount Pattern:     15 (similar but not identical)
  Pass-Through Speed: 10 (within 24 hours)
  Network Depth:       5 (two-tier)

MCS = 65 — 🔴 Mule Cluster Alert

False positive consideration:
  1 of 10 retained funds — possible 
  legitimate salary. Exclude from cluster.
  Flag 9 accounts as probable mule network.
```

---

### Scenario MC-3 — Dormant Activation Coordinated Attack
**Expected Outcome: MCS 70+ — Mule Cluster Alert**

```
6 accounts dormant for 4-8 months
All 6 receive credits within same 
48-hour window

All 6 transfer within 2 hours of receiving
Amounts between ₹8,000 and ₹12,000

Dimension scores:
  Concentration:      20 (6 senders → 2 receivers)
  Velocity:           20 (dormant + coordinated)
  Amount Pattern:     15 (similar threshold-adjacent)
  Pass-Through Speed: 10 (within 2 hours)
  Network Depth:       8 (three-tier structure)

MCS = 73 — 🔴 Mule Cluster Alert

BEH-001 also fires on each account individually
Combined: Individual alerts + Cluster alert
```

---

### Scenario MC-4 — UPI Smurfing Ring
**Expected Outcome: MCS 65 — Mule Cluster Alert**

```
15 different UPI VPAs each send ₹4,999
(just below ₹5,000 attention threshold)
to same recipient VPA within 1 hour

Recipient immediately transfers ₹72,000 
via NEFT to bank account

Dimension scores:
  Concentration:      30 (15 senders → 1)
  Velocity:           25 (within 1 hour)
  Amount Pattern:     20 (identical ₹4,999)
  Pass-Through Speed: 15 (immediate NEFT out)
  Network Depth:       5 (two-tier)

MCS = 95 — 🔴🔴 Organised Network Alert

UPI-001, UPI-002, UPI-003, UPI-006 all fire
NPCI notification recommended
```

---

### Scenario MC-5 — Legitimate Chit Fund (False Positive)
**Expected Outcome: MCS 25 — Medium — No Alert**

```
20 members each contribute ₹5,000 monthly
to registered chit fund company account

Consistent pattern for 8 months
All contributors are registered members
Chit fund company is RBI registered

Dimension scores:
  Concentration:      20 (20 contributors → 1)
  Velocity:            0 (monthly — not burst)
  Amount Pattern:     10 (identical amounts
                         but legitimate reason)
  Pass-Through Speed:  0 (funds retained 
                         for chit disbursement)
  Network Depth:       0 (single tier — 
                         no layering)

MCS = 30 — 🟡 Medium — Flag for Review

Exclusion rule applies:
  → Registered chit fund company ✅
  → Consistent 8-month pattern ✅
  → No pass-through behaviour ✅
  → MCS review → CLEAR with documentation
```

---

## 9. False Positive Management

### 9.1 Mule Detection False Positive Targets

| Metric | Target | Rationale |
|---|---|---|
| Overall MCS false positive rate | < 25% | Higher tolerance than CRS — cluster detection casts wider net by design |
| Chit fund false positive rate | < 5% | Highly documented legitimate pattern — should almost never alert |
| Salary mule false positive rate | < 20% | Hardest to distinguish — legitimate salary disbursement resembles mule pattern |
| Dormant activation false positive rate | < 15% | Legitimate account reactivation does occur — seasonal workers, returning travellers |

### 9.2 The Unknowing Mule Problem

> **Critical distinction:** Many mule accounts in India are owned by victims — individuals whose KYC was stolen, whose accounts were compromised via SIM swap, or who were tricked into sharing credentials. ScoreSentinel must distinguish between knowingly recruited mules and unknowing victims.

```
KNOWING MULE INDICATORS:
  → Multiple accounts linked to same device
  → Account holder has received multiple 
    small payments from unknown sources
  → Account holder contacted before activation
  → Pattern repeats monthly

UNKNOWING VICTIM INDICATORS:
  → Single activation event
  → Account holder reports fraud
  → No prior relationship with sending accounts
  → SIM swap detected around activation time

ACTION DIFFERENCE:
  Knowing mule: Freeze + report to FIU-IND
  Unknowing victim: Freeze + victim support 
                    + report to cyber cell
```

---

## 10. Integration with ScoreSentinel Engine

### 10.1 How Module 5 Connects

```
EXISTING FLOW (Modules 1-4):
Transaction arrives → score_transaction()
→ customer_module
→ structuring_module  
→ geo_module
→ transaction_module
→ CRS calculated
→ stored in transactions table

NEW FLOW (Module 5 added):
Transaction arrives → score_transaction()
→ [existing modules 1-4]
→ CRS calculated
→ mule_module.analyse_cluster(account_id)
   → fetch recent account network
   → score 5 dimensions
   → MCS calculated
→ Both CRS and MCS returned
→ stored in transactions table
→ Cluster stored in mule_clusters table
```

### 10.2 New Database Table Required

```sql
CREATE TABLE mule_clusters (
    cluster_id          VARCHAR(50) PRIMARY KEY,
    detected_at         TIMESTAMP DEFAULT NOW(),
    cluster_type        VARCHAR(30),
    mcs                 DECIMAL(5,2),
    risk_band           VARCHAR(20),
    account_ids         TEXT[],
    concentrator_id     VARCHAR(50),
    dimension_scores    JSONB,
    rules_fired         TEXT[],
    alert_generated     BOOLEAN DEFAULT TRUE,
    status              VARCHAR(20) DEFAULT 'PENDING',
    reviewer_id         VARCHAR(50),
    review_timestamp    TIMESTAMP,
    reviewer_rationale  TEXT,
    str_filed           BOOLEAN DEFAULT FALSE,
    str_reference       VARCHAR(50),
    created_at          TIMESTAMP DEFAULT NOW()
);
```

### 10.3 New API Endpoint Required

```
GET /api/clusters
Returns all detected mule clusters

GET /api/clusters/<cluster_id>
Returns full cluster detail with network map

PUT /api/clusters/<cluster_id>
Updates cluster disposition — STR filing,
account freeze status, reviewer rationale
```

---

## 11. RBI Regulatory Alignment

### 11.1 RBI Circulars and Directives

| Reference | Relevance |
|---|---|
| RBI Master Direction on KYC (2016, updated 2024) | Mule account identification — Section 38 |
| RBI Circular RBI/2023-24/100 | Digital payment fraud prevention |
| RBI Annual Report 2024 — Chapter on Payment Systems | ₹11,333 crore fraud statistics cited |
| NPCI UPI Circular NPCI/UPI/OC No. 176 | UPI transaction monitoring requirements |
| Prevention of Money Laundering Act 2002 (PMLA) | STR filing obligations — Section 12 |
| FIU-IND Typology Report 2024 | Mule account network patterns in India |

### 11.2 STR Filing Obligation

When MCS ≥ 60, ScoreSentinel recommends filing a Suspicious Transaction Report with FIU-IND:

```
STR TRIGGER CONDITIONS:
  MCS ≥ 60 AND cluster involves 3+ accounts
  → File STR within 7 days per PMLA Section 12

MCS ≥ 80 AND organised network indicators
  → File STR within 24 hours
  → Notify local LEA via cyber crime portal
  → If UPI involved → notify NPCI

ACCOUNT FREEZE:
  Indian banks may freeze accounts under
  RBI Master Direction Section 38
  ScoreSentinel generates freeze recommendation
  — actual freeze requires bank compliance 
  officer decision
```

### 11.3 RBI Innovation Hub (RBIH) Sandbox

ScoreSentinel Module 5 is designed for submission to the RBIH Regulatory Sandbox under the theme **"Prevention and Mitigation of Financial Frauds."**

**Sandbox submission positioning:**
> "ScoreSentinel Module 5 provides real-time, rules-based mule cluster detection as a complementary layer to RBI's existing Mule Hunter AI — addressing the gap between retrospective ML identification and real-time network detection. The engine is SR 11-7 compliant, fully explainable, and deployable at zero cost by any RBI-regulated entity."

---

## 12. Positioning vs RBI Mule Hunter AI

| Dimension | RBI Mule Hunter AI | ScoreSentinel Module 5 |
|---|---|---|
| Detection timing | Retrospective — after funds moved | Real-time — while funds moving |
| Methodology | Machine learning | Rules-based |
| Explainability | Requires XAI tools | Every rule documented |
| Alert unit | Individual account | Entire cluster |
| False positive documentation | Not public | Fully documented — Section 9 |
| Regulatory coverage | RBI internal | SR 11-7 + RBI + FATF |
| Deployment cost | Centralised RBI tool | Zero — open source |
| STR integration | Manual | Automated recommendation |
| UPI-specific rules | Unknown | 7 dedicated rules — Section 6 |

> **The complementary case:** RBI Mule Hunter AI operates at the network level across all Indian banks — it sees patterns no single institution can see. ScoreSentinel Module 5 operates at the institution level in real time. Together they provide complete coverage — network-level retrospective detection plus institution-level real-time detection.

---

## 13. SR 11-7 Model Risk Checklist

| Requirement | Status | Location |
|---|---|---|
| Module purpose documented | ✅ Complete | Section 1 |
| Mule taxonomy defined | ✅ Complete | Section 3 |
| Five detection dimensions documented | ✅ Complete | Section 4 |
| MCS formula documented | ✅ Complete | Section 5.1 |
| Threshold justification provided | ✅ Complete | Section 4 — per dimension |
| Independent triggers documented | ✅ Complete | Section 5.3 |
| UPI-specific rules documented | ✅ Complete | Section 6 |
| False positive targets defined | ✅ Complete | Section 9.1 |
| Unknowing victim distinction | ✅ Complete | Section 9.2 |
| RBI regulatory alignment | ✅ Complete | Section 11 |
| Integration architecture documented | ✅ Complete | Section 10 |
| Database schema defined | ✅ Complete | Section 10.2 |
| Worked scenarios provided | ✅ Complete | Section 8 |
| False positive scenario included | ✅ Complete | Scenario MC-5 |
| Independent validation | 🔄 Pending | RBIH Sandbox — planned |
| Back-testing against real data | 🔄 Pending | RBIH Sandbox — planned |

---

## 14. Future Roadmap — ScoreSentinel Network

### Phase 1 — ScoreSentinel Core (Current)
Single institution mule cluster detection. Rules-based. Open source. Zero cost.

### Phase 2 — ScoreSentinel Network (Year 2)
Cross-institution mule network detection. Requires data sharing consortium. RBI sandbox validation. Target — consortium of cooperative banks and fintechs.

### Phase 3 — ScoreSentinel Intelligence (Year 3)
Real-time mule network API. SaaS model. NPCI UPI data integration. Target — all RBI regulated entities via API subscription.

```
THE PRODUCT SUITE VISION:

ScoreSentinel Core    → Open source — builds credibility
ScoreSentinel Network → Consortium SaaS — generates revenue  
ScoreSentinel Intel   → Enterprise API — scales nationally

Each version is rules-based, explainable,
and RBI compliant by design.
The regulatory moat is the explainability.
Competitors using ML cannot match the
transparency requirement that Indian
regulators increasingly demand.
```

---

## 15. Version History

| Version | Change | Date | Author |
|---|---|---|---|
| 1.0 | Initial release — five detection dimensions, mule taxonomy, UPI-specific rules, five cluster scenarios, RBI regulatory alignment, RBIH sandbox positioning, SR 11-7 governance | 16 May 2026 | Atul Krishnan, CAMS |

---

*ScoreSentinel | MULE_CLUSTER_RULES.md | Mule Account Network Detection — Module 5 | Authored by Atul Krishnan, CAMS | Version 1.0 | 16 May 2026*
