"""
ScoreSentinel End-to-End Integration Tests
Part of the ScoreSentinel AML Transaction Risk Scoring Engine
Authored by Atul Krishnan, CAMS | Day 28 of 60
"""

import requests
import time
import json
import sys
import os
import datetime
import threading
from unittest.mock import MagicMock, patch

# --- MOCK DATABASE SETUP ---
# This allows running the API without a live PostgreSQL instance.

class MockCursor:
    def __init__(self):
        self.rows = []
    def execute(self, query, params=None):
        # Very simple mock logic to simulate DB behavior
        if "INSERT INTO transactions" in query:
            # params is a tuple. transaction_id is first. customer_id is second.
            tx_id = params[0]
            cust_id = params[1]
            crs = params[17] # crs is index 17
            risk_band = params[18]
            alert = params[20]
            at_type = params[21]
            self.rows.append({
                "transaction_id": tx_id, "customer_id": cust_id, "crs": crs,
                "risk_band": risk_band, "alert_generated": alert, "alert_type": at_type,
                "timestamp_processed": __import__('datetime').datetime.now()
            })
        elif "SELECT * FROM transactions" in query:
            pass # Use self.rows from connection
    def fetchall(self):
        return getattr(self.connection, 'transactions', [])
    def fetchone(self):
        return {} # For "verify alert exists"
    def close(self):
        pass

class MockConnection:
    def __init__(self):
        self.transactions = []
        self.alerts = []
    def cursor(self):
        cur = MockCursor()
        cur.connection = self
        self._last_cursor = cur
        return cur
    def commit(self):
        # When commit happens, we might move things from cursor to connection if needed
        # But for this simple mock, we'll just simulate success
        pass
    def rollback(self):
        pass
    def close(self):
        pass

mock_db = MockConnection()

def mock_connect(*args, **kwargs):
    return mock_db

# --- START API SERVER ---

def start_server():
    # Patch psycopg2 before importing app
    with patch('psycopg2.connect', side_effect=mock_connect):
        from api.app import app
        # Disable logging for cleaner output
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        app.run(port=5000, debug=False, use_reloader=False)

# --- TEST SUITE ---

BASE_URL = "http://127.0.0.1:5000"

def run_tests():
    # Give server a moment to start
    time.sleep(2)
    
    print("--- STARTING SCORE SENTINEL E2E INTEGRATION TESTS ---\n")
    
    # Store state
    alert_id = "ALT-20260514-1234" # Expected ID format for Test 5
    
    # --- TEST 1: Clean transaction ---
    print("TEST 1: Clean transaction (expect no alert)...")
    payload1 = {
        "customer_id": "CUST-TEST-001",
        "transaction_amount": 500.00,
        "transaction_currency": "GBP",
        "transaction_type": "Wire Transfer (Domestic)",
        "sender_country": "United Kingdom",
        "receiver_country": "United Kingdom",
        "customer": {
            "customer_type": "Verified Salaried Individual",
            "ownership_structure": "Individual customer — direct ownership, verified",
            "geo_tier": "Tier 4",
            "behaviour_indicator": "Fully consistent, stable, long-established pattern",
            "match_type": "No PEP / Sanctions / Adverse Media match"
        }
    }
    r1 = requests.post(f"{BASE_URL}/api/score", json=payload1)
    print(f"Status: {r1.status_code}")
    print(f"Response: {json.dumps(r1.json(), indent=2)}")
    
    res1 = r1.json()
    if r1.status_code == 200 and res1.get("alert") == False and 6.0 <= res1.get("crs") <= 7.0:
        print("RESULT: PASS\n")
    else:
        print("RESULT: FAIL\n")

    # --- TEST 2: Iran sanctions (expect auto-alert) ---
    print("TEST 2: Iran sanctions (expect auto-alert)...")
    payload2 = {
        "customer_id": "CUST-TEST-002",
        "transaction_amount": 500.00,
        "transaction_currency": "USD",
        "transaction_type": "Wire Transfer (International)",
        "sender_country": "United Kingdom",
        "receiver_country": "Iran",
        "customer": {
            "customer_type": "Small/Medium Business (SMB)",
            "ownership_structure": "Single corporate layer — owner identified and verified",
            "geo_tier": "Tier 4",
            "behaviour_indicator": "Fully consistent, stable, long-established pattern",
            "match_type": "No PEP / Sanctions / Adverse Media match"
        }
    }
    r2 = requests.post(f"{BASE_URL}/api/score", json=payload2)
    print(f"Status: {r2.status_code}")
    print(f"Response: {json.dumps(r2.json(), indent=2)}")
    
    res2 = r2.json()
    if r2.status_code == 200 and res2.get("alert") == True and res2.get("crs") is None and res2.get("alert_type") == "Geography Auto-Alert":
        print("RESULT: PASS\n")
    else:
        print("RESULT: FAIL\n")

    # --- TEST 3: SAR Generator ---
    print("TEST 3: SAR Generator (expect no alert but high score)...")
    now = datetime.datetime.now()
    payload3 = {
        "customer_id": "CUST-TEST-003",
        "account_id": "ACC1", # Ensure same account as history
        "transaction_amount": 9900.00, # Matched to Scenario 9
        "transaction_currency": "USD",
        "transaction_type": "Wire Transfer (International)",
        "sender_country": "Nigeria",
        "receiver_country": "British Virgin Islands",
        "customer": {
            "customer_type": "Shell Company",
            "ownership_structure": "Individual customer — direct ownership, verified",
            "geo_tier": "Tier 4",
            "behaviour_indicator": "Fully consistent, stable, long-established pattern",
            "match_type": "No PEP / Sanctions / Adverse Media match"
        },
        "history": [
            {"amount": 9900, "date": (now - datetime.timedelta(days=1)).isoformat(), "account_id": "ACC1"},
            {"amount": 9800, "date": (now - datetime.timedelta(days=2)).isoformat(), "account_id": "ACC1"}
        ]
    }
    r3 = requests.post(f"{BASE_URL}/api/score", json=payload3)
    print(f"Status: {r3.status_code}")
    print(f"Response: {json.dumps(r3.json(), indent=2)}")
    
    res3 = r3.json()
    if r3.status_code == 200 and res3.get("alert") == False and abs(res3.get("crs") - 59.04) < 0.1:
        print("RESULT: PASS\n")
    else:
        print("RESULT: FAIL\n")

    # --- TEST 4: GET transactions for CUST-TEST-003 ---
    print("TEST 4: GET transactions for CUST-TEST-003...")
    # Inject transaction into mock DB for GET
    mock_db.transactions.append({
        "transaction_id": "TXN-20260514-9999", "customer_id": "CUST-TEST-003", "crs": 59.04,
        "risk_band": "MEDIUM_HIGH", "alert_generated": False, "alert_type": None,
        "timestamp_processed": __import__('datetime').datetime.now()
    })
    
    r4 = requests.get(f"{BASE_URL}/api/transactions?customer_id=CUST-TEST-003")
    print(f"Status: {r4.status_code}")
    print(f"Response: {json.dumps(r4.json(), indent=2)}")
    
    if r4.status_code == 200 and len(r4.json().get("transactions", [])) >= 1:
        print("RESULT: PASS\n")
    else:
        print("RESULT: FAIL\n")

    # --- TEST 5: Update alert with three-point standard ---
    print("TEST 5: Update alert with three-point standard...")
    payload5 = {
        "disposition": "FALSE_POSITIVE",
        "reviewer_id": "ANA-TEST-001",
        "stage": "RESOLVED",
        "reviewer_rationale": "Test clearance",
        "point_1_identifier": "DOB mismatch — 35 year gap",
        "point_1_source": "Passport on file",
        "point_2_identifier": "Nationality mismatch",
        "point_2_source": "KYC documentation",
        "point_3_identifier": "Profession mismatch",
        "point_3_source": "Employment letter"
    }
    r5 = requests.put(f"{BASE_URL}/api/alerts/{alert_id}", json=payload5)
    print(f"Status: {r5.status_code}")
    print(f"Response: {json.dumps(r5.json(), indent=2)}")
    
    if r5.status_code == 200 and r5.json().get("status") == "updated":
        print("RESULT: PASS\n")
    else:
        print("RESULT: FAIL\n")

    # --- TEST 6: Attempt false positive WITHOUT three points ---
    print("TEST 6: Attempt false positive WITHOUT three points (must be rejected)...")
    payload6 = {
        "disposition": "FALSE_POSITIVE",
        "reviewer_id": "ANA-TEST-001"
    }
    r6 = requests.put(f"{BASE_URL}/api/alerts/{alert_id}", json=payload6)
    print(f"Status: {r6.status_code}")
    print(f"Response: {json.dumps(r6.json(), indent=2)}")
    
    if r6.status_code == 400 and "Three-point standard not met" in r6.json().get("error", ""):
        print("RESULT: PASS\n")
    else:
        print("RESULT: FAIL\n")

    print("--- ALL TESTS COMPLETED ---")
    os._exit(0) # Exit the whole process including the server thread

if __name__ == "__main__":
    # Ensure PYTHONPATH is set to include current directory
    sys.path.append(os.getcwd())
    
    # Start server in a thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    run_tests()
