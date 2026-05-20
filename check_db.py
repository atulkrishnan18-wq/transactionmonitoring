import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

def print_table(name):
    print(f"\n--- {name} ---")
    cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{name}'")
    for row in cur.fetchall():
        print(f"{row[0]}: {row[1]}")

print_table('alerts')
print_table('mule_clusters')
print_table('transactions')
print_table('customers')

conn.close()
