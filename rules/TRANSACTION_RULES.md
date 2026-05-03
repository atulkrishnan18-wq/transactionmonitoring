# TRANSACTION_RULES.md — Transaction Type Risk Scoring Rules

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.2 | **Day:** 5 of 60 | **Author:** Atul Krishnan, CAMS
**Last Updated:** 3 May 2026

---

## Table of Contents
1. [Purpose & Regulatory Basis](#1-purpose--regulatory-basis)
2. [Transaction Type Classification & Risk Scores](#2-transaction-type-classification--risk-scores)
3. [Velocity Rules](#3-velocity-rules)
4. [Threshold Justification & Weight Derivation](#4-threshold-justification--weight-derivation)
5. [False Positive Trade-Offs](#5-false-positive-trade-offs)
6. [Model Risk Explainability](#6-model-risk-explainability)
7. [Integration with Other ScoreSentinel Modules](#7-integration-with-other-scoresentinel-modules)
8. [Worked Scoring Examples](#8-worked-scoring-examples)
9. [Governance & Version Control](#9-governance--version-control)
10. [Success Criteria](#10-success-criteria)

---

## 1. Purpose & Regulatory Basis

This document defines transaction type risk scoring rules for ScoreSentinel. Different transaction types carry inherently different AML risk profiles — a cash deposit and a wire transfer may be identical in amount but represent completely different risk exposures. This module assigns a base risk score to each transaction type, which is then combined with structuring, geographic, and customer risk scores to produce a composite alert score.

### Regulatory Basis

- **FATF Recommendation 10** — Institutions must assess transaction risk as part of CDD and ongoing monitoring
- **FinCEN SAR Filing Guidance** — Transaction type is a mandatory field in suspicious activity reporting, reflecting its materiality to risk assessment
- **BSA/AML Examination Manual** — Transaction monitoring systems must account for transaction type as a risk variable
- **FATF Typologies Reports** — Specific transaction types are repeatedly identified as high-risk ML/TF vectors
- **SR 11-7** — Every scoring variable must be justified, documented, and explainable

> **Design Principle:** Transaction type scoring in ScoreSentinel assigns a base risk score reflecting the inherent risk of the transaction mechanism — independent of amount, geography, or customer profile. These scores are additive with other modules to produce a composite score.

---

## 2. Transaction Type Classification & Risk Scores

### 2.1 Risk Tier Summary

| Risk Tier | Score Range | Description |
|---|---|---|
| 🔴 High Risk | 40–55 | Transaction mechanisms most commonly exploited for ML/TF |
| 🟠 Medium-High Risk | 25–39 | Elevated risk requiring enhanced monitoring |
| 🟡 Medium Risk | 15–24 | Moderate risk — monitor for patterns |
| 🟢 Low Risk | 0–14 | Low inherent risk — standard monitoring |

---

### 2.2 High-Risk Transaction Types 🔴

#### 1. Cryptocurrency Transaction
**Base Score: 55**

| Attribute | Detail |
|---|---|
| Primary Risk | Anonymity, mixing/tumbling, unregulated exchange exposure, cross-border value transfer without correspondent banking trail |
| FATF Reference | FATF Recommendation 15 — Virtual Assets |
| FinCEN Reference | FinCEN Guidance FIN-2019-G001 — Application of BSA to Virtual Currency |
| Velocity Trigger | 3+ crypto transactions within 24 hours |
| Auto-Escalate If | Transaction involves unhosted wallet, mixer/tumbler service, or privacy coin (Monero, Zcash) |

**Scoring Rationale:** Highest base score in the engine. Cryptocurrency transactions combine anonymity, cross-border reach, irreversibility, and rapidly evolving evasion techniques. Even legitimate crypto transactions require enhanced scrutiny — the mechanism itself is the risk factor.

---

#### 2. Correspondent Banking
**Base Score: 50**

| Attribute | Detail |
|---|---|
| Primary Risk | Nested accounts, pass-through risk, inability to identify ultimate originator |
| FATF Reference | FATF Recommendation 13 — Correspondent Banking |
| FinCEN Reference | FinCEN Advisory FIN-2016-A003 — Correspondent Banking |
| Velocity Trigger | Any single correspondent transaction > $50,000 |
| Auto-Escalate If | Correspondent bank is domiciled in Tier 1A/1B country per GEO_RULES.md |

**Scoring Rationale:** Correspondent banking creates a chain of institutions where the originating institution may have weaker AML controls. The receiving institution cannot directly verify the ultimate customer — creating a structural blind spot that regulators have repeatedly flagged.

---

#### 3. Wire Transfer (International)
**Base Score: 45**

| Attribute | Detail |
|---|---|
| Primary Risk | Cross-border value movement, layering, sanctions exposure, speed of settlement |
| FATF Reference | FATF Recommendation 16 — Wire Transfers |
| FinCEN Reference | Travel Rule (31 CFR 103.33) — originator/beneficiary information required |
| Velocity Trigger | 2+ international wires to different countries within 48 hours |
| Auto-Escalate If | Destination country is Tier 1A or 1B per GEO_RULES.md |

**Scoring Rationale:** International wire transfers are the primary layering mechanism in large-scale money laundering. Speed, cross-border reach, and difficulty in reversibility make them structurally high risk. Travel Rule compliance is mandatory but frequently exploited through information gaps.

---

#### 4. Real Estate Payment
**Base Score: 45**

| Attribute | Detail |
|---|---|
| Primary Risk | Integration-stage ML — property used to convert illicit funds into legitimate assets |
| FATF Reference | FATF Guidance on ML through Real Estate (2022) |
| FinCEN Reference | Geographic Targeting Orders (GTOs) — mandatory reporting for all-cash real estate transactions |
| Velocity Trigger | Single transaction > $300,000 |
| Auto-Escalate If | Payment is all-cash (no mortgage), or buyer is a shell company per CUSTOMER_RULES.md |

**Scoring Rationale:** Real estate is the world's largest ML integration vehicle. All-cash purchases by shell companies or offshore entities are specifically flagged by FinCEN GTOs. Even single transactions warrant elevated scrutiny due to the scale of funds typically involved.

---

#### 5. Trade Finance / Letter of Credit
**Base Score: 45**

| Attribute | Detail |
|---|---|
| Primary Risk | Trade-Based Money Laundering (TBML) — over/under-invoicing, phantom shipments, multiple invoicing |
| FATF Reference | FATF Typologies Report on TBML (2006, updated 2020) |
| FinCEN Reference | FinCEN Advisory FIN-2010-A001 — Trade-Based Money Laundering |
| Velocity Trigger | Multiple LC amendments within single trade cycle |
| Auto-Escalate If | Counterparty is in Tier 1C or above per GEO_RULES.md, or goods description is vague |

**Scoring Rationale:** TBML is the largest ML typology by volume globally. The complexity of trade documentation creates natural concealment opportunities. Over/under-invoicing and phantom shipments are extremely difficult to detect without transaction type-specific rules.

> **TBML Over-Invoicing Indicator:** Where invoice value can be compared against publicly available commodity prices or industry benchmarks, a discrepancy of 20% or more above market price is a TBML red flag per FinCEN Advisory FIN-2010-A001. Vague goods descriptions (e.g. "general merchandise", "electronic components" without specification) combined with high invoice values require enhanced documentary scrutiny. Multiple LC amendments within a single trade cycle are an additional red flag — legitimate trade rarely requires more than one amendment.

---

#### 6. Foreign Currency Exchange (FX)
**Base Score: 40**

| Attribute | Detail |
|---|---|
| Primary Risk | Currency conversion as layering — converting illicit funds across currency boundaries to obscure origin |
| FATF Reference | FATF Typologies — Money Service Businesses |
| FinCEN Reference | MSB Registration requirements — currency exchange dealers |
| Velocity Trigger | 3+ FX transactions within 7 days aggregating > $10,000 |
| Auto-Escalate If | Conversion involves high-risk currency pair (e.g. USD to RUB, USD to IRR) |

**Scoring Rationale:** Currency exchange is a classic placement and layering tool. Multiple conversions across currency pairs rapidly obscure the audit trail. High-risk currency pairs — particularly those involving sanctioned jurisdictions — elevate the risk significantly.

---

#### 7. Money Order / Cashier's Cheque
**Base Score: 40**

| Attribute | Detail |
|---|---|
| Primary Risk | Cash equivalent — anonymity of cash with the appearance of legitimacy |
| FATF Reference | FATF Typologies — Negotiable Instruments |
| FinCEN Reference | BSA reporting requirements for money orders > $3,000 |
| Velocity Trigger | 3+ money orders purchased within 30 days |
| Auto-Escalate If | Multiple money orders purchased just below $3,000 reporting threshold (structuring indicator) |

**Scoring Rationale:** Money orders combine the anonymity of cash with the portability of a cheque. They are frequently used in structuring schemes — purchased in small denominations to avoid reporting thresholds. The BSA $3,000 record-keeping requirement exists specifically because of this risk.

---

### 2.3 Medium-High Risk Transaction Types 🟠

#### 8. Cash Deposit
**Base Score: 35**

| Attribute | Detail |
|---|---|
| Primary Risk | Placement-stage ML — introducing illicit cash into the financial system |
| FATF Reference | FATF Typologies — Cash Placement |
| FinCEN Reference | CTR filing requirement > $10,000 (31 CFR 1010.311) |
| Velocity Trigger | 3+ cash deposits within 10 days aggregating > $10,000 (structuring — see STRUCTURING_RULES.md) |
| Auto-Escalate If | Cash deposit inconsistent with customer's stated business profile |

**Scoring Rationale:** Cash is the entry point of most placement-stage ML. A single cash deposit is not unusual — the risk emerges in pattern and volume. Score of 35 reflects elevated base risk while allowing structuring and customer rules to drive the composite score.

---

#### 9. Cash Withdrawal
**Base Score: 35**

| Attribute | Detail |
|---|---|
| Primary Risk | Integration stage — converting electronic funds back to cash for onward use |
| FATF Reference | FATF Typologies — Integration via Cash |
| FinCEN Reference | CTR filing requirement > $10,000 |
| Velocity Trigger | 3+ cash withdrawals within 10 days aggregating > $10,000 |
| Auto-Escalate If | Large cash withdrawal immediately following an incoming international wire |

**Scoring Rationale:** Cash withdrawal following an inbound wire is a classic integration pattern — funds arrive electronically from abroad, are immediately withdrawn as cash, and disappear from the financial system. This sequencing is a specific red flag requiring velocity rule coverage.

---

#### 10. ATM Transaction
**Base Score: 30**

| Attribute | Detail |
|---|---|
| Primary Risk | Structured withdrawals across multiple ATMs to avoid detection thresholds |
| FATF Reference | FATF Typologies — Structuring |
| FinCEN Reference | Structuring prohibition (31 USC 5324) |
| Velocity Trigger | 5+ ATM transactions within 24 hours, or ATM use across 3+ locations in same day |
| Auto-Escalate If | ATM withdrawals in foreign country inconsistent with customer travel profile |

**Scoring Rationale:** ATM transactions are individually low risk but become high risk in velocity. Multiple ATM withdrawals across different locations in a single day is a textbook structuring indicator. The mechanism itself scores lower than cash deposit — the risk is in the pattern.

---

#### 11. Cheque Payment
**Base Score: 25**

| Attribute | Detail |
|---|---|
| Primary Risk | Cheque kiting, counterfeit cheques, third-party cheque deposits |
| FATF Reference | FATF Typologies — Negotiable Instruments |
| FinCEN Reference | BSA record-keeping requirements |
| Velocity Trigger | 5+ cheques deposited within 30 days from different issuers |
| Auto-Escalate If | Third-party cheques deposited and immediately withdrawn |

**Scoring Rationale:** Cheques are a declining but persistent ML mechanism. The primary risk is third-party cheques — depositing cheques made out to others, particularly when combined with immediate withdrawal. Score of 25 reflects moderate inherent risk.

---

#### 12. Securities Trade (Stocks / Bonds)
**Base Score: 25**

| Attribute | Detail |
|---|---|
| Primary Risk | Securities used as layering vehicle — purchase and rapid sale to create appearance of legitimate investment income |
| FATF Reference | FATF Typologies — Securities Sector ML |
| FinCEN Reference | FinCEN/SEC coordination on securities-related SARs |
| Velocity Trigger | Buy-sell cycle completed within 48 hours for amounts > $50,000 |
| Auto-Escalate If | Securities traded through offshore brokerage in Tier 3 jurisdiction per GEO_RULES.md |

**Scoring Rationale:** Securities provide a veneer of legitimacy — proceeds from ML appear as investment returns. Rapid buy-sell cycles are the key indicator. Score reflects elevated but not highest risk — the regulated nature of exchanges provides some inherent controls.

---

### 2.4 Medium Risk Transaction Types 🟡

#### 13. Internal Account Transfer
**Base Score: 20**

| Attribute | Detail |
|---|---|
| Primary Risk | Layering between own accounts — obscuring fund origin through multiple internal moves |
| FATF Reference | FATF Typologies — Layering |
| FinCEN Reference | SAR guidance — unusual internal transfer patterns |
| Velocity Trigger | 5+ internal transfers within 24 hours |
| Auto-Escalate If | Funds transferred internally then immediately wired internationally |

**Scoring Rationale:** Internal transfers are routine but can indicate layering when used to move funds rapidly between accounts before an outbound wire. The risk is almost entirely in velocity and sequencing — hence lower base score but active velocity rules.

---

#### 14. Mobile / Peer-to-Peer Transfer
**Base Score: 20**

| Attribute | Detail |
|---|---|
| Primary Risk | Smurfing — splitting large amounts across multiple P2P transfers to avoid detection |
| FATF Reference | FATF Guidance on Virtual Assets and P2P Transfers |
| FinCEN Reference | FinCEN Guidance on P2P payment applications |
| Velocity Trigger | 10+ P2P transfers within 24 hours, or aggregate > $5,000 in 24 hours |
| Auto-Escalate If | Transfers to multiple different recipients in rapid succession |

**Scoring Rationale:** P2P platforms (UPI, PayPal, Venmo) are increasingly used for smurfing. Individual transactions are typically small — the risk is volume and fragmentation. Score reflects moderate inherent risk with velocity rules doing the heavy lifting.

---

#### 15. Credit Card Transaction
**Base Score: 15**

| Attribute | Detail |
|---|---|
| Primary Risk | Refund fraud, card-not-present fraud, integration via luxury goods purchases |
| FATF Reference | FATF Typologies — Payment Card Fraud |
| FinCEN Reference | SAR guidance — unusual card activity |
| Velocity Trigger | 10+ transactions within 24 hours, or single transaction > $20,000 |
| Auto-Escalate If | Multiple high-value luxury purchases followed by immediate resale pattern |

**Scoring Rationale:** Credit cards are heavily monitored by card networks independently. ScoreSentinel scores them at 15 — elevated enough to capture unusual patterns but low enough to avoid flagging routine spending.

---

#### 16. Online Payment / E-commerce
**Base Score: 15**

| Attribute | Detail |
|---|---|
| Primary Risk | Refund fraud, synthetic identity fraud, marketplace ML |
| FATF Reference | FATF Guidance on Digital Payment Tokens |
| FinCEN Reference | FinCEN guidance on e-commerce payment processors |
| Velocity Trigger | 15+ online payments within 24 hours |
| Auto-Escalate If | Multiple refunds received for unverifiable purchases |

**Scoring Rationale:** E-commerce transactions are high volume and generally low individual risk. Score of 15 reflects this — the risk is in anomalous patterns (excessive refunds, purchases from high-risk merchant categories) rather than the transaction type itself.

> **Merchant ML Refund Rate Threshold:** Industry average refund rate for legitimate e-commerce merchants is below 2%. A refund rate exceeding 15% of transaction volume within any 30-day period is a Material Negative Indicator (MNI) requiring analyst review. A refund rate exceeding 40% is a high-conviction merchant ML indicator — escalate immediately. Refunds issued to accounts different from the original payment source are an additional red flag regardless of refund rate.

---

### 2.5 Low Risk Transaction Types 🟢

#### 16b. Domestic Salary Credit
**Base Score: 15**

| Attribute | Detail |
|---|---|
| Primary Risk | Low — predictable, regular, employer-verified |
| Classification | Treated as sub-type of Domestic Wire for scoring purposes |
| Velocity Trigger | None — regular salary credits are expected pattern |
| Auto-Escalate If | Salary amount changes by more than 50% unexpectedly, or employer changes to unverified entity |

> **Note:** Domestic Salary Credit does not appear as a standalone transaction type in the ScoreSentinel transaction taxonomy but is scored as a Domestic Wire (15 points) when the transaction description or payment reference indicates salary/payroll origin. This classification was identified during TEST_SCENARIOS.md Scenario 1 validation.

---

#### 17. Wire Transfer (Domestic)
**Base Score: 15**

| Attribute | Detail |
|---|---|
| Primary Risk | Domestic layering — moving funds between institutions to obscure origin |
| FATF Reference | FATF Recommendation 16 — Wire Transfers |
| FinCEN Reference | Travel Rule — domestic wire requirements |
| Velocity Trigger | 5+ domestic wires within 48 hours |
| Auto-Escalate If | Domestic wire immediately precedes or follows an international wire |

**Scoring Rationale:** Lower than international wire (45) because regulatory oversight within a single jurisdiction is stronger. However, domestic wires used as a pre-cursor to international transfers become high risk in combination — hence the velocity and sequencing rules.

---

#### 18. Loan Repayment
**Base Score: 10**

| Attribute | Detail |
|---|---|
| Primary Risk | Loan-back schemes — borrowing against illicitly deposited collateral to access clean funds |
| FATF Reference | FATF Typologies — Loan-Back Schemes |
| FinCEN Reference | SAR guidance — unusual loan repayment patterns |
| Velocity Trigger | Early full repayment of large loan within 90 days of origination |
| Auto-Escalate If | Loan repaid using funds from a high-risk jurisdiction or cash |
| Auto-Escalate If | Repayment made by third party not named on loan agreement → HIGH RISK ALERT |
| Auto-Escalate If | Repayment made by unknown or unverified third party → AUTO-ALERT |
| Auto-Escalate If | Multiple third parties each contributing portions of repayment → STRUCTURING ALERT |

**Scoring Rationale:** Loan repayments are routine and low risk in isolation. The loan-back scheme — depositing illicit funds as collateral, borrowing against them, then repaying — is the specific risk. Score of 10 reflects low base risk with targeted velocity and pattern rules.

> **Third-Party Repayment Rule:** Any loan repayment made by a party not named on the original loan agreement must be treated as high risk regardless of amount. The repaying party must be identified, verified, and their relationship to the borrower documented. Unknown third-party repayments trigger an immediate alert.

---

#### 19. Insurance Premium Payment
**Base Score: 10**

| Attribute | Detail |
|---|---|
| Primary Risk | Insurance policy used as ML vehicle — overpayment then refund as clean funds, early policy surrender |
| FATF Reference | FATF Typologies — Insurance Sector ML |
| FinCEN Reference | SAR guidance for insurance entities |
| Velocity Trigger | Early policy surrender within 12 months of inception |
| Auto-Escalate If | Premium paid in cash, or policy surrendered early with refund to third-party account |

**Scoring Rationale:** Insurance premium payments are generally low risk. The specific ML typology is early policy surrender — paying premiums with illicit funds then surrendering the policy for a clean refund cheque. Score of 10 with targeted escalation rules covers this.

> **Three-Indicator Insurance ML Escalation Rule:** If any TWO of the following three indicators are present simultaneously, mandatory escalation applies regardless of CRS:
> 1. Premium paid in cash or from high-risk jurisdiction account
> 2. Policy surrendered within 12 months of inception (VEL-022)
> 3. Surrender refund requested to a different account than the premium payment source
>
> All three indicators present = immediate escalation to Compliance Officer. This three-indicator rule is consistent with the ScoreSentinel three-point decision standard defined in AUDIT_REQUIREMENTS.md Section 3.

---

## 3. Velocity Rules

Velocity rules detect risk in **patterns over time** — not just individual transactions. A single $9,000 cash deposit may be innocent. Five $9,000 cash deposits in ten days is structuring.

### 3.1 Universal Velocity Rules (Apply to All Transaction Types)

| Rule ID | Rule | Threshold | Action |
|---|---|---|---|
| VEL-001 | Daily transaction count | > 20 transactions in 24 hours | Flag for review |
| VEL-002 | Daily aggregate value | > $50,000 aggregate in 24 hours | Flag for review |
| VEL-003 | Weekly aggregate value | > $100,000 aggregate in 7 days | EDD trigger |
| VEL-004 | Rapid round-trip | Funds in and out within 24 hours > $10,000 | High risk alert |
| VEL-005 | Dormant account spike | Account inactive 90+ days then sudden activity > $5,000 | Flag for review |

---

### 3.2 Transaction-Type Specific Velocity Rules

| Rule ID | Transaction Type | Velocity Trigger | Threshold | Action |
|---|---|---|---|---|
| VEL-010 | Cash Deposit | Multiple deposits | 3+ deposits within 10 days aggregating > $10,000 | Structuring alert — see STRUCTURING_RULES.md |
| VEL-011 | Cash Withdrawal | Multiple withdrawals | 3+ withdrawals within 10 days aggregating > $10,000 | Structuring alert |
| VEL-012 | ATM Transaction | Multiple ATM hits | 5+ ATM transactions in 24 hours OR 3+ locations same day | Structuring alert |
| VEL-013 | Wire Transfer (Int'l) | Multiple international wires | 2+ wires to different countries within 48 hours | High risk alert |
| VEL-014 | Wire Transfer (Int'l) | Sequential wiring | Wire received then wire sent within 24 hours > $10,000 | High risk alert — pass-through indicator |
| VEL-015 | Cryptocurrency | Multiple crypto transactions | 3+ crypto transactions within 24 hours | High risk alert |
| VEL-016 | Mobile / P2P | High volume P2P | 10+ P2P transfers within 24 hours OR aggregate > $5,000 | Smurfing alert |
| VEL-017 | FX Transaction | Multiple conversions | 3+ FX transactions within 7 days aggregating > $10,000 | Layering alert |
| VEL-018 | Internal Transfer | Rapid internal moves | 5+ internal transfers within 24 hours | Layering alert |
| VEL-019 | Cheque Payment | Multiple third-party cheques | 5+ cheques from different issuers within 30 days | Flag for review |
| VEL-020 | Money Order | Multiple purchases | 3+ money orders within 30 days | Structuring alert |
| VEL-021 | Loan Repayment | Early full repayment | Full repayment within 90 days of origination > $50,000 | Loan-back scheme alert |
| VEL-022 | Insurance | Early surrender | Policy surrendered within 12 months of inception | Insurance ML alert |
| VEL-025 | Loan Repayment | Third-party payment | Any third-party repayment > $5,000 by party not on loan agreement | Immediate flag — relationship justification required |
| VEL-026 | Loan Repayment | Unknown third-party | Repayment by unverified / unidentified third party — any amount | AUTO-ALERT — unknown source of funds |
| VEL-027 | Loan Repayment | Multiple third parties | 2+ different third parties contributing to same loan repayment | Structuring alert — third-party structuring indicator |
| VEL-023 | Real Estate | High-value single payment | Single payment > $300,000 | EDD trigger |
| VEL-024 | Securities | Rapid buy-sell | Buy-sell cycle < 48 hours > $50,000 | Layering alert |

---

### 3.3 Sequencing Rules (Cross-Transaction Pattern Detection)

These rules detect risk in the **sequence** of different transaction types — not just volume.

| Rule ID | Pattern | Transactions Involved | Risk | Action |
|---|---|---|---|---|
| SEQ-001 | Cash-to-Wire | Cash deposit followed by international wire within 72 hours | Classic placement → layering sequence | High risk alert |
| SEQ-002 | Wire-to-Cash | International wire received followed by cash withdrawal within 24 hours | Integration pattern | High risk alert |
| SEQ-003 | Internal-to-Wire | Multiple internal transfers then international wire | Layering before exit | High risk alert |
| SEQ-004 | Crypto-to-Wire | Crypto sale proceeds immediately wired internationally | Crypto layering | High risk alert |
| SEQ-005 | Loan-to-Wire | Loan disbursement immediately wired to high-risk jurisdiction | Loan-back + geo risk | High risk alert |
| SEQ-006 | Real Estate-to-FX | Real estate payment followed by FX conversion | Integration + currency layering | Flag for review |

---

## 4. Threshold Justification & Weight Derivation

> **SR 11-7 Requirement:** Every base score must be justified. This section documents the rationale for each tier boundary.

### 4.1 Why Cryptocurrency = 55 (Highest Score)

- Virtual assets combine anonymity, cross-border reach, irreversibility, and rapid evolution of evasion techniques
- FATF Recommendation 15 explicitly identifies VASPs as requiring the same AML controls as traditional FIs — reflecting the severity of the risk
- No other transaction type in ScoreSentinel combines all four risk dimensions simultaneously
- Score of 55 ensures that even a low-value crypto transaction from a clean customer scores 55 + 5 (customer) = 60 — triggering an alert
- This reflects the regulatory expectation that **every cryptocurrency transaction warrants enhanced scrutiny**

### 4.2 Why Wire Transfer International = 45, Domestic = 15

- International wires cross jurisdictional boundaries — removing the transaction from domestic regulatory oversight
- Domestic wires remain within a single regulatory environment — correspondent banks are known, regulated, and subject to the same BSA requirements
- The 30-point gap (45 vs 15) reflects this jurisdictional risk differential
- Consistent with FATF Recommendation 16 which treats cross-border wire transfers as materially higher risk than domestic

### 4.3 Why Cash Deposit and Withdrawal = 35 (Not Higher)

- Cash transactions are the most common ML placement vehicle but also the most common legitimate transaction type for large segments of the population
- Setting base score too high generates excessive false positives for cash-economy customers
- Score of 35 ensures cash alone does not alert — but cash + structuring pattern + high-risk customer does
- Calibrated so that 3 cash deposits in 10 days (structuring rule VEL-010) + base score = alert threshold breach

### 4.4 Why Loan Repayment and Insurance = 10 (Lowest Scores)

- Both are contractual obligations — the existence of a scheduled repayment is itself a legitimacy indicator
- Risk is in deviation from expected pattern (early repayment, cash payment, third-party refund) — not in the transaction type itself
- Low base score ensures routine repayments never generate noise
- Targeted escalation rules capture the specific ML typologies without penalising normal behaviour

---

## 5. False Positive Trade-Offs

### 5.1 Target Metrics

| Metric | Target | Rationale |
|---|---|---|
| Transaction Type Alert False Positive Rate | < 15% | Consistent with GEO_RULES.md and CUSTOMER_RULES.md targets |
| Velocity Rule False Positive Rate | < 20% | Velocity rules cast wider net by design — higher tolerance acceptable |
| Sequencing Rule False Positive Rate | < 10% | Sequencing rules are highly specific — low tolerance for noise |
| Recalibration Frequency | Every 6 months | Transaction mix evolves — crypto volumes, P2P adoption require regular review |

### 5.2 Documented Design Decisions

**Decision 1 — Cryptocurrency at 55**
> Will generate alerts on legitimate crypto users. This is accepted. Regulatory expectation is that all crypto transactions receive enhanced scrutiny. The false positive cost (analyst review) is lower than the compliance cost of a missed crypto-ML transaction.

**Decision 2 — Cash at 35, Not 50**
> Deliberately calibrated below alert threshold when standalone. Raising cash to 50 would alert on every large cash transaction regardless of other factors — generating unmanageable false positive volumes for cash-economy customers and small businesses.

**Decision 4 — Third-Party Loan Repayment Auto-Alert**
> Third-party loan repayments auto-alert regardless of amount. Even a $100 repayment by an unknown third party is suspicious — the identity and relationship of the repaying party is the risk factor, not the amount. False positive cost (relationship verification) is low. Miss cost (undetected integration) is high.

**Decision 3 — P2P at 20**
> P2P platforms are mainstream payment infrastructure. Scoring them higher would generate excessive alerts on legitimate users. Velocity rules (VEL-016) provide the safety net for genuine smurfing patterns.

---

## 6. Model Risk Explainability

### 6.1 Explainability Statement

Every transaction type score in ScoreSentinel is derived from:
1. A documented base score with explicit justification
2. Named FATF and FinCEN regulatory references
3. Specific velocity and sequencing rules with defined thresholds
4. A documented false positive tolerance decision

A compliance officer can explain any score to a regulator in one sentence:

> *"This wire transfer scored 45 because international wire transfers are classified as high-risk under FATF Recommendation 16, and the score is justified by the cross-jurisdictional nature of the transaction and the documented layering typology risk."*

### 6.2 No Black-Box ML

Transaction type scores are fixed, documented values — not ML-derived weights. This means:
- No training data bias
- No model drift
- No unexplainable outputs
- Full SR 11-7 compliance without additional validation burden

---

## 7. Integration with Other ScoreSentinel Modules

Transaction type scores are **additive** with all other ScoreSentinel modules:

```
COMPOSITE SCORE =
  Transaction Type Score      (this document — 0 to 55)
+ Structuring Score           (STRUCTURING_RULES.md — 0 to 70)
+ Geographic Risk Score       (GEO_RULES.md — 0 to 50 each side)
+ Customer Risk Score         (CUSTOMER_RULES.md — 0 to 175)
─────────────────────────────────────────────────────────────
Alert Threshold = 60
```

### Integration Examples

| Transaction | Type Score | + Structuring | + Geo | + Customer | = Total | Alert? |
|---|---|---|---|---|---|---|
| Small domestic wire — clean customer | 15 | 0 | 0 | 5 | 20 | ❌ No |
| Crypto tx — newly onboarded customer | 55 | 0 | 0 | 30 | 85 | ✅ Yes |
| Cash deposit — Nigeria customer | 35 | 0 | 25 | 5 | 65 | ✅ Yes |
| Int'l wire — shell company — BVI | 45 | 0 | 15 | 50 | 110 | ✅ Yes |
| Loan repayment — verified individual | 10 | 0 | 0 | 5 | 15 | ❌ No |

---

## 8. Worked Scoring Examples

### Example 1 — Routine Domestic Wire (Expected: No Alert)

```
Transaction:  $2,000 domestic wire
Customer:     Verified salaried individual — 3 years history
Geography:    UK to UK
Velocity:     First wire this month

Transaction Type Score  : 15 (domestic wire)
Structuring Score       : 0
Geographic Score        : 0
Customer Score          : 5
─────────────────────────
COMPOSITE SCORE         : 20 — ✅ No Alert
```

---

### Example 2 — Cryptocurrency Transaction — New Customer (Expected: Alert)

```
Transaction:  $3,000 cryptocurrency purchase
Customer:     Newly onboarded — 2 months history
Geography:    Domestic
Velocity:     Second crypto transaction this week

Transaction Type Score  : 55 (cryptocurrency)
Structuring Score       : 0
Geographic Score        : 0
Customer Score          : 30 (newly onboarded)
─────────────────────────
COMPOSITE SCORE         : 85 — 🚨 High Risk Alert
Velocity Rule Fired     : VEL-015 (2+ crypto in 7 days)
```

---

### Example 3 — Cash-to-Wire Sequence (Expected: High Risk Alert)

```
Transaction:  $9,000 cash deposit followed by $8,500 international
              wire to Panama within 48 hours
Customer:     SMB — 1 year history
Geography:    Panama — Tier 3 offshore

Transaction Type Score  : 35 (cash deposit) + 45 (int'l wire) = 80
Structuring Score       : 25 (near-threshold cash)
Geographic Score        : 15 (Panama — Tier 3)
Customer Score          : 20 (SMB)
─────────────────────────
COMPOSITE SCORE         : 140 — 🚨 Very High Risk Alert
Sequencing Rule Fired   : SEQ-001 (Cash-to-Wire within 72 hours)
```

---

### Example 4 — Insurance Premium Routine Payment (Expected: No Alert)

```
Transaction:  $500 monthly insurance premium
Customer:     Verified individual — 5 years history
Geography:    Domestic insurer
Velocity:     Consistent monthly payment — 36 months

Transaction Type Score  : 10 (insurance premium)
Structuring Score       : 0
Geographic Score        : 0
Customer Score          : 5
─────────────────────────
COMPOSITE SCORE         : 15 — ✅ No Alert
```

---

### Example 5 — Early Loan Repayment — High Risk Jurisdiction (Expected: Alert)

```
Transaction:  Full loan repayment of $75,000 — 45 days after origination
Customer:     Non-resident — Pakistan domicile
Geography:    Pakistan — Tier 1C FATF grey list
Velocity:     VEL-021 triggered — early full repayment within 90 days

Transaction Type Score  : 10 (loan repayment)
Structuring Score       : 0
Geographic Score        : 25 (Pakistan — Tier 1C)
Customer Score          : 25 (non-resident) + 20 (FATF geo) = 45
─────────────────────────
COMPOSITE SCORE         : 80 — 🚨 High Risk Alert
Velocity Rule Fired     : VEL-021 (early full repayment > $50,000)
Rule Rationale          : Loan-back scheme indicator + FATF grey list domicile
```

---

## 9. Governance & Version Control

### 9.1 Review Schedule

| Trigger | Frequency | Action |
|---|---|---|
| New transaction type emerges (e.g. new payment rail) | As identified | Add new type with full scoring rationale |
| FATF typology report update | Annual | Review all base scores against updated typologies |
| FinCEN advisory issued | As published | Assess impact on affected transaction types |
| Alert volume review | Every 6 months | Recalibrate velocity thresholds if false positive rate exceeds target |
| Crypto regulatory update | As issued | Crypto scores are most likely to require recalibration |

### 9.2 Version Control

| Version | Change | Date | Author |
|---|---|---|---|
| 1.0 | Initial release — 19 transaction types, velocity rules, sequencing rules | Day 5 — 2025 | Atul Krishnan, CAMS |
| 1.1 | Added third-party loan repayment rules VEL-025/026/027 | 25 April 2026 | Atul Krishnan, CAMS |
| 1.2 | Added merchant ML refund rate threshold (Online Payment), TBML over-invoicing indicator (Trade Finance), three-indicator insurance ML escalation rule, domestic salary credit sub-type classification. All gaps identified during Day 12 scenario validation | 3 May 2026 | Atul Krishnan, CAMS |

### 9.3 SR 11-7 Checklist

| Requirement | Status | Location |
|---|---|---|
| All transaction types documented | ✅ Complete | Section 2 |
| Base scores justified | ✅ Complete | Section 4 |
| Velocity rules defined with thresholds | ✅ Complete | Section 3 |
| Sequencing rules defined | ✅ Complete | Section 3.3 |
| False positive targets documented | ✅ Complete | Section 5 |
| Model explainability addressed | ✅ Complete | Section 6 |
| Integration with other modules documented | ✅ Complete | Section 7 |
| Independent validation | 🔄 Pending | Planned — Day 45 |
| Back-testing | 🔄 Pending | Planned — Day 30 |

---

## 10. Success Criteria

| Criterion | Met? |
|---|---|
| All 19 transaction types scored with explicit base scores | ✅ |
| Every score justified with regulatory reference | ✅ |
| Velocity rules defined for all high-risk transaction types | ✅ |
| Sequencing rules defined for cross-transaction patterns | ✅ |
| Threshold justification documented per SR 11-7 | ✅ |
| False positive trade-offs explicitly documented | ✅ |
| Integration with GEO_RULES.md, STRUCTURING_RULES.md, CUSTOMER_RULES.md explicit | ✅ |
| No black-box ML — full rules-based explainability | ✅ |
| Worked examples demonstrate scoring logic end-to-end | ✅ |
