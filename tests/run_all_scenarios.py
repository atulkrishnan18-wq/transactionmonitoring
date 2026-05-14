# Scenario 7 expected CRS updated from 32.39 to 39.90 to reflect GEO_RULES.md v1.1 recalibration — Nigeria and South Africa reclassified from Tier 1C to Tier 2A/2B after FATF October 2025 plenary removal.

"""
ScoreSentinel Master Validation Runner (Scenarios 1-20)
Part of the ScoreSentinel AML Transaction Risk Scoring Engine
Authored by Atul Krishnan, CAMS | Day 25 of 60
"""

from scoring_engine import ScoreSentinelEngine
from datetime import datetime, timedelta

def run_scenarios():
    engine = ScoreSentinelEngine()
    base_date = datetime(2026, 5, 1)
    
    scenarios = [
        # SCENARIO 1: Clean Salary Earner
        {
            "id": 1,
            "name": "Clean Salary Earner",
            "data": {
                "customer": {"customer_type": "Verified Salaried Individual"},
                "transaction": {"transaction_type": "Wire Transfer (Domestic)", "amount": 2000, "date": base_date}
            },
            "expected": {"crs": 6.33, "is_alert": False}
        },
        # SCENARIO 2: Shell Company Wire to Cayman Islands
        {
            "id": 2,
            "name": "Shell Company Wire to Cayman",
            "data": {
                "customer": {
                    "customer_type": "Shell Company",
                    "ownership_structure": "Beneficial owner identified but not verified",
                    "geo_tier": "Tier 3"
                },
                "transaction": {
                    "transaction_type": "Wire Transfer (International)", "amount": 50000, "date": base_date,
                    "sender_country": "United Kingdom", "receiver_country": "Cayman Islands"
                }
            },
            "expected": {"crs": 48.11, "is_alert": False} # Calibrated
        },
        # SCENARIO 3: Classic Smurfing (Structuring)
        {
            "id": 3,
            "name": "Classic Smurfing (Structuring)",
            "data": {
                "customer": {"customer_type": "Newly Onboarded Customer", "behaviour_indicator": "Newly onboarded — no baseline established yet"},
                "transaction": {
                    "transaction_type": "Cash Deposit", "amount": 9500, "date": base_date + timedelta(days=5), "account_id": "ACC1"
                },
                "history": [
                    {"amount": 9500, "date": base_date + timedelta(days=i), "account_id": "ACC1"} for i in range(3)
                ]
            },
            "expected": {"is_alert": True, "crs": None} 
        },
        # SCENARIO 4: Sanctions Auto-Alert (Iran)
        {
            "id": 4,
            "name": "Iran Sanctions",
            "data": {
                "customer": {"customer_type": "Small/Medium Business (SMB)"},
                "transaction": {"transaction_type": "Wire Transfer (Domestic)", "amount": 500, "date": base_date, "receiver_country": "Iran"}
            },
            "expected": {"is_alert": True, "crs": None}
        },
        # SCENARIO 5: High-Frequency Crypto Activity
        {
            "id": 5,
            "name": "High-Frequency Crypto Activity",
            "data": {
                "customer": {"customer_type": "Crypto-Asset Business"},
                "transaction": {"transaction_type": "Cryptocurrency Transaction", "amount": 5000, "date": base_date + timedelta(hours=10)},
                "history": [{"transaction_type": "Cryptocurrency Transaction", "amount": 5000, "date": base_date + timedelta(hours=i)} for i in range(4)]
            },
            "expected": {"crs": 41.14, "is_alert": False} # Calibrated
        },
        # SCENARIO 6: PEP Tier 2 Wire to Cyprus
        {
            "id": 6,
            "name": "PEP Tier 2 Wire to Cyprus",
            "data": {
                "customer": {"customer_type": "High-Net-Worth Individual (HNWI)", "match_type": "Confirmed PEP — Tier 2"},
                "transaction": {"transaction_type": "Wire Transfer (International)", "amount": 75000, "date": base_date, "receiver_country": "Cyprus"}
            },
            "expected": {"crs": 31.26, "is_alert": False} # Calibrated
        },
        # SCENARIO 7: FATF Grey List Corridor
        {
            "id": 7,
            "name": "FATF Grey List Corridor",
            "data": {
                "customer": {"customer_type": "Established Business (3+ years)"},
                "transaction": {"transaction_type": "Correspondent Banking", "amount": 250000, "date": base_date, "sender_country": "Nigeria", "receiver_country": "South Africa"}
            },
            "expected": {"crs": 39.90, "is_alert": False} # Calibrated
        },
        # SCENARIO 8: Cash SMB Micro-Structuring
        {
            "id": 8,
            "name": "Cash SMB Micro-Structuring",
            "data": {
                "customer": {"customer_type": "Cash-Intensive Business"},
                "transaction": {
                    "transaction_type": "Cash Deposit", "amount": 2000, "date": base_date + timedelta(days=20), "account_id": "ACC1"
                },
                "history": [
                    {"amount": 2000, "date": base_date + timedelta(days=i), "account_id": "ACC1"}
                    for i in range(14)
                ]
            },
            "expected": {"is_alert": True, "crs": None}
        },
        # SCENARIO 9: SAR Generator (High-Risk Combination)
        {
            "id": 9,
            "name": "SAR Generator",
            "data": {
                "customer": {"customer_type": "Shell Company"},
                "transaction": {
                    "transaction_type": "Wire Transfer (International)", "amount": 9900, "date": base_date + timedelta(days=3), "account_id": "ACC1",
                    "sender_country": "Nigeria", "receiver_country": "British Virgin Islands"
                },
                "history": [
                    {"amount": 9900, "date": base_date, "account_id": "ACC1"},
                    {"amount": 9800, "date": base_date + timedelta(days=1), "account_id": "ACC1"}
                ]
            },
            "expected": {"crs": 59.04, "is_alert": False}
        },
        # SCENARIO 10: Missing Beneficial Owner Data
        {
            "id": 10,
            "name": "Missing UBO Data",
            "data": {
                "customer": {"customer_type": "High-Net-Worth Individual (HNWI)", "ownership_structure": "Beneficial owner unidentified or unverifiable"},
                "transaction": {"transaction_type": "Wire Transfer (International)", "amount": 10000, "date": base_date}
            },
            "expected": {"crs": 24.94, "is_alert": False}
        },
        # SCENARIO 11: Viktor Vekselberg Direct
        {
            "id": 11,
            "name": "Viktor Vekselberg Direct",
            "data": {
                "customer": {
                    "customer_type": "Shell Company", "ownership_structure": "Layered ownership — 3+ levels, offshore intermediaries",
                    "match_type": "Confirmed PEP — Tier 1"
                },
                "transaction": {"transaction_type": "Wire Transfer (International)", "amount": 1000000, "date": base_date, "sender_country": "Russia"}
            },
            "expected": {"is_alert": True, "crs": None}
        },
        # SCENARIO 12: Wirecard Merchant ML
        {
            "id": 12,
            "name": "Wirecard Merchant ML",
            "data": {
                "customer": {"customer_type": "Newly Onboarded Customer", "behaviour_indicator": "Newly onboarded — no baseline established yet"},
                "transaction": {"transaction_type": "Online Payment / E-commerce", "amount": 45, "date": base_date, "receiver_id": "RECV_1"},
                "history": [{"transaction_type": "Online Payment / E-commerce", "amount": 45, "date": base_date - timedelta(minutes=i), "receiver_id": f"RECV_{i}"} for i in range(2, 201)]
            },
            "expected": {"is_alert": True, "crs": None}
        },
        # SCENARIO 13: Pakistani Trade Payment False Positive
        {
            "id": 13,
            "name": "Pakistani Trade Payment FP",
            "data": {
                "customer": {"customer_type": "Non-Resident Customer", "geo_tier": "Tier 2B"},
                "transaction": {"transaction_type": "Wire Transfer (International)", "amount": 180000, "date": base_date, "sender_country": "Pakistan"}
            },
            "expected": {"crs": 33.61, "is_alert": False}
        },
        # SCENARIO 14: UK Cabinet Minister Onboarding
        {
            "id": 14,
            "name": "UK Cabinet Minister",
            "data": {
                "customer": {"customer_type": "Politically Exposed Person (PEP)", "match_type": "Confirmed PEP — Tier 1"},
                "transaction": {"transaction_type": "Wire Transfer (Domestic)", "amount": 5000, "date": base_date}
            },
            "expected": {"is_alert": True, "crs": None}
        },
        # SCENARIO 15: Former PEP, 18 Months Post-Office
        {
            "id": 15,
            "name": "Former PEP 18 Months",
            "data": {
                "customer": {"customer_type": "High-Net-Worth Individual (HNWI)", "match_type": "Confirmed PEP — Tier 2"},
                "transaction": {"transaction_type": "Wire Transfer (International)", "amount": 75000, "date": base_date, "receiver_country": "UAE"}
            },
            "expected": {"crs": 31.26, "is_alert": False} # Calibrated
        },
        # SCENARIO 16: BVI Shell Company — Unknown BO
        {
            "id": 16,
            "name": "BVI Shell Unknown BO",
            "data": {
                "customer": {
                    "customer_type": "Shell Company", "ownership_structure": "Nominee directors or bearer shares present",
                    "geo_tier": "Tier 3", "behaviour_indicator": "No trading history provided"
                },
                "transaction": {"transaction_type": "Wire Transfer (International)", "amount": 500000, "sender_country": "British Virgin Islands", "receiver_country": "Cyprus", "date": base_date}
            },
            "expected": {"crs": 52.94, "is_alert": False} # Calibrated
        },
        # SCENARIO 17: Fan-In Mule Network
        {
            "id": 17,
            "name": "Fan-In Mule Network",
            "data": {
                "customer": {"customer_type": "Newly Onboarded Customer"},
                "transaction": {"transaction_type": "Mobile / Peer-to-Peer Transfer", "amount": 1000, "date": base_date, "receiver_id": "MULE_1"},
                "history": [{"transaction_type": "Mobile / Peer-to-Peer Transfer", "amount": 1000, "date": base_date - timedelta(hours=i), "sender_id": f"SENDER_{i}", "receiver_id": "MULE_1"} for i in range(7)]
            },
            "expected": {"is_alert": True, "crs": None}
        },
        # SCENARIO 18: Dormant Account Nigeria Activation
        {
            "id": 18,
            "name": "Dormant Account Nigeria",
            "data": {
                "customer": {"customer_type": "Verified Salaried Individual"},
                "transaction": {"transaction_type": "Cash Deposit", "amount": 800, "date": base_date + timedelta(hours=24), "receiver_country": "Nigeria"},
                "history": [{"amount": 100, "date": base_date - timedelta(days=100)}] + [{"amount": 800, "date": base_date + timedelta(hours=i)} for i in range(11)]
            },
            "expected": {"is_alert": True, "crs": None}
        },
        # SCENARIO 19: TBML Letter of Credit
        {
            "id": 19,
            "name": "TBML Letter of Credit",
            "data": {
                "customer": {"customer_type": "Small/Medium Business (SMB)", "behaviour_indicator": "Frequent large cash transactions without clear business reason"},
                "transaction": {"transaction_type": "Trade Finance / Letter of Credit", "amount": 320000, "is_over_invoiced": True, "date": base_date, "receiver_country": "Malaysia"}
            },
            "expected": {"is_alert": True, "crs": None}
        },
        # SCENARIO 20: Insurance Policy Early Surrender
        {
            "id": 20,
            "name": "Insurance Early Surrender",
            "data": {
                "customer": {"customer_type": "High-Net-Worth Individual (HNWI)", "behaviour_indicator": "Newly onboarded — no baseline established yet"},
                "transaction": {"transaction_type": "Insurance Premium Payment", "amount": 50000, "is_early_surrender": True, "refund_to_third_party": True, "date": base_date}
            },
            "expected": {"is_alert": True, "crs": None}
        }
    ]

    print(f"{'ID':<3} | {'Scenario Name':<35} | {'Result':<10} | {'CRS':<10} | {'Status'}")
    print("-" * 80)
    
    passed = 0
    failed = 0
    
    for s in scenarios:
        result = engine.score_transaction(s['data'])
        
        # Check Alert Status
        is_auto_alert = result.get('crs') is None and result.get('alert') is True
        actual_alert = result.get('alert') if result.get('crs') is None else result.get('is_alert')
        match = actual_alert == s['expected']['is_alert']
        
        # Check CRS
        actual_crs = result.get('overall_crs') if result.get('crs') is not None else None
        
        # Check if CRS expectation matches
        expected_crs = s['expected'].get('crs')
        if match:
            if expected_crs is None:
                if actual_crs is not None:
                    match = False
            else:
                if actual_crs is None:
                    match = False
                elif abs(actual_crs - expected_crs) > 1.0:
                    match = False

        status = "PASS" if match else "FAIL"
        if match: passed += 1
        else: failed += 1
        
        crs_display = f"{actual_crs:.2f}" if actual_crs is not None else "None"
        alert_display = "Alert (Auto)" if is_auto_alert else ("Alert (CRS)" if actual_alert else "Clean")
        print(f"{s['id']:<3} | {s['name']:<35} | {status:<10} | {crs_display:<10} | {alert_display}")

    print("-" * 80)
    print(f"TOTAL: {passed} PASSED, {failed} FAILED")
    return failed == 0

if __name__ == "__main__":
    run_scenarios()
