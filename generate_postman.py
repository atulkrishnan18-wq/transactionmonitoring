import json
from datetime import datetime, timedelta

def generate_postman():
    base_date = datetime.now()
    
    scenarios = [
        # Original 20 (simplified data for Postman)
        (1, 'Salary Earner', {'customer': {'customer_type': 'Verified Salaried Individual'}, 'transaction': {'transaction_type': 'Wire Transfer (Domestic)', 'amount': 2000}}),
        (2, 'Cayman Shell', {'customer': {'customer_type': 'Shell Company', 'ownership_structure': 'Beneficial owner identified but not verified', 'geo_tier': 'Tier 3'}, 'transaction': {'transaction_type': 'Wire Transfer (International)', 'amount': 50000, 'sender_country': 'United Kingdom', 'receiver_country': 'Cayman Islands'}}),
        (3, 'Smurfing', {'customer': {'customer_type': 'Newly Onboarded Customer'}, 'transaction': {'transaction_type': 'Cash Deposit', 'amount': 9500, 'account_id': 'ACC1'}, 'history': [{'amount': 9500, 'date': (base_date + timedelta(days=i)).isoformat()} for i in range(3)]}),
        (4, 'Iran Sanctions', {'customer': {'customer_type': 'SMB'}, 'transaction': {'transaction_type': 'Wire', 'amount': 500, 'receiver_country': 'Iran'}}),
        (5, 'Crypto Freq', {'customer': {'customer_type': 'Crypto-Asset Business'}, 'transaction': {'transaction_type': 'Cryptocurrency', 'amount': 5000}, 'history': [{'amount': 5000, 'date': (base_date + timedelta(hours=i)).isoformat()} for i in range(4)]}),
        (6, 'PEP Tier 2', {'customer': {'customer_type': 'HNWI', 'match_type': 'Confirmed PEP — Tier 2'}, 'transaction': {'transaction_type': 'Wire', 'amount': 75000, 'receiver_country': 'Cyprus'}}),
        (7, 'FATF Corridor', {'customer': {'customer_type': 'Established Business'}, 'transaction': {'transaction_type': 'Correspondent', 'amount': 250000, 'sender_country': 'Nigeria', 'receiver_country': 'South Africa'}}),
        (8, 'Cash SMB', {'customer': {'customer_type': 'Cash-Intensive Business'}, 'transaction': {'transaction_type': 'Cash Deposit', 'amount': 2000, 'account_id': 'ACC1'}, 'history': [{'amount': 2000, 'date': (base_date + timedelta(days=i)).isoformat()} for i in range(14)]}),
        (9, 'SAR Generator', {'customer': {'customer_type': 'Shell Company'}, 'transaction': {'transaction_type': 'Wire', 'amount': 9900, 'sender_country': 'Nigeria', 'receiver_country': 'British Virgin Islands'}, 'history': [{'amount': 9900, 'date': base_date.isoformat()}, {'amount': 9800, 'date': (base_date + timedelta(days=1)).isoformat()}]}),
        (10, 'Missing UBO', {'customer': {'customer_type': 'HNWI', 'ownership_structure': 'Beneficial owner unidentified or unverifiable'}, 'transaction': {'transaction_type': 'Wire', 'amount': 10000}}),
        (11, 'Vekselberg', {'customer': {'customer_type': 'Shell Company', 'match_type': 'Confirmed PEP — Tier 1'}, 'transaction': {'transaction_type': 'Wire', 'amount': 1000000, 'sender_country': 'Russia'}}),
        (12, 'Wirecard ML', {'customer': {'customer_type': 'Newly Onboarded'}, 'transaction': {'transaction_type': 'Online Payment', 'amount': 45}, 'history': [{'amount': 45, 'date': (base_date - timedelta(minutes=i)).isoformat()} for i in range(200)]}),
        (13, 'Pakistan FP', {'customer': {'customer_type': 'Non-Resident', 'geo_tier': 'Tier 2B'}, 'transaction': {'transaction_type': 'Wire', 'amount': 180000, 'sender_country': 'Pakistan'}}),
        (14, 'UK Minister', {'customer': {'customer_type': 'PEP', 'match_type': 'Confirmed PEP — Tier 1'}, 'transaction': {'transaction_type': 'Wire', 'amount': 5000}}),
        (15, 'Former PEP', {'customer': {'customer_type': 'HNWI', 'match_type': 'Confirmed PEP — Tier 2'}, 'transaction': {'transaction_type': 'Wire', 'amount': 75000, 'receiver_country': 'UAE'}}),
        (16, 'BVI Shell', {'customer': {'customer_type': 'Shell Company', 'geo_tier': 'Tier 3'}, 'transaction': {'transaction_type': 'Wire', 'amount': 500000, 'sender_country': 'British Virgin Islands', 'receiver_country': 'Cyprus'}}),
        (17, 'Fan-In Mule', {'customer': {'customer_type': 'Newly Onboarded'}, 'transaction': {'transaction_type': 'P2P', 'amount': 1000}, 'history': [{'amount': 1000, 'date': (base_date - timedelta(hours=i)).isoformat(), 'sender_id': f'S_{i}'} for i in range(7)]}),
        (18, 'Dormant Nigeria', {'customer': {'customer_type': 'Salaried'}, 'transaction': {'transaction_type': 'Cash', 'amount': 800, 'receiver_country': 'Nigeria'}, 'history': [{'amount': 100, 'date': (base_date - timedelta(days=100)).isoformat()}] + [{'amount': 800, 'date': (base_date + timedelta(hours=i)).isoformat()} for i in range(11)]}),
        (19, 'TBML LC', {'customer': {'customer_type': 'SMB', 'behaviour_indicator': 'Frequent large cash'}, 'transaction': {'transaction_type': 'Trade Finance', 'amount': 320000, 'is_over_invoiced': True, 'receiver_country': 'Malaysia'}}),
        (20, 'Insurance', {'customer': {'customer_type': 'HNWI'}, 'transaction': {'transaction_type': 'Insurance', 'amount': 50000, 'is_early_surrender': True, 'refund_to_third_party': True}}),
        
        # Mule Cluster 5
        (21, 'MC-1: Concentrator', {'customer': {'customer_type': 'Individual', 'device_nexus_count': 5}, 'transaction': {'amount': 95000, 'account_id': 'CONC_1', 'type': 'DEBIT'}, 'history': [{'sender_id': f'S_{i}', 'amount': 9500, 'date': (base_date - timedelta(minutes=i)).isoformat(), 'type': 'CREDIT'} for i in range(10)]}),
        (22, 'MC-2: Salary Mule', {'customer': {'customer_type': 'Individual'}, 'transaction': {'amount': 135000, 'account_id': 'MULE_1', 'type': 'DEBIT'}, 'history': [{'sender_id': f'M_{i}', 'amount': 15000, 'date': (base_date - timedelta(minutes=i*10)).isoformat(), 'type': 'CREDIT'} for i in range(9)]}),
        (23, 'MC-3: Dormant Activation', {'customer': {'customer_type': 'Individual', 'behaviour_indicator': 'Dormant'}, 'transaction': {'amount': 60000, 'account_id': 'DORM_1', 'type': 'DEBIT'}, 'history': [{'sender_id': f'M_{i}', 'amount': 10000, 'date': (base_date - timedelta(minutes=i*5)).isoformat(), 'type': 'CREDIT'} for i in range(6)]}),
        (24, 'MC-4: UPI Smurfing', {'customer': {'customer_type': 'Individual', 'device_nexus_count': 4}, 'transaction': {'amount': 74000, 'account_id': 'UPI_1', 'type': 'DEBIT'}, 'history': [{'sender_id': f'V_{i}', 'amount': 4999, 'date': (base_date - timedelta(minutes=i)).isoformat(), 'type': 'CREDIT'} for i in range(15)]}),
        (25, 'MC-5: Chit Fund', {'customer': {'customer_type': 'Business'}, 'transaction': {'amount': 5000, 'account_id': 'CHIT_1', 'type': 'CREDIT'}, 'history': [{'sender_id': f'MEM_{i}', 'amount': 5000, 'date': (base_date - timedelta(days=30)).isoformat(), 'type': 'CREDIT'} for i in range(20)]}),
    ]
    
    pm_items = []
    for idx, name, data in scenarios:
        item = {
            'name': f'{idx}. {name}',
            'request': {
                'method': 'POST',
                'header': [{'key': 'Content-Type', 'value': 'application/json'}],
                'body': {
                    'mode': 'raw',
                    'raw': json.dumps({
                        'customer_id': f'CUST-{idx}',
                        'transaction_amount': data.get('transaction', {}).get('amount', 0),
                        'transaction_currency': 'USD',
                        'transaction_type': data.get('transaction', {}).get('transaction_type', 'Wire'),
                        'sender_country': data.get('transaction', {}).get('sender_country', 'GB'),
                        'receiver_country': data.get('transaction', {}).get('receiver_country', 'GB'),
                        'customer': data.get('customer', {}),
                        'history': data.get('history', []),
                        'account_id': data.get('transaction', {}).get('account_id', 'ACC-DEFAULT'),
                        'type': data.get('transaction', {}).get('type', 'DEBIT')
                    })
                },
                'url': {'raw': '{{base_url}}/api/score', 'host': ['{{base_url}}'], 'path': ['api', 'score']}
            },
            'event': [{
                'listen': 'test',
                'script': {
                    'exec': ['pm.test("Status is 200", function () { pm.response.to.have.status(200); });'],
                    'type': 'text/javascript'
                }
            }]
        }
        pm_items.append(item)
        
    collection = {
        'info': {
            'name': 'ScoreSentinel Full Suite (Modules 1-5)',
            'description': 'Master collection for validating all 5 modules across 25 scenarios.',
            'schema': 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'
        },
        'item': pm_items,
        'variable': [{'key': 'base_url', 'value': 'http://localhost:5000'}]
    }
    
    with open('transactionmonitoring/postman/ScoreSentinel_Full_Suite.postman_collection.json', 'w') as f:
        json.dump(collection, f, indent=2)

if __name__ == "__main__":
    generate_postman()
