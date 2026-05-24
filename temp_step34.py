import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('transactionmonitoring/.env')
DATABASE_URL = os.environ.get('DATABASE_URL')

sql = """
-- STEP 3 additional
ALTER TABLE alerts 
DROP CONSTRAINT IF EXISTS valid_stage;

ALTER TABLE alerts 
ADD CONSTRAINT valid_stage 
CHECK (stage IN (
    'PENDING_ASSESSMENT',
    'PENDING_ACTION', 
    'SENT_FOR_REVIEW',
    'RESOLVED'
));

-- STEP 4 Seed demo data
DELETE FROM customers WHERE customer_id IN ('CUST-DEMO-001', 'CUST-DEMO-002', 'CUST-DEMO-003', 'CUST-DEMO-004', 'CUST-DEMO-005');

INSERT INTO customers 
(customer_id, full_name, customer_type, 
ccrs, risk_band, pep_tier, 
country_of_domicile, onboarding_date) 
VALUES
('CUST-DEMO-001', 'Rajesh Kumar', 
 'SMB Entity', 35, 'MEDIUM_LOW', 
 'N/A', 'IND', '2025-01-15'),
('CUST-DEMO-002', 'Renova Group Ltd', 
 'Shell Company', 125, 'VERY_HIGH', 
 'Tier 1', 'RUS', '2024-06-01'),
('CUST-DEMO-003', 'Karachi Textiles', 
 'Established Business', 35, 
 'MEDIUM_LOW', 'N/A', 'PAK', '2023-03-10'),
('CUST-DEMO-004', 'John Smith', 
 'Verified Salaried Individual', 5, 
 'LOW', 'N/A', 'GBR', '2022-08-20'),
('CUST-DEMO-005', 'FastPay Merchants', 
 'Payment Processor', 65, 'HIGH', 
 'N/A', 'IND', '2025-11-01');
"""

try:
    print(f"Connecting to {DATABASE_URL}")
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    print('Step 3 & 4 SQL applied successfully.')
except Exception as e:
    print(f'Error: {e}')
finally:
    if 'conn' in locals():
        conn.close()
