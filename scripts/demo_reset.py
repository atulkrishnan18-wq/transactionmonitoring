"""
ScoreSentinel — Demo Reset Script
Calls DELETE /api/demo/reset to wipe all IBM demo transactions and alerts.

Authored by Atul Krishnan, CAMS
"""

import os
import requests

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    pass

API_BASE_URL = os.environ.get("API_BASE_URL", "https://scoresentinel-api.onrender.com")
API_KEY = os.environ.get("DEMO_API_KEY")


def reset_demo():
    url = f"{API_BASE_URL.rstrip('/')}/api/demo/reset"
    headers = {
        "X-DEMO-API-KEY": API_KEY or "",
        "Content-Type": "application/json",
    }

    print("\n  ScoreSentinel — Demo Reset")
    print(f"  Calling DELETE {url}")
    print("  This will delete all IBM-prefixed transactions and alerts.\n")

    if not API_KEY:
        print("  ERROR DEMO_API_KEY is not set. Export it or add it to .env")
        return

    try:
        resp = requests.delete(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            tx_count = data.get("transactions_deleted", 0)
            alert_count = data.get("alerts_deleted", 0)
            total = data.get("transactions_deleted", 0) + data.get("alerts_deleted", 0)
            message = data.get("message") or f"Demo environment reset — {total} records deleted"
            print(f"  OK {message}")
            print(f"    Transactions deleted : {tx_count}")
            print(f"    Alerts deleted       : {alert_count}")
        elif resp.status_code == 403:
            print(f"  ERROR Reset blocked: {resp.json().get('message', 'Safety check failed')}")
        elif resp.status_code == 401:
            print("  ERROR Unauthorized — check your DEMO_API_KEY")
        else:
            print(f"  ERROR {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"  ERROR Connection: {e}")


if __name__ == "__main__":
    reset_demo()
