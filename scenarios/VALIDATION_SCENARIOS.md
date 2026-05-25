# VALIDATION_SCENARIOS.md — Master Validation Set (Scenarios 1–25)

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.5 | **Status:** Master Validation | **Author:** Atul Krishnan, CAMS
**Last Updated:** 24 May 2026

---

## Purpose

This document details the master validation set of 25 scenarios used to calibrate and verify the ScoreSentinel engine. These scenarios cover the full AML risk spectrum and the specialized **MuleCatcher™** intelligence module.

All scenarios listed here are part of the automated test suite and have been verified against the live cloud infrastructure (Render + Supabase).

---

## Scoring Framework Reference

```
Individual Transaction Risk (CRS):
  CRS = (Customer × 30%) + (Structuring × 25%)
      + (Geography × 25%) + (Transaction Type × 20%)

Mule Network Risk (MCS):
  MCS = Network Intelligence Overlay (Module 5)

Alert Thresholds:
  CRS Alert: ≥ 60
  MCS Alert: ≥ 60
  Auto-Alert: Sanctions, PEP Tier 1, High-Velocity Structuring
```

---

## Master 25-Scenario Summary Table

| # | Scenario | Typology | Result | Trigger |
|---|---|---|---|---|
| 1 | Clean Salary Earner | Low Risk Baseline | ✅ PASS (6.31) | None |
| 2 | Shell Company Wire Cayman | Offshore Layering | ✅ PASS (48.11)| EDD |
| 3 | Classic Smurfing | Structuring | ✅ PASS (Auto) | Structuring ≥75% |
| 4 | Iran Sanctions | Tier 1A Sanctions | ✅ PASS (Auto) | Geography 1A |
| 5 | High-Frequency Crypto | Velocity + Type Risk | ✅ PASS (41.14)| VEL-015 |
| 6 | PEP Tier 2 Wire | PEP EDD | ✅ PASS (31.26)| EDD |
| 7 | FATF Grey List Corridor | Geography Risk | ✅ PASS (39.90)| None |
| 8 | Cash SMB Micro-Structuring | Structuring | ✅ PASS (Auto) | Structuring 100% |
| 9 | SAR Generator | Calibration Proof | ✅ PASS (59.04)| None (<60) |
| 10 | Missing UBO Data | Data Integrity | ✅ PASS (24.94)| Data Flag |
| 11 | Vekselberg Direct | Sanctions + PEP1 | ✅ PASS (Auto) | SDN+PEP1 |
| 12 | Wirecard Merchant ML | Card-Not-Present Fraud| ✅ PASS (Auto) | Structuring 100% |
| 13 | Pakistani Trade FP | False Positive | ✅ PASS (33.61)| Documented Clear |
| 14 | UK Cabinet Minister | Domestic PEP Tier 1 | ✅ PASS (Auto) | PEP Tier 1 |
| 15 | Former PEP 18 Months | De-escalation | ✅ PASS (31.26)| EDD |
| 16 | BVI Shell Unknown BO | Fallback BO | ✅ PASS (52.94)| Data Block |
| 17 | Fan-In Mule Network | Velocity Consolidation | ✅ PASS (Auto) | Structuring 100% |
| 18 | Dormant Account Nigeria | Account Takeover | ✅ PASS (Auto) | Structuring 100% |
| 19 | TBML Letter of Credit | Trade-Based ML | ✅ PASS (Auto) | TBML Flag |
| 20 | Insurance Early Surrender| Integration Stage | ✅ PASS (Auto) | Insurance ML |
| MC-1| Classic Concentrator | Mule Cluster | ✅ PASS (95.00)| MCS Alert |
| MC-2| Salary Mule Network | Mule Cluster | ✅ PASS (60.00)| MCS Alert |
| MC-3| Dormant Activation | Mule Cluster | ✅ PASS (85.00)| MCS Alert |
| MC-4| UPI Smurfing Ring | Mule Cluster | ✅ PASS (95.00)| MCS Alert |
| MC-5| Legitimate Chit Fund | False Positive | ✅ PASS (5.00) | No Alert |

---

## ☁️ Cloud Infrastructure Verification
As of May 23, 2026, all 25 scenarios have been successfully executed against the live production environment:
- **API:** Render (Containerized Python)
- **DB:** Supabase (PostgreSQL Tokyo/Singapore)
- **UI:** Vercel (React)

---

## Version History

| Version | Change | Date | Author |
|---|---|---|---|
| 1.0 | Initial release Scenarios 11-20 | 3 May 2026 | Atul Krishnan, CAMS |
| 1.5 | Full 25-scenario set integration. Added MC-1 to MC-5. Verified against cloud environment. | 24 May 2026 | Atul Krishnan, CAMS |

---

*ScoreSentinel | Master Validation Scenarios | Authored by Atul Krishnan, CAMS | Version 1.5 | 24 May 2026*
