import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

def test_str_workflow():
    print("🚀 Starting Day 41-45 STR Workflow Test...")
    print("-" * 60)
    
    # Step 1: Submit MC-1 Scenario (Concentrator)
    # This should trigger a mule cluster alert.
    print("Step 1: Submitting MC-1 (Mule Concentrator) transaction...")
    payload = {
        "customer_id": "CUST-MC1-TEST",
        "transaction_amount": 95000,
        "transaction_currency": "USD",
        "transaction_type": "Wire",
        "sender_country": "GB",
        "receiver_country": "GB",
        "customer": {"customer_type": "Individual", "device_nexus_count": 5},
        "history": [
            {"sender_id": f"S_{i}", "amount": 9500, "date": datetime.now().isoformat(), "type": "CREDIT"} 
            for i in range(10)
        ],
        "account_id": "CONC_1_TEST",
        "type": "DEBIT"
    }
    
    resp = requests.post(f"{BASE_URL}/api/score", json=payload, timeout=10)
    if resp.status_code != 200:
        print(f"❌ Transaction submission failed: {resp.text}")
        return
    
    data = resp.json()
    cluster_id = data.get("cluster_id")
    print(f"✅ Transaction processed. Cluster ID: {cluster_id}, MCS: {data.get('mcs')}")
    
    if not cluster_id:
        print("❌ FAILED: No cluster_id returned for MC-1 typology.")
        return

    # Step 2: Verify str_filed defaults to false
    print("\nStep 2: Verifying str_filed defaults to False...")
    c_resp = requests.get(f"{BASE_URL}/api/clusters", timeout=10)
    clusters = c_resp.json().get("clusters", [])
    mc1_cluster = next((c for c in clusters if c['cluster_id'] == cluster_id), None)
    
    if mc1_cluster and mc1_cluster.get('str_filed') is False:
        print(f"✅ Verified: str_filed is False by default.")
    else:
        print(f"❌ FAILED: str_filed is not False or cluster not found. {mc1_cluster}")
        return
    
    # Step 3: Update cluster with STR filing info
    print("\nStep 3: Filing STR (marking str_filed=True with FIU-IND ref)...")
    fiu_ref = f"FIU-IND-2026-{int(time.time())}"
    update_payload = {
        "status": "RESOLVED",
        "reviewer_id": "ATUL-CAMS",
        "reviewer_rationale": "High-velocity coordinated network confirmed. Coordinated pass-through activity observed across 10 accounts.",
        "str_filed": True,
        "str_reference": fiu_ref
    }
    
    u_resp = requests.put(f"{BASE_URL}/api/clusters/{cluster_id}", json=update_payload, timeout=10)
    if u_resp.status_code == 200:
        print(f"✅ Cluster updated. STR Reference: {fiu_ref}")
    else:
        print(f"❌ Cluster update failed: {u_resp.text}")
        return

    # Step 4: Final verification via API
    print("\nStep 4: Verifying final state via API...")
    v_resp = requests.get(f"{BASE_URL}/api/clusters", timeout=10)
    v_clusters = v_resp.json().get("clusters", [])
    updated_cluster = next((c for c in v_clusters if c['cluster_id'] == cluster_id), None)
    
    if updated_cluster and updated_cluster.get('str_filed') is True and updated_cluster.get('str_reference') == fiu_ref:
        print(f"✅ Final Verification SUCCESS: str_filed=True, str_reference={fiu_ref}")
    else:
        print(f"❌ Final Verification FAILED: {updated_cluster}")
    
    print("-" * 60)
    print("Governance Test Logic Verified.")

if __name__ == "__main__":
    test_str_workflow()
