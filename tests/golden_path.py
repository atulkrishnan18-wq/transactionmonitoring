import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"
API_KEY = "SCORESENTINEL_DEMO_2027"

def run_golden_path():
    print("🌟 ScoreSentinel 'Golden Path' Automated Demo Script")
    print("-" * 60)
    
    headers = {"X-DEMO-API-KEY": API_KEY}
    
    # 1. Clear Baseline
    print("Action 1: Submitting Clean Salary Earner (Control)...")
    payload_1 = {
        "customer_id": "DEMO-CUST-001",
        "transaction_amount": 2500.00,
        "transaction_currency": "USD",
        "transaction_type": "Domestic Wire",
        "sender_country": "US",
        "receiver_country": "US",
        "customer": {
            "customer_type": "Verified Salaried Individual",
            "full_name": "Demo User (Clean)",
            "geo_tier": "Tier 4"
        }
    }
    r1 = requests.post(f"{BASE_URL}/api/score", json=payload_1, headers=headers)
    print(f"Result: CRS {r1.json().get('crs')} | Alert: {r1.json().get('alert')}")
    
    # 2. Sanctions Auto-Alert
    print("\nAction 2: Submitting Sanctioned Jurisdiction (Iran)...")
    payload_2 = {
        "customer_id": "DEMO-CUST-002",
        "transaction_amount": 500.00,
        "transaction_currency": "USD",
        "transaction_type": "International Wire",
        "sender_country": "IR",
        "receiver_country": "GB",
        "customer": {
            "customer_type": "Individual",
            "full_name": "Demo User (Sanctions Hit)"
        }
    }
    r2 = requests.post(f"{BASE_URL}/api/score", json=payload_2, headers=headers)
    alert_id = r2.json().get('alert_id')
    print(f"Result: AUTO-ALERT TRIGGERED | Alert ID: {alert_id}")
    
    # 3. Resolve using Three-Point Standard
    print("\nAction 3: Resolving Sanctions Alert using Three-Point Standard...")
    resolve_payload = {
        "disposition": "CLEARED",
        "stage": "RESOLVED",
        "reviewer_id": "DEMO-ADMIN",
        "reviewer_rationale": "Confirmed false positive via multi-factor identification.",
        "point_1_identifier": "DOB Mismatch (1985 vs 1960)",
        "point_1_source": "Customer Passport",
        "point_2_identifier": "Nationality Mismatch (Canadian)",
        "point_2_source": "Government ID Database",
        "point_3_identifier": "Profession Mismatch (Teacher)",
        "point_3_source": "Employer Verification"
    }
    requests.put(f"{BASE_URL}/api/alerts/{alert_id}", json=resolve_payload, headers=headers)
    print(f"Result: ALERT RESOLVED & AUDITED.")
    
    # 4. Mule Cluster Detection
    print("\nAction 4: Triggering MuleCatcher (MC-1 Concentrator Network)...")
    payload_3 = {
        "customer_id": "DEMO-CUST-003",
        "account_id": "DEMO-CONC-001",
        "transaction_amount": 95000,
        "transaction_currency": "USD",
        "transaction_type": "Wire",
        "sender_country": "GB",
        "receiver_country": "GB",
        "customer": {"customer_type": "Individual", "device_nexus_count": 8},
        "history": [{"sender_id": f"S_{i}", "amount": 9500, "date": datetime.now().isoformat(), "type": "CREDIT"} for i in range(10)]
    }
    r3 = requests.post(f"{BASE_URL}/api/score", json=payload_3, headers=headers)
    cluster_id = r3.json().get('cluster_id')
    print(f"Result: MULE CLUSTER DETECTED | MCS: {r3.json().get('mcs')} | Cluster ID: {cluster_id}")
    
    print("-" * 60)
    print("🌟 Demo Path Complete. Dashboard is now populated for display.")

if __name__ == "__main__":
    run_golden_path()
