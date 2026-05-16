"""
ScoreSentinel Database Initialization Script
Part of the ScoreSentinel AML Transaction Risk Scoring Engine
Authored by Atul Krishnan, CAMS | Day 28 of 60
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
DATABASE_URL = os.environ.get('DATABASE_URL')

def init_db():
    print(f"Connecting to database at {DATABASE_URL}...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Step 1: Run schema if tables don't exist
        print("Ensuring tables exist...")
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Split schema by semicolon and execute each statement
        # Or just try to execute the whole thing and ignore 'already exists' errors
        try:
            cur.execute(schema_sql)
            conn.commit()
        except Exception as e:
            conn.rollback()
            if "already exists" in str(e):
                print("Tables already exist, skipping schema creation.")
            else:
                raise e
        
        # Step 2: Clear existing sample data (Optional for init)
        cur.execute("DELETE FROM alerts CASCADE")
        cur.execute("DELETE FROM transactions CASCADE")
        cur.execute("DELETE FROM customers CASCADE")
        
        # Step 3: Insert Sample Customers
        print("Inserting sample customers...")
        customers = [
            ('CUST-001', 'John Doe', 'Verified Salaried Individual', 5, 'LOW', 'N/A', 'John Doe', 100.00, 'GB'),
            ('CUST-002', 'Global Shell Ltd', 'Shell Company', 90, 'HIGH', 'N/A', 'Unknown', 0.00, 'VG'),
            ('CUST-003', 'Viktor Vekselberg', 'Politically Exposed Person (PEP)', 150, 'HIGH', 'Tier 1', 'Viktor Vekselberg', 100.00, 'RU')
        ]
        cur.executemany("""
            INSERT INTO customers (
                customer_id, full_name, customer_type, ccrs, risk_band, 
                pep_tier, beneficial_owner, bo_ownership_pct, country_of_domicile
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, customers)

        # Step 4: Insert Sample Transactions
        print("Inserting sample transactions...")
        now = datetime.now()
        transactions = [
            ('TXN-20260514-0001', 'CUST-001', now - timedelta(hours=5), 500.00, 'GBP', 'Wire Transfer (Domestic)', 'GB', 'GB', 6.31, 'LOW_RISK', False),
            ('TXN-20260514-0002', 'CUST-002', now - timedelta(hours=4), 45000.00, 'USD', 'Wire Transfer (International)', 'NG', 'VG', 59.04, 'MEDIUM_HIGH', False),
            ('TXN-20260514-0003', 'CUST-003', now - timedelta(hours=3), 1000000.00, 'USD', 'Wire Transfer (International)', 'RU', 'CH', None, 'AUTO_ALERT', True),
            ('TXN-20260514-0004', 'CUST-001', now - timedelta(hours=2), 9500.00, 'GBP', 'Cash Deposit', 'GB', 'GB', 45.44, 'MEDIUM_HIGH', True),
            ('TXN-20260514-0005', 'CUST-002', now - timedelta(hours=1), 100.00, 'USD', 'Wire Transfer (International)', 'IR', 'GB', None, 'AUTO_ALERT', True)
        ]
        cur.executemany("""
            INSERT INTO transactions (
                transaction_id, customer_id, timestamp_processed, 
                transaction_amount, transaction_currency, transaction_type,
                sender_country, receiver_country, crs, risk_band, alert_generated
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, transactions)

        # Step 5: Insert Sample Alerts
        print("Inserting sample alerts...")
        alerts = [
            ('ALT-20260514-0001', 'TXN-20260514-0003', 'CUST-003', 'SANCTIONS', 'PENDING_ASSESSMENT', 'PENDING'),
            ('ALT-20260514-0002', 'TXN-20260514-0004', 'CUST-001', 'AML_RISK', 'PENDING_ASSESSMENT', 'PENDING')
        ]
        cur.executemany("""
            INSERT INTO alerts (
                alert_id, transaction_id, customer_id, alert_type, stage, status
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, alerts)

        conn.commit()
        print("Database initialized successfully with sample data.")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    init_db()
