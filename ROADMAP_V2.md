# 🛡️ ScoreSentinel 2.0: The 30-Day Consistency Roadmap

This roadmap transitions ScoreSentinel from a "Completed MVP" to an **Advanced Engineering Powerhouse**. Each day is designed to take **~60 minutes** to keep you consistent without burnout.

## 🎯 The Objective: Link Analysis & AI Explainability
Evolution from simple rules to **Graph-based Intelligence** and **Automated Rationale Generation**.

---

### Week 1: Link Analysis & Graph Intelligence (MuleCatcher™ Evolution)
*Focus: Detecting how accounts are connected beyond just transactions.*

*   **Day 01:** **Database Resurrection:** ✅ Unpause Supabase, run `check_db.py`, and run the full test suite.
*   **Day 02:** **Link Analysis Design:** ✅ Draft a schema for a `customer_links` table (Shared IP, Shared Device, Shared Address).
*   **Day 03:** **Schema Execution:** ✅ Apply the `customer_links` SQL migration and build graph traversal logic.
*   **Day 04:** **Nexus Logic:** Implement "Shared Device ID" detection in the scoring engine.
*   **Day 05:** **Circular Logic:** Build a rule to detect "Circular Flow of Funds" (User A -> B -> C -> A).
*   **Day 06:** **Validation Suite:** Create `tests/scenarios_v2/mule_ring.json` to test multi-hop links.
*   **Day 07:** **Git Sync:** Commit Week 1 changes and push to GitHub (Release v2.0-Alpha.1).

### Week 2: External Integrations & AI Explainability
*Focus: Real-world data feeds and making alerts "speak".*

*   **Day 08:** **External API Research:** Study the OFAC/Sanctions JSON structure for live integration.
*   **Day 09:** **Mock Sanctions Feed:** Build a local "Mock Sanctions API" to simulate live lookups.
*   **Day 10:** **Fuzzy Matching v2:** Implement Jaro-Winkler string similarity for better name screening.
*   **Day 11:** **AI Explainability (Design):** Draft the prompt for "XAI" (Explainable AI) to justify a score.
*   **Day 12:** **Explainer Module:** Create `engine/ai_explainer.py` to generate automated investigative rationales.
*   **Day 13:** **Audit Lock v2:** Update the "3-Point Standard" to require an AI-generated summary check.
*   **Day 14:** **Git Sync:** Commit Week 2 changes and push to GitHub.

### Week 3: Production Engineering & UI Refinement
*Focus: Making the dashboard feel like a professional bank tool.*

*   **Day 15:** **Dashboard Search:** Add a global search bar to the React UI for Transaction IDs.
*   **Day 16:** **Advanced Filtering:** Build filters for "High Risk Only" or "MuleCatcher Hits" on the queue.
*   **Day 17:** **Dark Mode / High Contrast:** Implement a "Regulatory Mode" (high-contrast accessibility).
*   **Day 18:** **Visual Timeline:** Create an interactive "Transaction History" graph for a single customer.
*   **Day 19:** **API Security:** Implement JWT-based Auth or robust API Key rotation logic.
*   **Day 20:** **Performance Benchmarking:** Use `cProfile` to find bottlenecks in the scoring loop.
*   **Day 21:** **Git Sync:** Commit Week 3 changes and push to GitHub.

### Week 4: The Narrative & Professional Outreach
*Focus: Showing the world that ScoreSentinel 2.0 is industry-leading.*

*   **Day 22:** **Data Stress Test:** Script 1,000 synthetic transactions to test system stability.
*   **Day 23:** **Technical Case Study:** Write `docs/MULECATCHER_V2.md` explaining Graph Intelligence.
*   **Day 24:** **Demo Video Prep:** Record a 2-minute "no-fluff" screen capture of the 2.0 features.
*   **Day 25:** **Model Risk (SR 11-7):** Update the governance docs to include v2.0 logic weights.
*   **Day 26:** **Dependency Audit:** Run `pip-audit` and update all packages for production safety.
*   **Day 27:** **Portfolio Update:** Update the main `README.md` with "v2.0" features and screenshots.
*   **Day 28:** **LinkedIn Deep-Dive:** Draft a post about "Bridging Link Analysis with AML Rules."
*   **Day 29:** **Final Bug Bash:** Resolve any UI glitches or logic edge cases.
*   **Day 30:** **V2.0 LAUNCH:** Tag the release on GitHub, push all final docs, and celebrate!

---
*Consistency is the only metric that matters. One task. One hour. Every day.*
