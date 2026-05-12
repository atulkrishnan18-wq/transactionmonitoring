# GEO_RULES.md — Geographic Risk & Sanctions Scoring Rules

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.1 | **Day:** 3 of 60 | **Author:** Atul Krishnan, CAMS
**Last Updated:** February 2026

---

## Table of Contents
1. [Purpose & Regulatory Basis](#1-purpose--regulatory-basis)
2. [Country Risk Tier Classification](#2-country-risk-tier-classification)
3. [Geographic Scoring Architecture](#3-geographic-scoring-architecture)
4. [Threshold Justification & Weight Derivation](#4-threshold-justification--weight-derivation)
5. [Sanctions Screening Logic](#5-sanctions-screening-logic)
6. [Worked Scoring Examples](#6-worked-scoring-examples)
7. [Model Governance & Maintenance](#7-model-governance--maintenance)

---

## 1. Purpose & Regulatory Basis

This document defines the geographic risk and sanctions screening rules for ScoreSentinel. Geographic risk is a mandatory component of AML transaction monitoring under:

- **FATF Recommendation 19** — Enhanced due diligence for higher-risk countries
- **FATF Recommendation 1** — Risk-based approach requiring documented country risk assessment
- **FinCEN guidance** — Geographic risk factors in transaction monitoring programs
- **SR 11-7 (Federal Reserve)** — Model risk management requiring documented, explainable, and validated scoring logic

> **SR 11-7 Compliance Statement**
> ScoreSentinel is a rules-based scoring engine, not a machine learning model. Every score is fully traceable to documented rules, threshold justifications, and weight derivations. This design ensures explainability to regulators, auditors, and model validators without requiring algorithmic black-box justification.

---

## 2. Country Risk Tier Classification

Countries are classified into tiers based on three independent regulatory sources:
- **OFAC** sanctions designations
- **FATF** mutual evaluation outcomes (Current as of Feb 2026)
- **Transparency International CPI** (2024 scores)

> A country may appear in **multiple tiers** — all applicable tier scores are **cumulative**.

---

### Tier 1A — OFAC Sanctioned AND FATF Black Listed 🔴

These jurisdictions carry the **highest possible risk designation**.

**Rule:** Any transaction involving these countries triggers an **automatic Sanctions Alert** regardless of transaction amount or composite score.

| Country | OFAC Status | FATF Status | Score Added |
|---|---|---|---|
| Iran | Comprehensive Sanctions | Black List | **+50 \| AUTO-ALERT** |
| North Korea (DPRK) | Comprehensive Sanctions | Black List | **+50 \| AUTO-ALERT** |
| Myanmar | Military Regime Sanctions | Black List | **+50 \| AUTO-ALERT** |

---

### Tier 1B — OFAC Sanctioned (Comprehensive or Sectoral) 🔴

**Rule:** Any transaction involving these countries triggers an **automatic Sanctions Alert**.

| Country | Primary Sanctions Basis | Score Added |
|---|---|---|
| Syria | Comprehensive OFAC sanctions | **+40 \| AUTO-ALERT** |
| Cuba | Comprehensive OFAC embargo | **+40 \| AUTO-ALERT** |
| Russia | Sectoral/Comprehensive sanctions | **+40 \| AUTO-ALERT** |
| Belarus | OFAC / EU sanctions | **+40 \| AUTO-ALERT** |
| Venezuela | OFAC sanctions | **+40 \| AUTO-ALERT** |

---

### Tier 1C — FATF Grey List (Feb 2026 Update) 🟠

Formally identified by FATF as having strategic AML/CFT deficiencies.

| Country | Primary FATF Concern | Score Added |
|---|---|---|
| Afghanistan | Severe CFT deficiencies | +25 |
| Algeria | Legal framework gaps | +25 |
| Angola | Strategic deficiencies | +25 |
| Bolivia | AML oversight gaps | +25 |
| Bulgaria | EU-monitored deficiencies | +25 |
| Cameroon | Regional TF risk | +25 |
| Côte d'Ivoire | Financial transparency gaps | +25 |
| DR Congo | Cash economy risk | +25 |
| Haiti | Governance/CFT risk | +25 |
| Kenya | Regional hub risk | +25 |
| Kuwait | AML framework update | +25 |
| Laos | Narcotics corridor | +25 |
| Lebanon | Banking sector risk | +25 |
| Monaco | Financial center oversight | +25 |
| Namibia | Regulatory capacity | +25 |
| Nepal | Legislative delays | +25 |
| Papua New Guinea | TF/ML deficiencies | +25 |
| South Sudan | Conflict/CFT risk | +25 |
| Syria *(also Tier 1B)* | Conflict/TF risk | +25 |
| Venezuela *(also Tier 1B)* | Kleptocracy risk | +25 |
| Vietnam | Crypto/Financial oversight | +25 |
| Virgin Islands (UK) | Secrecy/Offshore risk | +25 |
| Yemen | Conflict/TF risk | +25 |

---

### Tier 2A — High Corruption Risk (CPI Score 0–29) 🟠

Countries with a Transparency International CPI score of **0–29** indicate pervasive corruption.

| Country | CPI Score | Primary Risk | Score Added |
|---|---|---|---|
| Somalia | 11 | State failure | +20 |
| Venezuela *(also Tier 1B+1C)* | 13 | Kleptocracy | +20 |
| Syria *(also Tier 1B+1C)* | 13 | Conflict | +20 |
| Yemen *(also Tier 1C)* | 16 | Conflict | +20 |
| North Korea *(also Tier 1A)* | 17 | Sanctions evasion | +20 |
| Haiti *(also Tier 1C)* | 17 | Governance collapse | +20 |
| Libya | 18 | State instability | +20 |
| DR Congo *(also Tier 1C)* | 20 | Cash economy | +20 |
| Afghanistan *(also Tier 1C)* | 20 | Taliban regime | +20 |
| Sudan | 20 | Conflict | +20 |
| Cambodia | 22 | Corruption | +20 |
| Lebanon *(also Tier 1C)* | 24 | Banking risk | +20 |
| Nigeria | 26 | AML/Fraud risk | +20 |
| Russia *(also Tier 1B)* | 26 | Sanctions/Corruption | +20 |
| Pakistan | 28 | TF risk | +20 |

---

### Tier 2B — Elevated Corruption Risk (CPI Score 30–49) 🟡

Countries with CPI 30–49 carry meaningful corruption risk.

| Country | CPI Score | Primary Risk | Score Added |
|---|---|---|---|
| Kenya *(also Tier 1C)* | 31 | Corruption | +15 |
| Mexico | 31 | Cartel/AML risk | +15 |
| Indonesia | 34 | PEP exposure | +15 |
| Egypt | 35 | Institutional risk | +15 |
| India | 39 | Hawala/TBML | +15 |
| South Africa | 41 | PEP/ML risk | +15 |
| China | 42 | Capital flight | +15 |
| Malaysia | 50 | *Watchlist Tier 3* | +15 |

---

### Tier 3 — Offshore / Secrecy Jurisdictions (Watch List) 🟡

| Jurisdiction | Primary Risk | Score Added |
|---|---|---|
| Cayman Islands | Offshore hub | +15 |
| British Virgin Islands | Shell company risk | +15 |
| Panama | Secrecy/Layering | +15 |
| Seychelles | Beneficial ownership | +15 |
| Cyprus | Russian exposure | +15 |
| Malaysia | Borderline CPI / Secrecy | +15 |

---

## 3. Geographic Scoring Architecture

### 3.1 Cumulative Scoring Table (The "Highest Risk" Jurisdictions)

| Country | Tiers Applicable | Cumulative Score Added | Action Trigger |
|---|---|---|---|
| **Syria** | 1B + 1C + 2A | **+85** | 🚨 **AUTO-ALERT** |
| **Venezuela** | 1B + 1C + 2A | **+85** | 🚨 **AUTO-ALERT** |
| **North Korea** | 1A + 2A | **+70** | 🚨 **AUTO-ALERT** |
| **Russia** | 1B + 2A | **+60** | 🚨 **AUTO-ALERT** |
| **Afghanistan** | 1C + 2A | **+45** | ⚠️ **AML Risk Alert** |
| **Haiti** | 1C + 2A | **+45** | ⚠️ **AML Risk Alert** |
| **Yemen** | 1C + 2A | **+45** | ⚠️ **AML Risk Alert** |
| **DR Congo** | 1C + 2A | **+45** | ⚠️ **AML Risk Alert** |
| **Lebanon** | 1C + 2A | **+45** | ⚠️ **AML Risk Alert** |

---

## 6. Worked Scoring Examples (Updated v1.1)

| Transaction | Structuring | Sender Geo | Receiver Geo | Total | Alert? |
|---|---|---|---|---|---|
| $5,000 wire — India to Cayman | 15 | +15 (CPI 39) | +15 (Offshore) | 45 | ❌ No |
| $2,000 cash — Nigeria to UK | 45 | +20 (CPI 26) | +0 | 65 | ⚠️ Yes |
| $1,000 wire — UK to Syria | 10 | +0 | +85 (1B+1C+2A) | 95 | 🚨 Yes |
| $8,000 wire — Russia to China | 20 | +60 (1B+2A) | +15 (CPI 42) | 95 | 🚨 Yes |
| $4,000 wire — Lebanon to France | 25 | +45 (1C+2A) | +0 | 70 | ⚠️ Yes |

---

*ScoreSentinel | GEO_RULES.md | Version 1.1 (Feb 2026 Audit) | Authored by Atul Krishnan, CAMS | Day 3 of 60 | CONFIDENTIAL*
