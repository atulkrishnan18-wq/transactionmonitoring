# PEP_RULES.md — PEP Matching & Beneficial Owner Risk Logic

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.0 | **Day:** 11 of 60 | **Author:** Atul Krishnan, CAMS
**Last Updated:** 1 May 2026

---

## Table of Contents
1. [Purpose & Regulatory Basis](#1-purpose--regulatory-basis)
2. [PEP Tier Classification — UK MLR 2017](#2-pep-tier-classification--uk-mlr-2017)
3. [PEP Scoring & Alert Rules](#3-pep-scoring--alert-rules)
4. [Former PEP De-escalation Framework](#4-former-pep-de-escalation-framework)
5. [Beneficial Owner Definition & Thresholds](#5-beneficial-owner-definition--thresholds)
6. [Beneficial Owner Risk Logic](#6-beneficial-owner-risk-logic)
7. [Fuzzy Name Matching — Algorithm & Thresholds](#7-fuzzy-name-matching--algorithm--thresholds)
8. [Screening Workflow](#8-screening-workflow)
9. [False Positive Management](#9-false-positive-management)
10. [Regional Scope & ScoreSentinel 2.0 Roadmap](#10-regional-scope--scoresentinel-20-roadmap)
11. [SR 11-7 Model Risk Checklist](#11-sr-11-7-model-risk-checklist)
12. [Assumptions & Limitations](#12-assumptions--limitations)
13. [Version History](#13-version-history)

---

## 1. Purpose & Regulatory Basis

This document defines the PEP matching rules and beneficial owner risk logic for ScoreSentinel. PEP and beneficial owner screening are mandatory components of Customer Due Diligence under UK and global AML frameworks.

### 1.1 Regulatory Basis

- **UK Money Laundering Regulations 2017 (MLR 2017)** — Primary framework. Defines PEPs, beneficial owners, and enhanced due diligence requirements for UK-regulated entities
- **FCA Financial Crime Guide (FCG)** — FCA guidance on PEP identification, risk assessment, and ongoing monitoring
- **FATF Recommendation 12** — PEPs: enhanced measures required for all PEP relationships
- **FATF Recommendation 10** — CDD: beneficial ownership must be identified and verified for all legal entity customers
- **OFAC 50% Ownership Rule** — Entities owned 50%+ by sanctioned individuals are themselves treated as sanctioned
- **FinCEN CDD Rule (31 CFR 1010.230)** — Beneficial ownership identification mandatory for legal entity customers

### 1.2 UK Scope — Version 1.0

> **ScoreSentinel Version 1.0 applies UK MLR 2017 as the primary PEP and beneficial owner framework.** This covers both domestic UK PEPs and foreign PEPs transacting with UK-regulated entities. Regional overlays for APAC, EU, US, and GCC jurisdictions are planned for ScoreSentinel 2.0 — see Section 10.

---

## 2. PEP Tier Classification — UK MLR 2017

ScoreSentinel uses a three-tier PEP classification system. Tiers are assigned based on the level of political power, financial control, and corruption risk associated with the role — not solely on seniority.

### 2.1 Tier 1 — Highest Risk (Auto-Alert + Mandatory EDD)

Individuals holding or having held positions with the highest level of political authority, state control, or international equivalence:

| Category | Examples |
|---|---|
| Head of State / National Government | President, Prime Minister, Premier, Chancellor |
| Deputy Head of State | Vice President, Deputy Prime Minister |
| National Cabinet Ministers | Minister of Finance, Secretary of State, Home Secretary |
| Deputy Cabinet Ministers | First-level deputies to Cabinet Ministers |
| Royal Families & Dynasties | All members of recognised royal families |
| Heads of Supranational Entities | EU Commission President, World Bank President, IMF Managing Director |
| Designated Senior Religious Leaders | Pope of Roman Catholic Church, Supreme Leader (Ayatollah) of Iran |
| Chief of Staff to Head of State/PM | Directly appointed political advisors to President or PM |

> **Domestic UK PEPs — Tier 1:** UK Cabinet Ministers and their first-level deputies are classified as Tier 1 under UK MLR 2017, which explicitly includes domestic PEPs. A sitting UK Chancellor of the Exchequer is Tier 1 — same as a foreign Finance Minister.

---

### 2.2 Tier 2 — High Risk (Mandatory EDD — No Auto-Alert)

Individuals holding senior positions with significant authority but below the executive/cabinet level:

| Category | Examples |
|---|---|
| National Legislators | MPs (House of Commons), Members of House of Lords, Members of Congress (Senate/House), National Parliament members |
| Senior Judiciary | Supreme Court Justices, Final Appeal Court Judges, Constitutional Court Judges, Attorney General, Prosecutor General |
| Senior Military Officers | Generals, Admirals, Marshals (national armed forces) |
| Central Bank Governors & Board | Central Bank Governor, Deputy Governor, Board Members, Central Bank Auditors |
| Senior Diplomatic Service | Ambassadors, Chargés d'Affaires, Consul Generals |
| Senior Police Leadership | Chief of Police, Chief Constable, Chief Superintendent (national level) |
| SOE Senior Executives | Board members and senior decision-making executives of state-owned enterprises, nationalised industries, and government-controlled foundations |
| State / Provincial Heads | State Governors, Provincial Premiers, Heads of Devolved Administrations (Scottish First Minister, Welsh First Minister) |
| State / Provincial Legislators | Members of State Upper and Lower Houses, Members of Scottish Parliament, Senedd |
| State / Provincial Senior Judiciary | State Attorney Generals, State Supreme Court Justices |
| Senior State Agency Officials | Agency Directors, Secretaries of State agencies |
| Mayors of Major Cities | Mayors, City Council Members, County Commissioners of cities with population exceeding 1.5 million |
| Senior National Political Party Heads | Leaders of major national political parties (e.g. Leader of the Opposition, Party Chairpersons) |
| Senior Members of Executive Administration | Government-appointed political advisors below Chief of Staff level |

> **Domestic UK PEPs — Tier 2:** UK MPs (backbench), members of the House of Lords, Scottish Parliament members, and Welsh Senedd members are classified as Tier 2. They hold national legislative authority but not executive/cabinet power.

---

### 2.3 Tier 3 — Elevated Risk (Enhanced Monitoring)

Individuals with indirect PEP exposure through family relationship or close business association:

| Category | Definition | Degrees of Separation |
|---|---|---|
| **Immediate Family** | Spouse or civil partner, children (including step-children), parents (including step-parents) | 1 degree |
| **Extended Family** | Siblings, parents-in-law, siblings-in-law, children's spouses | 2 degrees |
| **Close Business Associates** | Individuals known to have joint beneficial ownership of a legal entity, joint financial interests, or close business relationships with a PEP | As identified |
| **Beneficial Owners of PEP-Controlled Entities** | Any individual who is beneficial owner of an entity known to be controlled by a Tier 1 or Tier 2 PEP | As identified |

> **Tier 3 Scope Note:** ScoreSentinel applies Tier 3 to immediate and extended family as defined above. Close associates are included where the relationship is documented or reasonably known. Speculative associations without evidence are not sufficient for Tier 3 classification — this prevents over-flagging common-name coincidences.

---

### 2.4 PEP Tier Summary

| Tier | Risk Level | Alert Type | EDD Required | Review Frequency |
|---|---|---|---|---|
| Tier 1 | 🚨 Highest | Auto-Alert — bypasses CRS | Mandatory — Senior approval | Every 3 months |
| Tier 2 | 🔴 High | AML Risk Alert if CRS ≥ 60 | Mandatory | Every 6 months |
| Tier 3 | 🟠 Elevated | Enhanced monitoring | Enhanced CDD | Every 12 months |

---

## 3. PEP Scoring & Alert Rules

PEP scores feed into the **Customer Risk module (CCRS)** as defined in `CUSTOMER_RULES.md` Section 3.6.

| PEP Status | Customer Risk Score Added | Alert Rule |
|---|---|---|
| Confirmed Tier 1 PEP | +50 | 🚨 AUTO-ALERT regardless of CRS |
| Confirmed Tier 2 PEP | +40 | EDD mandatory — alert if CRS ≥ 60 |
| Confirmed Tier 3 PEP | +30 | Enhanced monitoring |
| Adverse Media — confirmed financial crime (PEP-related) | +35 | EDD mandatory |
| Adverse Media — unconfirmed / single source | +10 | Flag for analyst review |
| No PEP match | +0 | Standard monitoring |

### 3.1 Why Tier 1 Auto-Alerts

UK MLR 2017 Regulation 35 requires enhanced due diligence for all PEP relationships. For Tier 1 PEPs — heads of state and cabinet ministers — the FCA FCG states that the risk is sufficiently elevated that no transaction should be processed without a compliance review. Auto-alert ensures this requirement is met regardless of transaction amount or CRS.

---

## 4. Former PEP De-escalation Framework

A former PEP retains elevated monitoring status for a defined period after leaving public office. ScoreSentinel applies the following de-escalation framework, consistent with FCA guidance and `EDGE_CASES.md` Section 3 (Edge Case 2):

```
FORMER PEP DE-ESCALATION:

0–12 months post-office:
  → Maintain full original PEP Tier status
  → Full EDD mandatory
  → Rationale: Influence, assets, and relationships
    from office remain active — FCA minimum requirement

13–36 months post-office:
  → Downgrade one tier
    (Tier 1 → Tier 2, Tier 2 → Tier 3)
  → Enhanced monitoring maintained
  → Annual review required
  → Rationale: Direct influence waning but network intact

37+ months post-office:
  → Downgrade to Tier 3 OR standard customer
    if no other risk factors present
  → Standard CDD with annual PEP re-check
  → Rationale: Risk has materially reduced —
    proportionate monitoring required under MLR 2017

NEVER DE-ESCALATE IF ANY OF:
  → Individual held Head of State / PM / President role
    (maintain Tier 1 indefinitely)
  → Active corruption investigation or prosecution
  → Adverse media Category A or B in last 24 months
  → Customer domiciled in jurisdiction with CPI < 30
    per GEO_RULES.md
```

---

## 5. Beneficial Owner Definition & Thresholds

### 5.1 Who Is a Beneficial Owner

Under UK MLR 2017 and ScoreSentinel, an individual is a Beneficial Owner if they meet **any** of the following:

| Criterion | Threshold | Definition |
|---|---|---|
| **Shares / Voting Rights** | > 25% | Ownership or control over more than 25% of the entity's shares or voting rights — directly or indirectly |
| **Ultimate Control** | Any level | Ultimate control over the entity or its management, even without shareholding — e.g. ability to appoint or remove directors |
| **Legal Representative** | Sole control | A Legal Representative with sole control over the account is treated as a Beneficial Owner |

### 5.2 Fallback Beneficial Owner Rule

> **If no individual meets the 25% ownership or control threshold, the CEO or one equivalent person must be identified as the Fallback Beneficial Owner.**

```
FALLBACK BO RULES:

Required for:
  → All entity types including:
     - Standard corporate entities
     - State-Owned Enterprises incorporated under company law
     - Sovereign Wealth Funds

NOT required for:
  → Direct dealings with a Government Department,
    government ministry, or equivalent authority

The one equivalent person:
  → A single individual with significant responsibility
    for managing or directing the entity
  → Must be identified, verified, and documented
    even when no 25%+ shareholder exists
```

### 5.3 Nominee Shareholders

If a Beneficial Owner is also a Nominee Shareholder, this must be documented. Nominee shareholders acting on behalf of an undisclosed principal represent elevated beneficial ownership opacity — add +15 to ownership transparency dimension in Customer Risk module.

### 5.4 Dual Threshold System — UK MLR vs OFAC

ScoreSentinel applies **two independent beneficial ownership thresholds** serving different regulatory purposes:

| Threshold | Framework | Trigger | Action |
|---|---|---|---|
| **> 25% ownership** | UK MLR 2017 | Beneficial owner identification required | EDD — collect full BO data per Section 5.5 |
| **≥ 50% ownership by sanctioned entity** | OFAC 50% Rule | Entity treated as sanctioned | 🚨 AUTO-ALERT — sanctions screening — see `GEO_RULES.md` Section 5.4 |

> **Key Distinction:** The 25% threshold triggers a **due diligence obligation** — collect and verify BO data. The 50% OFAC threshold triggers a **sanctions alert** — the entity is treated as if it appears on the SDN list regardless of its own name. Both thresholds must be checked independently for every legal entity customer.

---

## 6. Beneficial Owner Risk Logic

### 6.1 Data Collection Requirements

For every identified Beneficial Owner, the following must be collected and verified:

```
MANDATORY BO DATA ELEMENTS:

1. Full legal name
2. Country of residence
3. Date of birth
   (Minimum MM/YYYY acceptable if full DOB refused
    — document business acceptance decision)
4. Percentage of ownership (if applicable)
5. Source of Wealth confirmation (if applicable)
6. Confirmation whether BO resides in UK High Risk
   Third Country — if yes → EDD required
7. Confirmation whether BO is also a Nominee Shareholder
```

### 6.2 Acceptable Sources for BO Identification

| Source | Acceptability |
|---|---|
| Client confirmation of individuals owning > 25% | ✅ Acceptable — primary source |
| Customer's public website (certain entity types) | ✅ Acceptable |
| Official government company registry (Companies House PSC register) | ✅ Acceptable — preferred for UK entities |
| Trade / corporate registers | ✅ Acceptable |
| Prospectus, offering memorandum, Investment Management Agreement | ✅ Acceptable |
| Representation letter from reputable law firm or accountancy firm | ✅ Acceptable |
| Representation letter from regulated financial institution (approved) | ✅ Acceptable |
| Most recently published audited financial statements (up to 18 months old) | ✅ Acceptable |
| SEC filings or Form ADV (within last 12 months) | ✅ Acceptable |
| Unverified internet search alone | ❌ Not acceptable as sole source |

> **Companies House Integration Note:** For UK-incorporated entities, the PSC (Persons with Significant Control) register at Companies House is the primary verification source for beneficial ownership. ScoreSentinel flags any discrepancy between client-stated BO and Companies House PSC data as a high-risk indicator requiring immediate escalation.

### 6.3 BO Risk Scoring

| Beneficial Owner Status | Ownership Transparency Score Added | Action |
|---|---|---|
| BO unidentified or unverifiable | +25 | Mandatory KYC remediation — 30-day deadline |
| Nominee shareholder present | +15 | Document nominee relationship — identify principal |
| BO identified — resides in UK High Risk Third Country | +20 | EDD mandatory per GEO_RULES.md |
| BO is also a PEP (any tier) | Apply PEP score from Section 3 | Combined BO + PEP risk |
| BO identified and verified — clean | +0 | Standard monitoring |
| Fallback BO applied (no 25%+ owner) | +10 | Document fallback — annual review |

---

## 7. Fuzzy Name Matching — Algorithm & Thresholds

### 7.1 Matching Threshold — Why 85%

ScoreSentinel uses an **85% fuzzy match threshold** for PEP and sanctions name screening. This threshold was selected as the optimisation point between false positive rate and false negative rate:

| Threshold | Est. False Positive Rate | Est. False Negative Rate | Assessment |
|---|---|---|---|
| 70% | ~55% | ~1% | Operationally unmanageable |
| 80% | ~35% | ~3% | Too many false positives — alert fatigue |
| **85%** | **~12%** | **~4–5%** | **Optimal — industry standard** |
| 90% | ~5% | ~8–12% | Miss rate too high — regulatory risk |
| 95% | ~2% | ~20%+ | Unacceptable miss rate |

**Industry alignment:** 85% is the default threshold used by SWIFT Sanctions Screening, Refinitiv World-Check, and Actimize — the three dominant enterprise sanctions screening platforms globally. ScoreSentinel aligns with industry standard.

### 7.2 Regulatory Defence — OCC / FCA Examiner Script

If challenged on the 85% threshold by a regulator:

> *"85% was selected as the threshold that optimises between false positive rate and false negative rate simultaneously. Below 85%, our false positive rate exceeds our 15% operational target — creating alert fatigue that reduces program effectiveness. Above 85%, our false negative rate increases materially on transliteration variations, which is the most documented sanctions evasion technique.*
>
> *85% is also the default threshold used by SWIFT, Refinitiv, and Actimize. Aligning with industry standard provides a defensible benchmark while we complete back-testing against our own transaction population.*
>
> *Our model documentation explicitly acknowledges this threshold is based on industry benchmarks rather than back-tested data — that level of documented transparency is what SR 11-7 requires."*

**On false negative rate:**
> *"At 85% our estimated false negative rate is 4–5% based on published vendor benchmarking. Back-testing against our own population is planned. If back-testing shows a rate materially above 7%, our documented recalibration protocol requires a threshold review."*

### 7.3 Match Categories & Actions

| Match % | Match Type | Example | Action |
|---|---|---|---|
| 100% | Exact match | BANK MELLI IRAN | 🚨 Block + Sanctions Alert immediately |
| 85–99% | Strong fuzzy match | Mohamed Al-Qahtani vs Mohammed Al-Kahtani | 🚨 Hold + escalate for review |
| 70–84% | Moderate fuzzy match | Ali Hassan vs Ali Hasan | ⚠️ Flag for analyst review — do not block |
| < 70% | No match | Ali Hassan vs Alan Harris | ✅ Clear — no action required |

### 7.4 Algorithm Specification

ScoreSentinel recommends **Jaro-Winkler distance** as the primary matching algorithm for name screening:

```
WHY JARO-WINKLER:

1. Prefix weighting — gives higher scores to names
   that share the same beginning characters
   (Mohammed / Mohamed / Mohammad all match well)

2. Handles transposition — catches letter-order
   variations common in transliteration
   (Qahtani / Kahtani / Qatani)

3. Industry standard — used by major TM vendors
   including Actimize and Temenos

SECONDARY ALGORITHM — Levenshtein Distance:
  Used as a cross-check for short names where
  Jaro-Winkler may over-score partial matches
  (e.g. "Ali" vs "Al" — Jaro-Winkler scores high,
   Levenshtein correctly scores lower)

COMBINED APPROACH:
  Final match score = weighted average of
  Jaro-Winkler (70%) + Levenshtein (30%)
```

### 7.5 Transliteration Variants — High-Collision Name Handling

The following name categories require enhanced disambiguation before escalation — consistent with `EDGE_CASES.md` EC-003 and EC-004:

| Name Origin | High-Collision Examples | Protocol |
|---|---|---|
| Arabic | Mohammed/Mohamed/Ahmad/Abdullah | Apply EC-004 — 3-step DOB/nationality/profession check |
| South Asian | Singh/Kumar/Sharma/Khan/Patel | Apply EC-004 — 3-step disambiguation |
| Chinese | Wang/Li/Zhang/Chen/Liu | Apply EC-004 — include DOB as primary disambiguator |
| African | Diallo/Traore/Coulibaly/Koné | Apply EC-004 — nationality check essential |

---

## 8. Screening Workflow

### 8.1 When Screening Occurs

| Trigger | Frequency | Scope |
|---|---|---|
| New customer onboarding | Once — before account activation | Full PEP + sanctions + adverse media + BO |
| Periodic review — Tier 1 PEP | Every 3 months | Full rescreening |
| Periodic review — Tier 2 PEP | Every 6 months | Full rescreening |
| Periodic review — Tier 3 / standard | Every 12–24 months | Full rescreening |
| SDN list update (OFAC) | Within 24 hours | Rescreen entire active customer base |
| Adverse media alert | Immediate | Triggered rescreening of affected customer |
| Staff referral | Immediate | Full rescreening |

### 8.2 Six Mandatory Screening Fields

Consistent with `GEO_RULES.md` Section 5.1:

| # | Field | Screened Against |
|---|---|---|
| 1 | Customer name | PEP database + OFAC SDN |
| 2 | Beneficial owner name(s) | PEP database + OFAC SDN |
| 3 | Country of residence | GEO_RULES.md tier classification |
| 4 | Counterparty name (transactions) | OFAC SDN |
| 5 | Intermediary institution | OFAC SDN |
| 6 | Country of incorporation | GEO_RULES.md tier classification |

### 8.3 Post-Hit Workflow

```
PEP HIT WORKFLOW:

Step 1 → Generate PEP Alert — type "PEP" not "AML Risk"
Step 2 → Apply fuzzy match disambiguation (Section 7.3)
Step 3 → Determine tier — Tier 1, 2, or 3
Step 4 → Tier 1 → Escalate to Compliance Officer
          within 24 hours — EDD mandatory
          Tier 2 → Analyst review within 5 business days
          Tier 3 → Enhanced monitoring — next review cycle
Step 5 → Real Hit → Complete EDD, document SOW,
          obtain senior approval (Tier 1),
          ongoing enhanced monitoring
Step 6 → False Positive → Document full disambiguation
          reasoning — see EDGE_CASES.md EC-004
          Clear with documented rationale
          Apply enhanced rescreening frequency
```

---

## 9. False Positive Management

PEP screening generates the highest false positive volume of any screening type — particularly for common names in APAC, MENA, and African markets.

### 9.1 PEP-Specific False Positive Targets

| Metric | Target |
|---|---|
| Overall PEP screening false positive rate | < 30% |
| Common name PEP match false positive rate | < 50% |
| Former PEP false positive rate | < 20% |
| Average analyst time per PEP false positive | < 30 minutes |

### 9.2 Primary False Positive Categories

Refer to `EDGE_CASES.md` for full protocols:

| False Positive Type | Edge Case Reference |
|---|---|
| Adverse media — wrong person | EC-001 |
| Former PEP — left office | EC-002 |
| SDN name collision — common name | EC-003 |
| Common name PEP match | EC-004 |

---

## 10. Regional Scope & ScoreSentinel 2.0 Roadmap

### 10.1 Version 1.0 Scope — UK Only

ScoreSentinel Version 1.0 implements UK MLR 2017 as the primary PEP and beneficial owner framework. This covers:
- All UK-regulated entity customers
- Foreign PEPs transacting with UK entities
- UK domestic PEPs (included under MLR 2017)

### 10.2 ScoreSentinel 2.0 — Planned Regional Overlays

> **The following regional overlays are planned for ScoreSentinel 2.0 upon completion of the 60-day build. Each overlay will add jurisdiction-specific PEP categories, beneficial owner thresholds, and screening list integrations on top of the universal tier framework.**

| Region | Key Additions Planned |
|---|---|
| **APAC — Japan** | Anti-Social Forces (ASF/Yakuza) screening — NPA list integration. ASF to be treated as Tier 2 equivalent. Online gambling watchlist |
| **APAC — Indonesia** | OJK, PPATK, SIPENDAR list integration. SOE officials classification. Regional PEP definition alignment |
| **APAC — Hong Kong** | HKMA guidance alignment. Cross-border China PEP exposure |
| **APAC — South Korea** | KOFIU guidance. Chaebol-linked beneficial ownership |
| **APAC — Thailand** | BOT guidance. Royal family classification |
| **EU** | 4AMLD/6AMLD alignment. Domestic PEP inclusion. European Parliament members |
| **US** | FinCEN alignment. Foreign PEPs only (domestic PEPs excluded under US framework). FBAR implications |
| **GCC / Middle East** | Sovereign Wealth Fund BO rules. Royal family classifications for UAE, Saudi, Qatar |

---

## 11. SR 11-7 Model Risk Checklist

| Requirement | Status | Location |
|---|---|---|
| Model purpose documented | ✅ Complete | Section 1 |
| PEP tier taxonomy defined | ✅ Complete | Section 2 |
| PEP scoring rules documented | ✅ Complete | Section 3 |
| Alert threshold justified | ✅ Complete | Section 3.1 |
| Former PEP de-escalation framework | ✅ Complete | Section 4 |
| BO definition and thresholds documented | ✅ Complete | Section 5 |
| Dual threshold system justified | ✅ Complete | Section 5.4 |
| Fallback BO rule documented | ✅ Complete | Section 5.2 |
| BO data collection requirements | ✅ Complete | Section 6.1 |
| Acceptable BO verification sources | ✅ Complete | Section 6.2 |
| Fuzzy match threshold justified | ✅ Complete | Section 7.1 |
| Regulatory defence documented | ✅ Complete | Section 7.2 |
| Algorithm specification documented | ✅ Complete | Section 7.4 |
| High-collision name handling | ✅ Complete | Section 7.5 |
| Screening workflow defined | ✅ Complete | Section 8 |
| False positive targets defined | ✅ Complete | Section 9.1 |
| Regional scope documented | ✅ Complete | Section 10 |
| Future roadmap documented | ✅ Complete | Section 10.2 |
| Independent validation | 🔄 Pending | Planned Day 45 |
| Back-testing | 🔄 Pending | Planned Day 30 |

---

## 12. Assumptions & Limitations

- Version 1.0 applies UK MLR 2017 as the sole primary framework. Regional variations for APAC, EU, US, and GCC are acknowledged but not implemented — see Section 10.2
- The 85% fuzzy match threshold is based on industry benchmark data from SWIFT, Refinitiv, and Actimize — not back-tested against ScoreSentinel's own transaction population. Back-testing is planned for Day 30
- PEP database quality directly affects screening accuracy — ScoreSentinel assumes use of a commercially maintained PEP database (e.g. World-Check, Dow Jones, LexisNexis) updated at least monthly
- Beneficial owner data quality depends on client disclosure and public registry accuracy — Companies House PSC data for UK entities may lag actual ownership changes by up to 28 days (statutory filing deadline)
- The Jaro-Winkler + Levenshtein combined algorithm is a recommendation — actual implementation algorithm will be confirmed during Python engine build on Day 21
- Tier 3 close associate identification depends on available intelligence — not all close associates will be known at onboarding

---

## 13. Version History

| Version | Change | Date | Author |
|---|---|---|---|
| 1.0 | Initial release — UK MLR 2017 PEP tier taxonomy, dual BO threshold system, fuzzy match justification with OCC examiner defence, fallback BO rule, regional overlay roadmap for ScoreSentinel 2.0 | 3 May 2026 | Atul Krishnan, CAMS |

---

*ScoreSentinel | PEP_RULES.md | PEP Matching & Beneficial Owner Risk Logic | Authored by Atul Krishnan, CAMS | Version 1.0 | 1 May 2026*
