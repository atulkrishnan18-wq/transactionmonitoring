import os
import psycopg2
from dotenv import load_dotenv
import subprocess
import sys

# Load environment variables
load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')

def reset_database():
    print("🧹 Wiping database for Demo Reset...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    try:
        # Cascade ensures all related records are wiped
        cur.execute("TRUNCATE TABLE mule_clusters, alerts, transactions, customers CASCADE;")
        conn.commit()
        print("✅ Database is now EMPTY.")
    except Exception as e:
        print(f"❌ Error during wipe: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def seed_master_scenarios():
    print("🌱 Re-seeding Master Scenarios (1-25)...")
    
    # We use the existing Postman runner to populate the DB through the API
    # Ensure the API is running before this script is called.
    try:
        # Update current timestamps to ensure 24h mule detection works
        subprocess.run(["python", "transactionmonitoring/generate_postman.py"], check=True)
        # Submit the scenarios
        subprocess.run(["python", "run_postman_scenarios.py"], check=True)
        print("✅ Re-seeding COMPLETE.")
    except Exception as e:
        print(f"❌ Error during re-seeding: {e}")

if __name__ == "__main__":
    confirm = input("This will WIPE all data. Type 'RESET' to confirm: ")
    if confirm == "RESET":
        reset_database()
        seed_master_scenarios()
        print("\n✨ Demo Environment is now FRESH and READY.")
    else:
        print("Reset cancelled.")
