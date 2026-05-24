import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('transactionmonitoring/.env')
DATABASE_URL = os.environ.get('DATABASE_URL')

sql = """
-- Add device_nexus_count to customers table
ALTER TABLE customers ADD COLUMN IF NOT EXISTS device_nexus_count INTEGER DEFAULT 0;
"""

try:
    print(f"Connecting to {DATABASE_URL}")
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    print('Column device_nexus_count added successfully.')
except Exception as e:
    print(f'Error: {e}')
finally:
    if 'conn' in locals():
        conn.close()
