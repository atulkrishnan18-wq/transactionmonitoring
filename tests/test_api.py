"""
ScoreSentinel API Integration Tests (Pytest version)
Part of the ScoreSentinel AML Transaction Risk Scoring Engine
Authored by Atul Krishnan, CAMS | Day 28 of 60
"""

import pytest
import requests
import time
import os
import json
from datetime import datetime, timedelta

# Base URL for the API (assumes server is running)
BASE_URL = "http://127.0.0.1:5000"

@pytest.fixture(scope="session", autouse=True)
def wait_for_api():
    """Ensure the API is reachable before running tests."""
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/api/health", timeout=10)
            if response.status_code == 200:
                return
        except requests.exceptions.ConnectionError:
            pass
        print(f"Waiting for API to start (attempt {i+1}/{max_retries})...")
        time.sleep(2)
    pytest.fail("API server not reachable at localhost:5000")

def test_api_health():
    """Verify the health check endpoint."""
    response = requests.get(f"{BASE_URL}/api/health", timeout=10)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_clean_transaction():
    """TEST 1: Clean transaction (expect no alert)"""
    payload = {
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
    response = requests.post(f"{BASE_URL}/api/score", json=payload, timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert data["alert"] == False
    assert 6.0 <= data["crs"] <= 7.0

def test_sanctions_auto_alert():
    """TEST 2: Iran sanctions (expect auto-alert)"""
    payload = {
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
    response = requests.post(f"{BASE_URL}/api/score", json=payload, timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert data["alert"] == True
    assert data["crs"] is None
    assert data["alert_type"] == "Geography Auto-Alert"

def test_sar_generator():
    """TEST 3: SAR Generator (expect no alert but high score)"""
    now = datetime.now()
    payload = {
        "customer_id": "CUST-TEST-003",
        "account_id": "ACC1",
        "transaction_amount": 9900.00,
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
            {"amount": 9900, "date": (now - timedelta(days=1)).isoformat(), "account_id": "ACC1"},
            {"amount": 9800, "date": (now - timedelta(days=2)).isoformat(), "account_id": "ACC1"}
        ]
    }
    response = requests.post(f"{BASE_URL}/api/score", json=payload, timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert data["alert"] == False
    assert abs(data["crs"] - 59.04) < 0.1

def test_get_transactions():
    """TEST 4: GET transactions for CUST-TEST-003"""
    response = requests.get(f"{BASE_URL}/api/transactions?customer_id=CUST-TEST-003", timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert len(data["transactions"]) >= 1
    assert data["transactions"][0]["customer_id"] == "CUST-TEST-003"

def test_update_alert_three_point_fail():
    """TEST 6: Attempt false positive for SCREENING_MATCH WITHOUT three points (must be rejected)"""
    # Use a dummy alert ID for logic testing
    alert_id = "ALT-20260514-9999"
    payload = {
        "disposition": "FALSE_POSITIVE",
        "reviewer_id": "ANA-TEST-001"
    }
    # Note: In a real test, the alert in the DB must be alert_type='SCREENING_MATCH'
    # For this unit test of the logic, we'll assume the mock alert setup.
    response = requests.put(f"{BASE_URL}/api/alerts/{alert_id}", json=payload, timeout=10)
    # The API now checks the alert_type in the DB. To test this thoroughly, 
    # we should use a known screening alert from the seed data.
    
    # Use Viktor Vekselberg alert (CUST-004) if available
    response = requests.get(f"{BASE_URL}/api/alerts", timeout=10)
    alerts = response.json().get("alerts", [])
    screening_alert = next((a for a in alerts if a['alert_type'] == 'SCREENING_MATCH'), None)
    
    if screening_alert:
        res = requests.put(f"{BASE_URL}/api/alerts/{screening_alert['alert_id']}", json=payload, timeout=10)
        assert res.status_code == 400
        assert "Three-point standard required for screening match dispositions" in res.json()["error"]

def test_transaction_risk_rationale_fail():
    """TEST 7: Attempt resolution for TRANSACTION_RISK WITHOUT rationale (must be rejected)"""
    response = requests.get(f"{BASE_URL}/api/alerts", timeout=10)
    alerts = response.json().get("alerts", [])
    behavioral_alert = next((a for a in alerts if a['alert_type'] == 'TRANSACTION_RISK'), None)
    
    if behavioral_alert:
        payload = {
            "disposition": "CLEARED",
            "reviewer_id": "ANA-TEST-001"
            # Rationale is missing
        }
        res = requests.put(f"{BASE_URL}/api/alerts/{behavioral_alert['alert_id']}", json=payload, timeout=10)
        assert res.status_code == 400
        assert "Reviewer rationale mandatory for transaction risk dispositions" in res.json()["error"]
