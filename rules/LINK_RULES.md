# Link Analysis Rules (LNK)
**Module:** Graph Intelligence / LinkAnalysisModule
**Version:** 1.0 | **Status:** ACTIVE 🛡️

## Overview
Link Analysis rules detect relationships between customers based on shared attributes (IP, Device ID, Physical Address). These rules identify potential mule networks and coordinated fraud rings that evade traditional transaction-based rules.

---

## Rule Definitions

| Rule Code | Title | Description | Logic | Risk Weight |
|---|---|---|---|---|
| **LNK-001** | **Direct Device Nexus** | Customer shares a hardware device with 1 other customer. | Depth 1 link via `SHARED_DEVICE`. | 25 |
| **LNK-002** | **Multi-Account Device Nexus** | Customer shares a hardware device with 2+ other customers. | Multiple Depth 1 links via `SHARED_DEVICE`. | 50 |
| **LNK-003** | **Extended Device Network** | Customer is connected to a shared device via an intermediary. | Depth 2 link via `SHARED_DEVICE`. | 15 |
| **LNK-004** | **High Frequency Shared Access** | Repeated logins/transactions from the same shared IP or Device. | `link_count` >= 10 on any connection. | 20 |
| **LNK-005** | **Fully Connected Cluster** | Customer is part of a triangle (A-B-C-A) where all members are linked. | Presence of a 3-member fully connected sub-graph. | 40 |

---

## Scoring Logic
- **Module Maximum:** 100
- **Alert Threshold:** 50
- **Normalization:** `min(sum(triggered_rules.weight), 100)`

---

## Risk Bands
- **CRITICAL (80+):** High probability of an organized mule ring or professional money laundering network.
- **HIGH (50-79):** Significant coordination detected; requires immediate investigative priority.
- **MEDIUM (25-49):** Suspicious links detected; requires enhanced due diligence (EDD).
- **LOW (<25):** Common household or incidental sharing detected.
