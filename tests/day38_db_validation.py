import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def run_validation():
    print("🔍 Starting Day 38 Bulk Data Validation...")
    print("-" * 60)
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 1. Row Counts
        cur.execute("SELECT COUNT(*) FROM customers")
        cust_count = cur.fetchone()['count']
        cur.execute("SELECT COUNT(*) FROM transactions")
        tx_count = cur.fetchone()['count']
        cur.execute("SELECT COUNT(*) FROM alerts")
        alert_count = cur.fetchone()['count']
        cur.execute("SELECT COUNT(*) FROM mule_clusters")
        cluster_count = cur.fetchone()['count']
        
        print(f"📊 Total Records: {cust_count} Customers, {tx_count} Transactions, {alert_count} Alerts, {cluster_count} Clusters")
        
        # 2. Alert Consistency Check
        # Check for transactions flagged as alerts but missing alert records
        cur.execute("""
            SELECT transaction_id FROM transactions 
            WHERE alert_generated = TRUE 
            AND transaction_id NOT IN (SELECT transaction_id FROM alerts)
        """)
        orphaned_tx_alerts = cur.fetchall()
        
        if orphaned_tx_alerts:
            print(f"❌ FAILED: Found {len(orphaned_tx_alerts)} transactions marked as alert_generated=True with no matching alert record.")
        else:
            print("✅ SUCCESS: All flagged transactions have corresponding alert records.")
            
        # 3. Orphaned Alerts Check
        cur.execute("""
            SELECT alert_id FROM alerts 
            WHERE transaction_id NOT IN (SELECT transaction_id FROM transactions)
        """)
        orphaned_alerts = cur.fetchall()
        if orphaned_alerts:
            print(f"❌ FAILED: Found {len(orphaned_alerts)} alerts pointing to non-existent transactions.")
        else:
            print("✅ SUCCESS: No orphaned alert records found.")

        # 4. CRS/MCS Range Validation
        cur.execute("""
            SELECT COUNT(*) FROM transactions 
            WHERE (crs IS NOT NULL AND (crs < 0 OR crs > 100))
        """)
        invalid_crs = cur.fetchone()['count']
        if invalid_crs > 0:
            print(f"❌ FAILED: Found {invalid_crs} transactions with CRS outside 0-100 range.")
        else:
            print("✅ SUCCESS: All CRS values are within valid bounds.")

        # 5. Mule Cluster Risk Band Check
        cur.execute("""
            SELECT cluster_id, mcs, risk_band FROM mule_clusters 
            WHERE (mcs >= 90 AND risk_band != 'ORGANISED_NETWORK')
        """)
        mismatched_clusters = cur.fetchall()
        if mismatched_clusters:
            print(f"⚠️ WARNING: Found {len(mismatched_clusters)} clusters with MCS >= 90 not labeled as ORGANISED_NETWORK.")
        else:
            print("✅ SUCCESS: Mule cluster risk bands are consistent with MCS scores.")

        # 6. Null Value Check for Critical Fields
        cur.execute("""
            SELECT COUNT(*) FROM transactions 
            WHERE customer_id IS NULL OR transaction_amount IS NULL OR timestamp_processed IS NULL
        """)
        null_critical = cur.fetchone()['count']
        if null_critical > 0:
            print(f"❌ FAILED: Found {null_critical} transactions with NULL critical fields.")
        else:
            print("✅ SUCCESS: No NULL values in critical transaction fields.")

    except Exception as e:
        print(f"❌ ERROR: Database validation failed - {str(e)}")
    finally:
        cur.close()
        conn.close()

    print("-" * 60)
    print("Validation Complete!")

if __name__ == "__main__":
    run_validation()
