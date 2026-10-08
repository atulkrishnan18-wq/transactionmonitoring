# DR_BCP.md — Disaster Recovery and Business Continuity Plan

**ScoreSentinel AML Transaction Risk Scoring Engine**
**Version:** 1.0 | **Author:** Atul Krishnan, CAMS
**Last Updated:** September 2026
**Classification:** Internal — Governance

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Components and Architecture](#2-system-components-and-architecture)
3. [Failure Scenarios and Response Procedures](#3-failure-scenarios-and-response-procedures)
4. [Recovery Time Objectives (RTO)](#4-recovery-time-objectives-rto)
5. [Recovery Point Objectives (RPO)](#5-recovery-point-objectives-rpo)
6. [Backup Procedures](#6-backup-procedures)
7. [DR Drill Schedule](#7-dr-drill-schedule)
8. [Client Communication Templates](#8-client-communication-templates)
9. [Regulatory Considerations](#9-regulatory-considerations)
10. [Escalation Matrix](#10-escalation-matrix)
11. [Version History](#11-version-history)

---

## 1. Executive Summary

This Disaster Recovery and Business Continuity Plan (DR/BCP) defines the procedures, responsibilities, and timelines that govern ScoreSentinel's response to service disruptions, data loss events, and security incidents. The plan is designed to ensure that AML transaction screening capabilities are restored within documented Recovery Time Objectives (RTOs) and that data loss does not exceed the defined Recovery Point Objectives (RPOs).

ScoreSentinel's primary obligation is to the AML compliance function of its client institutions. Any extended outage directly impairs a regulated entity's ability to screen transactions in real time — a failure with potential regulatory consequences for both the client and ScoreSentinel. This plan treats availability as a compliance requirement, not merely a technical goal.

### 1.1 Scope

This plan covers all production components of ScoreSentinel:

- **API Layer:** Flask application hosted on Render (planned migration to AWS Mumbai ap-south-1)
- **Database Layer:** Supabase PostgreSQL (primary data store)
- **Dashboard Layer:** React application hosted on Vercel
- **Sanctions Feeds:** Locally cached JSON files (UAPA, OFAC, UN Consolidated)
- **Rules Configuration:** `rules/rules_config.json` — version-controlled

### 1.2 Plan Owner

| Role | Name | Contact |
|---|---|---|
| Plan Owner | Atul Krishnan, CAMS | Primary escalation contact |
| Technical Lead | Atul Krishnan | Incident response coordinator |
| Compliance Lead | Atul Krishnan | Regulatory notification authority |

### 1.3 Last DR Test

| Test Type | Date | Result | Next Scheduled |
|---|---|---|---|
| API failover simulation | TBD | Not yet tested | Q1 2027 |
| Database restore test | TBD | Not yet tested | Q1 2027 |
| Dashboard rollback test | TBD | Not yet tested | Q1 2027 |
| Full DR drill | TBD | Not yet tested | Q1 2027 |

---

## 2. System Components and Architecture

### 2.1 Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT INSTITUTIONS                     │
│     NBFCs, Cooperative Banks, Payment Aggregators (India)    │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS API Calls
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               RENDER (API Hosting) — Current                 │
│  Flask REST API — ScoreSentinel Scoring Engine               │
│  Region: US (Oregon) → Planned: AWS Mumbai ap-south-1        │
│  Auto-deploy from GitHub main branch                         │
└───────────────────────────┬─────────────────────────────────┘
                            │ psycopg2 PostgreSQL connection
                            ▼
┌─────────────────────────────────────────────────────────────┐
│             SUPABASE PostgreSQL (Database)                   │
│  Primary data store for transactions, alerts, customers      │
│  Daily automated backups (Supabase dashboard)                │
│  Region: AWS ap-northeast-1 (Tokyo)                          │
│  Planned: Migration to ap-south-1 (Mumbai) for RBI           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              VERCEL (Dashboard Hosting)                      │
│  React application — ScoreSentinel AML Dashboard             │
│  Auto-deploy from GitHub main branch                         │
│  Region: Vercel CDN (global edge nodes)                      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 API Layer — Render

| Attribute | Current Value | Target Value |
|---|---|---|
| Platform | Render | AWS Mumbai ap-south-1 |
| Runtime | Python 3.x / Flask | Python 3.x / Flask |
| Deployment | GitHub auto-deploy | GitHub Actions → AWS |
| Health endpoint | `GET /api/health` | `GET /api/health` |
| Session persistence | Stateless | Stateless |
| Uptime target | 99.5% | 99.9% |

**Render Free Tier Limitations:** The current Render deployment may experience cold-start delays (30–60 seconds) after periods of inactivity. Cold-start delay does not constitute a failure event but should be monitored and disclosed to clients.

### 2.3 Database Layer — Supabase PostgreSQL

| Attribute | Value |
|---|---|
| Platform | Supabase |
| Engine | PostgreSQL 15+ |
| Tables | `transactions`, `customers`, `alerts`, `mule_clusters` |
| Connection pool | Supabase pooler (pgBouncer) |
| Backup frequency | Daily (Supabase automated) |
| Backup retention | 7 days (free tier) |
| Current region | AWS ap-northeast-1 (Tokyo) |
| Planned region | AWS ap-south-1 (Mumbai) |

**Critical Note:** The `transactions` table implements an INSERT-ONLY immutability rule enforced at the application layer. No UPDATE or DELETE operations are permitted after scoring. Any restore from backup must preserve this constraint.

### 2.4 Dashboard Layer — Vercel

| Attribute | Value |
|---|---|
| Platform | Vercel |
| Framework | React (Vite) |
| Deployment | GitHub auto-deploy from `main` |
| Region | Global CDN (edge nodes) |
| API dependency | Render API endpoint |

**Dashboard Dependency:** The Vercel dashboard is a read-only consumer of the Render API. A Render outage will cause the dashboard to display error states, even if Vercel itself is fully operational. Dashboard failures must be diagnosed by checking the API health endpoint first.

### 2.5 Sanctions Feeds

| Feed | Update Method | Local Cache | Source |
|---|---|---|---|
| UAPA Schedule I | Manual (RBI circulars) | `feeds/uapa/uapa_schedule1.json` | MHA India |
| UAPA Schedule IV | Manual (MHA gazette) | `feeds/uapa/uapa_schedule4.json` | MHA India |
| UNSC 1267 | Manual | `feeds/uapa/unsc_1267.json` | UN Security Council |
| UNSC 1988 | Manual | `feeds/uapa/unsc_1988.json` | UN Security Council |
| OFAC SDN | Automated ingestion | `feeds/ofac/ofac_latest.json` | US Treasury |
| UN Consolidated | Automated ingestion | `feeds/un/un_latest.json` | UNSC |

Sanctions feeds are local JSON files version-controlled in GitHub. A platform outage does not affect sanctions screening availability as long as the API container can access the local filesystem. This design ensures sanctions screening is resilient to database failures.

---

## 3. Failure Scenarios and Response Procedures

### Scenario A — Render API Goes Down

**Definition:** The Flask API hosted on Render is unresponsive. `GET /api/health` returns a non-200 response or times out within 10 seconds.

**Detection Method:**
- Render dashboard alert (configure via Render notifications)
- Client institution reports API timeout or HTTP 502/503
- Manual health check: `curl -w "%{http_code}" https://<render-url>/api/health`
- Automated uptime monitor (UptimeRobot or StatusCake — to be configured)

**Immediate Response Steps (0–5 minutes):**
1. Check Render status page at `status.render.com`
2. Check Render service logs in the Render dashboard under `Logs`
3. Confirm if the issue is a cold-start delay (30–60 seconds) or a true outage
4. Notify internal stakeholders if outage is confirmed after 2 minutes
5. Post initial status update on client communication channel

**Recovery Procedure:**

*If Render platform failure:*
1. Attempt manual redeploy via Render dashboard → `Manual Deploy → Deploy latest commit`
2. If redeploy fails, examine build logs for environment variable or dependency errors
3. If Render platform is confirmed down (status.render.com), initiate interim failover

*Interim cloud failover (if Render is down > 15 minutes):*
```bash
# All code is in GitHub — all secrets stored in environment variables
# Deploy Flask API to Railway.app or Google Cloud Run as interim endpoint

git clone https://github.com/atulkrishnan18-wq/transactionmonitoring
cd transactionmonitoring

# Set required environment variables
export DATABASE_URL="<supabase-connection-string>"
export DEMO_API_KEY="<api-key>"

# Run API locally or push to alternative cloud
python api/app.py
```

*If code deployment failure (Render running, app crashing):*
1. Review recent commits for breaking changes (`git log --oneline -10`)
2. Roll back to last known good commit via Render's deploy history tab
3. Test health endpoint after rollback

**Recovery Verification:**
- `GET /api/health` returns HTTP 200 with `{"status": "ok"}`
- `POST /api/score` with a test payload completes without error
- Database connectivity confirmed in API response metadata

**Expected Recovery Time:** 30 minutes (RTO-A)
**Escalation trigger:** If unresolved after 15 minutes, notify client institutions (Template A).

---

### Scenario B — Supabase Database Unavailable

**Definition:** The PostgreSQL database hosted on Supabase is unreachable. Scoring API returns HTTP 500 on database-dependent endpoints.

**Detection Method:**
- API logs showing `psycopg2.OperationalError` or `connection pool exhausted`
- `POST /api/score` returning HTTP 500
- Supabase status page: `status.supabase.com`
- Direct connection test: `psql $DATABASE_URL -c "SELECT 1;"`

**Immediate Response Steps (0–5 minutes):**
1. Check Supabase project dashboard for connectivity and project health indicators
2. Verify `DATABASE_URL` environment variable is correctly set in Render dashboard
3. Check if the Supabase free tier has hit the row limit (500MB storage limit on free tier)
4. Confirm if connection pool is exhausted — restart Render service to flush stale connections
5. Notify client institutions that database-dependent scoring is temporarily unavailable

**Recovery Procedure:**

*If Supabase connectivity failure (platform-side):*
1. Check `status.supabase.com` for active incidents
2. If Supabase is performing scheduled maintenance, wait and monitor — do not intervene
3. If a connection pool exhaustion is suspected, restart the Render service to release connections

*If free tier resource limit reached:*
1. Log in to Supabase dashboard → Settings → Usage
2. If storage limit exceeded: delete test data, archive old records, or upgrade to Pro plan
3. If row limit exceeded: same remediation

*If data corruption is suspected:*
1. **Immediately halt all write operations:** Set `MAINTENANCE_MODE=true` in Render environment variables
2. Take a manual Supabase snapshot via Dashboard → Settings → Database → Create snapshot
3. Review the `transactions` table for anomalous entries: `SELECT * FROM transactions ORDER BY timestamp_processed DESC LIMIT 100;`
4. Do NOT restore from backup until data loss scope is confirmed
5. Follow restore procedure in Section 6.2

**Recovery Verification:**
- `GET /api/customers` returns customer data from the database
- `POST /api/score` completes without a 500 error
- Confirm record count post-recovery matches pre-failure count

**Expected Recovery Time:** 1 hour (RTO-B)
**Escalation trigger:** If data loss is confirmed, treat as Scenario E (security/data incident).

---

### Scenario C — Vercel Dashboard Fails

**Definition:** The React dashboard at the Vercel-hosted URL is inaccessible, returns errors, or displays an application failure state.

**Detection Method:**
- Browser returns 404, 502, or blank page
- Vercel deployment failure email notification
- Vercel status page: `vercel-status.com`

**Immediate Response Steps (0–5 minutes):**
1. Check Vercel project dashboard for build and deployment status
2. **Critical first step:** Test the Render API directly — dashboard failures are often caused by API outages, not Vercel issues
3. Check browser console (`F12 → Console`) for JavaScript errors or failed API requests
4. If API is returning errors, resolve Scenario A first before investigating Vercel

**Recovery Procedure:**

*If Vercel deployment failure (build error):*
1. Review Vercel build logs for specific errors (missing `npm` dependencies, incorrect environment variables, TypeScript errors)
2. Fix the identified issue in the local `dashboard/` directory
3. Trigger manual redeployment: `vercel --prod` from the dashboard directory, or push a fix to `main`

*If Vercel platform failure (Vercel-side outage):*
1. Vercel CDN failures are typically short-lived and resolved by Vercel automatically
2. No manual intervention is required during platform-side outages
3. Monitor `vercel-status.com` and communicate the expected resolution time to clients

*Interim access procedure (dashboard down, API operational):*
- Direct API access via `curl` or any REST client remains fully functional
- Provide clients with the direct API endpoint and refer to `API_DOCUMENTATION.md`
- Example: `curl -X POST https://<api-url>/api/score -H "Content-Type: application/json" -d '{...}'`

**Recovery Verification:**
- Dashboard loads at Vercel URL without JavaScript console errors
- Transaction scoring form submits and returns a result
- Alert and transaction history tables populate from the live database

**Expected Recovery Time:** 15 minutes (RTO-C)

---

### Scenario D — Full Simultaneous Failure (API + Database + Dashboard)

**Definition:** All three platform components are simultaneously unavailable. This most commonly occurs due to a GitHub deployment failure affecting all services, or a correlated regional cloud outage affecting both Render and Supabase.

**Immediate Response Steps (0–10 minutes):**
1. Check `githubstatus.com` — if GitHub is degraded, all deployments are frozen
2. Check AWS us-west-2 (Render origin) status independently at `health.aws.amazon.com`
3. Check AWS ap-northeast-1 (Supabase Tokyo) status independently
4. Issue a client-facing incident notification immediately using Template A (Section 8.1)
5. Do not spend time diagnosing individual components until the platform layer is understood

**Recovery Priority Order:**
```
Priority 1 → Database (Supabase)    — All other services depend on data
Priority 2 → API (Render)           — Core AML screening function  
Priority 3 → Dashboard (Vercel)     — Client interface (non-critical to core function)
```

**Recovery Procedure:**

1. **Stabilise database first.** Confirm Supabase is accessible before attempting API recovery. A functional API against a broken database will produce misleading and difficult-to-diagnose errors.
2. **Deploy API to interim endpoint.** If Render is unavailable for more than 15 minutes, deploy the Flask API to a local machine or alternative cloud endpoint (Railway, Google Cloud Run). Update the `DATABASE_URL` and `DEMO_API_KEY` environment variables. Communicate the new endpoint URL to clients.
3. **Recover Vercel last.** The dashboard is non-critical to core AML screening. Direct API access satisfies all compliance monitoring requirements during dashboard downtime.

**Expected Recovery Time:** 2–4 hours (combined sequential RTO)

**Regulatory obligation:** Full outage exceeding 1 hour must trigger client notification (Template B) and a regulatory considerations review. Client institutions with continuous screening obligations must be supported in implementing manual fallback procedures for the duration of the outage.

---

### Scenario E — Data Breach or Security Incident

**Definition:** Unauthorised access to transaction data, customer records, alert data, or API credentials. Includes credential compromise, API key exposure, SQL injection exploitation, or confirmed data exfiltration.

**Detection Method:**
- Unexpected database read patterns (anomalous SELECT volumes or export operations in Supabase logs)
- Exposed credentials detected in GitHub repository (GitHub secret scanning alerts)
- Unusual API traffic from unknown IP addresses or geographic anomalies
- Client report of receiving data they did not expect
- Supabase activity log showing access from unrecognised sessions or IP addresses

**Immediate Response Steps (0–15 minutes):**

> ⚠️ **STOP ALL WRITES IMMEDIATELY.** Do not allow further transaction scoring until the scope of the breach is understood and contained.

1. **Rotate all credentials immediately (in this order):**
   - Supabase database password: Dashboard → Settings → Database → Reset password
   - Update `DATABASE_URL` in Render environment variables with new password
   - Rotate `DEMO_API_KEY` in Render environment variables
   - Revoke and regenerate any GitHub personal access tokens if exposed

2. **Freeze Supabase access:**
   - Enable Row Level Security (RLS) on all tables if not already enforced
   - If active exfiltration is suspected: pause the Supabase project (Settings → Pause project)

3. **Preserve forensic evidence before pausing:**
   - Download Supabase access logs and query history
   - Export Render application logs
   - Document exact timestamps of anomalous events

4. **Scope the compromise:**
   - Which tables were accessed? (`transactions`, `customers`, `alerts`, `mule_clusters`)
   - Were PII fields exposed? (`full_name`, `customer_id`, `beneficial_owner`)
   - Were sanctions screening results or alert data disclosed?
   - What is the breach time window?

**Regulatory Notification Obligations (India):**

| Authority | Trigger | Deadline | Method |
|---|---|---|---|
| **CERT-In** | Any security incident affecting Indian data subjects | Within **6 hours** of detection | Online portal: `cert-in.org.in` |
| **Client institution CISO** | Any breach affecting data processed for that client | Within **24 hours** | Direct communication |
| **RBI (via client)** | If client is an RBI-regulated entity and client data is affected | Client's own obligation — support with information | Via client institution |
| **FIU-IND** | If transaction records are compromised and STR obligations may be affected | Assess within **24 hours** | Via client institution |

**Recovery Procedure (post-containment):**
1. Restore from the last verified clean backup (confirm backup timestamp pre-dates breach window)
2. Conduct SQL-level audit of all records created after the clean backup
3. Re-run all transactions from the compromise window through the clean engine instance
4. Update all API keys and database credentials before restoring public access
5. Conduct a post-incident review within 5 business days
6. Document full findings, timeline, and remediation in the Version History section below

**Expected Recovery Time:** 4–24 hours depending on breach scope

---

## 4. Recovery Time Objectives (RTO)

RTOs define the maximum acceptable time from failure detection to confirmed service restoration.

| Component | RTO Target | Measurement Point | Basis |
|---|---|---|---|
| **API (Render)** | **30 minutes** | `GET /api/health` returns HTTP 200 | AML screening must resume within 30 min to avoid compliance gap |
| **Database (Supabase)** | **1 hour** | `SELECT COUNT(*) FROM transactions` returns expected count | Data restore and connectivity verification requires structured process |
| **Dashboard (Vercel)** | **15 minutes** | Dashboard loads at Vercel URL | Dashboard is non-critical to AML function; fastest recovery path |
| **Full platform failure** | **4 hours** | All three components confirmed healthy | Sequential recovery: database → API → dashboard |
| **Security incident** | **24 hours** | Clean service confirmed by post-incident review | Scope assessment + credential rotation + restore + audit |

### 4.1 RTO Regulatory Basis

The 30-minute API RTO reflects the following regulatory context: under RBI Master Directions on KYC, regulated entities must apply transaction monitoring continuously and comprehensively. An AML screening outage exceeding 30 minutes without a documented manual fallback may constitute a gap in the client institution's transaction monitoring programme. The 30-minute RTO is therefore calibrated to allow client institutions sufficient time to implement manual screening before a compliance gap becomes material to their regulator.

---

## 5. Recovery Point Objectives (RPO)

RPOs define the maximum acceptable data loss in the event of a failure requiring database restore.

| Component | RPO Target | Recovery Mechanism |
|---|---|---|
| **Transaction records** | **24 hours** | Supabase daily backup; transactions are INSERT-ONLY so no updates are lost |
| **Alert records** | **24 hours** | Alert status changes are low-frequency and regenerable |
| **Customer records** | **24 hours** | Customer risk profiles change infrequently |
| **Rules configuration** | **0 minutes** | `rules_config.json` is version-controlled in GitHub — no data loss possible |
| **Sanctions feeds** | **0 minutes** | All feed JSON files are version-controlled; redownload available on demand |

### 5.1 RPO Rationale and Mitigant

The 24-hour RPO reflects the practical limitation of Supabase's daily backup schedule on the current plan. In a worst-case database failure requiring a full restore, up to 24 hours of transaction scoring records may be lost.

**Operational mitigant:** All transactions processed through the API are logged in real time by the calling client institution's own systems. In a restore scenario, client institutions can resubmit the previous day's transactions through the API to regenerate scoring records. This substantially reduces the practical impact of the 24-hour RPO.

**RPO improvement roadmap:**
- **Short-term:** Enable point-in-time recovery (PITR) on Supabase Pro plan — reduces RPO to 1 hour
- **Medium-term:** Implement write-ahead log (WAL) streaming to AWS S3 in Mumbai region
- **Long-term:** Multi-region active-passive replication post-Mumbai migration

### 5.2 Supabase Daily Backup Confirmation Procedure

1. Log in to `supabase.com` → Select project → Settings → Database → Backups tab
2. Confirm the most recent backup timestamp is within the past 24 hours
3. Confirm backup status shows `Completed` (not `Failed` or `In Progress`)
4. Record the confirmed backup timestamp in the quarterly DR drill log

**Verification frequency:** Weekly manual confirmation. Monthly documented confirmation recorded in drill logs.

---

## 6. Backup Procedures

### 6.1 Daily Supabase Database Export Procedure

Supabase provides automated daily backups. A manual export must additionally be performed before any significant code deployment or schema change.

**Automated backup verification:**
- Navigate to: Supabase Dashboard → Project → Settings → Database → Backups
- Automated backups occur daily (typically at 00:00 UTC)
- Free tier retains 7 days of point-in-time backups

**Manual export via `pg_dump` (required before schema changes or major deployments):**

```bash
# Step 1: Set connection string
export DATABASE_URL="postgresql://postgres:<password>@<host>:<port>/postgres"

# Step 2: Full database dump in custom format (supports selective restore)
pg_dump "$DATABASE_URL" \
  --no-owner \
  --no-acl \
  --format=custom \
  --file="scoresentinel_backup_$(date +%Y%m%d_%H%M%S).dump"

# Step 3: Verify dump integrity (list contents without restoring)
pg_restore --list "scoresentinel_backup_$(date +%Y%m%d)_*.dump" | head -30
```

**Export retention and storage:**
- Retain all exports for a minimum of 90 days
- Store in a secure location — not in the GitHub repository
- Naming convention: `scoresentinel_backup_YYYYMMDD_HHMMSS.dump`

**Tables to confirm in each export:**
```sql
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size('public.'||tablename)) AS size,
    (SELECT COUNT(*) FROM transactions) AS tx_count,
    (SELECT COUNT(*) FROM customers) AS customer_count,
    (SELECT COUNT(*) FROM alerts) AS alert_count
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
```

Expected tables: `transactions`, `customers`, `alerts`, `mule_clusters`

### 6.2 Database Restore Procedure

**Pre-restore checklist:**
- [ ] Confirm the scope of data loss (which tables, which time range)
- [ ] Identify the correct backup to restore (backup timestamp must pre-date the incident)
- [ ] Confirm the restore will not corrupt records outside the affected time range
- [ ] Obtain Plan Owner approval before initiating any restore operation
- [ ] Take a snapshot of the current (damaged) database state before restoring

**Restore from Supabase automated backup:**
1. Supabase Dashboard → Project → Settings → Database → Backups
2. Select the backup from the last confirmed clean state
3. Click `Restore` — note: this replaces the **entire database**
4. After restore: verify row counts match expected pre-incident values
5. Reconnect the API by restarting the Render service

**Restore from manual `pg_dump` export:**

```bash
# Option A: Restore to the existing Supabase project (replaces current data)
pg_restore \
  --no-owner \
  --no-acl \
  --clean \
  --if-exists \
  --dbname="$DATABASE_URL" \
  scoresentinel_backup_<timestamp>.dump

# Option B: Restore to a new Supabase project (safer for validation)
# Create a new project in Supabase, get new DATABASE_URL
pg_restore \
  --no-owner \
  --no-acl \
  --dbname="$NEW_DATABASE_URL" \
  scoresentinel_backup_<timestamp>.dump

# Step 3: Verify restore integrity
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM transactions;"
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM customers;"
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM alerts;"
```

**Post-restore verification checklist:**
- [ ] Row counts match expected values from pre-incident records
- [ ] INSERT-ONLY constraint on `transactions` is enforced (attempt `UPDATE` — must fail with application error)
- [ ] API `POST /api/score` scores a test transaction successfully and writes to the database
- [ ] Alert pipeline writes to `alerts` table correctly
- [ ] Database schema matches `database/schema.sql` (run schema comparison)
- [ ] Sanctions screening returns correct results on a known test case

---

## 7. DR Drill Schedule

### 7.1 Quarterly Drill Overview

| Quarter | Drill Focus | Estimated Duration | Lead |
|---|---|---|---|
| **Q1 (January–March)** | API failover and redeploy simulation | 2 hours | Technical Lead |
| **Q2 (April–June)** | Database backup restore validation | 3 hours | Technical Lead |
| **Q3 (July–September)** | Full platform failure simulation | 4 hours | Plan Owner |
| **Q4 (October–December)** | Security incident response rehearsal | 3 hours | Plan Owner |

### 7.2 Q1 Drill — API Failover and Redeploy

**Objective:** Confirm that the Render API can be detected as failed and recovered to a healthy state within the 30-minute RTO.

**Test steps:**
1. Deliberately disable the Render web service (Dashboard → Settings → Suspend service)
2. Start stopwatch
3. Diagnose failure using Render dashboard, logs, and health check
4. Trigger manual redeploy from GitHub main branch
5. Verify `GET /api/health` returns HTTP 200
6. Stop stopwatch — record total elapsed time

**Pass criteria:** API health check passes within 30 minutes.
**Documentation required:** Record actual elapsed time and any steps that caused delay.

### 7.3 Q2 Drill — Database Backup Restore

**Objective:** Confirm that a Supabase backup can be restored and the API can operate against the restored database within the 1-hour RTO.

**Test steps:**
1. Create a new Supabase project for the drill (do not restore to production)
2. Restore the latest `pg_dump` export to the test project
3. Verify all four tables are present with correct row counts
4. Update `DATABASE_URL` on Render (or local environment) to point to the test database
5. Score three test transactions and confirm they write to the test database
6. Verify the API returns correct scoring results
7. Record elapsed time
8. Restore `DATABASE_URL` to production after drill

**Pass criteria:** Database restored, API operating correctly against restored data, within 1 hour.

### 7.4 Q3 Drill — Full Platform Failure Simulation

**Objective:** Validate the complete sequential recovery playbook for Scenario D.

**Test steps:**
1. Suspend Render service, pause Supabase project, and suspend Vercel deployment simultaneously
2. Start stopwatch
3. Follow Scenario D recovery procedure exactly as documented — do not improvise
4. Record actual elapsed time at each recovery milestone:
   - Database connectivity restored: ___
   - API health check passes: ___
   - Dashboard loads: ___
5. Total elapsed time: ___
6. Compare actual times against documented RTOs

**Pass criteria:** All three components recovered within 4 hours.

### 7.5 Q4 Drill — Security Incident Response Rehearsal

**Objective:** Test the speed and accuracy of credential rotation and incident response procedures.

**Test steps:**
1. Simulate a credential exposure (paper exercise only — do not actually expose credentials)
2. Execute the full credential rotation procedure from Scenario E against a test environment
3. Verify the API continues functioning with the new credentials
4. Verify the old credentials are rejected by the database
5. Practice completing the CERT-In incident notification template (Section 8.3)
6. Review escalation matrix contacts for accuracy and update as needed

**Pass criteria:** All credentials rotated and service restored within 2 hours. CERT-In template completed within 30 minutes of simulated detection.

### 7.6 Drill Documentation Template

Complete and file the following record for each quarterly drill:

```
═══════════════════════════════════════════
   SCORESENTINEL DR DRILL RECORD
═══════════════════════════════════════════
Date:
Quarter:
Drill Type:
Lead Executor:
Observers:

Start Time:
End Time:
Total Duration:

Result: [ ] PASS   [ ] FAIL   [ ] PARTIAL PASS

Milestone Timings:
- Milestone 1 [___]: achieved at ___
- Milestone 2 [___]: achieved at ___
- Milestone 3 [___]: achieved at ___

Backup Verification:
- Latest backup timestamp confirmed: ___
- Backup status: [ ] Completed   [ ] Failed
- Row counts verified: [ ] Yes   [ ] No

Issues Identified:
1. ___
2. ___

Runbook Updates Required:
1. ___

Client Communication Drafted: [ ] Yes   [ ] N/A

Next Drill Scheduled:
Sign-off (Plan Owner):
═══════════════════════════════════════════
```

---

## 8. Client Communication Templates

### 8.1 Template A — Initial Incident Notification

**Subject:** ScoreSentinel Service Disruption — [Date] [Time IST]

```
Dear [Client Compliance Team / CISO],

We are writing to notify you of a service disruption affecting 
ScoreSentinel.

INCIDENT SUMMARY
────────────────
Affected Component: [API / Database / Dashboard / All components]
Detection Time: [HH:MM] IST, [DD Month YYYY]
Current Status: Under investigation and remediation
Estimated Resolution: [HH:MM] IST (within [X] minutes)

IMPACT ON YOUR OPERATIONS
──────────────────────────
[If API unavailable]:
  Transaction screening via the ScoreSentinel API is currently 
  unavailable. Please activate your manual transaction screening 
  procedures and retain a record of all transactions processed 
  manually for resubmission once service is restored.

[If dashboard only]:
  The API scoring endpoint at POST /api/score remains fully 
  operational. Only the web dashboard is affected. Direct API 
  access via any REST client is unaffected.

[If database degraded]:
  Screening results are available but may not be persisted to 
  the database during this window. Please retain your own records.

NEXT UPDATE
───────────
We will provide a status update by [HH:MM] IST.

Regards,
Atul Krishnan, CAMS
ScoreSentinel — Model Owner
```

### 8.2 Template B — Service Restored Notification

**Subject:** ScoreSentinel Service Restored — [Date]

```
Dear [Client Compliance Team / CISO],

ScoreSentinel AML Transaction Scoring Engine has been fully restored.

RESTORATION SUMMARY
────────────────────
Service restored at: [HH:MM] IST, [DD Month YYYY]
Total outage duration: [X hours Y minutes]
Root cause: [One-line description]

DATA IMPACT ASSESSMENT
───────────────────────
[If no data loss]:
  No transaction records were lost during this incident. All 
  scoring data remains intact. No action is required from your team.

[If data loss occurred]:
  Transaction records from [HH:MM] to [HH:MM] on [Date] may not 
  have been captured. Please resubmit transactions processed 
  manually during this window via POST /api/score to ensure 
  audit trail completeness.

PREVENTIVE MEASURES
────────────────────
[Brief description of what was changed or improved]

We apologise for any disruption to your compliance operations 
and remain available should you require any further assistance.

Regards,
Atul Krishnan, CAMS
ScoreSentinel — Model Owner
```

### 8.3 Template C — Security Incident Notification

**Subject:** URGENT — ScoreSentinel Security Incident Notice — [Date]

```
CONFIDENTIAL — PLEASE TREAT AS URGENT

Dear [Chief Compliance Officer / CISO],

We are writing to inform you of a security incident affecting 
ScoreSentinel that may have implications for data processed 
through our platform.

INCIDENT DETAILS
─────────────────
Detection date/time: [HH:MM] IST, [DD Month YYYY]
Nature of incident: [Unauthorised access / Credential exposure / 
                    Data exfiltration — as determined]
Data potentially affected: [Transaction records / Customer records / 
                            Alert data — specify scope]
Time window affected: [From HH:MM on Date to HH:MM on Date]

IMMEDIATE ACTIONS TAKEN BY SCORESENTINEL
──────────────────────────────────────────
- All credentials rotated as of [HH:MM] IST
- Platform access suspended pending full forensic review
- CERT-In notification filed at [HH:MM] IST [if applicable]
- Forensic investigation in progress

ACTION REQUIRED FROM YOUR INSTITUTION
───────────────────────────────────────
As a regulated entity, your institution may have an independent 
obligation to assess whether this incident triggers reporting 
requirements to your regulator (RBI, FIU-IND, SEBI — as applicable).

We will provide a comprehensive incident report within 5 business 
days. Please contact us immediately if you require information to 
fulfil your own regulatory notification obligations.

This communication is confidential. Please do not share outside 
your compliance and information security teams.

Regards,
Atul Krishnan, CAMS
ScoreSentinel — Model Owner
```

---

## 9. Regulatory Considerations

### 9.1 RBI Outsourcing Guidelines — Compliance Status

ScoreSentinel is deployed by regulated entities as a technology tool supporting their AML transaction monitoring obligations. The applicable RBI frameworks include the **Master Direction on Outsourcing of IT Services (2023)** and the **Guidelines on Managing Risks and Code of Conduct in Outsourcing of Financial Services by NBFCs**.

| RBI Requirement | Current Status | Gap / Action Required |
|---|---|---|
| Business continuity plan documented | ✅ This document | Annual review required |
| Disaster recovery capability demonstrated | ⚠️ Drills not yet conducted | Q1 2027 drill — schedule confirmed |
| Data security and access controls | ✅ API key auth; Supabase access controls | Penetration test pending |
| Vendor concentration risk assessment | ⚠️ Three US-based vendors (Render, Supabase, Vercel) | Mumbai migration plan in Section 9.2 |
| Contractual SLA with vendors | ⚠️ Free tier — no formal SLA | Upgrade plan required |
| Audit rights and transparency | ✅ All code open-source in GitHub; all data in client-controlled DB | No gap |
| Exit strategy and data portability | ✅ Full `pg_dump` portability; no vendor lock-in | No gap |
| Client disclosure of outsourcing | ⚠️ Requires formal client agreement | Include in client onboarding |

### 9.2 RBI Data Localisation — Current Gap and Migration Plan

RBI's **Payment System Data Storage Policy (2018)** and **KYC Master Direction (2023)** require that data related to Indian payment transactions be stored within India.

**Current Data Localisation Status:**

| Component | Current Location | Compliant | Planned Location | Target Date |
|---|---|---|---|---|
| API processing (Render) | US-West (Oregon) | ❌ No | AWS Mumbai ap-south-1 | Q2 2027 |
| Database (Supabase) | AWS Tokyo ap-northeast-1 | ❌ No | AWS Mumbai ap-south-1 | Q2 2027 |
| Dashboard (Vercel CDN) | Global edge (static assets only) | ✅ No PII stored | No change required | N/A |
| Sanctions feed files | Git repository (GitHub servers) | ⚠️ Static reference data | GitHub — no change | N/A |

**Migration Plan:**

- **Phase 1 — API Migration (Q1 2027):** Deploy Flask API to AWS Elastic Beanstalk or ECS in `ap-south-1`. Configure GitHub Actions for deployment. Update client API endpoint documentation.
- **Phase 2 — Database Migration (Q2 2027):** Provision Supabase project in `ap-south-1` region when available, or migrate to AWS RDS PostgreSQL in Mumbai. Execute `pg_dump / pg_restore` migration. Validate with full DR drill.
- **Phase 3 — Certification (Q2 2027):** Conduct post-migration DR drill confirming all transaction data is processed and stored within India. Update client disclosures and vendor risk assessments.

**Interim client disclosure requirement:** Until migration is complete, all client institutions must be informed in writing that transaction data is currently processed via US and Tokyo-region infrastructure. This disclosure must appear in any engagement letter, terms of service, or vendor risk questionnaire response.

---

## 10. Escalation Matrix

| Severity Level | Scenario | Response Time | First Contact | Escalation If Unresolved |
|---|---|---|---|---|
| **P1 — Critical** | Full outage / Data breach | Immediate (< 5 min) | Atul Krishnan | Client institution CISO + CERT-In (breach only) |
| **P2 — High** | Single component outage > 30 min | Within 15 minutes | Atul Krishnan | Client compliance team — Template A |
| **P3 — Medium** | Dashboard failure / Degraded performance | Within 1 hour | Atul Krishnan | Client notification if > 2 hours — Template A |
| **P4 — Low** | Cold-start delay / Minor latency spike | Monitor — no immediate action | Internal monitoring | Investigate root cause if pattern repeats 3+ times |

---

## 11. Version History

| Version | Change | Date | Author |
|---|---|---|---|
| 1.0 | Initial DR/BCP: five failure scenarios with detection, response, and recovery procedures; RTO/RPO framework; backup procedures with `pg_dump` scripts; quarterly drill schedule; three client communication templates; RBI outsourcing compliance status; data localisation gap analysis and migration roadmap | September 2026 | Atul Krishnan, CAMS |

---

*ScoreSentinel | DR_BCP.md | Disaster Recovery and Business Continuity Plan | Authored by Atul Krishnan, CAMS | Version 1.0 | September 2026*
