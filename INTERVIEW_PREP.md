# INTERVIEW_PREP.md — ScoreSentinel Interview Guide

**Author:** Atul Krishnan, CAMS
**Purpose:** Strategic talking points and demo scripts for professional AML interviews.

---

## 🛡️ The Elevator Pitch (60 Seconds)
"ScoreSentinel is a professional-grade AML Transaction Monitoring engine I built to solve the 'black-box' problem in compliance technology. As a CAMS-certified professional at Bank of America, I wanted to create a system that doesn't just score risk, but enforces regulatory defensibility. It features a proprietary **Composite Risk Scoring (CRS)** framework and **MuleCatcher™** for network intelligence. Most importantly, it enforces a **Three-Point Identifier Standard**, making it impossible for an analyst to close a case without a bulletproof audit trail. It’s currently live on a multi-cloud stack (Render, Supabase, Vercel) and has been validated against 25+ complex AML scenarios."

---

## 💎 The "Three Pillars" of Your Story

### 1. Model Explainability (SR 11-7)
*   **The Point:** "We don't use black-box AI."
*   **The Logic:** Every alert shows a color-coded breakdown of exactly which module (Customer, Geo, Structuring, TX Type) contributed to the score.
*   **Interview Hook:** "If a regulator asks why we flagged a specific transaction, ScoreSentinel provides a documented, rules-based answer in plain English."

### 2. Operational Integrity (The 3-Point Standard)
*   **The Point:** "The system prevents analyst errors."
*   **The Logic:** The 'Audit Lock' prevents case resolution unless 3 identifiers and 3 sources are verified.
*   **Interview Hook:** "I designed this based on real-world operational gaps I've seen. It ensures that 100% of our 'False Positive' decisions are backed by evidence."

### 3. Network Intelligence (MuleCatcher™)
*   **The Point:** "We catch organized crime, not just individuals."
*   **The Logic:** It uses 'Fan-In' detection and 'Device Nexus' tracking to find clusters of 10-20 accounts acting in coordination.
*   **Interview Hook:** "Traditional systems often miss the 'Mule' because the individual amounts are small. MuleCatcher™ looks at the network coordination, targeting the ₹11,000 Crore fraud problem."

---

## 🎬 5-Minute Demo Script (The "Winning Walkthrough")

1.  **The Queue:** "Here is our live production environment. We prioritize by CRS score."
2.  **The Analysis:** "Let's look at this high-risk wire. You can see the Geography hits 90% because of the grey-list corridor, while the Customer risk is elevated due to shell company layering."
3.  **The Network:** "If we switch to MuleCatcher™, you can see this isn't an isolated event—this account is the 'Concentrator' for a 10-account smurfing ring."
4.  **The Resolution:** "To close this, notice I can't just click Resolve. I must first enter my Passport and Utility Bill verifications in the Audit tab to satisfy the Three-Point Standard."

---

## ❓ Anticipated "Gotcha" Questions

**Q: Why use a 60-point threshold for alerts?**
*   **Answer:** "It was calibrated through iterative backtesting (Scenario 9 proof). A score of 60 ensures that at least TWO major risk dimensions must be elevated before we interrupt the customer experience, keeping our False Positive rate below 15%."

**Q: How does the system handle Sanctions differently than AML Risk?**
*   **Answer:** "Sanctions are 'Auto-Alert' triggers. They bypass the CRS score entirely because a match against OFAC or SDN lists is non-discretionary. This prevents 'averaging out' a high-risk match with low-risk customer data."

**Q: What happens if a customer has no 'Device Nexus' data?**
*   **Answer:** "The system uses a 'Fallback Rule' (MUL-018). It flags the missing data as a risk factor itself, ensuring that 'Data Silence' is treated with suspicion during the onboarding phase."

---
*Prepared by Atul Krishnan, CAMS | Day 52 of 60*
