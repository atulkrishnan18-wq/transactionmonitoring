# GAPS_TO_ADDRESS.md — Known Gaps & Improvement Log

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 2.0 | **Author:** Atul Krishnan, CAMS
**Last Updated:** 3 May 2026

---

## Purpose

This document tracks all identified gaps, limitations, and planned improvements to ScoreSentinel. It is a living document — updated whenever a gap is identified during validation, testing, or regulatory review.

---

## Status Key

| Status | Meaning |
|---|---|
| ✅ Resolved | Fixed and committed to repository |
| 🔄 In Progress | Being addressed in current phase |
| 📋 Planned | Scheduled for a future day |
| 🔵 ScoreSentinel 2.0 | Deferred to next version |

---

## Resolved Gaps — Phase 1

| # | Gap | Found By | Resolution | Date |
|---|---|---|---|---|
| 1 | FATF black list had only 1 country | Day 3 QA — Atul Krishnan | Corrected to Iran, DPRK, Myanmar | Day 3 |
| 2 | CPI not included in geographic risk | Day 3 QA — Atul Krishnan | Added Tier 2A/2B CPI scoring | Day 3 |
| 3 | COMPOSITE_LOGIC.md wrong module maximums (Structuring 115, TxType 100) | Gemini validation Day 9 | Fixed to 70 and 55 in v1.2 | Day 14 |
| 4 | Structuring ≥75% independent trigger missing from COMPOSITE_LOGIC.md | Gemini validation Day 9 | Added Section 3.1 with worked example | Day 14 |
| 5 | OFAC 50% rule not cross-referenced in CUSTOMER_RULES.md | Gemini validation Day 9 | Added cross-reference in v1.1 | Day 14 |
| 6 | COMPOSITE_LOGIC.md had 5-module architecture remnants | Gemini validation Day 9 | Corrected to 4-module in v1.2 | Day 14 |
| 7 | STRUCTURING_RULES.md missing governance and version history | Gemini validation Day 9 | Added in v1.1 | Day 14 |
| 8 | Switzerland not in GEO_RULES.md Tier 3 | TEST_SCENARIOS Scenario 6 | Documented below — see Gap 8 | Day 14 |
| 9 | Domestic Salary Credit not in TRANSACTION_RULES.md | TEST_SCENARIOS Scenario 1 | Added as Domestic Wire sub-type v1.2 | Day 14 |
| 10 | Scenario 9 labelled HIGH RISK at 59% — below threshold | Gemini v1.0 error | Corrected to MEDIUM-HIGH in v1.1 | Day 8 |
| 11 | Missing data penalty pushed score above 100% | Gemini v1.0 error | Redesigned — penalty in customer module | Day 8 |
| 12 | Merchant ML refund rate threshold not defined | Scenario 12 — Wirecard | Added to TRANSACTION_RULES.md v1.2 | Day 14 |
| 13 | TBML over-invoicing indicator not documented | Scenario 19 — TBML | Added to TRANSACTION_RULES.md v1.2 | Day 14 |
| 14 | Three-indicator insurance ML escalation not explicit | Scenario 20 — Insurance | Added to TRANSACTION_RULES.md v1.2 | Day 14 |
| 15 | 40–50% BO ownership monitoring zone not documented | Scenario 11 — Sulzer | Added to PEP_RULES.md v1.1 | Day 14 |
| 16 | Velocity scores added directly to CRS — architecture error | Gemini VELOCITY_RULES v1.0 | Corrected — all feed into Structuring module | Day 10 |
| 17 | VEL-STR rule IDs conflicted with existing VEL sequence | Gemini VELOCITY_RULES v1.0 | Renamed to VEL-028 to VEL-031 | Day 10 |
| 18 | AML_RULES.md master index missing new documents | Day 14 review | Updated to v1.2 with all new files | Day 14 |
| 19 | Switzerland not in GEO_RULES.md | Day 20 | Added to Tier 3 (v1.1) | Day 20 |
| 20 | Assumptions & limitations sections | Day 20 | Added to all mandatory modules | Day 20 |

---

## Open Gaps — To Be Resolved

| # | Gap | Priority | Planned Resolution | Day |
|---|---|---|---|---|
| 21 | Back-testing against historical transaction data not yet completed | 🔴 High | Planned Day 30 | Day 30 |
| 22 | Independent model validation not yet completed | 🔴 High | Planned Day 45 | Day 45 |
| 23 | Alert-to-SAR ratio not yet measured — no live data | 🟠 Medium | Measurable after Python engine live — Day 25+ | Day 35 |
| 24 | Fuzzy match threshold (85%) based on industry benchmarks only — not back-tested on own population | 🔴 High | Validate during Day 30 back-testing | Day 30 |
| 25 | Alert rate in synthetic test data is 22% — above the 15% production target | 🟠 Medium | Production calibration to be validated with real transaction data via RBIH sandbox | Day 40 |

---

## ScoreSentinel 2.0 — Deferred Improvements

| # | Improvement | Rationale for Deferral |
|---|---|---|
| D1 | APAC regional PEP overlays — Japan ASF, Indonesia OJK/PPATK/SIPENDAR | Requires operational data and list access — Phase 2 project |
| D2 | EU 4AMLD/6AMLD PEP overlay | Requires EU-specific list integration |
| D3 | US FinCEN — foreign PEP only framework | Different definition from UK — separate module needed |
| D4 | GCC / Middle East — Sovereign Wealth Fund BO rules | Royal family classifications require specialist input |
| D5 | Dynamic alert threshold segmentation by customer type | Requires back-testing data to justify — not yet available |
| D6 | ML-assisted name matching layer | Would require SR 11-7 independent model validation — out of scope for rules-based v1.0 |
| D7 | Real-time OFAC SDN list integration | Requires API connection — Phase 2 technical build |
| D8 | Automated beneficial ownership registry lookup (Companies House API) | Requires API integration — Phase 2 |

---

## Version History

| Version | Change | Date | Author |
|---|---|---|---|
| 1.0 | Initial gaps identified — Day 1 | Day 1 — 2025 | Atul Krishnan, CAMS |
| 2.0 | Full refresh — all resolved and open gaps documented. Phase 1 Week 2 complete. ScoreSentinel 2.0 deferred improvements listed | 3 May 2026 | Atul Krishnan, CAMS |

---

*ScoreSentinel | GAPS_TO_ADDRESS.md | Known Gaps & Improvement Log | Authored by Atul Krishnan, CAMS | Version 2.0 | 3 May 2026*
