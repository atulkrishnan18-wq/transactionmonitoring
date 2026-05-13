"""
Day 22 Validation Tests — Structuring & Geography
Part of the ScoreSentinel AML Transaction Risk Scoring Engine
Authored by Atul Krishnan, CAMS | Day 22 of 60
"""

from scoring_engine import ScoreSentinelEngine
from datetime import datetime, timedelta

def run_day22_tests():
    engine = ScoreSentinelEngine()
    base_date = datetime(2026, 5, 1)

    print("--- RUNNING DAY 22 VALIDATION TESTS ---")

    # Scenario 1: Classic Smurfing
    # 3 transactions between $8,000–$9,999 within 7 days
    s1_data = {
        "customer": {"customer_type": "Verified Salaried Individual", "geo_tier": "Tier 4"},
        "transaction": {"amount": 9200, "date": base_date + timedelta(days=4), "account_id": "ACC1", "sender_country": "United Kingdom", "receiver_country": "United States"},
        "history": [
            {"amount": 9500, "date": base_date, "account_id": "ACC1"},
            {"amount": 9800, "date": base_date + timedelta(days=2), "account_id": "ACC1"}
        ]
    }
    r1 = engine.score_transaction(s1_data)
    # Rule 1 (15) + Rule 3 (10) should trigger
    print(f"Scenario 1 (Classic Smurfing) - CRS: {r1['overall_crs']}, Structuring Raw: {r1['module_scores']['structuring']['raw']}")
    assert r1['module_scores']['structuring']['raw'] == 25

    # Scenario 2: Velocity Structuring
    # 5+ transactions within 72 hours
    s2_data = {
        "customer": {"customer_type": "Verified Salaried Individual", "geo_tier": "Tier 4"},
        "transaction": {"amount": 1000, "date": base_date + timedelta(hours=60), "account_id": "ACC1", "sender_country": "United Kingdom", "receiver_country": "United States"},
        "history": [
            {"amount": 1000, "date": base_date, "account_id": "ACC1"},
            {"amount": 1000, "date": base_date + timedelta(hours=12), "account_id": "ACC1"},
            {"amount": 1000, "date": base_date + timedelta(hours=24), "account_id": "ACC1"},
            {"amount": 1000, "date": base_date + timedelta(hours=36), "account_id": "ACC1"}
        ]
    }
    r2 = engine.score_transaction(s2_data)
    print(f"Scenario 2 (Velocity Structuring) - CRS: {r2['overall_crs']}, Structuring Raw: {r2['module_scores']['structuring']['raw']}")
    assert r2['module_scores']['structuring']['raw'] == 10

    # Scenario 3: Round Number Avoidance
    # $9,500–$9,999 more than once in 30 days
    s3_data = {
        "customer": {"customer_type": "Verified Salaried Individual", "geo_tier": "Tier 4"},
        "transaction": {"amount": 9999, "date": base_date + timedelta(days=14), "sender_country": "United Kingdom", "receiver_country": "United States"},
        "history": [
            {"amount": 9875, "date": base_date, "account_id": "ACC1"}
        ]
    }
    r3 = engine.score_transaction(s3_data)
    print(f"Scenario 3 (Round Number) - CRS: {r3['overall_crs']}, Structuring Raw: {r3['module_scores']['structuring']['raw']}")
    assert r3['module_scores']['structuring']['raw'] == 10

    # Scenario 4: Micro-Structuring
    # 10+ transactions < $3,000 each; total > $30,000 within 30 days
    s4_history = [{"amount": 2800, "date": base_date + timedelta(days=i), "account_id": "ACC1"} for i in range(11)]
    s4_data = {
        "customer": {"customer_type": "Verified Salaried Individual", "geo_tier": "Tier 4"},
        "transaction": {"amount": 2800, "date": base_date + timedelta(days=12), "sender_country": "United Kingdom", "receiver_country": "United States"},
        "history": s4_history
    }
    r4 = engine.score_transaction(s4_data)
    print(f"Scenario 4 (Micro-Structuring) - CRS: {r4['overall_crs']}, Structuring Raw: {r4['module_scores']['structuring']['raw']}")
    assert r4['module_scores']['structuring']['raw'] == 40

    # Scenario 5: Multiple Account Structuring + Smurfing (Independent Trigger)
    # Account A $9,500 + Account B $9,500 + Account C $9,500 same day
    # This triggers Rule 1 (3 tx in 7 days) and Rule 5 (2+ accounts) and Rule 3 (round num)
    s5_data = {
        "customer": {"customer_type": "Verified Salaried Individual", "geo_tier": "Tier 4"},
        "transaction": {"amount": 9500, "date": base_date, "account_id": "ACC_C", "sender_country": "United Kingdom", "receiver_country": "United States"},
        "history": [
            {"amount": 9500, "date": base_date, "account_id": "ACC_A"},
            {"amount": 9500, "date": base_date, "account_id": "ACC_B"}
        ]
    }
    r5 = engine.score_transaction(s5_data)
    # Rule 1 (15) + Rule 5 (40) + Rule 3 (10) = 65
    print(f"Scenario 5 (Multiple Account) - CRS: {r5['overall_crs']}, Structuring Raw: {r5['module_scores']['structuring']['raw']}, Is Trigger: {r5['module_scores']['structuring']['is_trigger']}")
    assert r5['module_scores']['structuring']['raw'] == 65
    assert r5['module_scores']['structuring']['is_trigger'] == True
    assert r5['is_alert'] == True

    # Scenario 6: Geography Test (India to Cayman)
    s6_data = {
        "customer": {"customer_type": "Verified Salaried Individual", "geo_tier": "Tier 4"},
        "transaction": {"amount": 5000, "date": base_date, "sender_country": "India", "receiver_country": "Cayman Islands"},
        "history": []
    }
    r6 = engine.score_transaction(s6_data)
    print(f"Scenario 6 (India to Cayman) - CRS: {r6['overall_crs']}, Geo Raw: {r6['module_scores']['geo']['raw']}")
    # India (Tier 2B: 15) + Cayman (Tier 3: 15) = 30
    assert r6['module_scores']['geo']['raw'] == 30

    # Scenario 7: Sanctions Auto-Alert (United Kingdom to Iran)
    s7_data = {
        "customer": {"customer_type": "Verified Salaried Individual", "geo_tier": "Tier 4"},
        "transaction": {"amount": 500, "date": base_date, "sender_country": "United Kingdom", "receiver_country": "Iran"},
        "history": []
    }
    r7 = engine.score_transaction(s7_data)
    print(f"Scenario 7 (UK to Iran) - CRS: {r7['overall_crs']}, Auto-Alert: {r7['is_auto_alert']}")
    assert r7['is_auto_alert'] == True
    assert r7['is_alert'] == True

    print("--- ALL DAY 22 TESTS PASSED ---")

if __name__ == "__main__":
    run_day22_tests()
