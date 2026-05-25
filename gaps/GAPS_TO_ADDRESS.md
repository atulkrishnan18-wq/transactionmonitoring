# GAPS_TO_ADDRESS.md — Known Gaps & Improvement Log

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 3.0 | **Author:** Atul Krishnan, CAMS
**Last Updated:** 24 May 2026

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

## Resolved Gaps — Final Review

| # | Gap | Found By | Resolution | Date |
|---|---|---|---|---|
| 21 | Back-testing against historical transaction data | Model Validation Phase | Completed via 25-scenario master suite and mass-seeding. | 23 May 2026 |
| 22 | Independent model validation | Governance Review | Completed under SR 11-7 standards. | 22 May 2026 |
| 23 | Alert-to-SAR ratio measurement | API Deployment | System enabled for measurable metrics in live dashboard. | 23 May 2026 |
| 24 | Fuzzy match threshold validation | Testing Phase | Validated at 85% against variant name scenarios. | 20 May 2026 |
| 25 | Production calibration (Alert Rate) | Cloud Deployment | Calibrated to 12-15% target range via Scenario 9 anchor. | 23 May 2026 |
| 26 | Connection Stability in Cloud | Render Deployment | Resolved via robust connection pooling and SSL enforcement. | 24 May 2026 |
| 27 | UI Blank Screen Safety | User Acceptance Test | Resolved via Null-Safety integration for rules-fired data. | 24 May 2026 |
| 28 | Compliance Workflow Alignment | Expert Review | Implemented Dual-Resolution Standard (Screening vs Risk). | 25 May 2026 |

---

## ScoreSentinel 2.0 — Deferred Improvements

| # | Improvement | Rationale for Deferral |
|---|---|---|
| D1 | APAC regional PEP overlays — Japan ASF, Indonesia OJK/PPATK | Requires specific localized data partnerships. |
| D2 | EU 4AMLD/6AMLD PEP overlay | Future international expansion. |
| D3 | US FinCEN — Foreign PEP only framework | Localized regulatory variation. |
| D4 | GCC / Middle East — Sovereign Wealth Fund BO rules | Specialized sovereign risk modeling. |
| D5 | Temporal Graph Persistence | Future MuleCatcher™ upgrade for historical link analysis. |
| D6 | ML-assisted name matching layer | Planned for AI-native version with XAI explainability. |
| D7 | Real-time SDN/OFAC API integration | Future phase: Direct data feed integration. |
| D8 | Automated Companies House / Registry API links | Future phase: Direct UBO verification. |

---

## Version History

| Version | Change | Date | Author |
|---|---|---|---|
| 3.0 | Final Project Audit — All Phase 3 deployment and stability gaps resolved. | 24 May 2026 | Atul Krishnan, CAMS |
| 2.0 | Full refresh — all resolved and open gaps documented. | 3 May 2026 | Atul Krishnan, CAMS |
| 1.0 | Initial gaps identified. | 1 May 2026 | Atul Krishnan, CAMS |

---

*ScoreSentinel | GAPS_TO_ADDRESS.md | Final Improvement Log | Authored by Atul Krishnan, CAMS | Version 3.0 | 24 May 2026*
