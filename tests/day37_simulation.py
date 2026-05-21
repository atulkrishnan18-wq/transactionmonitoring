import requests
import random
import time
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

COUNTRIES = ["US", "GB", "IN", "AE", "KY", "NG", "PK", "RU", "IR", "CY"]
TX_TYPES = ["Wire Transfer (Domestic)", "Wire Transfer (International)", "Cash Deposit", "P2P", "Online Payment"]
CUST_TYPES = ["Verified Salaried Individual", "Small/Medium Business (SMB)", "Shell Company", "HNWI", "Crypto-Asset Business"]

def generate_random_transaction(idx):
    cust_id = f"SIM-CUST-{random.randint(100, 999)}"
    amount = round(random.uniform(10, 15000), 2)
    
    # Introduce some "suspicious" amounts
    if random.random() < 0.2:
        amount = random.choice([9900, 9950, 4999, 10000])
        
    sender = random.choice(COUNTRIES)
    receiver = random.choice(COUNTRIES)
    
    # Force some sanctions
    if idx % 10 == 0:
        receiver = "Iran"
        
    payload = {
        "customer_id": cust_id,
        "transaction_amount": amount,
        "transaction_currency": "USD",
        "transaction_type": random.choice(TX_TYPES),
        "sender_country": sender,
        "receiver_country": receiver,
        "customer": {
            "customer_type": random.choice(CUST_TYPES),
            "full_name": f"Simulated User {idx}",
            "geo_tier": "Tier 4" if sender in ["US", "GB"] else "Tier 2B"
        },
        "account_id": f"ACC-{random.randint(1000, 9999)}",
        "history": [] # Simplified for load test
    }
    
    # Randomly add history to some to test velocity
    if random.random() < 0.3:
        payload["history"] = [
            {"amount": amount, "date": (datetime.now() - timedelta(hours=i)).isoformat(), "type": "CREDIT"}
            for i in range(random.randint(1, 5))
        ]
        
    return payload

def run_simulation(count=50):
    print(f"🚀 Starting Day 37 Real-time Scoring Simulation: {count} transactions...")
    print("-" * 60)
    
    success = 0
    alerts = 0
    
    for i in range(1, count + 1):
        payload = generate_random_transaction(i)
        try:
            start_time = time.time()
            resp = requests.post(f"{BASE_URL}/api/score", json=payload)
            latency = (time.time() - start_time) * 1000
            
            if resp.status_code == 200:
                data = resp.json()
                success += 1
                is_alert = data.get("alert", False)
                if is_alert:
                    alerts += 1
                
                status_icon = "⚠️" if is_alert else "✅"
                print(f"[{i:02d}] {status_icon} Cust: {payload['customer_id']} | Amt: ${payload['transaction_amount']:>8} | CRS: {str(data.get('crs')):>5} | {latency:.0f}ms")
            else:
                print(f"[{i:02d}] ❌ FAILED - Status {resp.status_code}")
        except Exception as e:
            print(f"[{i:02d}] ❌ ERROR - {str(e)}")
            
        # Small delay to simulate real-time arrival
        time.sleep(0.1)

    print("-" * 60)
    print(f"Simulation Complete!")
    print(f"Total Submitted: {count}")
    print(f"Successful:      {success}")
    print(f"Alerts Triggered: {alerts}")
    
    # Final check of the alert queue
    try:
        q_resp = requests.get(f"{BASE_URL}/api/alerts")
        if q_resp.status_code == 200:
            total_alerts = q_resp.json().get("total", 0)
            print(f"Live Alert Queue Total: {total_alerts}")
    except:
        pass

if __name__ == "__main__":
    run_simulation(50)
