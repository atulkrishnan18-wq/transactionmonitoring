# AUDIT_REQUIREMENTS.md — Compliance Audit Trail Framework

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.0 | **Day:** 13 of 60 | **Author:** Atul Krishnan, CAMS
**Last Updated:** 3 May 2026

---

## Table of Contents
1. [Purpose & Regulatory Basis](#1-purpose--regulatory-basis)
2. [Audit Trail Design Principles](#2-audit-trail-design-principles)
3. [Three-Point Decision Standard](#3-three-point-decision-standard)
4. [Transaction Scoring Audit Log](#4-transaction-scoring-audit-log)
5. [Customer Risk Audit Log](#5-customer-risk-audit-log)
6. [PEP & Sanctions Screening Audit Log](#6-pep--sanctions-screening-audit-log)
7. [Reviewer Sign-Off Framework](#7-reviewer-sign-off-framework)
8. [Documentation Timing Requirements](#8-documentation-timing-requirements)
9. [Jurisdiction-Specific Audit Requirements](#9-jurisdiction-specific-audit-requirements)
10. [Audit Log Retention](#10-audit-log-retention)
11. [Quality Assurance Framework](#11-quality-assurance-framework)
12. [SR 11-7 Model Risk Checklist](#12-sr-11-7-model-risk-checklist)
13. [Version History](#13-version-history)

---

## 1. Purpose & Regulatory Basis

This document defines the audit trail and logging requirements for ScoreSentinel. An audit trail is the legal and regulatory record that demonstrates every AML decision was made correctly, by the right person, at the right time, with the right evidence.

A missing or incomplete audit trail is treated by regulators as equivalent to not having made the compliance decision at all. Documentation is not an administrative task — it is the compliance deliverable.

### 1.1 Regulatory Basis

- **UK MLR 2017 Regulation 40** — Record keeping: firms must keep records of CDD measures, supporting evidence, and transaction monitoring for a minimum of 5 years
- **FCA Financial Crime Guide (FCG) 3.2** — Systems and controls must include adequate record keeping to demonstrate compliance decisions
- **FATF Recommendation 11** — Record keeping: transaction records and CDD documentation must be maintained for at least 5 years
- **FATF Recommendation 20** — Suspicious transaction reports: firms must maintain records of all STR/SAR decisions including the rationale for filing or not filing
- **EU 4AMLD / 6AMLD** — Strictest audit requirements in practice — member states including Ireland, UK (pre-Brexit equivalent), France, and Sweden apply rigorous documentation standards
- **MAS Notice 626 (Singapore)** — Detailed record keeping requirements for financial institutions
- **SR 11-7** — Model outputs must be fully traceable with documented decision rationale

### 1.2 Strictest Jurisdictions in Practice

> **Operational Note from HRDT Experience:** EU MLROs — particularly Ireland, UK, France, and Sweden — apply the most rigorous audit trail standards in practice. Malaysia and Hong Kong also apply strict documentation requirements consistent with FATF standards. ScoreSentinel's audit framework is calibrated to meet the highest standard across these jurisdictions, ensuring compliance wherever the engine is deployed.

---

## 2. Audit Trail Design Principles

### 2.1 Core Principles

```
PRINCIPLE 1 — CONTEMPORANEOUS DOCUMENTATION
  Every decision must be documented at the same
  time as the disposal of the case.
  
  NOT acceptable:
  → Documenting decisions hours or days later
  → Batch documentation at end of day
  → Reconstructing reasoning after the fact
  
  REQUIRED:
  → Documentation completed before case is
    marked as disposed in the system
  → Timestamp of documentation = timestamp
    of disposal decision

PRINCIPLE 2 — DECISION TRACEABILITY
  Every score, alert, and disposal decision must
  be traceable to:
  → The specific rule that fired
  → The specific evidence reviewed
  → The specific analyst who decided
  → The specific time the decision was made

PRINCIPLE 3 — THREE-POINT STANDARD
  Every match or false positive decision requires
  a minimum of three strong corroborating points
  — see Section 3

PRINCIPLE 4 — REVIEWER INDEPENDENCE
  MNN (Material Negative News) and PEP cases
  require a second, independent reviewer sign-off
  before disposal — see Section 7

PRINCIPLE 5 — IMMUTABILITY
  Audit logs must not be editable after submission.
  Corrections require a new log entry referencing
  the original — never overwriting existing records
```

### 2.2 What Must Always Be Logged

Every interaction with a customer record, transaction alert, or screening hit must generate an audit log entry. There are no exceptions — even a "no match" result on a screening check must be logged.

---

## 3. Three-Point Decision Standard

### 3.1 The Standard

> **ScoreSentinel requires a minimum of three strong corroborating points to establish either a confirmed match or a confirmed false positive during EDD manual review.**

This standard is derived from operational best practice at Tier 1 financial institutions and reflects the evidentiary standard regulators expect when reviewing disposal decisions.

### 3.2 Establishing a CONFIRMED MATCH — Three Points Required

To confirm a PEP, sanctions, or adverse media hit as genuine, the analyst must establish at least three of the following:

| Point | Evidence Type | Example |
|---|---|---|
| **Point 1 — Name** | Name match at 85%+ with documented variant explanation | "Mohamed Al-Qahtani" matches "Mohammed Al-Kahtani" — Arabic transliteration variant |
| **Point 2 — Date of Birth** | DOB match within 2 years | Customer DOB 1965 — SDN entry DOB 1963 — within tolerance |
| **Point 3 — Nationality** | Nationality or country of birth matches | Customer: Iranian national — SDN entry: Iranian national |
| **Point 4 — Geography** | Current or historical address overlaps | Customer: Tehran address — SDN entry: last known location Tehran |
| **Point 5 — Employer / Role** | Current or historical role matches | Customer: CEO of state bank — SDN entry: CEO of Bank Melli |
| **Point 6 — Associates** | Known associates or family members overlap | Customer's director is named associate of SDN-listed individual |
| **Point 7 — Adverse Media** | Corroborated media coverage from independent source | Two independent sources confirm name and role in financial crime |

```
CONFIRMED MATCH DOCUMENTATION TEMPLATE:

"Match confirmed on [DATE] by [ANALYST ID].

Point 1 — Name: Customer name [X] matches SDN/PEP
entry [Y] at [Z]% fuzzy match. Variant explained by
[Arabic transliteration / spelling variation / alias].

Point 2 — [Second identifier]: [Evidence and source].

Point 3 — [Third identifier]: [Evidence and source].

Conclusion: Three-point standard met. Match confirmed.
Escalated to [COMPLIANCE OFFICER] at [TIME] on [DATE].
Case reference: [REF NUMBER]."
```

### 3.3 Establishing a FALSE POSITIVE — Three Points Required

To clear a hit as a false positive, the analyst must establish at least three points of **distinction** between the customer and the matched entity:

| Point | Evidence Type | Example |
|---|---|---|
| **Point 1 — DOB Mismatch** | Date of birth differs by more than 2 years | Customer DOB 1990 — SDN entry DOB 1955 — 35-year gap |
| **Point 2 — Nationality Mismatch** | Different nationality or country of birth | Customer: British national — SDN entry: Iranian national |
| **Point 3 — Geography Mismatch** | No geographic overlap in current or historical addresses | Customer: UK resident 20 years — SDN entry: last known Beirut |
| **Point 4 — Profession Mismatch** | Incompatible professional roles | Customer: NHS nurse — SDN entry: arms dealer |
| **Point 5 — Photograph** | Visual confirmation of different individual | Photograph obtained from passport — clearly different person |
| **Point 6 — Employer Mismatch** | Employer/business has no connection to matched entity | Customer employed by NHS — SDN entity is private arms trader |
| **Point 7 — Independent Source** | Third-party source confirms customer is different person | Companies House, LinkedIn, public records confirm distinct identity |

### 3.4 Risk-Based Application of the Standard

> **The evidentiary requirement for case disposal in ScoreSentinel is risk-based, distinguishing between Identity Disambiguation and Investigative Depth.**

#### 3.4.1 Screening Match Alerts (Identity Disambiguation)
*   **Case Types:** Sanctions Hits, PEP Matches, Adverse Media.
*   **Standard:** **THREE-POINT STANDARD (MANDATORY)**.
*   **Rationale:** These cases require forensic proof of identity. The standard ensures that the customer is correctly identified as either a genuine match or a false positive via multi-factor corroboration.

#### 3.4.2 Transaction Risk Alerts (Investigative Depth)
*   **Case Types:** CRS >= 60, Structuring, Velocity, Mule Cluster Alerts.
*   **Standard:** **MANDATORY RATIONALE STANDARD**.
*   **Requirement:** Detailed step-by-step reasoning for the disposition, documenting why the activity is either suspicious or legitimate. 
*   **Note:** While the three-point standard is not technically enforced for these alerts, analysts are encouraged to use corroborating evidence (CDD docs) to support their rationale.

```
FALSE POSITIVE DOCUMENTATION TEMPLATE:

"False positive cleared on [DATE] by [ANALYST ID].

Hit: Customer [NAME] matched [SDN/PEP/ADVERSE MEDIA]
entry [ENTRY NAME] at [MATCH %].

Point 1 — [Distinction identifier]: [Evidence].
Source: [Where evidence was obtained].

Point 2 — [Distinction identifier]: [Evidence].
Source: [Where evidence was obtained].

Point 3 — [Distinction identifier]: [Evidence].
Source: [Where evidence was obtained].

Conclusion: Three-point distinction standard met.
Customer is a different individual from matched entry.
No further action required.
Residual risk: [State any residual risk acknowledged].
Enhanced rescreening applied: [Yes/No — frequency].
Cleared by: [ANALYST ID] at [TIMESTAMP]."
```

### 3.4 Why Three Points

Two points can be coincidental. Three independent points of match or distinction represent a deliberate evidentiary standard that:
- Prevents single-identifier false positives on common names
- Provides a defensible record if the decision is reviewed by a regulator
- Is consistent with the standard applied by Tier 1 banks in EDD manual review workflows
- Satisfies FCA FCG expectation that firms document "how they reached their conclusion"

---

## 4. Transaction Scoring Audit Log

Every transaction processed by ScoreSentinel must generate the following log entry automatically:

```
TRANSACTION SCORING LOG — MANDATORY FIELDS:

System Fields (auto-generated):
  transaction_id          : Unique transaction identifier
  customer_id             : Customer account reference
  timestamp_processed     : Date and time of scoring
  engine_version          : ScoreSentinel version number

Input Fields (transaction data):
  transaction_amount      : Amount in original currency
  transaction_currency    : Currency code
  transaction_type        : Type per TRANSACTION_RULES.md
  sender_country          : ISO country code
  receiver_country        : ISO country code
  customer_type           : Per CUSTOMER_RULES.md taxonomy

Module Scores (raw):
  customer_risk_raw       : Raw CCRS score (0–175)
  structuring_raw         : Raw structuring score (0–70)
  geography_raw           : Raw geography score (0–100)
  transaction_type_raw    : Raw transaction type score (0–55)

Module Scores (normalised):
  customer_normalised     : Normalised % (0–100)
  structuring_normalised  : Normalised % (0–100)
  geography_normalised    : Normalised % (0–100)
  transaction_normalised  : Normalised % (0–100)

Composite Score:
  crs                     : Composite Risk Score (0–100)
  risk_band               : Low/Medium-Low/Medium-High/High/Very High

Rules Fired:
  rules_fired             : List of all rule IDs triggered
                            e.g. ["VEL-015", "GEO-1C", "STR-001"]

Alert Status:
  alert_generated         : Boolean — true/false
  alert_type              : AML_RISK / SANCTIONS / PEP / STRUCTURING
  auto_alert_trigger      : Which independent trigger fired (if any)

Disposition:
  disposition_status      : PENDING / REVIEWED / CLEARED / ESCALATED / SAR_FILED
  reviewer_id             : Analyst ID (populated on review)
  review_timestamp        : Time of disposal decision
  reviewer_rationale      : Free text — mandatory for all non-standard disposals
  second_reviewer_id      : Required for MNN and PEP cases
  second_review_timestamp : Time of second review
  next_review_date        : Scheduled next review
```

---

## 5. Customer Risk Audit Log

Every change to a customer's risk score or risk band must be logged:

```
CUSTOMER RISK CHANGE LOG — MANDATORY FIELDS:

  customer_id             : Customer account reference
  change_timestamp        : Date and time of change
  previous_ccrs           : Previous Composite Customer Risk Score
  new_ccrs                : New Composite Customer Risk Score
  previous_risk_band      : Previous risk band
  new_risk_band           : New risk band
  change_trigger          : SCHEDULED / SDN_UPDATE / ADVERSE_MEDIA /
                            STAFF_REFERRAL / PERIODIC_REVIEW /
                            OWNERSHIP_CHANGE
  dimensions_changed      : Which of the 5 CCRS dimensions changed
  evidence_reviewed       : Documents or sources reviewed
  three_point_standard    : Three points documented (yes/no)
  reviewer_id             : Analyst ID
  review_timestamp        : Time of decision
  reviewer_rationale      : How the decision was reached
  approver_id             : Required if CCRS ≥ 90 or risk band escalation
  approver_timestamp      : Time of senior approval
  next_review_date        : Scheduled next review
```

---

## 6. PEP & Sanctions Screening Audit Log

Every screening check — including negative results — must be logged:

```
SCREENING AUDIT LOG — MANDATORY FIELDS:

  screening_id            : Unique screening event identifier
  customer_id             : Customer reference
  screening_timestamp     : Date and time of screening
  screening_trigger       : ONBOARDING / PERIODIC / SDN_UPDATE /
                            ADVERSE_MEDIA / STAFF_REFERRAL
  lists_screened          : Which lists were checked
                            e.g. ["OFAC_SDN", "WORLD_CHECK_PEP",
                                  "ADVERSE_MEDIA", "COMPANIES_HOUSE"]

Match Results:
  match_found             : Boolean
  match_percentage        : Fuzzy match score (if applicable)
  matched_entry           : Name and reference of matched entry
  match_category          : PEP_TIER_1 / PEP_TIER_2 / PEP_TIER_3 /
                            SDN / ADVERSE_MEDIA_A / ADVERSE_MEDIA_B /
                            ADVERSE_MEDIA_C / ADVERSE_MEDIA_D /
                            ADVERSE_MEDIA_E / NO_MATCH

Disposition (if match found):
  three_point_standard    : Met (yes/no)
  point_1_identifier      : First corroborating point
  point_1_source          : Source of evidence
  point_2_identifier      : Second corroborating point
  point_2_source          : Source of evidence
  point_3_identifier      : Third corroborating point
  point_3_source          : Source of evidence
  disposal_decision       : CONFIRMED_MATCH / FALSE_POSITIVE /
                            PENDING_REVIEW / ESCALATED
  disposal_rationale      : Free text — mandatory
  reviewer_id             : Primary analyst ID
  review_timestamp        : Time of disposal — must equal case close time
  second_reviewer_id      : Mandatory for MNN and PEP cases
  second_review_timestamp : Time of second review
  residual_risk_noted     : Any residual risk acknowledged
  enhanced_rescreening    : Frequency applied after false positive clearance
```

---

## 7. Reviewer Sign-Off Framework

### 7.1 When Second Review Is Required

| Case Type | Second Reviewer Required | Rationale |
|---|---|---|
| **MNN (Material Negative News)** | ✅ Always | Adverse media with financial crime category — too significant for single reviewer |
| **PEP Identification — any tier** | ✅ Always | PEP designation has significant consequences — requires independent confirmation |
| **Sanctions Hit — confirmed** | ✅ Always — Compliance Officer | Sanctions have legal liability — Compliance Officer must sign off |
| **SAR / STR Filing Decision** | ✅ Always — MLRO | Tipping-off risk and legal obligation — MLRO must authorise |
| **Risk Band Escalation (CCRS ≥ 90)** | ✅ Always — Senior Management | Highest risk customers require senior approval |
| **EDD Approval** | ✅ Always — Senior Analyst or above | EDD decisions must be reviewed by experienced reviewer |
| **Standard false positive clearance** | ❌ Not required | Subject to QA random sampling — see Section 11 |
| **Standard CDD — no flags** | ❌ Not required | Subject to QA random sampling |

### 7.2 Second Reviewer Independence

The second reviewer must be:
- Independent of the primary analyst — cannot be a direct supervisor reviewing their own team's work in the same case
- Of equal or higher seniority to the primary analyst
- Not involved in the original case decision prior to review

### 7.3 Sign-Off Documentation

```
SECOND REVIEWER LOG ENTRY:

"Secondary review completed on [DATE] by [REVIEWER ID].

Primary analyst decision: [DECISION]
Primary analyst rationale reviewed: [YES/NO]
Three-point standard verified: [YES/NO]

Second reviewer assessment:
[AGREE WITH PRIMARY DECISION]
OR
[DISAGREE — reason and revised decision]

Second reviewer disposition: [CONFIRMED / REVISED]
Second reviewer timestamp: [TIMESTAMP]"
```

---

## 8. Documentation Timing Requirements

### 8.1 The Contemporaneous Standard

> **All documentation must be completed at the same time as case disposal. Documentation completed after disposal is not compliant — it is reconstruction, not recording.**

| Case Type | Maximum Time to Document | Standard |
|---|---|---|
| Standard screening — no match | At time of disposal | Contemporaneous |
| Standard screening — false positive | At time of disposal | Contemporaneous |
| MNN / adverse media | At time of disposal | Contemporaneous |
| PEP identification | At time of disposal | Contemporaneous |
| Sanctions hit | At time of disposal — escalation within 24 hours | Contemporaneous + escalation deadline |
| SAR / STR filing | At time of filing decision | Contemporaneous |
| EDD completion | At time of case close | Contemporaneous |

### 8.2 Why Contemporaneous Documentation Matters

```
REGULATORY RISK OF LATE DOCUMENTATION:

1. FCA / EU MLRO view: Documentation completed
   after disposal raises questions about whether
   the analysis was actually performed or
   reconstructed to justify an earlier decision

2. OFAC view: In sanctions cases, late documentation
   suggests the institution did not have adequate
   controls at the time of the transaction

3. Litigation risk: In enforcement actions,
   backdated or reconstructed records can constitute
   evidence of willful non-compliance — significantly
   increasing penalty exposure

4. SR 11-7 view: Model decisions that are not
   contemporaneously documented cannot be validated
   — the model's actual behaviour is unknown
```

---

## 9. Jurisdiction-Specific Audit Requirements

### 9.1 UK — FCA / MLR 2017

| Requirement | Standard |
|---|---|
| Record retention | 5 years from end of customer relationship |
| CDD records | Must be kept for 5 years post-relationship |
| Transaction records | 5 years from date of transaction |
| SAR records | 5 years from date of filing |
| PEP records | Enhanced — must show ongoing monitoring decisions |
| Audit trail format | Must be retrievable and legible — electronic acceptable |

### 9.2 EU — 4AMLD / 6AMLD (Ireland, France, Sweden)

> **EU MLROs apply the strictest audit standards in practice.** Key additional requirements beyond UK baseline:

| Requirement | EU Standard |
|---|---|
| Record retention | 5 years minimum — some member states extend to 10 |
| Cross-border transaction records | Enhanced documentation required |
| UBO register verification | Must be documented for all legal entities |
| Risk assessment documentation | Full audit trail of risk assessment methodology |
| Training records | Staff AML training must be documented and retrievable |

### 9.3 Hong Kong — HKMA / AMLO

| Requirement | HK Standard |
|---|---|
| Record retention | 6 years from transaction date |
| CDD records | 6 years from end of relationship |
| STR records | 6 years from date of filing |
| Enhanced monitoring | Documentation of monitoring decisions for high-risk customers |

### 9.4 Malaysia — BNM / AMLA 2001

| Requirement | Malaysia Standard |
|---|---|
| Record retention | 6 years |
| STR filing | Must document reason for filing AND reason for not filing |
| CDD documentation | Full chain of evidence required |
| Ongoing monitoring | Documented review decisions required |

### 9.5 ScoreSentinel Default Standard

> **ScoreSentinel applies the highest common standard across all jurisdictions — 6-year retention, contemporaneous documentation, three-point decision standard, and mandatory second review for MNN and PEP cases. This ensures compliance across UK, EU, Hong Kong, and Malaysia without requiring jurisdiction-specific configuration in Version 1.0.**

---

## 10. Audit Log Retention

### 10.1 Retention Periods

| Log Type | Retention Period | Rationale |
|---|---|---|
| Transaction scoring logs | 6 years from transaction date | Highest jurisdiction standard |
| Customer risk change logs | 6 years from last change | Covers full review cycle |
| Screening logs — no match | 6 years from screening date | Proves screening was performed |
| Screening logs — match found | 6 years from disposal | Covers investigation period |
| SAR / STR filing logs | 6 years from filing date | Regulatory requirement |
| EDD records | 6 years from end of relationship | MLR 2017 requirement |
| Second reviewer sign-offs | 6 years from sign-off date | Independent validation record |
| QA review records | 6 years from review date | Model validation evidence |

### 10.2 Immutability Requirements

```
IMMUTABILITY RULES:

1. No audit log entry may be edited after submission

2. Errors must be corrected by creating a new log
   entry that:
   → References the original entry ID
   → States the reason for correction
   → Is signed by the correcting analyst AND
      their supervisor
   → Does not delete or overwrite the original

3. System must enforce immutability technically
   — no manual database edits permitted on
   audit log tables

4. Access to audit logs is read-only for all
   users except the system write process
```

---

## 11. Quality Assurance Framework

### 11.1 QA Sampling Approach

Second reviewer sign-off is not required for all cases — but QA sampling provides an equivalent control for standard cases:

| Case Type | QA Sample Rate | Who Conducts QA |
|---|---|---|
| Standard false positive — no flags | 10% random sample | QA Team — independent of case analyst |
| Standard CDD — no flags | 5% random sample | QA Team |
| Velocity alerts — cleared | 15% random sample | Senior Analyst |
| Geography alerts — cleared | 15% random sample | Senior Analyst |
| All MNN cases | 100% — mandatory second review | Senior Analyst (not QA) |
| All PEP cases | 100% — mandatory second review | Compliance Officer |

### 11.2 QA Review Criteria

For each sampled case, QA reviews:

```
QA CHECKLIST:

☐ Three-point decision standard met and documented
☐ All evidence sources cited and retrievable
☐ Documentation completed contemporaneously
   (timestamp of documentation = timestamp of disposal)
☐ Reviewer ID recorded
☐ Residual risk acknowledged where applicable
☐ Enhanced rescreening applied where required
☐ Decision is consistent with ScoreSentinel rules
☐ No evidence of outcome-driven documentation
   (reasoning written to justify a pre-formed conclusion)
```

### 11.3 QA Findings Management

```
QA FINDING LEVELS:

Level 1 — Administrative: Minor documentation gap
  → Feedback to analyst — no escalation

Level 2 — Process: Decision standard not fully met
  → Escalate to Team Leader
  → Analyst retraining required
  → Case may require re-review

Level 3 — Compliance: Decision appears incorrect
  → Escalate to Compliance Officer immediately
  → Case must be re-reviewed
  → Root cause analysis required

Level 4 — Regulatory: Potential reportable failure
  → Escalate to MLRO immediately
  → Consider whether SAR filing is required
  → Regulator notification may be required
```

---

## 12. SR 11-7 Model Risk Checklist

| Requirement | Status | Location |
|---|---|---|
| Audit trail purpose documented | ✅ Complete | Section 1 |
| Three-point decision standard defined | ✅ Complete | Section 3 |
| Match confirmation template provided | ✅ Complete | Section 3.2 |
| False positive clearance template provided | ✅ Complete | Section 3.3 |
| Transaction scoring log fields defined | ✅ Complete | Section 4 |
| Customer risk change log defined | ✅ Complete | Section 5 |
| Screening audit log defined | ✅ Complete | Section 6 |
| Reviewer sign-off framework defined | ✅ Complete | Section 7 |
| Contemporaneous documentation standard | ✅ Complete | Section 8 |
| Jurisdiction-specific requirements | ✅ Complete | Section 9 |
| Retention periods defined | ✅ Complete | Section 10 |
| Immutability requirements defined | ✅ Complete | Section 10.2 |
| QA framework defined | ✅ Complete | Section 11 |
| Independent validation | 🔄 Pending | Planned Day 45 |

---

## 13. Version History

| Version | Change | Date | Author |
|---|---|---|---|
| 1.0 | Initial release — three-point decision standard from operational HRDT experience, contemporaneous documentation requirement, MNN/PEP mandatory second review framework, jurisdiction-specific requirements covering UK FCA, EU 4AMLD/6AMLD, Hong Kong HKMA, Malaysia BNM, QA sampling framework | 3 May 2026 | Atul Krishnan, CAMS |

---

## 14. Indian Regulatory Compliance Checklist

This section supplements the global audit framework with a specific compliance checklist for Indian regulated entities deploying ScoreSentinel. All items below must be addressed by the client institution's compliance function. ScoreSentinel's technical output supports but does not substitute for the institution's own regulatory obligations.

**Last Updated:** September 2026 | **Applicable Jurisdiction:** India

---

### 14.1 PMLA 2002 Obligations

The Prevention of Money Laundering Act 2002 is the primary AML legislation in India. The following obligations apply to all Reporting Entities (REs) under Section 2(wa) of PMLA, including banking companies, financial institutions, and intermediaries.

#### Section 12(1) — Transaction Record Maintenance

| Requirement | Standard | ScoreSentinel Coverage | Client Action Required |
|---|---|---|---|
| Maintain records of all transactions | All transactions, regardless of amount or alert status | Every transaction submitted to ScoreSentinel is persisted to the `transactions` table with full scoring audit trail | Integrate ScoreSentinel API into all transaction processing workflows; do not selectively submit transactions |
| Records must be in a manner that enables reconstruction of individual transactions | Transaction ID, customer ID, amount, currency, type, scoring output, timestamp | Full reconstruction possible from `transactions` table using `transaction_id` as primary key | Retain the `transaction_id` returned by the API in your own systems for cross-reference |
| Records to be maintained for **5 years** from date of transaction | 5-year retention | ScoreSentinel database retains records indefinitely subject to storage; no auto-deletion policy | Confirm with your IT/legal team that ScoreSentinel records are within your 5-year retention policy scope |

**Audit checklist — Section 12(1):**
- [ ] All transactions processed by the institution flow through ScoreSentinel
- [ ] ScoreSentinel `transaction_id` is stored in the institution's core banking system
- [ ] Database records are confirmed to be retained for a minimum of 5 years
- [ ] Backup and restore procedure confirms data is recoverable for the full 5-year period

#### Section 12(1A) — Cash Transaction Reporting (CTR)

| Requirement | Standard | ScoreSentinel Coverage |
|---|---|---|
| Report all cash transactions above ₹10 lakh (INR 1,000,000) to FIU-IND within 15 days of close of month | Cash transactions ≥ ₹10,00,000 | Transaction type module flags cash transactions with elevated risk score; SCN-007 (CASH_INTENSIVE) detects high-volume cash patterns |
| Integrated cash transactions (structuring): report if single or linked transactions aggregate ≥ ₹10 lakh | Linked sub-threshold transactions | SCN-001 (STRUCTURING) and velocity module structuring dimension detect sub-threshold patterning |

**Audit checklist — Section 12(1A):**
- [ ] Institution's CTR filing process is triggered for any cash transaction ≥ ₹10 lakh regardless of ScoreSentinel CRS
- [ ] SCN-001 alerts are reviewed for CTR applicability — structuring patterns may indicate aggregate cash transactions requiring CTR
- [ ] CTR filing dates are recorded in the `alerts` table or in the institution's own case management system

#### Rule 3 — Suspicious Transaction Reporting (STR) to FIU-IND

| Requirement | Standard | ScoreSentinel Coverage |
|---|---|---|
| Report suspicious transactions to FIU-IND within **7 days** of suspicion arising | Any transaction giving rise to suspicion regardless of amount | ScoreSentinel alert (CRS ≥ 60 or auto-alert) triggers the STR workflow; STR filing decision rests with the designated officer |
| Suspicion may arise before or after transaction is completed | Monitoring must be ongoing | Velocity module provides rolling 7-day monitoring; rules engine provides pattern-based detection |
| No tipping off — client must not be informed that an STR has been or may be filed | Section 12(2) PMLA — tipping off prohibition | ScoreSentinel does not communicate alert status to customer-facing channels; API response is for compliance team use only |

**Audit checklist — Rule 3 (STR):**
- [ ] Designated Director / Principal Officer is identified and has authority to file STRs
- [ ] Escalation procedure from ScoreSentinel alert to STR decision is documented and tested
- [ ] STR filing deadline of 7 days from suspicion is tracked; alerts older than 7 days without disposition must be escalated
- [ ] Tipping-off risk: confirm ScoreSentinel API response is not visible to customers or front-line staff who interact with the subject customer
- [ ] All STRs filed are referenced in the corresponding `alerts` table entry

#### Rule 7 — Maintenance of Records

| Requirement | Standard | ScoreSentinel Coverage |
|---|---|---|
| Records must be maintained in a retrievable form | Must be able to produce records to regulatory authorities on demand | ScoreSentinel `GET /api/transactions/<id>` retrieves full scoring record; PostgreSQL database is queryable with full audit fields |
| Records must be legible and in English or a scheduled language | English | All ScoreSentinel outputs are in English |
| Principal Officer must have access to all records | Designated compliance officer must have unrestricted access | Supabase dashboard provides direct database access; API endpoints provide programmatic access |

**Audit checklist — Rule 7:**
- [ ] Principal Officer has credentials to access the ScoreSentinel database directly
- [ ] Record retrieval process is tested: confirm ability to produce a specific transaction record within 24 hours of a regulatory request
- [ ] Records are stored in a format that does not require proprietary software to read (PostgreSQL — open standard)

---

### 14.2 RBI KYC Directions 2025 Obligations

The Reserve Bank of India's KYC Master Directions (updated 2025) apply to all RBI-regulated entities. The following requirements are directly relevant to ScoreSentinel deployment.

#### Chapter IX — UAPA and UNSC Sanctions Compliance

| Requirement | Standard | ScoreSentinel Coverage |
|---|---|---|
| Screen all customers and transactions against UAPA Schedule I (banned organisations) | Section 51A UAPA 1967 | UAPA Schedule I screening integrated — all entries including aliases |
| Screen against UAPA Schedule IV (designated terrorists) | Section 51A UAPA 1967 | UAPA Schedule IV screening integrated with gazette reference numbers |
| Screen against all UNSC designations | UNSC Resolutions 1267, 1988, 1373 | UNSC 1267 and 1988 lists fully integrated; 1373 is addressed via UAPA Schedule IV cross-reference |
| Screening must be done at onboarding AND on an ongoing basis | Both point-in-time and continuous | ScoreSentinel screens on every transaction submission — continuous monitoring by design |

**Audit checklist — Chapter IX:**
- [ ] UAPA Schedule I and IV lists in ScoreSentinel are current — verify against latest MHA gazette notification
- [ ] UNSC 1267 and 1988 lists in ScoreSentinel are current — verify against latest UNSC publication
- [ ] Screening is applied to all customer names, not just the transaction initiator (beneficial owner, authorised signatories)
- [ ] List update procedure is documented and assigned to a named responsible individual

#### UAPA Order dated February 2, 2021 — Mandatory Action on Match

The RBI circular of February 2, 2021 (reference: DBR.AML.BC.No.26/14.01.001/2020-21) mandates the following immediate actions on any UAPA or UNSC match:

| Mandatory Action | Timing | ScoreSentinel Coverage |
|---|---|---|
| **Freeze the account** | Immediately on identification of match | `mandatory_actions` field in API response includes `FREEZE_ACCOUNT` on any UAPA/UNSC match |
| **Report to FIU-IND** | Without delay | `mandatory_actions` includes `REPORT_FIU_IND`; STR must be filed immediately |
| **Follow MHA advisory** | As per MHA communication | `FOLLOW_MHA_ADVISORY` included in mandatory actions; institution must contact MHA for guidance |
| **Do not tip off the customer** | At no point | ScoreSentinel does not expose alert status externally; tipping-off prohibition must be enforced by the institution |

**Audit checklist — UAPA February 2021 Order:**
- [ ] Account freeze capability is connected to the ScoreSentinel UAPA alert — alert must trigger automatic freeze, not just a notification
- [ ] FIU-IND reporting template is pre-populated and the filing process takes less than 24 hours from alert generation
- [ ] MHA advisory protocol is documented — institution knows how to contact MHA and what information to provide
- [ ] Three-point identifier verification is completed before confirming the match (see `AUDIT_REQUIREMENTS.md` Section 3)

#### Customer Due Diligence Requirements

| Requirement | Standard | ScoreSentinel Coverage |
|---|---|---|
| Risk-categorise all customers as Low, Medium, or High | Based on customer type, geography, transaction patterns | Customer risk module (CCRS) produces a normalised score driving risk band categorisation in the `customers` table |
| Simplified due diligence for low-risk customers | Low-risk: reduced monitoring frequency | CRS < 20 = Low Risk band; monitoring frequency aligned to risk band |
| Standard due diligence for medium-risk customers | Medium-risk: standard monitoring | CRS 21–59 = Medium-Low or Medium-High bands |

#### Enhanced Due Diligence for Politically Exposed Persons (PEPs)

| Requirement | Standard | ScoreSentinel Coverage |
|---|---|---|
| Senior management approval for PEP relationships | Before or during onboarding | PEP Tier 1 triggers auto-alert; institution must obtain SM approval as a separate process |
| Source of wealth / source of funds for PEPs | Required for all PEP accounts | Not automated by ScoreSentinel; must be collected by the institution's KYC team and documented in `alerts` table |
| Ongoing enhanced monitoring for PEPs | Increased frequency and scrutiny | PEP status elevates CCRS in every scored transaction; alerts route to enhanced review queue |
| EDD documentation in file | Documented before first transaction | ScoreSentinel `alerts` table `internal_summary` field must contain EDD reference |

**Audit checklist — PEP EDD:**
- [ ] All PEP customers are marked in ScoreSentinel with correct PEP tier (Tier 1, 2, or 3)
- [ ] Senior management approval document reference is stored in the customer record
- [ ] Source of wealth evidence is on file and referenced in `alerts.reviewer_rationale`
- [ ] PEP review frequency meets RBI requirement (at minimum annual for all PEPs; quarterly for Tier 1)

---

### 14.3 FIU-IND Reporting Obligations

Financial Intelligence Unit — India (FIU-IND) is the nodal agency for receiving and processing financial intelligence reports under PMLA 2002.

#### Suspicious Transaction Reports (STR)

| Requirement | Deadline | ScoreSentinel Integration |
|---|---|---|
| File STR for any transaction giving rise to suspicion | **Within 7 days** of suspicion arising | ScoreSentinel alert (CRS ≥ 60 or auto-alert) is the trigger event; alert `created_at` timestamp is the start of the 7-day clock |
| STR must contain: customer details, transaction details, grounds for suspicion, details of officer filing | As per FIU-IND format | ScoreSentinel API response provides customer ID, transaction details, CRS, rules fired, and module scores — all required as grounds for suspicion |
| Maintain record of all STRs filed | 5 years | Reference FIU-IND reference number in `alerts.str_reference` field (available in `mule_clusters` table; replicate to `alerts`) |

**Audit checklist — STR:**
- [ ] Alert age monitoring: all alerts with status `PENDING` and `created_at` > 5 days old must be escalated daily
- [ ] STR filing log maintained: every filed STR has a FIU-IND acknowledgement reference stored
- [ ] Annual STR reconciliation: total STRs filed reconciles with total alerts dispositioned as True Positive or Escalated

#### Cash Transaction Reports (CTR)

| Requirement | Deadline | ScoreSentinel Integration |
|---|---|---|
| File CTR for all cash transactions ≥ ₹10 lakh | Within **15 days** of close of the month | SCN-007 (CASH_INTENSIVE) flags high-volume cash patterns; institution must run a monthly CTR extraction query |
| Mandatory CTR regardless of alert status | CTR is a reporting obligation, not a risk decision | Even if CRS is low, all cash transactions above threshold must be reported |

**Monthly CTR extraction query (guidance):**
```sql
SELECT 
    transaction_id,
    customer_id,
    timestamp_processed,
    transaction_amount,
    transaction_currency,
    transaction_type,
    sender_country,
    receiver_country
FROM transactions
WHERE transaction_type ILIKE '%cash%'
  AND transaction_amount >= 1000000  -- INR 10 lakh
  AND timestamp_processed >= DATE_TRUNC('month', NOW() - INTERVAL '1 month')
  AND timestamp_processed < DATE_TRUNC('month', NOW())
ORDER BY timestamp_processed;
```

#### Non-Profit Organisation Transaction Reports (NTR)

| Requirement | Deadline | ScoreSentinel Integration |
|---|---|---|
| File NTR for all cross-border transactions of NGOs/NPOs | Within **15 days** of close of the month | Geography module flags cross-border transactions; customer type `Non-Profit Organisation` elevates CCRS |
| Threshold: All cross-border transactions by NPOs | No minimum threshold | Filter transactions table by customer_type = 'NGO' or 'NPO' |

---

### 14.4 FATF Recommendations Addressed by ScoreSentinel

| FATF Recommendation | Full Title | ScoreSentinel Implementation |
|---|---|---|
| **Recommendation 1** | Risk-Based Approach | Five-module weighted CRS implements a risk-proportionate scoring framework; higher-risk customers, geographies, and transaction types receive proportionally higher scores. Alert threshold of 60 ensures resources are focused on genuinely elevated risk. |
| **Recommendation 6** | Targeted Financial Sanctions Related to Terrorism and Terrorist Financing | Six-list sanctions waterfall executed before every transaction scores. Any match triggers immediate auto-alert with mandatory freeze action. No delay — sanctions screening completes in milliseconds per transaction. |
| **Recommendation 10** | Customer Due Diligence | Customer risk module (CCRS) implements a full risk-based CDD framework covering entity type, PEP status, beneficial ownership transparency, account age, and sanctions screening. EDD-level scoring applied to PEPs, shell companies, and high-risk entity types. |
| **Recommendation 29** | Financial Intelligence Units | Alert output is structured for FIU-IND STR submission. Rules fired provide human-readable grounds for suspicion. Module scores provide quantitative evidence. Velocity module provides historical transaction context. All required STR fields are captured in the scoring output and `alerts` table. |

**Additional FATF Recommendations — Partial Coverage:**

| Recommendation | Partial Coverage | Gap |
|---|---|---|
| Rec. 12 — PEPs | PEP scoring in customer module; PEP auto-alert for Tier 1 | No commercial PEP database — reliance on self-reported PEP status |
| Rec. 19 — Higher-Risk Countries | Geography module applies elevated scores for FATF grey/black list jurisdictions | Scores are updated on FATF plenary schedule, not real-time |
| Rec. 20 — STR Reporting | Alert pipeline generates STR-ready output | STR filing is a human decision — ScoreSentinel does not auto-file |
| Rec. 28 — Regulation of DNFBPs | ScoreSentinel can be deployed by reporting entities beyond banks | DNFBP-specific typologies not yet implemented in rules engine |

---

### 14.5 Indian Regulatory Compliance Summary Dashboard

| Regulatory Area | Regulation | ScoreSentinel Status | Client Action |
|---|---|---|---|
| Transaction record maintenance | PMLA 2002 Section 12(1) | ✅ Full coverage | Integrate all transactions; confirm 5-year retention |
| Cash transaction reporting | PMLA 2002 Section 12(1A) | ✅ Detection; ⚠️ Filing is client obligation | Run monthly CTR extraction; file within 15 days of month-end |
| Suspicious transaction reporting | PMLA 2002 Rule 3 | ✅ Alert generation; ⚠️ STR filing is client obligation | File STR within 7 days of alert; monitor alert age |
| UAPA sanctions screening | Section 51A UAPA 1967 | ✅ Full — 6-list waterfall | Confirm lists are current; test freeze procedure |
| UAPA match mandatory actions | RBI Circular Feb 2, 2021 | ✅ mandatory_actions in API response | Connect freeze action to core banking; train staff |
| PEP enhanced due diligence | RBI KYC Directions 2025 Ch. VII | ✅ Scoring; ⚠️ EDD process is client obligation | Document source of wealth; obtain senior management approval |
| Ongoing transaction monitoring | RBI KYC Directions 2025 para 37 | ✅ Velocity module + rules engine | Ensure all transactions submitted — no cherry-picking |
| Data localisation | RBI Payment Data Policy 2018 | ⚠️ GAP — data currently processed outside India | Disclose to regulator; monitor Mumbai migration progress |
| STR format compliance | FIU-IND STR format | ✅ ScoreSentinel output maps to STR fields | Pre-populate STR template using ScoreSentinel API response |
| Risk-based approach | FATF Recommendation 1 | ✅ Five-module weighted CRS | Document risk appetite and threshold rationale for regulator |

---

*Last Updated: September 2026 | Section 14 added by: Atul Krishnan, CAMS*

---

*ScoreSentinel | AUDIT_REQUIREMENTS.md | Compliance Audit Trail Framework | Authored by Atul Krishnan, CAMS | Version 1.1 | September 2026 (Section 14 added)*
