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
            response = requests.get(f"{BASE_URL}/api/health")
            if response.status_code == 200:
                return
        except requests.exceptions.ConnectionError:
            pass
        print(f"Waiting for API to start (attempt {i+1}/{max_retries})...")
        time.sleep(2)
    pytest.fail("API server not reachable at localhost:5000")

def test_api_health():
    """Verify the health check endpoint."""
    response = requests.get(f"{BASE_URL}/api/health")
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
    response = requests.post(f"{BASE_URL}/api/score", json=payload)
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
    response = requests.post(f"{BASE_URL}/api/score", json=payload)
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
    response = requests.post(f"{BASE_URL}/api/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["alert"] == False
    assert abs(data["crs"] - 59.04) < 0.1

def test_get_transactions():
    """TEST 4: GET transactions for CUST-TEST-003"""
    response = requests.get(f"{BASE_URL}/api/transactions?customer_id=CUST-TEST-003")
    assert response.status_code == 200
    data = response.json()
    assert len(data["transactions"]) >= 1
    assert data["transactions"][0]["customer_id"] == "CUST-TEST-003"

def test_update_alert_three_point_fail():
    """TEST 6: Attempt false positive WITHOUT three points (must be rejected)"""
    # Use a dummy alert ID since we just want to test validation logic
    alert_id = "ALT-20260514-9999"
    payload = {
        "disposition": "FALSE_POSITIVE",
        "reviewer_id": "ANA-TEST-001"
    }
    response = requests.put(f"{BASE_URL}/api/alerts/{alert_id}", json=payload)
    assert response.status_code == 400
    assert "Three-point standard not met" in response.json()["error"]
