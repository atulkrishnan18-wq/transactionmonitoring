import datetime
import json
from scoring_engine import ScoreSentinelEngine

class MockCursor:
    def __init__(self, rows):
        self.rows = rows
    def execute(self, query, params):
        pass
    def fetchall(self):
        return self.rows

class MockConnection:
    def __init__(self, rows):
        self.rows = rows
    def cursor(self):
        return MockCursor(self.rows)

def run_tests():
    engine = ScoreSentinelEngine()
    
    # Test 1: Customer without history (0 rows)
    conn_no_history = MockConnection([])
    
    tx_no_history = {
        "customer": {"customer_id": "NEW-CUST", "customer_type": "INDIVIDUAL"},
        "transaction": {
            "amount": 5000,
            "transaction_type": "WIRE",
            "sender_country": "US",
            "receiver_country": "US",
            "date": datetime.datetime.now()
        },
        "history": []
    }
    
    print("=== TEST 1: Customer without history ===")
    res1 = engine.score_transaction(tx_no_history, db_connection=conn_no_history)
    print(json.dumps(res1["module_scores"]["velocity"], indent=2))
    print("Velocity Rules Fired:", [r for r in res1["rules_fired"] if r.startswith("VEL")])
    
    # Test 2: Customer with existing history (high frequency, high volume, structuring)
    # rows: (transaction_amount, counterparty)
    mock_rows = [
        (9000, "ACC1"),
        (9500, "ACC2"),
        (8000, "ACC3"),
        (9800, "ACC4"),
        (8500, "ACC5"),
        (50000, "ACC6"),
        (10000, "ACC7"),
        (1000, "ACC8"),
        (1000, "ACC9"),
        (1000, "ACC10"),
        (1000, "ACC11"),
        (1000, "ACC12"),
    ] # 12 txs (score 70 for count), volume = 108800 (score 90 for volume), distinct cp = 12 (score 90), structuring = 5 (score 85)
    
    conn_history = MockConnection(mock_rows)
    
    tx_history = {
        "customer": {"customer_id": "EXISTING-CUST", "customer_type": "INDIVIDUAL"},
        "transaction": {
            "amount": 5000,
            "transaction_type": "WIRE",
            "sender_country": "US",
            "receiver_country": "US",
            "date": datetime.datetime.now()
        },
        "history": []
    }
    
    print("\n=== TEST 2: Customer with existing history ===")
    res2 = engine.score_transaction(tx_history, db_connection=conn_history)
    print(json.dumps(res2["module_scores"]["velocity"], indent=2))
    print("Velocity Rules Fired:", [r for r in res2["rules_fired"] if r.startswith("VEL")])
    print(f"Overall CRS: {res2['overall_crs']}")

if __name__ == "__main__":
    run_tests()
