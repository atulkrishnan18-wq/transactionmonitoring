import os
import psycopg2
from dotenv import load_dotenv

# This script is used by GitHub Actions to prevent Supabase from pausing the project.
# It performs a simple SELECT query to register "activity" on the database.

def heartbeat():
    load_dotenv()
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        print("❌ Error: DATABASE_URL not found in environment.")
        return

    try:
        print(f"💓 Sending heartbeat to Supabase...")
        # We use sslmode=require for Supabase
        conn = psycopg2.connect(db_url, sslmode='require')
        cur = conn.cursor()
        
        # Simple query to show activity
        cur.execute("SELECT 1;")
        result = cur.fetchone()
        
        if result[0] == 1:
            print("✅ Heartbeat SUCCESS. Database is active.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Heartbeat FAILED: {e}")

if __name__ == "__main__":
    heartbeat()
