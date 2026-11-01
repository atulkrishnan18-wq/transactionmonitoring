# TROUBLESHOOT.md — Common Issues Guide

## Issue 1 — Flask will not start
Error: Address already in use port 5000
Fix: 
  Windows: netstat -ano | findstr :5000
  Then: taskkill /PID [pid] /F
  Then restart: python api/app.py

## Issue 2 — Database connection fails
Error: psycopg2.OperationalError
Fix:
  Check PostgreSQL is running
  Check .env file has correct DATABASE_URL
  Format: DATABASE_URL=CHANGE_ME

## Issue 3 — React cannot connect to API
Error: Network Error / CORS error
Fix:
  Confirm Flask is running on port 5000
  Confirm CORS is enabled in api/app.py
  Check dashboard/.env has:
  REACT_APP_API_URL=http://localhost:5000

## Issue 4 — Mule cluster not detecting
Symptom: MCS always 0
Fix:
  Check transaction history is being
  passed to the mule module
  Timestamps must be within last 24 hours
  Use datetime.now() not static dates

## Issue 5 — Scenario 9 alerting incorrectly
Symptom: SAR Generator CRS > 60
Fix:
  Run: python tests/run_all_scenarios.py
  If Scenario 9 fails, a recent code
  change has broken calibration
  Check scoring_engine.py weights

## Issue 6 — Sanctions match failing
Symptom: Known terrorist name not flagging
Fix:
  Confirm JSON files exist in engine/data/
  Run: python engine/sanctions_screening.py
  Check all 10 unit tests pass
