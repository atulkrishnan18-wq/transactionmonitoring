# DEMO_GUIDE.md — ScoreSentinel Presentation Script

**Author:** Atul Krishnan, CAMS
**Purpose:** Structured 5-minute walkthrough for live demos and recording.

---

## 🎬 Introduction (30 Seconds)
"Hello, I'm Atul Krishnan, a CAMS-certified AML professional. Today I'm demonstrating **ScoreSentinel**, a risk-based transaction monitoring engine I built to bridge the gap between regulatory theory and technical execution. The system is live on a multi-cloud stack featuring Render, Supabase, and Vercel."

---

## 🛡️ Step 1: The Alert Queue (1 Minute)
**Action:** Open `https://transactionmonitoring.vercel.app/`
**Talk Track:**
*   "This is the production analyst dashboard. Unlike traditional binary systems, every transaction is assigned a **Composite Risk Score (CRS)**."
*   "We prioritize cases by risk score or alert type. You can see we have active alerts for **Sanctions** (auto-triggered) and **AML Risk** (score-triggered)."
*   "Notice the 'Mule Cluster' alerts—these indicate organized network activity rather than isolated individual risk."

---

## 🔍 Step 2: Case Investigation & 3-Point Audit (2 Minutes)
**Action:** Click 'View Case' on a high-risk alert (e.g., John Doe).
**Talk Track:**
*   "Inside the case, we have total model transparency. The **Score Breakdown** shows exactly which module—Customer, Geography, or Structuring—contributed to the score."
*   "This satisfies **SR 11-7** requirements for model explainability. There is no 'black box' here."
*   "The most critical feature is the **Dual-Resolution Standard (Audit Lock)**. I've programmed a 'Hard Block' into the system that adjusts based on the risk type."
*   "For **Screening Matches** (Sanctions/PEP), I **cannot** resolve this case without entering the **Three-Point Identifier Standard**—three unique IDs and their sources."
*   "For **Transaction Risk** (Behavioral), the system enforces a **Mandatory Rationale Standard**, requiring a detailed investigative write-up before closure."
*   **Action:** Try to click 'Resolve' on a screening match without filling the audit form to show the error message.
*   "This ensures operational integrity and provides a bulletproof audit trail for regulators."

---

## 🕸️ Step 3: MuleCatcher™ Intelligence (1 Minute)
**Action:** Navigate to the 'Mule Clusters' tab.
**Talk Track:**
*   "Finally, we look at **MuleCatcher™**. Traditional systems miss organized fraud because individual transactions are small. MuleCatcher looks at the **Network**."
*   "Here you see a **Fan-In Cluster**. Fifteen different accounts are sending round-sum amounts to a single concentrator. The engine correlates this activity in real-time, targeting the massive fraud problem in the Indian banking sector."

---

## 🏁 Conclusion (30 Seconds)
"ScoreSentinel proves that compliance logic can be automated without losing regulatory defensibility. It’s secure, explainable, and production-ready. Thank you for your time."

---

## 🎥 Recording Checklist:
1.  **Resolution:** 1080p (Full HD).
2.  **Audio:** Use a clear microphone; ensure no background noise.
3.  **Speed:** Don't rush. Pause for 2 seconds after each click to allow the cloud API to respond.
4.  **Cursor:** Use a mouse highlighter or move the cursor slowly to guide the viewer's eye.

---
*Prepared by Atul Krishnan, CAMS | Day 55 of 60*
