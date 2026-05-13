"""
Day 23 Validation Tests — Transaction Types & Velocity
Part of the ScoreSentinel AML Transaction Risk Scoring Engine
Authored by Atul Krishnan, CAMS | Day 23 of 60
"""

from scoring_engine import ScoreSentinelEngine
from datetime import datetime, timedelta

def run_day23_tests():
    engine = ScoreSentinelEngine()
    base_date = datetime(2026, 5, 1)

    print("--- RUNNING DAY 23 VALIDATION TESTS ---")

    # Scenario 1: Cryptocurrency Transaction (High Risk)
    s1_data = {
        "customer": {"customer_type": "Verified Salaried Individual", "geo_tier": "Tier 4"},
        "transaction": {"transaction_type": "Cryptocurrency Transaction", "amount": 1000, "date": base_date, "sender_country": "United Kingdom", "receiver_country": "United States"},
        "history": []
    }
    r1 = engine.score_transaction(s1_data)
    print(f"Scenario 1 (Crypto) - CRS: {r1['overall_crs']}, TxType Raw: {r1['module_scores']['transaction_type']['raw']}")
    # Crypto (55/55 = 100% normalised * 20% = 20)
    # Customer (5/175 = 2.86% * 30% = 0.86)
    # Total CRS approx 20.86
    assert r1['module_scores']['transaction_type']['raw'] == 55
    assert r1['overall_crs'] >= 20

    # Scenario 2: Burst Velocity Trigger (Independent Structuring Alert)
    # 5+ transactions in 30 minutes
    s2_history = [{"transaction_type": "Internal Account Transfer", "amount": 100, "date": base_date + timedelta(minutes=i), "account_id": "ACC1"} for i in range(4)]
    s2_data = {
        "customer": {"customer_type": "Verified Salaried Individual", "geo_tier": "Tier 4"},
        "transaction": {"transaction_type": "Internal Account Transfer", "amount": 100, "date": base_date + timedelta(minutes=10), "account_id": "ACC1"},
        "history": s2_history
    }
    r2 = engine.score_transaction(s2_data)
    print(f"Scenario 2 (Burst) - Structuring Raw: {r2['module_scores']['structuring']['raw']}, Is Trigger: {r2['module_scores']['structuring']['is_trigger']}")
    # Burst adds +55. Structuring module max 70. 55/70 = 78.6% > 75%.
    assert r2['module_scores']['structuring']['raw'] >= 55
    assert r2['module_scores']['structuring']['is_trigger'] == True

    # Scenario 3: Fan-In Pattern (VEL-028)
    # 5+ senders -> 1 receiver within 24 hours
    s3_history = [{"transaction_type": "Wire Transfer (Domestic)", "amount": 500, "date": base_date + timedelta(hours=i), "sender_id": f"SENDER_{i}", "receiver_id": "MULE_1"} for i in range(4)]
    s3_data = {
        "customer": {"customer_type": "Verified Salaried Individual", "geo_tier": "Tier 4"},
        "transaction": {"transaction_type": "Wire Transfer (Domestic)", "amount": 500, "date": base_date + timedelta(hours=5), "sender_id": "SENDER_4", "receiver_id": "MULE_1"},
        "history": s3_history
    }
    r3 = engine.score_transaction(s3_data)
    print(f"Scenario 3 (Fan-In) - Structuring Raw: {r3['module_scores']['structuring']['raw']}, Rules: {r3['module_scores']['structuring']['triggered_rules']}")
    # Fan-In (+40) + Unusual Velocity (+15) = 55. 55/70 = 78.6% > 75%.
    assert "VEL-028: Fan-In" in r3['module_scores']['structuring']['triggered_rules']
    assert r3['module_scores']['structuring']['is_trigger'] == True

    # Scenario 4: Dormant-to-Active (BEH-001)
    # 90+ days inactivity, then 5+ tx in 48h
    s4_history = [{"transaction_type": "Internal Account Transfer", "amount": 100, "date": base_date - timedelta(days=100), "account_id": "ACC1"}]
    # Add 4 tx in the last 24 hours
    s4_history.extend([{"transaction_type": "Internal Account Transfer", "amount": 100, "date": base_date + timedelta(hours=i), "account_id": "ACC1"} for i in range(4)])
    s4_data = {
        "customer": {"customer_type": "Verified Salaried Individual", "geo_tier": "Tier 4"},
        "transaction": {"transaction_type": "Internal Account Transfer", "amount": 100, "date": base_date + timedelta(hours=5), "account_id": "ACC1"},
        "history": s4_history
    }
    r4 = engine.score_transaction(s4_data)
    print(f"Scenario 4 (Dormant-to-Active) - Structuring Raw: {r4['module_scores']['structuring']['raw']}, Rules: {r4['module_scores']['structuring']['triggered_rules']}")
    assert "BEH-001: Dormant-to-Active" in r4['module_scores']['structuring']['triggered_rules']

    # Scenario 5: Insurance Escalation Rule
    s5_data = {
        "customer": {"customer_type": "Verified Salaried Individual", "geo_tier": "Tier 4"},
        "transaction": {"transaction_type": "Insurance Premium Payment", "amount": 5000, "date": base_date, "is_early_surrender": True, "refund_to_third_party": True},
        "history": []
    }
    r5 = engine.score_transaction(s5_data)
    print(f"Scenario 5 (Insurance) - Auto-Alert: {r5['is_auto_alert']}, Reason: {r5['alert_reason']}")
    assert r5['is_auto_alert'] == True
    assert "Insurance" in r5['alert_reason']

    print("--- ALL DAY 23 TESTS PASSED ---")

if __name__ == "__main__":
    run_day23_tests()
