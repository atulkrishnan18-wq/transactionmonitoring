import asyncio
import aiohttp
import time
import random
import datetime

# Use the Demo API Key we set up
API_KEY = "SCORESENTINEL_DEMO_2027"
BASE_URL = "http://127.0.0.1:5000/api/score"

def generate_payload(i):
    return {
        "customer_id": f"MUSCLE-CUST-{random.randint(1000, 9999)}",
        "transaction_amount": round(random.uniform(10, 50000), 2),
        "transaction_currency": "USD",
        "transaction_type": random.choice(["Wire", "Cash", "Crypto", "P2P"]),
        "sender_country": random.choice(["IN", "US", "GB", "AE", "IR"]),
        "receiver_country": random.choice(["IN", "US", "GB", "AE", "IR"]),
        "customer": {
            "customer_type": "Individual",
            "device_nexus_count": random.randint(1, 10)
        },
        "history": []
    }

async def send_transaction(session, i):
    payload = generate_payload(i)
    headers = {
        "X-DEMO-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }
    try:
        async with session.post(BASE_URL, json=payload, headers=headers) as response:
            status = response.status
            await response.json()
            return status
    except Exception as e:
        return f"Error: {str(e)}"

async def run_muscle_test(total_requests=1000, concurrency=50):
    print(f"🏋️ Starting ScoreSentinel MUSCLE TEST: {total_requests} requests...")
    print(f"🔥 Concurrency Level: {concurrency} parallel requests")
    print("-" * 60)
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(total_requests):
            tasks.append(send_transaction(session, i))
            
            # Control concurrency
            if len(tasks) >= concurrency:
                await asyncio.gather(*tasks)
                tasks = []
                
        if tasks:
            await asyncio.gather(*tasks)

    end_time = time.time()
    duration = end_time - start_time
    
    print("-" * 60)
    print(f"✅ Muscle Test Complete!")
    print(f"⏱️  Total Duration: {duration:.2f} seconds")
    print(f"🚀 Throughput: {total_requests / duration:.2f} transactions/sec")
    print(f"📊 Avg Latency: {(duration / total_requests) * 1000:.2f} ms per transaction")

if __name__ == "__main__":
    # Total 1000 transactions, 50 at a time
    asyncio.run(run_muscle_test(1000, 50))
