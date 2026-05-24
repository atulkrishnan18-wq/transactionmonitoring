import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"
API_KEY = "SCORESENTINEL_DEMO_2027"

def run_demo():
    print("=== ScoreSentinel Demo Script ===")
    print(f"Connecting to API at {BASE_URL}")
    print("-" * 50)

    demo_transactions = [
        # 1. Clean UK domestic wire
        {
            "name": "Transaction 1: Clean UK Domestic Wire",
            "payload": {
                "customer_id": "CUST-DEMO-004", # John Smith
                "transaction_amount": 2000.00,
                "transaction_currency": "GBP",
                "transaction_type": "Wire Transfer (Domestic)",
                "sender_country": "United Kingdom",
                "receiver_country": "United Kingdom",
                "customer": {
                    "customer_type": "Verified Salaried Individual",
                    "geo_tier": "Tier 4",
                    "match_type": "No PEP / Sanctions / Adverse Media match"
                }
            }
        },
        # 2. Iran sanctions wire
        {
            "name": "Transaction 2: Iran Sanctions Wire",
            "payload": {
                "customer_id": "CUST-DEMO-001", # Rajesh Kumar
                "transaction_amount": 500.00,
                "transaction_currency": "USD",
                "transaction_type": "Wire Transfer (International)",
                "sender_country": "India",
                "receiver_country": "Iran",
                "customer": {
                    "customer_type": "Small/Medium Business (SMB)",
                    "geo_tier": "Tier 4"
                }
            }
        },
        # 3. SAR Generator
        {
            "name": "Transaction 3: SAR Generator (High-Risk Combination)",
            "payload": {
                "customer_id": "CUST-DEMO-002", # Renova Group
                "account_id": "ACC_RENOVA_1",
                "transaction_amount": 9900.00,
                "transaction_currency": "USD",
                "transaction_type": "Wire Transfer (International)",
                "sender_country": "Nigeria",
                "receiver_country": "British Virgin Islands",
                "customer": {
                    "customer_type": "Shell Company"
                },
                "history": [
                    {"amount": 9900, "date": "2026-05-20T10:00:00", "account_id": "ACC_RENOVA_1"},
                    {"amount": 9800, "date": "2026-05-21T10:00:00", "account_id": "ACC_RENOVA_1"}
                ]
            }
        },
        # 4. Mule concentrator cluster
        {
            "name": "Transaction 4: Mule Concentrator Cluster",
            "payload": {
                "customer_id": "CUST-DEMO-005", # FastPay
                "account_id": "MULE_CONC_1",
                "transaction_amount": 150000.00,
                "transaction_currency": "INR",
                "transaction_type": "Mobile / Peer-to-Peer Transfer",
                "sender_country": "India",
                "receiver_country": "India",
                "customer": {
                    "customer_type": "Payment Processor",
                    "device_nexus_count": 8
                },
                "history": [
                    {"sender_id": f"SENDER_{i}", "amount": 15000, "date": (datetime.now()).isoformat(), "type": "CREDIT", "account_id": "MULE_CONC_1"} for i in range(10)
                ]
            }
        },
        # 5. Pakistani trade payment
        {
            "name": "Transaction 5: Pakistani Trade Payment (False Positive)",
            "payload": {
                "customer_id": "CUST-DEMO-003", # Karachi Textiles
                "transaction_amount": 180000.00,
                "transaction_currency": "USD",
                "transaction_type": "Wire Transfer (International)",
                "sender_country": "Pakistan",
                "receiver_country": "United Kingdom",
                "customer": {
                    "customer_type": "Established Business (3+ years)",
                    "geo_tier": "Tier 2B"
                }
            }
        }
    ]

    headers = {
        "X-DEMO-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

    for tx in demo_transactions:
        print(f"\nProcessing {tx['name']}...")
        try:
            response = requests.post(f"{BASE_URL}/api/score", json=tx['payload'], headers=headers, timeout=10)
            if response.status_code == 200:
                result = response.json()
                print(f"  CRS Score: {result.get('crs') if result.get('crs') is not None else 'AUTO-ALERT'}")
                print(f"  Risk Band: {result.get('risk_band')}")
                print(f"  Alert Generated: {'YES 🚨' if result.get('alert') else 'NO ✅'}")
                if result.get('mule_alert'):
                    print(f"  Mule Cluster Score (MCS): {result.get('mcs')} 🕸️")
                print(f"  Rules Fired: {', '.join(result.get('rules_fired', []))}")
                if "trigger" in result:
                    print(f"  Trigger Reason: {result['trigger']}")
            else:
                print(f"  Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  Connection Error: {e}")
        
        time.sleep(1) # Pause for effect

    print("\n" + "=" * 50)
    print("Demo complete. All data has been persisted to Supabase.")

if __name__ == "__main__":
    run_demo()
