# EDGE_CASES.md — False Positive Prevention & Edge Case Library

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.0 | **Day:** 9 of 60 | **Author:** Atul Krishnan, CAMS
**Last Updated:** 25 April 2026

---

## Table of Contents
1. [Purpose](#1-purpose)
2. [False Positive Design Philosophy](#2-false-positive-design-philosophy)
3. [Screening Edge Cases — From Operational Experience](#3-screening-edge-cases--from-operational-experience)
4. [Transaction Edge Cases](#4-transaction-edge-cases)
5. [False Positive Decision Rules](#5-false-positive-decision-rules)
6. [False Positive Metrics & Targets](#6-false-positive-metrics--targets)
7. [Governance](#7-governance)

---

## 1. Purpose

This document defines the edge cases ScoreSentinel must handle correctly to avoid over-alerting on legitimate activity. Edge cases are transactions or customer profiles that **appear suspicious** under a surface-level rule check but are **explainable and legitimate** upon review.

Failure to handle edge cases correctly produces two regulatory risks:

1. **Over-alerting** — false positive rate exceeds 15% target, analyst capacity consumed by noise, genuine alerts missed
2. **Under-alerting** — rules tuned too loosely to reduce noise, real ML activity passes through undetected

> **Source:** The four primary screening edge case categories in this document are derived from operational experience in financial crime screening at a Tier 1 global bank — specifically PEP screening, sanctions screening, and adverse media review workflows.

---

## 2. False Positive Design Philosophy

### 2.1 The Two Types of False Positive

| Type | Definition | Risk |
|---|---|---|
| **Type 1 — Screening FP** | Name match or media hit on wrong person | Wastes analyst time, damages customer relationship |
| **Type 2 — Scoring FP** | CRS exceeds 60 on a legitimate transaction | Generates unnecessary alert, erodes analyst trust in system |

ScoreSentinel addresses both types through dedicated rules in this document.

### 2.2 The Core Principle

> A false positive is not just an inconvenience — it is a **model calibration failure.** Every false positive that reaches an analyst without being filtered represents a gap in the rules. This document exists to close those gaps systematically.

### 2.3 SR 11-7 Requirement

SR 11-7 requires that false positive management be documented as a deliberate design decision — not treated as an acceptable side effect. Every edge case rule in this document includes:
- The false positive pattern it prevents
- The legitimate explanation it recognises
- The residual risk it accepts
- The control that mitigates that residual risk

---

## 3. Screening Edge Cases — From Operational Experience

These four categories represent the most common and time-consuming false positives encountered in Tier 1 financial crime screening operations.

---

### Edge Case 1 — Adverse Media: Wrong Person (Name Collision in Media)

**Pattern:** A news article about a fraudster, money launderer, or sanctioned individual shares the same name as a clean customer. The screening system flags the customer based on name match against the article.

**Real Example:**
```
Customer:    Mr. David Johnson, UK retail customer, 
             salaried accountant, 10-year account history
Media Hit:   "David Johnson convicted of $2M fraud" 
             — New York Post, 2023
Problem:     Different David Johnson — US citizen, 
             different DOB, different employer
Result:      False positive — wrong person entirely
```

**Why It Happens:**
- Adverse media screening uses name matching without sufficient corroborating identifiers
- Common names produce high collision rates — Smith, Johnson, Khan, Singh, Ahmed
- Single-source articles often lack DOB, nationality, or employer details needed to disambiguate

**ScoreSentinel Rule — EC-001:**
```
IF adverse media hit on customer name:
  REQUIRE corroboration on at least 2 of:
    - Date of birth match
    - Nationality / country of residence match
    - Employer or business name match
    - Address or city match
    - Photograph confirmation (where available)

  IF fewer than 2 identifiers corroborate:
    → Classify as Category E (unverified, single source)
    → Score: +10 to customer risk (not +35)
    → Flag for analyst review — do not auto-escalate

  IF 2 or more identifiers corroborate:
    → Classify as Category A–D per CUSTOMER_RULES.md
    → Apply full adverse media score
    → Escalate per standard workflow
```

**Residual Risk Accepted:** A genuine adverse media hit on a customer with a common name and limited corroborating identifiers may be downgraded to Category E. Mitigated by mandatory analyst review queue for all Category E hits involving financial crime categories.

**Operational Note from HRDT Experience:** Adverse media false positives on common names are the highest-volume screening false positive type in practice. A two-identifier corroboration rule reduces false positive rate significantly without materially increasing miss rate — the genuine hits almost always have at least two corroborating identifiers available.

---

### Edge Case 2 — Former PEP: Left Office (Temporal PEP Risk)

**Pattern:** A customer was a PEP — held a senior government position — but left office 1, 2, or 3 years ago. The screening system continues to flag them as an active PEP, generating EDD requirements that may no longer be proportionate.

**Real Example:**
```
Customer:    Mr. Rajesh Kumar, former Deputy Minister 
             of Finance, India — left office March 2022
Current:     Private sector consultant, no government role
Screening:   PEP Tier 2 flag still active — April 2026
Problem:     4 years post-office, still generating full 
             EDD workflow — disproportionate to current risk
```

**Why It Happens:**
- PEP lists are updated slowly — some vendors lag by 12–24 months
- "Once a PEP, always a PEP" rules are applied without a de-escalation framework
- No documented sunset clause for PEP monitoring intensity

**ScoreSentinel Rule — EC-002:**
```
PEP DE-ESCALATION FRAMEWORK:

IF customer held PEP status AND has left public office:

  0–12 months post-office:
    → Maintain full PEP Tier status
    → Full EDD mandatory
    → Rationale: Influence, assets, and relationships 
      from office remain active

  13–36 months post-office:
    → Downgrade one tier (Tier 1 → Tier 2, Tier 2 → Tier 3)
    → Enhanced monitoring maintained
    → Annual review required
    → Rationale: Direct influence waning but network intact

  37+ months post-office:
    → Downgrade to PEP-Adjacent (Tier 3) OR standard 
      customer if no other risk factors
    → Standard CDD with annual PEP re-check
    → Rationale: Risk has materially reduced — 
      proportionate monitoring required

EXCEPTION — Never de-escalate if:
    → Customer held Head of State / President / PM role
      (maintain Tier 1 indefinitely)
    → Ongoing corruption investigation or prosecution
    → Adverse media Category A or B in last 24 months
    → Customer is in a jurisdiction with CPI score < 30
```

**Residual Risk Accepted:** A former senior official de-escalated after 37 months may re-engage corrupt networks. Mitigated by annual PEP re-check, ongoing adverse media monitoring, and transaction velocity rules that would catch unusual financial activity regardless of PEP status.

**Operational Note from HRDT Experience:** Former PEP de-escalation is one of the most contested decisions in screening operations. The framework above provides a documented, defensible de-escalation path that satisfies both proportionality requirements and regulatory expectations — with clear exceptions for heads of state and active investigations.

---

### Edge Case 3 — Name Collision: SDN List (Common Name Multiple Matches)

**Pattern:** A customer's name matches multiple entries on the OFAC SDN list. The screening system generates a hit but the customer is a different individual entirely — same name, different person.

**Real Example:**
```
Customer:    Mr. Ali Hassan, British-Pakistani retail 
             customer, Bradford, UK — born 1985
SDN Matches: 14 entries for "Ali Hassan" / "Ali Hasan" 
             / "Aly Hassan" on SDN list — various 
             nationalities, DOBs ranging 1955–1975
Problem:     Name match at 85–95% on multiple entries
             None share DOB, nationality, or address
Result:      High-priority sanctions alert on a clean 
             UK retail customer
```

**Why It Happens:**
- Arabic, South Asian, and African names have high phonetic collision rates
- Transliteration variations (Hassan/Hasan/Hussan) all score above 85% fuzzy match
- SDN list contains many common regional names

**ScoreSentinel Rule — EC-003:**
```
MULTI-ENTRY SDN COLLISION PROTOCOL:

IF name matches 3+ SDN entries simultaneously:
  → Apply enhanced disambiguation before escalating

  STEP 1 — Date of Birth check:
    IF customer DOB matches any SDN entry DOB (±2 years):
      → Escalate immediately as potential real hit
    IF no DOB match across all entries:
      → Proceed to Step 2

  STEP 2 — Nationality / Country of Birth check:
    IF customer nationality matches any SDN entry nationality:
      → Escalate — potential real hit despite DOB gap
    IF no nationality match:
      → Proceed to Step 3

  STEP 3 — Address / City check:
    IF customer address country matches any SDN entry 
    last known location:
      → Escalate — geographic proximity is a risk signal
    IF no geographic match:
      → Classify as PROBABLE FALSE POSITIVE
      → Document: "Name collision — [X] SDN entries, 
        no DOB / nationality / geographic match"
      → Clear with documented rationale
      → Flag customer for enhanced periodic rescreening 
        (every 6 months instead of standard 12 months)

MANDATORY: All clearance decisions on SDN name 
collisions must include full disambiguation 
documentation regardless of outcome.
```

**Residual Risk Accepted:** A genuine sanctioned individual sharing a common name with a clean customer may be cleared through this protocol if they do not have matching DOB, nationality, or address on file. Mitigated by enhanced rescreening frequency and mandatory documentation of all clearance decisions.

**Operational Note from HRDT Experience:** SDN name collisions on common Arabic, South Asian, and African names are a persistent operational challenge in APAC and EMEA screening. A three-step disambiguation protocol with mandatory documentation significantly reduces analyst time while maintaining a defensible audit trail for every clearance decision.

---

### Edge Case 4 — Common Name PEP Match (High-Collision PEP Names)

**Pattern:** A customer's name matches a PEP on a commercial PEP database, but the name is extremely common in the relevant region. The customer is a private individual with no political connections.

**Real Example:**
```
Customer:    Mr. Mohamed Al-Ahmed, UAE retail customer,
             engineer, born 1990, Dubai
PEP Match:   "Mohammed Al-Ahmed" — Senior official, 
             Ministry of Finance, Saudi Arabia, born 1965
Database:    200+ individuals named Mohamed/Mohammed 
             Al-Ahmed in GCC region
Problem:     85% fuzzy name match — different country,
             different DOB, different profession
Result:      PEP Tier 2 EDD requirement on a clean 
             retail engineer
```

**Why It Happens:**
- Arabic naming conventions produce extremely high collision rates — Mohamed, Ahmed, Abdullah, Al-Hassan are among the most common names globally
- Commercial PEP databases prioritise recall over precision — they flag broadly to avoid misses
- Screening systems apply fuzzy match without sufficient secondary identifier checks

**ScoreSentinel Rule — EC-004:**
```
HIGH-COLLISION PEP NAME PROTOCOL:

IF PEP match on customer name AND name is classified 
as high-collision (regional frequency > 1 in 500):

  High-collision name indicators:
    - Arabic: Mohamed/Mohammed/Ahmad/Abdullah/Al-Hassan
    - South Asian: Singh/Kumar/Sharma/Khan/Patel
    - Chinese: Wang/Li/Zhang/Chen/Liu
    - African: Diallo/Traore/Coulibaly/Koné

  STEP 1 — Date of Birth:
    If DOB gap > 10 years between customer and PEP:
      → Strong false positive indicator
      → Proceed to Step 2 before escalating

  STEP 2 — Nationality / Country of Residence:
    If customer nationality differs from PEP nationality:
      → Additional false positive indicator
      → Proceed to Step 3

  STEP 3 — Profession / Employer:
    If customer profession has no plausible connection 
    to political role (e.g., engineer vs. minister):
      → Classify as PROBABLE FALSE POSITIVE
      → Document full disambiguation reasoning
      → Apply standard CDD — do not trigger EDD
      → Flag for enhanced annual PEP re-check

  ESCALATE IMMEDIATELY if any of:
    → DOB within 5 years of PEP DOB
    → Same nationality as PEP
    → Same city / region as PEP
    → Customer has transacted with PEP's known entities

MANDATORY: Document the specific PEP entry matched,
the identifiers checked, and the reasoning for 
clearance or escalation on every case.
```

**Residual Risk Accepted:** A genuine PEP with a common name may be cleared if they do not share DOB, nationality, or geographic location on file. Mitigated by mandatory documentation, annual PEP re-check, and transaction monitoring rules that would catch unusual financial behaviour regardless of PEP status.

**Operational Note from HRDT Experience:** Common name PEP false positives are especially prevalent in APAC and MENA screening operations where a small number of names account for a large proportion of the population. The three-step protocol with profession check is the most effective operational solution — it adds 5 minutes to a case but prevents 30-minute full EDD workflows on clear false positives.

---

## 4. Transaction Edge Cases

These scenarios involve transactions that score above the alert threshold but represent legitimate activity. ScoreSentinel must distinguish these from genuine ML.

---

### Edge Case 5 — Legitimate Cash-Intensive Business

**Pattern:** A restaurant owner makes 15 cash deposits per month averaging $2,000 each. Under structuring rules, this triggers a micro-structuring alert. But it is legitimate weekend and weekday takings from a food business.

**ScoreSentinel Rule — EC-005:**
```
IF cash deposit pattern triggers structuring rule AND
customer is classified as Cash-Intensive Business:

  REQUIRE documented business justification:
    → Cash register receipts or POS summaries
    → Business registration confirming cash-intensive 
      sector (restaurant, retail, parking)
    → Deposit pattern consistent with trading hours
      (Monday deposits larger = weekend takings)

  IF business justification documented:
    → Reduce structuring score by 40%
    → Maintain enhanced monitoring
    → Annual review of deposit pattern vs. revenue

  IF no business justification:
    → Maintain full structuring score
    → Escalate per standard workflow
```

---

### Edge Case 6 — International Student Tuition Payment

**Pattern:** A parent in Nigeria sends $25,000 to their child's UK university account. Nigeria is Tier 1C (FATF grey list). The transaction scores high on geography and amount.

**ScoreSentinel Rule — EC-006:**
```
IF international wire from FATF grey list country AND
receiver is an accredited educational institution:

  REQUIRE:
    → University enrollment confirmation
    → Payment matches tuition invoice amount (±10%)
    → Sender is documented family member of student

  IF all three conditions met:
    → Reduce geography score by 50%
    → Transaction type score unchanged
    → Document as education payment exemption
    → Annual review — does pattern remain consistent?
```

---

### Edge Case 7 — Payroll Multiple Same-Amount Transactions

**Pattern:** An employer sends 50 identical $3,200 wire transfers on the same day — one to each employee. Velocity rules flag this as suspicious high-frequency activity.

**ScoreSentinel Rule — EC-007:**
```
IF 10+ identical-amount transactions same day AND
customer is classified as Established Business:

  REQUIRE:
    → Payroll schedule on file
    → Receiver accounts are pre-approved beneficiaries
    → Pattern is consistent with historical payroll dates

  IF all conditions met:
    → Exempt from velocity rule VEL-001 and VEL-002
    → Standard monitoring maintained
    → Flag for annual payroll pattern review
```

---

## 5. False Positive Decision Rules

### 5.1 Clear Hierarchy for False Positive Decisions

```
LEVEL 1 — System Auto-Clear (no analyst needed):
  → Name collision with zero identifier matches 
    after EC-003 protocol
  → Common name PEP match with DOB gap > 10 years,
    different nationality, different profession

LEVEL 2 — Analyst Review Required (30 min max):
  → Adverse media Category E — single source, 
    no corroboration
  → Former PEP 13–36 months post-office
  → Cash-intensive business structuring pattern 
    with documented business justification

LEVEL 3 — Senior Analyst Review (same day):
  → Former PEP 0–12 months post-office
  → SDN collision with partial identifier match
  → Common name PEP with DOB within 5 years

LEVEL 4 — Compliance Officer Escalation (24 hours):
  → Any auto-alert regardless of subsequent analysis
  → Any case where analyst is uncertain after Level 3
```

### 5.2 Mandatory Documentation for Every False Positive Clearance

Regardless of level, every false positive clearance must document:
1. The specific rule or hit that generated the flag
2. The identifiers checked during disambiguation
3. The specific reason for clearance — one clear sentence
4. The reviewer's name and timestamp
5. The residual risk acknowledged and the control applied

---

## 6. False Positive Metrics & Targets

| Metric | Target | Breach Action |
|---|---|---|
| Overall false positive rate | < 15% | Review all rules — recalibrate thresholds |
| Screening FP rate (PEP/sanctions) | < 30% | Review matching thresholds and disambiguation protocols |
| Adverse media FP rate | < 40% | Review source quality and corroboration requirements |
| SDN name collision FP rate | < 50% | Review identifier requirements in EC-003 |
| Alert-to-SAR conversion ratio | 5:1 to 20:1 | Below 5:1 — thresholds too tight. Above 20:1 — thresholds too loose |
| Average analyst time per FP | < 30 minutes | Review decision rules — Level 1 auto-clears should be expanding |

---

## 7. Governance

### 7.1 Edge Case Library Maintenance

| Trigger | Action |
|---|---|
| New FP pattern identified by analyst | Add to edge case library within 30 days |
| FP rate exceeds target for 2 consecutive months | Full edge case review — identify new patterns |
| Regulatory guidance on FP management issued | Review all decision rules against new guidance |
| Annual review | Full library review — remove obsolete cases, add new ones |

### 7.2 SR 11-7 Checklist

| Requirement | Status | Location |
|---|---|---|
| False positive philosophy documented | ✅ Complete | Section 2 |
| Operational edge cases documented with rationale | ✅ Complete | Section 3 |
| Transaction edge cases documented | ✅ Complete | Section 4 |
| Decision hierarchy defined | ✅ Complete | Section 5 |
| False positive metrics and targets defined | ✅ Complete | Section 6 |
| Maintenance schedule defined | ✅ Complete | Section 7.1 |

### 7.3 Version History

| Version | Change | Date | Author |
|---|---|---|---|
| 1.0 | Initial release — 4 screening edge cases from operational HRDT experience, 3 transaction edge cases, full decision hierarchy | 25 April 2026 | Atul Krishnan, CAMS |

---

*ScoreSentinel | EDGE_CASES.md | False Positive Prevention Library | Authored by Atul Krishnan, CAMS | Version 1.0 | Day 9 of 60*
