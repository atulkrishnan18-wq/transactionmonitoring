# VELOCITY_RULES.md - 7-day Rolling Velocity Detection Module

## Overview
This document outlines the scoring methodology and thresholds for the velocity detection module, which calculates risk across four dimensions over a 7-day rolling window for a given customer.

## Regulatory Basis
- PMLA 2002
- FIU-IND STR Guidelines
- FATF Recommendation 29

## Dimensions & Scoring Thresholds

The velocity score is the equally weighted average (25% each) of the following four dimensions:

### 1. Transaction Count
Counts all transactions executed by the customer in the last 7 days.
- **< 5 tx:** Score 0
- **5-10 tx:** Score 40
- **11-20 tx:** Score 70 (Triggers `VEL-001-HIGH-FREQUENCY`)
- **> 20 tx:** Score 90

### 2. Total Volume
Sums all transaction amounts executed by the customer in the last 7 days.
- **< 10,000:** Score 0
- **10,000 - 50,000:** Score 40
- **50,000 - 100,000:** Score 70 (Triggers `VEL-002-HIGH-VOLUME`)
- **> 100,000:** Score 90

### 3. Distinct Counterparties
Counts the number of distinct receiver accounts interacted with in the last 7 days.
- **< 3:** Score 0
- **3 - 5:** Score 40
- **6 - 10:** Score 70 (Triggers `VEL-003-MANY-COUNTERPARTIES`)
- **> 10:** Score 90

### 4. Structuring Pattern
Counts the number of transactions falling between 75% and 99% of the reporting threshold (e.g., 7,500 - 9,900 against a 10,000 threshold).
- **< 2:** Score 0
- **2 - 3:** Score 60 (Triggers `VEL-004-STRUCTURING-PATTERN`)
- **4 - 5:** Score 85
- **> 5:** Score 95

## Rules Fired
If a dimension breaches its high-risk threshold, the system appends the respective rule to the transaction's `rules_fired` array, driving alert generation and prioritization.
- `VEL-001-HIGH-FREQUENCY` (Count >= 70)
- `VEL-002-HIGH-VOLUME` (Volume >= 70)
- `VEL-003-MANY-COUNTERPARTIES` (Counterparties >= 70)
- `VEL-004-STRUCTURING-PATTERN` (Structuring >= 60)