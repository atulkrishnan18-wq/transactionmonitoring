# MULE_CLUSTER_RULES.md — Cluster Intelligence Layer

**ScoreSentinel: Project MuleCatcher Overlay**
**Focus:** Coordinated Network Detection (India/RBI Context)
**Version:** 1.0 | **Author:** Atul Krishnan, CAMS

---

## 1. The Mule Cluster Problem
In the Indian context, mules are recruited in clusters (students, rural labourers). Detection of a single account is "reactive." Detection of the **cluster nexus** is "proactive."

## 2. Cluster Detection Rules (The "Weapon" Logic)

| Rule ID | Name | Threshold / Trigger | MPS Weight |
|---|---|---|---|
| **MUL-001** | **Rapid Depletion (Drain)** | >95% of credit funds transferred out within <2 hours. | 35 |
| **MUL-002** | **Nexus Velocity (Fan-In)** | >5 unique senders sending near-identical amounts in <24 hours. | 25 |
| **MUL-003** | **Dormant-to-Burst** | Account silent for >90 days suddenly processes >₹1,00,000 in <48 hours. | 20 |
| **MUL-004** | **Common Device Nexus** | >3 accounts sharing the same IP, Device ID, or MAC Address (Dashboard logic). | 50 (AUTO) |
| **MUL-005** | **Profile Contrast** | High-volume activity in accounts with occupation: 'Student', 'Unemployed', or 'Farmer'. | 15 |
| **MUL-006** | **Micro-Test Signal** | A ₹1.00 - ₹10.00 "test" transaction followed by a large burst within 1 hour. | 10 |

## 3. Mule Probability Score (MPS) Calculation
The MPS is a secondary score (0–100) specifically for the "Mule-Hunting" dashboard.

$$MPS = \sum (Rule Score \times Weight)$$

*   **MPS > 80:** High-Confidence Mule Cluster — Immediate Hard Block.
*   **MPS 50–80:** Probable Mule — Enhanced Monitoring / Document Request.
*   **MPS < 50:** Low Mule Signal.

## 4. RBI Typology Alignment
This module aligns with the **RBI Circular on Money Mules (2024)** focusing on the use of Jan Dhan accounts and the "re-purposing" of inactive savings accounts for cyber-fraud proceeds.

---
*ScoreSentinel | MULE_CLUSTER_RULES.md | Version 1.0 | Project MuleCatcher*
