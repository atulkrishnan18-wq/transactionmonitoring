# ROADMAP.md — ScoreSentinel 60-Day Build Plan

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.0 | **Author:** Atul Krishnan, CAMS | **Last Updated:** 25 April 2026

---

## Overview

| | Lead AML Architect | Gemini CLI (Technical Implementation) |
|---|---|---|
| **Focus** | Architectural design, risk threshold specification, and rule validation | Full-stack development: Python engine, Flask API, and React dashboard |
| **Result** | Proprietary AML risk scoring framework and functional prototype | Comprehensive technical transparency and component mastery |
| **By Day 60** | Production-ready project repository | Strategic project defense and technical fluency |

---

## Three Phases

| Phase | Days | Focus |
|---|---|---|
| **Phase 1** | Days 1–20 | AML Logic Design — rules, thresholds, testing, tech literacy |
| **Phase 2** | Days 21–45 | I Build, You Guide — Python engine, database, API, dashboard |
| **Phase 3** | Days 46–60 | You Own It — mastery, deployment, portfolio, launch |

---

## Progress Tracker

| Day | Deliverable | Status |
|---|---|---|
| 1 | AML_RULES.md | ✅ Done |
| 2 | STRUCTURING_RULES.md | ✅ Done |
| 3 | GEO_RULES.md | ✅ Done |
| 4 | CUSTOMER_RULES.md | ✅ Done |
| 5 | TRANSACTION_RULES.md | ✅ Done |
| 6 | COMPOSITE_LOGIC.md | 🔄 Pending |
| 7 | AML_RULES_FINAL.md | 🔄 Pending |
| 8–60 | See full plan below | 🔄 Pending |

---

# PHASE 1 — AML LOGIC DESIGN (Days 1–20)

---

## WEEK 1 — Rule Documentation & Structuring Detection

---

### Day 1 — Project Kickoff ✅
**Objective:** Get organised and document current rules
**Time:** 60 minutes

**Tasks:**
1. Review Excel scoring model (20 min)
2. Document current rules in detail (20 min)
3. List gaps to fix (10 min)
4. Create AML_RULES.md covering:
   - Amount thresholds
   - Geographic risk levels
   - Customer categories
   - Transaction types
   - Composite scoring logic

**Deliverable:** `rules/AML_RULES.md`
**Success Criteria:** Rules model fully documented and readable

---

### Day 2 — Structuring Detection Rules ✅
**Objective:** Deep dive into structuring patterns
**Time:** 60 minutes

**Tasks:**
1. Deep dive into structuring patterns (20 min)
2. Define structuring detection rules (30 min):
   - How many transactions = suspicious?
   - Time window — 24 hours vs 7 days?
   - Amount triggers
   - CTR threshold logic
3. Document test scenarios (10 min)

**Deliverable:** `rules/STRUCTURING_RULES.md`, `rules/STRUCTURING_SCENARIOS.md`
**Success Criteria:** Clear thresholds that can be coded

---

### Day 3 — Geography & Sanctions ✅
**Objective:** Define geographic risk and sanctions screening rules
**Time:** 60 minutes

**Tasks:**
1. List high-risk countries by tier — OFAC, FATF, CPI (15 min)
2. Define geography scoring logic — both sender and receiver (20 min)
3. Plan sanctions screening logic — fuzzy match, 50% ownership rule (20 min)
4. Document in GEO_RULES.md with SR 11-7 threshold justification (5 min)

**Deliverable:** `rules/GEO_RULES.md`
**Success Criteria:** Clear country tier classifications with justified scores

---

### Day 4 — Customer Risk Categorization ✅
**Objective:** Define customer types and risk scoring
**Time:** 60 minutes

**Tasks:**
1. Define customer types (10 min):
   - High risk: shell companies, PEPs, cash-intensive businesses, tax haven association
   - Medium risk: newly onboarded, non-resident, HNWI, trusts, charities
   - Low risk: verified individuals, listed companies, government entities
2. Create 5-dimension Composite Customer Risk Score (CCRS) (20 min)
3. Document PEP tiers and sanctions matching process (15 min)
4. Create CUSTOMER_RULES.md with SR 11-7 governance (15 min)

**Deliverable:** `rules/CUSTOMER_RULES.md`
**Success Criteria:** Clear categorisation logic with justified thresholds

---

### Day 5 — Transaction Type Analysis ✅
**Objective:** Assign risk scores to all transaction types
**Time:** 60 minutes

**Tasks:**
1. Analyse Excel transaction types — identified 13, added 6 (15 min)
2. Assign risk scores to all 19 types (20 min):
   - Cryptocurrency = 55 (highest)
   - Correspondent Banking = 50
   - Wire Transfer International = 45
   - Real Estate Payment = 45
   - Trade Finance / LC = 45
   - FX Transaction = 40
   - Money Order = 40
   - Cash Deposit / Withdrawal = 35
   - ATM = 30
   - Cheque = 25
   - Securities = 25
   - Internal Transfer = 20
   - Mobile / P2P = 20
   - Credit Card = 15
   - Online Payment = 15
   - Wire Transfer Domestic = 15
   - Loan Repayment = 10
   - Insurance Premium = 10
3. Document velocity rules VEL-001 to VEL-027 (15 min)
4. Document sequencing rules SEQ-001 to SEQ-006 (10 min)

**Deliverable:** `rules/TRANSACTION_RULES.md`
**Success Criteria:** All 19 transaction types scored with velocity and sequencing rules

---

### Day 6 — Composite Scoring Logic
**Objective:** Design final composite score calculation
**Time:** 60 minutes

**Tasks:**
1. Design composite score architecture (20 min):
   - Should amount weight 30%?
   - Should geography weight 25%?
   - Should customer weight 25%?
   - Should transaction type weight 20%?
2. Define final risk categories (15 min):
   - Low Risk: Score 0–20
   - Medium Risk: Score 21–59
   - High Risk: Score 60–89
   - Very High Risk: Score 90+
3. Address normalisation — prevent double counting across modules
4. Create COMPOSITE_LOGIC.md with SR 11-7 weight derivation (25 min)

**Deliverable:** `scoring/COMPOSITE_LOGIC.md`
**Success Criteria:** Weights and thresholds defined with documented rationale

---

### Day 7 — Rule Review & Refinement
**Objective:** Consolidate Week 1 and prepare for testing
**Time:** 60 minutes

**Tasks:**
1. Review all rules created this week for internal consistency (20 min)
2. Check cross-module alignment — do geo scores double count? (15 min)
3. Create AML_RULES_FINAL.md — master summary of all rules (15 min)
4. Commit everything to GitHub under correct folder structure (10 min)

**Deliverable:** `rules/AML_RULES_FINAL.md`
**Success Criteria:** All rules internally consistent, no contradictions

---

## WEEK 2 — Testing Scenarios & Edge Cases

---

### Day 8 — Real Transaction Scenarios
**Objective:** Create test cases with expected outcomes
**Time:** 60 minutes

**Tasks:**
1. Take 10 transactions from Excel (15 min)
2. Manually calculate risk scores using all modules (30 min)
3. Document expected outcomes for each (15 min)

**Deliverable:** `scenarios/TEST_SCENARIOS.md`
**Success Criteria:** 10 scenarios with expected composite scores

```
Example:
Scenario 1: Structuring Detection
Input: 5 cash deposits $9,500 each, same customer, 10 days
Expected: HIGH RISK — Score 85+
Logic: Structuring flag + near-CTR threshold + cash type score
```

---

### Day 9 — False Positive Testing
**Objective:** Prevent system from over-alerting
**Time:** 60 minutes

**Tasks:**
1. Identify false positive risk scenarios (20 min)
2. Design edge cases — legitimate transactions that look suspicious (20 min)
3. Document thresholds that prevent false positives (15 min)
4. Create EDGE_CASES.md (5 min)

**Deliverable:** `scenarios/EDGE_CASES.md`
**Success Criteria:** System will not over-alert on legitimate activity

---

### Day 10 — Velocity & Pattern Rules
**Objective:** Define transaction velocity and behavioural patterns
**Time:** 60 minutes

**Tasks:**
1. Define velocity patterns (15 min):
   - Normal: 1–2 transactions per week
   - Unusual: 5+ per week
   - Suspicious: 20+ per day
2. Document behavioural change indicators (15 min)
3. Create standalone VELOCITY_RULES.md (20 min)
4. Test velocity rules against Day 8 scenarios (10 min)

**Deliverable:** `rules/VELOCITY_RULES.md`
**Success Criteria:** All velocity patterns documented with thresholds

---

### Day 11 — Beneficial Owner & PEP Matching
**Objective:** Define PEP and beneficial owner risk logic
**Time:** 60 minutes

**Tasks:**
1. Define PEP matching rules in detail (20 min):
   - Tier 1: Heads of State, Cabinet Ministers
   - Tier 2: Senior Officials, Legislators
   - Tier 3: Family Members, Close Associates
2. Create beneficial owner risk logic — OFAC 50% rule (20 min)
3. Document fuzzy matching algorithm and thresholds (15 min)
4. Create standalone PEP_RULES.md (5 min)

**Deliverable:** `rules/PEP_RULES.md`
**Success Criteria:** Clear PEP tier structure and matching criteria

---

### Day 12 — Rules Validation
**Objective:** Test all rules comprehensively
**Time:** 60 minutes

**Tasks:**
1. Walk through all rules created (20 min)
2. Test against 20 transactions — 10 from Day 8 + 10 new (25 min)
3. Document any refinements needed (10 min)
4. Update AML_RULES_FINAL.md with changes (5 min)

**Deliverable:** Updated `rules/AML_RULES_FINAL.md`
**Success Criteria:** Confident in all thresholds after 20-transaction validation

---

### Day 13 — Audit Trail & Logging
**Objective:** Define compliance audit requirements
**Time:** 60 minutes

**Tasks:**
1. Design audit logging requirements (20 min):
   - What fields must every log entry contain?
   - Customer ID, score, rules fired, reviewer, timestamp
2. Define what needs to be logged for regulatory compliance (20 min)
3. Create AUDIT_REQUIREMENTS.md (15 min)
4. Commit all rules to GitHub (5 min)

**Deliverable:** `governance/AUDIT_REQUIREMENTS.md`
**Success Criteria:** Audit trail requirements fully defined

---

### Day 14 — Rules Review & GitHub Commit
**Objective:** Finalise and upload all rules
**Time:** 60 minutes

**Tasks:**
1. Final review of all rule documents (20 min)
2. Organise into correct GitHub folder structure (10 min):
   - `/rules/` — all rule documents
   - `/scenarios/` — test cases and edge cases
   - `/governance/` — audit requirements
   - `/scoring/` — composite logic
3. Update README.md with full project description (15 min)
4. Final commit: "Phase 1 Week 2 Complete — All AML rules documented" (15 min)

**Deliverable:** Clean GitHub repo — all rules live
**Success Criteria:** Complete rule documentation live on GitHub

---

## WEEK 3 — Tech Literacy (What's Under the Hood)

---

### Day 15 — How Python Will Execute Your Logic
**Objective:** Understand concepts without needing to code
**Time:** 60 minutes

**Tasks:**
1. Watch: "Python in 5 Minutes" (5 min)
2. Understand functions — your rules = functions (10 min):
   - Input: transaction data
   - Output: risk score
3. Understand data structures (15 min):
   - Your Excel rows = Python dictionaries
   - `{"amount": 5000, "country": "Nigeria", "type": "wire"}`
4. Watch high-level overview video (20 min)
5. Take notes in plain English (10 min)

**Deliverable:** Personal notes
**Success Criteria:** Can explain what a function does and why it matters

---

### Day 16 — Understanding Databases
**Objective:** Learn database concepts
**Time:** 60 minutes

**Tasks:**
1. Learn what a database is — tables = Excel sheets (10 min)
2. Understand columns = headers, rows = data (10 min)
3. Learn basic SQL concepts (15 min):
   - `SELECT` = show me these rows
   - `WHERE` = only if this condition
   - `SELECT * FROM transactions WHERE risk_score > 60`
4. Watch "Databases Explained Simply" (15 min)
5. Understand your transaction schema (10 min)

**Deliverable:** Personal notes
**Success Criteria:** Know what a database does — literacy not mastery

---

### Day 17 — APIs & System Architecture
**Objective:** Understand how your system will work end-to-end
**Time:** 60 minutes

**Tasks:**
1. Learn what an API is (10 min)
2. Understand request-response model (15 min):
   - You send: `{"amount": 5000, "country": "Iran", "type": "wire"}`
   - System returns: `{"score": 95, "alert": true, "rules_fired": ["GEO-1A", "TXN-WIRE-INT"]}`
3. Understand full data flow (15 min):
   - Transaction arrives → Engine scores it → Database stores it → Dashboard displays it
4. Watch "APIs Explained for Non-Programmers" (15 min)
5. Draw your own architecture diagram (5 min)

**Deliverable:** Architecture diagram sketch
**Success Criteria:** Can explain data flow end-to-end in plain English

---

### Day 18 — Dashboard & Frontend Basics
**Objective:** Understand and design the dashboard interface
**Time:** 60 minutes

**Tasks:**
1. Learn what React is — the tool for building dashboards (15 min)
2. Design what your dashboard should show (20 min):
   - Transaction list with risk scores
   - Filters by geography, type, customer, date
   - Charts — high risk by country, by type, by day
   - Transaction detail view — score breakdown by module
3. Create mockup sketch on paper or in Figma (20 min)
4. Document dashboard requirements (5 min)

**Deliverable:** Dashboard mockup and requirements document
**Success Criteria:** Clear UI/UX specification for the build phase

---

### Day 19 — Full Tech Stack Overview
**Objective:** Understand the complete system architecture
**Time:** 60 minutes

**Tasks:**
1. Understand the full tech stack (30 min):
   - **Python** = Scoring engine — calculates risk scores from your rules
   - **PostgreSQL** = Database — stores every transaction and its score
   - **Flask** = API — receives transactions, calls engine, returns scores
   - **React** = Dashboard — displays results, filters, charts
2. Understand how they connect (15 min)
3. Create data flow diagram (10 min)
4. Document in TECH_STACK_EXPLAINED.md (5 min)

**Deliverable:** `docs/TECH_STACK_EXPLAINED.md`
**Success Criteria:** Can explain how all four pieces fit together

---

### Day 20 — Tech Learning Review
**Objective:** Consolidate tech literacy foundation
**Time:** 60 minutes

**Tasks:**
1. Review what you learned across Week 3 (15 min)
2. Create TECHNICAL_OVERVIEW.md (20 min):
   - What Python does in ScoreSentinel
   - What the database does
   - What the API does
   - What the dashboard does
3. Write down any questions for clarification (15 min)
4. Commit all Phase 1 documents to GitHub (10 min)

**Deliverable:** `docs/TECHNICAL_OVERVIEW.md`
**Success Criteria:** Can explain the tech stack to a non-technical person

---

# PHASE 2 — I BUILD, YOU GUIDE (Days 21–45)

---

## Days 21–25 — Python Scoring Engine

**What Gets Built:** The engine that calculates risk scores based on your rules

**Your Daily Role (30 min/day):**
- Review code written
- Validate it matches your documented rules
- Test with your scenarios
- Suggest changes — no coding required

**My Role:**
- Convert your markdown rules into Python code
- Test against all 20 scenarios
- Handle errors and edge cases
- Explain every function in plain English

---

### Day 21 — Engine Structure & AML Base Rules
**Deliverable:** `engine/scoring_engine.py` — base structure, amount scoring
**Your Task:** Validate the amount thresholds match AML_RULES.md exactly

---

### Day 22 — Structuring & Geography Modules
**Deliverable:** `engine/structuring_module.py`, `engine/geo_module.py`
**Your Task:** Run 5 structuring scenarios, confirm scores match STRUCTURING_RULES.md

---

### Day 23 — Customer & Transaction Type Modules
**Deliverable:** `engine/customer_module.py`, `engine/transaction_module.py`
**Your Task:** Validate PEP scoring, shell company scoring, all 19 transaction types

---

### Day 24 — Composite Score & Velocity Rules
**Deliverable:** `engine/composite.py`, `engine/velocity.py`
**Your Task:** Confirm composite calculation matches COMPOSITE_LOGIC.md weights

---

### Day 25 — All 20 Scenarios Pass
**Deliverable:** Working scoring engine — all test scenarios produce correct scores
**Your Task:** Run every TEST_SCENARIOS.md case through the engine, confirm results

---

## Days 26–30 — Database & API

**What Gets Built:** PostgreSQL database + Flask REST API

---

### Day 26 — Database Schema Design
**Deliverable:** `database/schema.sql` — transactions table, customers table, alerts table
**Your Task:** Confirm all fields needed for audit logging are included

---

### Day 27 — Flask API — Core Endpoints
**Deliverable:** `api/app.py` — POST /score endpoint, GET /transactions endpoint
**Your Task:** Test with a sample transaction using Postman or browser

---

### Day 28 — Connect Engine to API
**Deliverable:** API calls scoring engine, returns composite score + rules fired
**Your Task:** Send 5 test transactions, confirm API returns correct scores

---

### Day 29 — API Testing & Validation
**Deliverable:** All endpoints tested, error handling added
**Your Task:** Test edge cases — what happens with missing fields, invalid countries

---

### Day 30 — Working API
**Deliverable:** Fully functional API — can score any transaction via API call
**Your Task:** Run all 20 TEST_SCENARIOS through the API, document results

---

## Days 31–35 — React Dashboard

**What Gets Built:** Visual interface to see transactions and scores

---

### Day 31 — Transaction List View
**Deliverable:** Dashboard with transaction list, risk scores, colour-coded alerts
**Your Task:** Review against Day 18 mockup — does it match your specification?

---

### Day 32 — Charts & Visualisations
**Deliverable:** Bar charts — alerts by country, by transaction type, by day
**Your Task:** Confirm charts show data that is useful for AML analysis

---

### Day 33 — Filters & Search
**Deliverable:** Filter by geography, transaction type, risk band, date range
**Your Task:** Test filters — can you find all Nigeria transactions from last week?

---

### Day 34 — Transaction Detail View
**Deliverable:** Click any transaction to see full score breakdown by module
**Your Task:** Confirm breakdown shows each module score — structuring, geo, customer, type

---

### Day 35 — Complete Dashboard
**Deliverable:** Fully functional dashboard — list, charts, filters, detail view
**Your Task:** Full walkthrough — does it feel like a real compliance tool?

---

## Days 36–40 — Integration & Testing

**What Gets Built:** All three layers connected — engine + API + dashboard working together

---

### Day 36 — End-to-End Integration
**Deliverable:** Full flow working — transaction in → score calculated → stored → displayed
**Your Task:** Submit a transaction through the dashboard, watch it appear in the list

---

### Day 37 — Bug Fixing
**Deliverable:** All bugs from Day 36 testing fixed
**Your Task:** Test 10 different scenarios end-to-end, document any issues

---

### Day 38 — Performance & Optimisation
**Deliverable:** System handles bulk transactions without slowing
**Your Task:** Submit 50 transactions, confirm dashboard stays responsive

---

### Day 39 — Full Scenario Test
**Deliverable:** All 20 TEST_SCENARIOS pass end-to-end through live system
**Your Task:** Run every scenario, compare live system output to expected outcomes

---

### Day 40 — Stable System v1.0
**Deliverable:** No bugs, all features working, system stable
**Your Task:** Final sign-off — confirm system is ready for documentation phase

---

## Days 41–45 — Refinement & Documentation

---

### Day 41 — User Acceptance Testing
**Deliverable:** UAT report — system tested as if you were a compliance analyst
**Your Task:** Spend 30 minutes using the system as you would in your BofA role

---

### Day 42 — Technical Documentation
**Deliverable:** `docs/ARCHITECTURE.md` — system architecture diagrams, component descriptions
**Your Task:** Review accuracy — does the diagram match what was actually built?

---

### Day 43 — SR 11-7 Model Governance
**Deliverable:** `governance/MODEL_GOVERNANCE.md` — full SR 11-7 compliance checklist
**Your Task:** Confirm all governance artifacts are in place across all modules

---

### Day 44 — Backtesting Methodology
**Deliverable:** `governance/BACKTESTING.md` — how to validate rules against historical data
**Your Task:** Review methodology — does it match regulatory expectations?

---

### Day 45 — Production-Ready System
**Deliverable:** System v1.0 — complete, tested, documented, ready to deploy
**Your Task:** Final review of entire codebase and documentation

---

# PHASE 3 — YOU OWN IT (Days 46–60)

---

## Days 46–50 — Mastery & Deployment

---

### Day 46 — System Deep Dive
**Objective:** Understand the complete codebase
**Time:** 60 minutes

**Tasks:**
1. Walk through entire codebase — every file explained (30 min)
2. Understand each component's role (15 min)
3. Ask clarification questions (10 min)
4. Take detailed notes (5 min)

**Deliverable:** Architecture notes
**Success Criteria:** Can explain what every file does

---

### Day 47 — Configuration & Rules Management
**Objective:** Learn to modify rules independently
**Time:** 60 minutes

**Tasks:**
1. Learn how to modify existing rules — change a threshold (20 min)
2. Learn how to add a new rule — add a new country to Tier 1C (20 min)
3. Practice modifying the alert threshold (15 min)
4. Document in HOW_TO_MODIFY.md (5 min)

**Deliverable:** `docs/HOW_TO_MODIFY.md`
**Success Criteria:** Can modify any rule without touching code logic

---

### Day 48 — Database & Queries
**Objective:** Learn basic database operations
**Time:** 60 minutes

**Tasks:**
1. Learn basic SQL queries (20 min):
   - `SELECT * FROM transactions WHERE risk_score >= 60`
   - `SELECT country, COUNT(*) FROM transactions GROUP BY country`
2. Practice retrieving your own data (20 min)
3. Learn how to export data to CSV (15 min)
4. Document common queries in QUERIES.md (5 min)

**Deliverable:** `docs/QUERIES.md`
**Success Criteria:** Can retrieve and export your own transaction data

---

### Day 49 — Troubleshooting & Bug Fixing
**Objective:** Handle common issues independently
**Time:** 60 minutes

**Tasks:**
1. Learn how to read Python error messages (20 min)
2. Practice debugging a broken scenario (20 min)
3. Learn how to fix the 5 most common issues (15 min)
4. Document troubleshooting guide (5 min)

**Deliverable:** `docs/TROUBLESHOOT.md`
**Success Criteria:** Can diagnose and fix common problems without help

---

### Day 50 — Deployment — Go Live
**Objective:** Deploy ScoreSentinel to the internet
**Time:** 60 minutes

**Tasks:**
1. Learn deployment process — Render or Vercel (20 min)
2. Deploy live system — get a public URL (20 min)
3. Test live system end-to-end (15 min)
4. Document deployment steps (5 min)

**Deliverable:** Live ScoreSentinel URL — accessible from anywhere
**Success Criteria:** System live and accessible online

---

## Days 51–55 — Portfolio & Presentation

---

### Day 51 — Portfolio Preparation
**Objective:** Create professional portfolio presentation
**Time:** 60 minutes

**Tasks:**
1. Write project summary — what ScoreSentinel is and what problem it solves (15 min)
2. Write about YOUR AML logic — emphasise the design decisions you made (20 min)
3. Take screenshots of live system (10 min)
4. Update GitHub README with full project description, live URL, architecture diagram (15 min)

**Deliverable:** Professional GitHub README
**Success Criteria:** README showcases your AML design expertise, not just the code

---

### Day 52 — Interview Preparation Part 1
**Objective:** Prepare your interview story
**Time:** 60 minutes

**Tasks:**
1. Practice explaining ScoreSentinel in 2 minutes (20 min)
2. Prepare demo video script — what to show and say (15 min)
3. Anticipate tough questions (15 min):
   - Why these thresholds?
   - How would you adapt for a different jurisdiction?
   - What about false positives?
   - How does SR 11-7 apply?
4. Create INTERVIEW_PREP.md (10 min)

**Deliverable:** `docs/INTERVIEW_PREP.md`
**Success Criteria:** Comfortable explaining every design decision

---

### Day 53 — Architecture Documentation
**Objective:** Create visual system documentation
**Time:** 60 minutes

**Tasks:**
1. Create system architecture diagram (20 min)
2. Create data flow diagram — transaction to alert (20 min)
3. Document each component's role in plain English (15 min)
4. Add all diagrams to GitHub (5 min)

**Deliverable:** `docs/ARCHITECTURE_DIAGRAMS.md`
**Success Criteria:** Any hiring manager can understand the system from the diagrams

---

### Day 54 — AML Logic Documentation
**Objective:** Document your AML expertise as the centrepiece of the project
**Time:** 60 minutes

**Tasks:**
1. Create detailed explanation of all AML rules (20 min)
2. Add examples and rationale for key decisions (20 min)
3. Explain scoring decisions — why these weights, why these thresholds (15 min)
4. Create AML_LOGIC_EXPLAINED.md (5 min)

**Deliverable:** `docs/AML_LOGIC_EXPLAINED.md`
**Success Criteria:** A CCO could read this and understand your risk philosophy

---

### Day 55 — Live Demo Practice
**Objective:** Prepare a smooth system demonstration
**Time:** 60 minutes

**Tasks:**
1. Practice live demo walkthrough (25 min):
   - Submit a transaction
   - Show it scored
   - Show the alert generated
   - Show the audit trail
2. Record demo video (20 min)
3. Review and refine (10 min)
4. Document demo script (5 min)

**Deliverable:** Demo video — ready to share
**Success Criteria:** Smooth, confident 3-minute demo from start to finish

---

## Days 56–60 — Launch

---

### Day 56 — Blog Post / Case Study
**Objective:** Publish your ScoreSentinel story
**Time:** 60 minutes

**Tasks:**
1. Write technical case study for Medium or LinkedIn (40 min):
   - Problem: AML transaction monitoring is opaque and hard to explain
   - Solution: A rules-based, fully transparent, SR 11-7 compliant scoring engine
   - Built: 60 days, 1 hour per day, no coding background
   - Result: Live system, documented rules, regulatory-grade governance
2. Publish article (15 min)
3. Share on LinkedIn with project link (5 min)

**Deliverable:** Published case study — publicly accessible
**Success Criteria:** Article clearly positions you as a compliance + technology leader

---

### Day 57 — Interview Preparation Part 2
**Objective:** Master the tough interview questions
**Time:** 60 minutes

**Tasks:**
1. Practice answering these questions out loud (20 min):
   - "Why did you choose 85% for your fuzzy match threshold?"
   - "How would you adapt this for a crypto exchange?"
   - "What is SR 11-7 and how does your model comply?"
   - "What are the limitations of your model?"
   - "How would you back-test this?"
2. Record practice interview (20 min)
3. Self-review — what needs to be sharper? (15 min)
4. Refine answers (5 min)

**Deliverable:** Practice interview recording
**Success Criteria:** Confident, specific, 60-second answers to any ScoreSentinel question

---

### Day 58 — Project Showcase
**Objective:** Create final presentation materials
**Time:** 60 minutes

**Tasks:**
1. Create presentation slides (30 min):
   - Slide 1: Problem statement
   - Slide 2: ScoreSentinel architecture
   - Slide 3: Key design decisions + regulatory basis
   - Slide 4: Live demo screenshots
   - Slide 5: What I built and what I learned
2. Practice full presentation (20 min)
3. Final screenshots and visuals (5 min)
4. Final polish (5 min)

**Deliverable:** Presentation deck — 5 slides, ready for any audience
**Success Criteria:** Could present this to a CCO, a regulator, or a hiring manager

---

### Day 59 — Final Review & Polish
**Objective:** Final quality check on everything
**Time:** 60 minutes

**Tasks:**
1. Review entire GitHub repo — every file, every folder (15 min)
2. Check all documentation — no placeholder text, no missing sections (15 min)
3. Fix any typos, broken links, or inconsistencies (15 min)
4. Final commit: "ScoreSentinel v1.0 — Project Complete" (15 min)

**Deliverable:** Clean, professional GitHub repo
**Success Criteria:** Would not be embarrassed to share this link in any professional context

---

### Day 60 — LAUNCH DAY 🚀
**Objective:** Production cutover, system health verification, and v2.0 roadmap formalization
**Time:** 60 minutes

**Tasks:**
1. Final system check — confirm live URL is working (10 min)
2. Share project on LinkedIn — tag it as a 60-day build (10 min)
3. Reflect on what you built (20 min)
4. Plan next steps (20 min):
   - What would Version 2 look like?
   - Which financial institutions would benefit from this?
   - How does this position you for your next role?

**Deliverable:** Live ScoreSentinel — publicly accessible, fully documented
**Success Criteria:** System live, portfolio complete, interview-ready

---

# What You Will Have By Day 60

## Technical Deliverables
- ✅ Live AML transaction monitoring system
- ✅ Rules-based scoring engine with YOUR rules
- ✅ PostgreSQL database with transaction history
- ✅ Flask REST API
- ✅ React dashboard with charts and filters
- ✅ Full SR 11-7 compliant documentation

## Portfolio Deliverables
- ✅ GitHub repo — complete, professional, version-controlled
- ✅ Professional README with live URL
- ✅ Architecture diagrams
- ✅ AML logic documentation
- ✅ Demo video
- ✅ Case study blog post
- ✅ Live system URL

## Interview Deliverables
- ✅ Clear understanding of every component you built
- ✅ Ability to explain every rule and its rationale
- ✅ Prepared answers to every tough question
- ✅ Practice demo ready
- ✅ Presentation slides
- ✅ LinkedIn case study

---

# Daily Time Commitment

| Phase | Days | Time per Day | Focus |
|---|---|---|---|
| Phase 1 | 1–20 | 60 min | AML logic design |
| Phase 2 | 21–45 | 60 min | Review and validate builds |
| Phase 3 | 46–60 | 60 min | Own, master, deploy, present |

**Total: 60 hours over 60 days**

---

# Folder Structure at Day 60

```
transactionmonitoring/
│
├── README.md
│
├── rules/
│   ├── AML_RULES.md              ✅ Day 1
│   ├── STRUCTURING_RULES.md      ✅ Day 2
│   ├── GEO_RULES.md              ✅ Day 3
│   ├── CUSTOMER_RULES.md         ✅ Day 4
│   ├── TRANSACTION_RULES.md      ✅ Day 5
│   ├── COMPOSITE_LOGIC.md        Day 6
│   ├── AML_RULES_FINAL.md        Day 7
│   ├── VELOCITY_RULES.md         Day 10
│   ├── PEP_RULES.md              Day 11
│   └── ESCALATION_RULES.md       Day 12
│
├── scoring/
│   ├── COMPOSITE_LOGIC.md        Day 6
│   ├── WEIGHT_DERIVATION.md      Day 9
│   └── NORMALISATION.md          Day 11
│
├── scenarios/
│   ├── TEST_SCENARIOS.md         Day 8
│   ├── EDGE_CASES.md             Day 9
│   └── COMBINED_SCENARIOS.md     Day 20
│
├── governance/
│   ├── AUDIT_REQUIREMENTS.md     Day 13
│   ├── MODEL_GOVERNANCE.md       Day 43
│   ├── BACKTESTING.md            Day 44
│   └── SR11_7_COMPLIANCE.md      Day 43
│
├── engine/                        Days 21–25
│   ├── scoring_engine.py
│   ├── geo_module.py
│   ├── customer_module.py
│   ├── transaction_module.py
│   ├── composite.py
│   └── velocity.py
│
├── api/                           Days 26–30
│   └── app.py
│
├── database/                      Day 26
│   └── schema.sql
│
├── dashboard/                     Days 31–35
│   └── [React components]
│
├── docs/
│   ├── TECH_STACK_EXPLAINED.md   Day 19
│   ├── TECHNICAL_OVERVIEW.md     Day 20
│   ├── ARCHITECTURE.md           Day 42
│   ├── HOW_TO_MODIFY.md          Day 47
│   ├── QUERIES.md                Day 48
│   ├── TROUBLESHOOT.md           Day 49
│   ├── INTERVIEW_PREP.md         Day 52
│   ├── AML_LOGIC_EXPLAINED.md    Day 54
│   └── WHITEPAPER.md             Day 60
│
└── gaps/
    ├── GAPS_TO_ADDRESS.md        ✅ Day 1
    ├── KNOWN_LIMITATIONS.md      Day 18
    └── FUTURE_ENHANCEMENTS.md    Day 50
```

---

*ScoreSentinel | ROADMAP.md | Authored by Atul Krishnan, CAMS | Version 1.0 | 25 April 2026*
