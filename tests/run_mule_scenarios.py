"""
ScoreSentinel Mule Cluster Validation Runner (Scenarios MC-1 to MC-5)
Part of the ScoreSentinel AML Transaction Risk Scoring Engine
Authored by Atul Krishnan, CAMS | Day 30 of 60
"""

from scoring_engine import ScoreSentinelEngine
from datetime import datetime, timedelta

def run_mule_scenarios():
    engine = ScoreSentinelEngine()
    now = datetime.now()
    
    scenarios = [
        # MC-1: Classic Concentrator (expected MCS 95)
        # 10 senders, coordinated 30-min, identical amounts, <30min pass-through
        {
            "id": "MC-1",
            "name": "Classic Concentrator Network",
            "data": {
                "customer": {"customer_type": "Individual", "device_nexus_count": 5},
                "transaction": {"amount": 95000, "account_id": "CONC_1", "type": "DEBIT", "date": now},
                "history": [
                    {"sender_id": f"SENDER_{i}", "amount": 9500, "date": now - timedelta(minutes=(i+1)), "type": "CREDIT"} for i in range(10)
                ]
            },
            "expected": {"mcs_min": 90, "alert": True}
        },
        # MC-2: Salary Mule Network (expected MCS 65)
        # 9 senders, 24h window, similar amounts, 24h pass-through
        {
            "id": "MC-2",
            "name": "Salary Mule Network",
            "data": {
                "customer": {"customer_type": "Individual", "device_nexus_count": 1},
                "transaction": {"amount": 135000, "account_id": "CONC_2", "type": "DEBIT", "date": now},
                "history": [
                    {"sender_id": f"MULE_{i}", "amount": 15000, "date": now - timedelta(minutes=i*10 + 1), "type": "CREDIT"} for i in range(9)
                ]
            },
            "expected": {"mcs_min": 60, "mcs_max": 90, "alert": True}
        },
        # MC-3: Dormant Activation (expected MCS 73)
        # 6 senders, dormant, coordinated 48h, 2h pass-through
        {
            "id": "MC-3",
            "name": "Dormant Activation Attack",
            "data": {
                "customer": {"customer_type": "Individual", "behaviour_indicator": "Dormant for 6 months"},
                "transaction": {"amount": 60000, "account_id": "CONC_3", "type": "DEBIT", "date": now},
                "history": [
                    {"sender_id": f"MULE_{i}", "amount": 10000, "date": now - timedelta(minutes=i*5 + 1), "type": "CREDIT"} for i in range(6)
                ]
            },
            "expected": {"mcs_min": 70, "alert": True}
        },
        # MC-4: UPI Smurfing Ring (expected MCS 95)
        # 15 senders, <1h, identical ₹4,999, immediate out
        {
            "id": "MC-4",
            "name": "UPI Smurfing Ring",
            "data": {
                "customer": {"customer_type": "Individual", "device_nexus_count": 4},
                "transaction": {"amount": 74000, "account_id": "UPI_RECV_1", "type": "DEBIT", "date": now},
                "history": [
                    {"sender_id": f"VPA_{i}", "amount": 4999, "date": now - timedelta(minutes=(i+1)), "type": "CREDIT"} for i in range(15)
                ]
            },
            "expected": {"mcs_min": 90, "alert": True}
        },
        # MC-5: Legitimate Chit Fund (expected MCS 30)
        # 20 senders, monthly, no burst, no pass-through
        {
            "id": "MC-5",
            "name": "Legitimate Chit Fund",
            "data": {
                "customer": {"customer_type": "Registered Business", "full_name": "Registered Chit Fund Co"},
                "transaction": {"amount": 5000, "account_id": "CHIT_1", "type": "CREDIT", "date": now},
                "history": [
                    {"sender_id": f"MEMBER_{i}", "amount": 5000, "date": now - timedelta(days=30, hours=i), "type": "CREDIT"} for i in range(20)
                ]
            },
            "expected": {"mcs_max": 35, "alert": False}
        }
    ]

    print(f"{'ID':<5} | {'Scenario Name':<35} | {'Result':<10} | {'MCS':<10} | {'Alert'}")
    print("-" * 80)
    
    passed = 0
    failed = 0
    
    for s in scenarios:
        # Prepare dates for structuring module
        if isinstance(s['data']['transaction']['date'], datetime):
            s['data']['transaction']['date'] = s['data']['transaction']['date'].isoformat()
        for h in s['data']['history']:
            if isinstance(h['date'], datetime):
                h['date'] = h['date'].isoformat()

        result = engine.score_transaction(s['data'])
        
        mcs = result.get("mcs", 0)
        mule_alert = result.get("mule_alert", False)
        
        match = True
        if "mcs_min" in s['expected'] and mcs < s['expected']['mcs_min']: match = False
        if "mcs_max" in s['expected'] and mcs > s['expected']['mcs_max']: match = False
        if mule_alert != s['expected']['alert']: match = False

        status = "PASS" if match else "FAIL"
        if match: passed += 1
        else: failed += 1
        
        print(f"{s['id']:<5} | {s['name']:<35} | {status:<10} | {mcs:<10.2f} | {mule_alert}")

    print("-" * 80)
    print(f"TOTAL: {passed} PASSED, {failed} FAILED")
    return failed == 0

if __name__ == "__main__":
    run_mule_scenarios()
