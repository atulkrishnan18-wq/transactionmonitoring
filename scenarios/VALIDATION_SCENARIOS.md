# VALIDATION_SCENARIOS.md — Extended Validation Set (Scenarios 11–20)

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.0 | **Day:** 12 of 60 | **Author:** Atul Krishnan, CAMS
**Last Updated:** 1 May 2026

---

## Purpose

This document extends the master validation set from `TEST_SCENARIOS.md` (Scenarios 1–10) with 10 additional scenarios covering:

- Real-world typologies from operational HRDT screening experience
- PEP_RULES.md validation — UK MLR 2017 tier structure
- VELOCITY_RULES.md validation — Fan-In, dormant account
- Beneficial owner edge cases — Sulzer/Vekselberg ownership cliff
- Merchant money laundering — Wirecard-style card-not-present fraud
- False positive — legitimate Pakistani trade payment
- Trade-based money laundering (TBML)
- Insurance ML typology

Together with TEST_SCENARIOS.md, this gives ScoreSentinel a **20-scenario master validation set** covering the full risk spectrum before Python implementation on Day 21.

---

## Scoring Framework Reference

```
CRS = (Customer × 30%) + (Structuring × 25%)
    + (Geography × 25%) + (Transaction Type × 20%)

Module Maximums:
  Customer Risk     : 175
  Structuring       : 70
  Geography         : 100
  Transaction Type  : 55

Alert Threshold     : CRS ≥ 60
Independent Triggers: Tier 1A/1B sanctions, PEP Tier 1,
                      Structuring ≥ 75%, OFAC 50% rule
```

---

## Scenario 11 — Viktor Vekselberg / Renova Group / Sulzer AG
**Typology: Sanctions Evasion via Beneficial Ownership Engineering**
**Expected Outcome: AUTO-ALERT — Sanctions + PEP Tier 1**

### Background

Viktor Vekselberg is a Russian oligarch designated by OFAC in April 2018 under Executive Order 13662 (Ukraine-related sanctions). He is simultaneously:
- An **OFAC SDN-listed individual** — direct sanctions hit
- A **Tier 1 PEP** — senior political figure with Kremlin ties
- The **controlling beneficial owner** of Renova Group

Renova Group held approximately **48.8% of Sulzer AG** (Swiss industrial engineering company) at the time of Vekselberg's designation. This created a critical sanctions exposure question — does the OFAC 50% ownership rule apply at 48.8%?

### The Sulzer Evasion Mechanism

```
OFAC designates Vekselberg — April 2018
         ↓
Renova holds 48.8% of Sulzer AG
         ↓
48.8% < 50% OFAC threshold
→ Sulzer argues: 50% rule not triggered
         ↓
Sulzer conducts emergency share buyback
→ Reduces Renova stake further below 50%
         ↓
OFAC accepts argument — Sulzer cleared
         ↓
RESULT: Deliberate ownership engineering
        to avoid the 50% threshold cliff edge
```

### ScoreSentinel Scoring — Vekselberg Direct Transaction

| Module | Raw Score | Derivation | Maximum | Normalised |
|---|---|---|---|---|
| Customer Risk | 175 | PEP Tier 1 (50) + OFAC SDN confirmed (50) + Shell structure (50) + Unknown BO layers (25) = capped at 175 | 175 | 100% |
| Structuring | 0 | Single transaction | 70 | 0% |
| Geography | 100 | Russia — Tier 1B OFAC sanctioned | 100 | 100% |
| Transaction Type | 45 | International Wire | 55 | 81.8% |

**CRS Calculation:**
```
(100 × 30%) + (0 × 25%) + (100 × 25%) + (81.8 × 20%)
= 30 + 0 + 25 + 16.36
= 71.36
```

**CRS: 71.36 — 🔴 HIGH RISK**

**Independent Triggers:**
- ✅ PEP Tier 1 — AUTO-ALERT
- ✅ OFAC SDN direct hit — AUTO-ALERT (Tier 1B Russia)
- ✅ Vekselberg name match ≥ 85% — Sanctions Alert

**DISPOSITION: 🚨 TRIPLE AUTO-ALERT — SDN Hit + PEP Tier 1 + Sanctioned Jurisdiction**

---

### ScoreSentinel Scoring — Renova Group Entity Transaction

| Module | Raw Score | Derivation | Maximum | Normalised |
|---|---|---|---|---|
| Customer Risk | 125 | Shell company (50) + Unknown BO (25) + Sanctions-adjacent (50) | 175 | 71.4% |
| Structuring | 0 | Single transaction | 70 | 0% |
| Geography | 100 | Russia Tier 1B — Renova incorporated Russia | 100 | 100% |
| Transaction Type | 45 | International Wire | 55 | 81.8% |

**CRS: (71.4×30%)+(0×25%)+(100×25%)+(81.8×20%) = 21.42+0+25+16.36 = 62.78**

**OFAC 50% Rule Assessment:**
```
Vekselberg owns Renova Group — majority ownership
→ Renova Group treated as OFAC sanctioned entity
→ OFAC 50% rule triggers AUTO-ALERT
→ Any transaction with Renova = sanctions violation risk
```

**DISPOSITION: 🚨 AUTO-ALERT — OFAC 50% Ownership Rule**

---

### ScoreSentinel Scoring — Sulzer AG (48.8% Renova Stake)

| Module | Raw Score | Derivation | Maximum | Normalised |
|---|---|---|---|---|
| Customer Risk | 65 | Established business (10) + Sanctions-adjacent BO (50) + Unknown ultimate control (25) — capped at reasonable level | 175 | 37.1% |
| Structuring | 0 | Single transaction | 70 | 0% |
| Geography | 15 | Switzerland — Tier 3 offshore-adjacent | 100 | 15% |
| Transaction Type | 45 | International Wire | 55 | 81.8% |

**CRS: (37.1×30%)+(0×25%)+(15×25%)+(81.8×20%) = 11.13+0+3.75+16.36 = 31.24**

**OFAC 50% Rule Assessment:**
```
Renova stake = 48.8% — BELOW 50% threshold
→ OFAC 50% rule does NOT trigger on raw ownership
→ BUT: Ongoing monitoring obligation exists
→ ScoreSentinel flags: Beneficial owner is sanctioned
   entity at 48.8% — monitor for ownership changes

CRITICAL LESSON — THE CLIFF EDGE:
  49.9% → Not sanctioned under 50% rule
  50.0% → Sanctioned under 50% rule
  
This 0.1% difference is the single most
exploited gap in sanctions compliance.
ScoreSentinel requires:
→ Any BO ownership between 40–50% from
  a sanctioned entity triggers enhanced
  monitoring and quarterly ownership
  verification — not just at onboarding
```

**DISPOSITION: 🟠 MEDIUM-HIGH (31.24) + ⚠️ ENHANCED MONITORING — Sanctions-Adjacent BO at 48.8%**

**What This Proves:** The OFAC 50% rule has a precise cliff edge that sophisticated actors deliberately engineer. ScoreSentinel's 40–50% enhanced monitoring zone catches this gap. Ongoing ownership monitoring — not just onboarding checks — is essential.

---

## Scenario 12 — Merchant Money Laundering (Wirecard-Style)
**Typology: Card-Not-Present Fraud + Payment Processor Layering**
**Expected Outcome: HIGH RISK — Alert Generated**

### Background

Wirecard-style merchant ML uses a payment processor as the layering vehicle. Illicit funds are introduced as apparent legitimate card transactions through phantom merchants — businesses that exist on paper but process no real sales. Refunds are then issued to different accounts, creating clean electronic funds.

```
ML MECHANISM:
Criminal controls → Phantom merchant account
                    (fake e-commerce store)
         ↓
Illicit funds paid as "customer purchases"
via multiple prepaid/stolen cards
         ↓
Merchant processes "refunds" to different
accounts — clean funds emerge
         ↓
Layering complete — funds appear as
legitimate e-commerce revenue
```

### Transaction Profile

```
Customer:     Payment processor / e-commerce merchant
              — newly onboarded, 3 months history
Transaction:  High volume card-not-present transactions
              — 200+ daily, averaging $45 each
Pattern:      85% of transactions end in refund
              within 24 hours to different accounts
Geography:    Domestic — UK merchant account
Velocity:     Fan-Out pattern — 1 merchant, 200+ receivers
```

| Module | Raw Score | Derivation | Maximum | Normalised |
|---|---|---|---|---|
| Customer Risk | 65 | Newly onboarded (30) + Cash-intensive business equivalent (35) | 175 | 37.1% |
| Structuring | 70 | Fan-Out VEL-029 (+40) + Suspicious velocity 200+/day (+35) = capped at 70 | 70 | 100% |
| Geography | 0 | Domestic UK | 100 | 0% |
| Transaction Type | 15 | Online Payment / E-commerce | 55 | 27.3% |

**CRS Calculation:**
```
(37.1 × 30%) + (100 × 25%) + (0 × 25%) + (27.3 × 20%)
= 11.13 + 25 + 0 + 5.46
= 41.59
```

**CRS: 41.59 — 🟠 MEDIUM-HIGH**

**Structuring normalised = 100% — exceeds 75% independent trigger**

**Additional Red Flags:**
```
Refund rate of 85% — industry average < 2%
→ Flags as phantom merchant indicator
→ Card network fraud rules would also fire
→ EDGE_CASES.md EC-005 refund fraud detection applies

Fan-Out VEL-029:
→ 1 merchant → 200+ different receiver accounts → 24hrs
→ Classic layering dispersion pattern
```

**DISPOSITION: 🚨 ALERT — Independent Structuring Trigger (100%) + Refund Fraud Flag**

**What This Proves:** Merchant ML does not require cross-border transactions to generate an alert. The refund pattern and Fan-Out velocity catch the typology domestically. Card-not-present fraud is detectable through pattern analysis even when individual transaction amounts are small.

---

## Scenario 13 — Pakistani Trade Payment False Positive
**Typology: Legitimate Trade Payment — FATF Grey List Jurisdiction**
**Expected Outcome: MEDIUM-HIGH — False Positive — Cleared With Documentation**

### Background

A Pakistani textile manufacturer makes a $180,000 wire payment to a UK fabric supplier for a confirmed export order. Pakistan is FATF grey-listed (Tier 1C). The transaction scores high on geography and amount — but is entirely legitimate.

```
Customer:     Karachi Textiles Ltd — established 8 years
              Pakistani incorporated, UK trading relationship
Transaction:  $180,000 wire — Pakistan to UK
Purpose:      Payment against confirmed purchase order
              PO-2026-UK-4471 — cotton fabric shipment
Geography:    Pakistan sender — Tier 1C FATF grey list
Documents:    Commercial invoice, Bill of Lading,
              Letter of Credit — all verified
```

| Module | Raw Score | Derivation | Maximum | Normalised |
|---|---|---|---|---|
| Customer Risk | 35 | Non-resident (25) + Pakistan CPI Tier 2B (10) | 175 | 20% |
| Structuring | 0 | Single transaction — consistent with trading pattern | 70 | 0% |
| Geography | 45 | Pakistan sender Tier 1C (25) + UK receiver clean (0) + Pakistan CPI 25 score (20) | 100 | 45% |
| Transaction Type | 45 | International Wire | 55 | 81.8% |

**CRS Calculation:**
```
(20 × 30%) + (0 × 25%) + (45 × 25%) + (81.8 × 20%)
= 6 + 0 + 11.25 + 16.36
= 33.61
```

**CRS: 33.61 — 🟡 MEDIUM-LOW**

**Initial System Flag:**
```
Geography flag: Pakistan Tier 1C — enhanced monitoring
Wire amount: $180,000 — above standard review threshold
Combined: Analyst review triggered
```

**False Positive Clearance — EC-003 Protocol Applied:**
```
STEP 1 — Trade document verification:
  ✅ Commercial invoice matches wire amount (±2%)
  ✅ Purchase Order PO-2026-UK-4471 on file
  ✅ Bill of Lading confirmed — goods shipped
  ✅ Letter of Credit verified — issuing bank clean

STEP 2 — Customer due diligence:
  ✅ 8-year established business — known trading pattern
  ✅ 12 prior similar transactions — consistent corridor
  ✅ UK counterparty verified — Companies House clean
  ✅ No adverse media on either party

STEP 3 — Geography assessment:
  Pakistan Tier 1C — grey list adds score but
  does NOT auto-alert (not Tier 1A/1B)
  Trade payment from grey-list jurisdiction
  with full documentation = explainable

DISPOSITION: ✅ FALSE POSITIVE — CLEARED
Clearance Rationale:
  "Transaction represents legitimate trade payment
  supported by verified commercial documents.
  Pakistan Tier 1C geography adds scoring weight
  but is explained by 8-year established trading
  relationship with consistent corridor history.
  No structuring, no velocity anomaly, full
  documentary evidence. Cleared by [Analyst ID]
  on [Date] — enhanced monitoring maintained."
```

**DISPOSITION: 🟡 MEDIUM-LOW CRS + ✅ CLEARED — Documented False Positive**

**What This Proves:** A Pakistani trade payment to the UK scores in medium-low territory — not auto-alert. The geography adds risk weight correctly, but full documentation + established relationship + consistent pattern clears it. This is the correct calibration — FATF grey list should flag, not block.

---

## Scenario 14 — UK Cabinet Minister Onboarding
**Typology: Domestic UK PEP — Tier 1**
**Expected Outcome: AUTO-ALERT — PEP Tier 1 Domestic UK**

```
Customer:     Rt Hon [Name], Secretary of State
              for Business and Trade — sitting UK
              Cabinet Minister
Transaction:  Account opening — personal current account
              Salary credit from government payroll
Geography:    Domestic UK
```

| Module | Raw Score | Derivation | Maximum | Normalised |
|---|---|---|---|---|
| Customer Risk | 55 | PEP Tier 1 domestic (50) + HNWI ministerial salary (5) | 175 | 31.4% |
| Structuring | 0 | Salary credit — routine | 70 | 0% |
| Geography | 0 | Domestic UK | 100 | 0% |
| Transaction Type | 15 | Domestic wire — salary | 55 | 27.3% |

**CRS: (31.4×30%)+(0×25%)+(0×25%)+(27.3×20%) = 9.42+0+0+5.46 = 14.88**

**CRS: 14.88 — Below threshold**

**BUT: PEP Tier 1 confirmed — AUTO-ALERT fires**

**DISPOSITION: 🚨 AUTO-ALERT — PEP Tier 1 UK Domestic Cabinet Minister**

**UK MLR 2017 Note:** UK domestic PEPs are explicitly included under MLR 2017. A sitting Cabinet Minister requires EDD and senior management approval before onboarding regardless of transaction type or amount.

---

## Scenario 15 — Former PEP, 18 Months Post-Office
**Typology: Former PEP De-escalation — Tier 1 → Tier 2**
**Expected Outcome: MEDIUM-HIGH — Downgraded Tier, EDD Maintained**

```
Customer:     Former Deputy Prime Minister —
              left office 18 months ago
              Now: Private sector board advisor
Transaction:  $75,000 international wire — consultancy fee
Geography:    UK to UAE (Tier 3 offshore-adjacent)
```

| Module | Raw Score | Derivation | Maximum | Normalised |
|---|---|---|---|---|
| Customer Risk | 65 | Former PEP Tier 1→2 (de-escalated per EC-002, 13-36 months) (40) + HNWI (25) | 175 | 37.1% |
| Structuring | 0 | Single transaction | 70 | 0% |
| Geography | 15 | UAE receiver — Tier 3 | 100 | 15% |
| Transaction Type | 45 | International Wire | 55 | 81.8% |

**CRS: (37.1×30%)+(0×25%)+(15×25%)+(81.8×20%) = 11.13+0+3.75+16.36 = 31.24**

**De-escalation Framework Applied:**
```
18 months post-office → falls in 13–36 month window
→ Tier 1 downgraded to Tier 2 per EDGE_CASES.md EC-002
→ EDD still mandatory
→ Annual review required
→ No auto-alert — but AML alert if CRS ≥ 60
```

**DISPOSITION: 🟡 MEDIUM-LOW CRS + 🔴 EDD MANDATORY — Former PEP Tier 2**

---

## Scenario 16 — BVI Shell Company — Unknown BO
**Typology: Offshore Shell — Fallback BO Required**
**Expected Outcome: VERY HIGH RISK — Alert + EDD**

```
Customer:     Meridian Holdings Ltd — BVI incorporated
              No identified shareholders above 25%
              Nominee directors only
              No trading history provided
Transaction:  $500,000 international wire to Cyprus account
```

| Module | Raw Score | Derivation | Maximum | Normalised |
|---|---|---|---|---|
| Customer Risk | 140 | Shell company (50) + Unknown BO (25) + Nominee directors (20) + Offshore incorporation (15) + No trading history (30) | 175 | 80% |
| Structuring | 0 | Single large transaction | 70 | 0% |
| Geography | 55 | BVI sender Tier 3 (15) + Cyprus receiver Tier 3 (15) + combined offshore premium (25) | 100 | 55% |
| Transaction Type | 45 | International Wire | 55 | 81.8% |

**CRS: (80×30%)+(0×25%)+(55×25%)+(81.8×20%) = 24+0+13.75+16.36 = 54.11**

**Fallback BO Rule Applied:**
```
No individual identified with > 25% ownership
→ Fallback BO rule triggers per PEP_RULES.md Section 5.2
→ CEO or equivalent must be identified
→ Nominee directors do not satisfy fallback rule
→ Account cannot be activated until fallback BO named
→ Data quality flag raised — KYC remediation required
```

**DISPOSITION: 🟠 MEDIUM-HIGH CRS (54.11) + 🔴 DATA QUALITY BLOCK — Fallback BO not identified**

---

## Scenario 17 — Fan-In Mule Network
**Typology: Mule Account Consolidation**
**Expected Outcome: ALERT — Independent Structuring Trigger**

```
Customer:     Student account — newly onboarded
Transaction:  8 different individuals each send £1,000
              within 6 hours — all round amounts
              Total received: £8,000
              Immediately followed by single outbound
              wire of £7,800 to Eastern Europe
```

| Module | Raw Score | Derivation | Maximum | Normalised |
|---|---|---|---|---|
| Customer Risk | 30 | Newly onboarded (30) | 175 | 17.1% |
| Structuring | 70 | Fan-In VEL-028 (+40) + Round Number Burst VEL-030 (+25) + Rapid Round-Trip BEH-005 (+50) = capped at 70 | 70 | 100% |
| Geography | 20 | Eastern Europe receiver — Tier 2B CPI | 100 | 20% |
| Transaction Type | 20 | Mobile/P2P receive + wire out | 55 | 36.4% |

**CRS: (17.1×30%)+(100×25%)+(20×25%)+(36.4×20%) = 5.13+25+5+7.28 = 42.41**

**Structuring normalised = 100% — independent trigger fires**

**DISPOSITION: 🚨 ALERT — Independent Structuring + Fan-In + Round-Trip Pattern**

---

## Scenario 18 — Dormant Account — Nigeria Activation
**Typology: Account Takeover / Mule Activation**
**Expected Outcome: ALERT Generated**

```
Customer:     Retail individual — account dormant 7 months
Transaction:  Sudden burst of 12 transactions in 48 hours
              8 × cash deposits averaging £800 each
              4 × international wires to Nigeria
              Total: £6,400 in, £5,900 out
```

| Module | Raw Score | Derivation | Maximum | Normalised |
|---|---|---|---|---|
| Customer Risk | 5 | Verified individual — previously clean | 175 | 2.9% |
| Structuring | 70 | BEH-001 Dormant-to-Active (+40) + Suspicious velocity (+35) = capped at 70 | 70 | 100% |
| Geography | 25 | Nigeria receiver Tier 1C | 100 | 25% |
| Transaction Type | 35 | Cash Deposit | 55 | 63.6% |

**CRS: (2.9×30%)+(100×25%)+(25×25%)+(63.6×20%) = 0.87+25+6.25+12.72 = 44.84**

**Structuring normalised = 100% — independent trigger fires**

**DISPOSITION: 🚨 ALERT — Dormant Account Activation + Nigeria Geo + Independent Structuring Trigger**

---

## Scenario 19 — Trade Finance / Letter of Credit — TBML
**Typology: Trade-Based Money Laundering**
**Expected Outcome: HIGH RISK — Alert Generated**

```
Customer:     Import/Export trading company — 2 years old
Transaction:  Letter of Credit — $320,000
              Goods: "Electronic components" — vague description
              Counterparty: Malaysia (Tier 2B CPI)
              Multiple LC amendments within single trade cycle
              Invoice value inconsistent with market price
              (over-invoiced by estimated 40%)
```

| Module | Raw Score | Derivation | Maximum | Normalised |
|---|---|---|---|---|
| Customer Risk | 40 | SMB (20) + Cash-intensive trade sector (20) | 175 | 22.9% |
| Structuring | 35 | Multiple LC amendments VEL-019 equivalent (+25) + Over-invoicing indicator (+10) | 70 | 50% |
| Geography | 25 | Malaysia sender Tier 2B CPI (15) + vague goods description premium (10) | 100 | 25% |
| Transaction Type | 45 | Trade Finance / Letter of Credit | 55 | 81.8% |

**CRS: (22.9×30%)+(50×25%)+(25×25%)+(81.8×20%) = 6.87+12.5+6.25+16.36 = 41.98**

**Additional Red Flags:**
```
Over-invoicing 40% above market price
→ Classic TBML indicator — FinCEN Advisory FIN-2010-A001
→ Vague goods description "electronic components"
→ Multiple LC amendments — unusual in clean trade

Combined flags push to manual review despite
CRS below alert threshold
```

**DISPOSITION: 🟠 MEDIUM-HIGH (41.98) + ⚠️ TBML Red Flag — Manual Review Required**

---

## Scenario 20 — Insurance Policy Early Surrender
**Typology: Insurance Sector ML — Integration Stage**
**Expected Outcome: MEDIUM-HIGH + Insurance ML Flag**

```
Customer:     HNW individual — Nigerian nationality
              UK resident — 3 years
Transaction:  Life insurance policy surrendered
              11 months after inception
              Premium paid in cash: £45,000
              Surrender value: £43,200
              Refund requested to third-party account
              (not the account premiums were paid from)
```

| Module | Raw Score | Derivation | Maximum | Normalised |
|---|---|---|---|---|
| Customer Risk | 40 | HNWI (25) + Non-resident origin (15) | 175 | 22.9% |
| Structuring | 25 | Early surrender VEL-022 (+15) + Third-party refund account (+10) | 70 | 35.7% |
| Geography | 20 | Nigerian nationality — Tier 1C CPI | 100 | 20% |
| Transaction Type | 10 | Insurance Premium — early surrender | 55 | 18.2% |

**CRS: (22.9×30%)+(35.7×25%)+(20×25%)+(18.2×20%) = 6.87+8.93+5+3.64 = 24.44**

**Insurance ML Indicators:**
```
VEL-022 — Early surrender within 12 months ✅
Cash-funded premium ✅
Refund to different account than premium source ✅
→ Three-indicator insurance ML pattern

Per TRANSACTION_RULES.md Section 2.5:
Auto-escalate if: "Premium paid in cash OR
policy surrendered early with refund to
third-party account"
→ Both conditions met → Escalation mandatory
```

**DISPOSITION: 🟡 MEDIUM-LOW CRS (24.44) + 🚨 INSURANCE ML ESCALATION — Three-indicator pattern**

---

## Full 20-Scenario Summary Table

| # | Scenario | CRS | Disposition | Trigger |
|---|---|---|---|---|
| 1 | Clean Salary Earner | 6.33 | 🟢 Low Risk | None |
| 2 | Shell Company Wire Cayman | 45.53 | 🟠 Medium-High + EDD | None |
| 3 | Classic Smurfing | 37.5 | 🚨 Alert | ✅ Structuring ≥75% |
| 4 | Iran Sanctions | 33.88 | 🚨 Auto-Alert | ✅ Tier 1A |
| 5 | High-Frequency Crypto | 41.15 | 🟠 Medium-High | ⚠️ VEL-015 |
| 6 | PEP Tier 2 Wire | 31.24 | 🟡 Medium-Low + EDD | None |
| 7 | FATF Corridor | 32.39 | 🟡 Medium-Low | None |
| 8 | Cash SMB Structuring | 45.43 | 🚨 Alert | ✅ Structuring 100% |
| 9 | SAR Generator | 59.04 | 🟠 Medium-High | None — 0.96 below |
| 10 | Missing UBO Data | 24.94 | 🟡 Medium-Low + Flag | None |
| 11 | Vekselberg/Renova/Sulzer | 71.36 | 🚨 Triple Auto-Alert | ✅ SDN+PEP1+Tier1B |
| 12 | Wirecard Merchant ML | 41.59 | 🚨 Alert | ✅ Structuring 100% |
| 13 | Pakistan Trade FP | 33.61 | ✅ Cleared FP | None — documented |
| 14 | UK Cabinet Minister | 14.88 | 🚨 Auto-Alert | ✅ PEP Tier 1 |
| 15 | Former PEP 18 Months | 31.24 | 🟡 Medium-Low + EDD | None — de-escalated |
| 16 | BVI Shell Unknown BO | 54.11 | 🟠 Medium-High + Block | Fallback BO missing |
| 17 | Fan-In Mule Network | 42.41 | 🚨 Alert | ✅ Structuring 100% |
| 18 | Dormant Account Nigeria | 44.84 | 🚨 Alert | ✅ Structuring 100% |
| 19 | TBML Letter of Credit | 41.98 | 🟠 Medium-High | ⚠️ TBML Red Flag |
| 20 | Insurance Early Surrender | 24.44 | 🟡 Medium-Low + Escalation | ✅ Insurance ML |

---

## Rules Validated by This Extended Set

| Rule Document | Scenarios Tested |
|---|---|
| GEO_RULES.md | 4, 7, 11, 13, 18 |
| CUSTOMER_RULES.md | 2, 6, 11, 14, 15, 16 |
| STRUCTURING_RULES.md | 3, 8, 12, 17, 18 |
| TRANSACTION_RULES.md | 5, 12, 19, 20 |
| VELOCITY_RULES.md | 12, 17, 18 |
| PEP_RULES.md | 11, 14, 15 |
| EDGE_CASES.md | 13, 15 |
| COMPOSITE_LOGIC.md | All 20 |

---

## Gaps Identified During Extended Validation

| Gap | Scenario | Action Required |
|---|---|---|
| 40–50% BO ownership enhanced monitoring zone not documented | Scenario 11 (Sulzer) | Add to PEP_RULES.md Section 5 and CUSTOMER_RULES.md |
| Refund rate threshold for merchant ML not defined | Scenario 12 | Add to TRANSACTION_RULES.md — Online Payment section |
| TBML over-invoicing indicator not in TRANSACTION_RULES.md | Scenario 19 | Add to Trade Finance section |
| Three-indicator insurance ML escalation rule not explicit | Scenario 20 | Clarify in TRANSACTION_RULES.md Section 2.5 |

---

## Version History

| Version | Change | Date | Author |
|---|---|---|---|
| 1.0 | Initial release — 10 extended scenarios covering Vekselberg/Sulzer sanctions evasion, Wirecard-style merchant ML, Pakistani trade payment false positive, UK domestic PEP, former PEP de-escalation, BVI shell fallback BO, Fan-In mule network, dormant account activation, TBML, and insurance ML | 3 May 2026 | Atul Krishnan, CAMS |

---

*ScoreSentinel | VALIDATION_SCENARIOS.md | Extended Validation Set Scenarios 11–20 | Authored by Atul Krishnan, CAMS | Version 1.0 | Day 12 of 60*
