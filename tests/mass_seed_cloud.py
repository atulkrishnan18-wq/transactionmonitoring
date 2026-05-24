import requests
import time
from datetime import datetime, timedelta

# BASE_URL = "http://localhost:5000"
BASE_URL = "https://scoresentinel-api.onrender.com"
API_KEY = "SCORESENTINEL_DEMO_2027"

def seed_cloud():
    print(f"=== ScoreSentinel Mass Seed Script ===")
    print(f"Targeting LIVE API at {BASE_URL}")
    print("This will populate your Supabase DB with 25+ professional scenarios.")
    print("-" * 50)

    # Base Scenarios
    scenarios = [
        {"name": "Scenario 1: Clean Salary Earner", "payload": {"customer_id": "CUST-001", "transaction_amount": 2000, "transaction_type": "Wire Transfer (Domestic)", "sender_country": "United Kingdom", "receiver_country": "United Kingdom", "customer": {"customer_type": "Verified Salaried Individual"}}},
        {"name": "Scenario 2: Shell Company Wire to Cayman", "payload": {"customer_id": "CUST-002", "transaction_amount": 50000, "transaction_type": "Wire Transfer (International)", "sender_country": "United Kingdom", "receiver_country": "Cayman Islands", "customer": {"customer_type": "Shell Company", "geo_tier": "Tier 3"}}},
        {"name": "Scenario 4: Iran Sanctions Auto-Alert", "payload": {"customer_id": "CUST-003", "transaction_amount": 500, "transaction_type": "Wire Transfer (Domestic)", "sender_country": "UK", "receiver_country": "Iran", "customer": {"customer_type": "Small/Medium Business (SMB)"}}},
        {"name": "Scenario 9: SAR Generator Calibration", "payload": {"customer_id": "CUST-002", "transaction_amount": 9900, "transaction_type": "Wire Transfer (International)", "sender_country": "Nigeria", "receiver_country": "British Virgin Islands", "customer": {"customer_type": "Shell Company"}, "history": [{"amount": 9900, "date": "2026-05-20T10:00:00"}, {"amount": 9800, "date": "2026-05-21T10:00:00"}]}},
        {"name": "Scenario 11: Viktor Vekselberg Direct", "payload": {"customer_id": "CUST-004", "transaction_amount": 1000000, "transaction_type": "Wire Transfer (International)", "sender_country": "Russia", "receiver_country": "UK", "customer": {"customer_type": "Shell Company", "match_type": "Confirmed PEP — Tier 1"}}},
        {"name": "Scenario 13: Pakistani Trade FP", "payload": {"customer_id": "CUST-005", "transaction_amount": 180000, "transaction_type": "Wire Transfer (International)", "sender_country": "Pakistan", "receiver_country": "UK", "customer": {"customer_type": "Established Business (3+ years)", "geo_tier": "Tier 2B"}}},
        {"name": "MC-1: Classic Concentrator Network", "payload": {"customer_id": "MULE_CONC_1", "transaction_amount": 95000, "account_id": "CONC_1", "transaction_type": "DEBIT", "customer": {"customer_type": "Individual", "device_nexus_count": 5}, "history": [{"sender_id": f"SENDER_{i}", "amount": 9500, "date": (datetime.now() - timedelta(minutes=i)).isoformat(), "type": "CREDIT"} for i in range(10)]}},
        {"name": "MC-4: UPI Smurfing Ring", "payload": {"customer_id": "UPI_RECV_1", "transaction_amount": 74000, "transaction_type": "DEBIT", "customer": {"customer_type": "Individual", "device_nexus_count": 4}, "history": [{"sender_id": f"VPA_{i}", "amount": 4999, "date": (datetime.now() - timedelta(minutes=i)).isoformat(), "type": "CREDIT"} for i in range(15)]}}
    ]

    headers = {"X-DEMO-API-KEY": API_KEY, "Content-Type": "application/json"}
    
    success_count = 0
    for s in scenarios:
        print(f"Processing: {s['name']}...")
        try:
            # We hit the LIVE API
            resp = requests.post(f"{BASE_URL}/api/score", json=s['payload'], headers=headers, timeout=60)
            if resp.status_code == 200:
                print(f"  ✅ Scored successfully. CRS: {resp.json().get('crs', 'AUTO')}")
                success_count += 1
            else:
                print(f"  ❌ Error: {resp.status_code} - {resp.text[:100]}")
        except Exception as e:
            print(f"  ❌ Connection Failed: {e}")
        time.sleep(0.5)

    print("-" * 50)
    print(f"Seeding Complete! {success_count} scenarios added to Supabase.")
    print(f"Check your dashboard: https://transactionmonitoring.vercel.app")

if __name__ == "__main__":
    seed_cloud()
