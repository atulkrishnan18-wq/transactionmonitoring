"""
Day 03: Link Analysis Module Test Suite
Verifies 2-hop graph traversal and link-based risk scoring.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.link_module import LinkAnalysisModule

# Load env
load_dotenv()
DATABASE_URL = os.environ.get('DATABASE_URL')

def setup_test_data(conn):
    cur = conn.cursor()
    print("Setting up temporary test data...")
    
    # Ensure customers exist
    test_customers = [
        ('CUST-L1', 'Isolated User', 'Individual'),
        ('CUST-L2A', 'User 2A', 'Individual'),
        ('CUST-L2B', 'User 2B', 'Individual'),
        ('CUST-L3A', 'User 3A', 'Individual'),
        ('CUST-L3B', 'User 3B', 'Individual'),
        ('CUST-L3C', 'User 3C', 'Individual')
    ]
    cur.executemany("INSERT INTO customers (customer_id, full_name, customer_type) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", test_customers)
    
    # Clear existing links for these customers
    ids = tuple([c[0] for c in test_customers])
    cur.execute("DELETE FROM customer_links WHERE customer_id_1 IN %s OR customer_id_2 IN %s", (ids, ids))
    
    # Scenario L2: Direct Device Link
    cur.execute("""
        INSERT INTO customer_links (customer_id_1, customer_id_2, link_type, link_value, link_count)
        VALUES ('CUST-L2A', 'CUST-L2B', 'SHARED_DEVICE', 'DEV-999', 1)
    """)
    
    # Scenario L3: Triangle Cluster
    # A <-> B, B <-> C, A <-> C
    cur.execute("""
        INSERT INTO customer_links (customer_id_1, customer_id_2, link_type, link_value, link_count)
        VALUES 
        ('CUST-L3A', 'CUST-L3B', 'SHARED_DEVICE', 'DEV-CLUSTER-1', 1),
        ('CUST-L3B', 'CUST-L3C', 'SHARED_DEVICE', 'DEV-CLUSTER-1', 1),
        ('CUST-L3A', 'CUST-L3C', 'SHARED_DEVICE', 'DEV-CLUSTER-1', 1)
    """)
    
    conn.commit()
    cur.close()

def teardown_test_data(conn):
    cur = conn.cursor()
    print("Cleaning up test data...")
    test_ids = ('CUST-L1', 'CUST-L2A', 'CUST-L2B', 'CUST-L3A', 'CUST-L3B', 'CUST-L3C')
    cur.execute("DELETE FROM customer_links WHERE customer_id_1 IN %s OR customer_id_2 IN %s", (test_ids, test_ids))
    cur.execute("DELETE FROM customers WHERE customer_id IN %s", (test_ids,))
    conn.commit()
    cur.close()

def run_tests():
    conn = psycopg2.connect(DATABASE_URL)
    module = LinkAnalysisModule()
    
    try:
        setup_test_data(conn)
        
        # Scenario L1: Isolated
        print("\n--- Running Scenario L1: Isolated Customer ---")
        network_l1 = module.get_network('CUST-L1', conn)
        result_l1 = module.calculate_link_risk_score('CUST-L1', network_l1)
        print(f"Score: {result_l1['link_risk_score']} | Rules: {result_l1['triggered_rules']}")
        assert result_l1['link_risk_score'] == 0
        
        # Scenario L2: Direct Device Link
        print("\n--- Running Scenario L2: Direct Device Link ---")
        network_l2 = module.get_network('CUST-L2A', conn)
        result_l2 = module.calculate_link_risk_score('CUST-L2A', network_l2)
        print(f"Score: {result_l2['link_risk_score']} | Rules: {result_l2['triggered_rules']}")
        assert "LNK-001" in result_l2['triggered_rules']
        
        # Scenario L3: Triangle Cluster
        print("\n--- Running Scenario L3: Triangle Cluster ---")
        network_l3 = module.get_network('CUST-L3A', conn)
        result_l3 = module.calculate_link_risk_score('CUST-L3A', network_l3)
        print(f"Score: {result_l3['link_risk_score']} | Rules: {result_l3['triggered_rules']}")
        # Expected: LNK-002 (multiple direct) + LNK-005 (triangle)
        assert "LNK-002" in result_l3['triggered_rules']
        assert "LNK-005" in result_l3['triggered_rules']
        
        print("\n✅ All Day 03 Link Analysis tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        teardown_test_data(conn)
        conn.close()

if __name__ == "__main__":
    run_tests()
