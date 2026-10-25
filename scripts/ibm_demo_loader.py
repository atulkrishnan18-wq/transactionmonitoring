"""
ScoreSentinel — IBM Demo Loader
Loads a curated 50-transaction demo set (25 laundering + 25 clean)
showcasing different AML typologies with live console output.

Authored by Atul Krishnan, CAMS | Day 28+ of 60
"""

import os
import csv
import time
import requests
import webbrowser
import random
from datetime import datetime, timedelta
from collections import defaultdict

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    pass

# ── CONFIG ──────────────────────────────────────────────────
IBM_FILE_PATH = "C:/Users/Roots and Arrow/AML_Data/HI-Small_Trans.csv"
API_BASE_URL = os.environ.get("API_BASE_URL", "https://scoresentinel-api.onrender.com")
API_KEY = os.environ.get("DEMO_API_KEY")
DELAY_SECONDS = 1.0
DASHBOARD_URL = "https://transactionmonitoring.vercel.app"
MAX_SCAN_ROWS = 250000
# ────────────────────────────────────────────────────────────

PAYMENT_FORMAT_MAP = {
    "Cheque": "CHEQUE", "ACH": "ACH", "Wire": "WIRE_TRANSFER",
    "Credit Card": "CARD_PAYMENT", "Bitcoin": "CRYPTO", "Reinvestment": "REINVESTMENT",
}
BANK_COUNTRY_MAP = {
    "0": "US", "1": "GB", "2": "DE", "3": "CN",
    "4": "AE", "5": "SG", "6": "IN", "7": "HK", "8": "JP",
}


def map_payment_format(fmt):
    return PAYMENT_FORMAT_MAP.get(fmt, "OTHER")


def map_country(bank):
    return BANK_COUNTRY_MAP.get(str(bank)[0], "US") if bank else "US"


def map_customer_type(account):
    return "CORPORATE" if str(account).startswith("8") else "INDIVIDUAL"


def ibm_customer_id(from_account):
    account = str(from_account)
    return account if account.startswith("IBM-") else f"IBM-{account}"


HEADERS = {
    "Content-Type": "application/json",
    "X-DEMO-API-KEY": API_KEY or "",
}

HIGH_RISK_GEO_ISO = ["IR", "KP", "SY", "CU", "RU"]


def score_row(row):
    """Call POST /api/score for one curated IBM/demo row. Returns (crs, alert)."""
    try:
        from_account = row["from_account"]
        customer_id = ibm_customer_id(from_account)
        pattern = row.get("pattern", "")
        sender_country = row.get("sender_country") or map_country(row.get("from_bank"))
        receiver_country = row.get("receiver_country") or map_country(row.get("to_bank"))

        if pattern == "high_risk_geo":
            sender_country = HIGH_RISK_GEO_ISO[hash(from_account) % len(HIGH_RISK_GEO_ISO)]

        payload = {
            "customer_id": customer_id,
            "account_id": from_account,
            "transaction_amount": float(row["amount"]),
            "transaction_currency": (row.get("currency") or "USD")[:3],
            "transaction_type": map_payment_format(row["fmt"]),
            "sender_country": sender_country,
            "receiver_country": receiver_country,
            "customer": {
                "customer_id": customer_id,
                "customer_type": map_customer_type(from_account),
                "full_name": f"IBM-{from_account}",
            },
        }

        if row.get("history"):
            payload["history"] = row["history"]

        resp = requests.post(
            f"{API_BASE_URL.rstrip('/')}/api/score",
            json=payload,
            headers=HEADERS,
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            crs = data.get("overall_crs")
            if crs is None:
                crs = data.get("crs")
            return crs, data.get("alert", False)
        print(f"  ERROR API {resp.status_code}: {resp.text[:120]}")
        return None, False
    except Exception as e:
        print(f"  ERROR API: {e}")
        return None, False


def row_to_rec(row, pattern, is_l):
    return {
        "from_account": row.get("From Account", "UNKNOWN"),
        "to_account": row.get("To Account", "UNKNOWN"),
        "amount": float(row.get("Amount Paid", 1000) or 1000),
        "currency": row.get("Payment Currency", "USD") or "USD",
        "fmt": row.get("Payment Format", "Wire"),
        "from_bank": row.get("From Bank", "0"),
        "to_bank": row.get("To Bank", "0"),
        "is_laundering": is_l,
        "label": "LAUNDERING" if is_l else "CLEAN",
        "pattern": pattern,
    }


def attach_structuring_history(rec):
    amount = rec["amount"]
    rec["history"] = [
        {
            "amount": amount,
            "date": (datetime.now() - timedelta(hours=i * 6)).isoformat(),
            "account_id": rec["from_account"],
            "transaction_type": rec["fmt"],
        }
        for i in range(1, 5)
    ]
    return rec


def attach_fan_in_history(rec, sibling_accounts):
    rec["history"] = [
        {
            "amount": rec["amount"],
            "date": (datetime.now() - timedelta(hours=i)).isoformat(),
            "account_id": acct,
            "transaction_type": "CREDIT",
        }
        for i, acct in enumerate(sibling_accounts[:6], 1)
    ]
    return rec


def load_demo_records():
    """Read IBM CSV and pick 25 laundering (by typology) + 25 clean."""
    if not os.path.exists(IBM_FILE_PATH):
        print(f"\nWARNING: IBM data not found at: {IBM_FILE_PATH}")
        print("   Generating synthetic demo records instead...\n")
        return generate_synthetic_records()

    buckets = {
        "structuring": [],
        "fan_in": [],
        "high_risk_geo": [],
        "high_value": [],
        "ach_pattern": [],
        "clean": [],
        "laundering_other": [],
    }
    by_dest = defaultdict(list)

    with open(IBM_FILE_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            if idx >= MAX_SCAN_ROWS:
                break
            is_l = int(row.get("Is Laundering", row.get("Is_Laundering", 0)) or 0)
            amount = float(row.get("Amount Paid", 0) or 0)
            fmt = row.get("Payment Format", "")
            from_bank = str(row.get("From Bank", "") or "")
            to_account = row.get("To Account", "")

            if is_l == 0:
                if len(buckets["clean"]) < 25:
                    buckets["clean"].append(row_to_rec(row, "clean", 0))
                continue

            rec = row_to_rec(row, "laundering_other", 1)
            by_dest[to_account].append(rec)

            if 9500 <= amount <= 9900 and len(buckets["structuring"]) < 5:
                rec["pattern"] = "structuring"
                buckets["structuring"].append(attach_structuring_history(rec))
            elif fmt == "ACH" and len(buckets["ach_pattern"]) < 5:
                rec["pattern"] = "ach_pattern"
                buckets["ach_pattern"].append(rec)
            elif amount >= 100000 and len(buckets["high_value"]) < 5:
                rec["pattern"] = "high_value"
                buckets["high_value"].append(rec)
            elif from_bank[:1] in ("3", "4", "7") and len(buckets["high_risk_geo"]) < 5:
                rec["pattern"] = "high_risk_geo"
                buckets["high_risk_geo"].append(rec)
            else:
                buckets["laundering_other"].append(rec)

            if (
                len(buckets["structuring"]) >= 5
                and len(buckets["ach_pattern"]) >= 5
                and len(buckets["high_value"]) >= 5
                and len(buckets["high_risk_geo"]) >= 5
                and len(buckets["clean"]) >= 25
            ):
                # still need fan-in groups; keep scanning a bit more
                if any(len(v) >= 5 for v in by_dest.values()) or idx > 50000:
                    break

    fan_in = []
    for dest, recs in by_dest.items():
        if len(recs) >= 5 and len(fan_in) < 5:
            pick = recs[0]
            pick["pattern"] = "fan_in"
            siblings = [r["from_account"] for r in recs if r["from_account"] != pick["from_account"]]
            fan_in.append(attach_fan_in_history(pick, siblings or [pick["from_account"]]))
    buckets["fan_in"] = fan_in[:5]

    def fill(name, n):
        while len(buckets[name]) < n and buckets["laundering_other"]:
            rec = buckets["laundering_other"].pop(0)
            rec["pattern"] = name
            if name == "structuring":
                rec = attach_structuring_history(rec)
            elif name == "fan_in":
                rec = attach_fan_in_history(rec, [rec["from_account"]])
            buckets[name].append(rec)

    for name, n in [
        ("structuring", 5),
        ("fan_in", 5),
        ("high_risk_geo", 5),
        ("high_value", 5),
        ("ach_pattern", 5),
    ]:
        fill(name, n)

    selected = (
        buckets["structuring"][:5]
        + buckets["fan_in"][:5]
        + buckets["high_risk_geo"][:5]
        + buckets["high_value"][:5]
        + buckets["ach_pattern"][:5]
        + buckets["clean"][:25]
    )

    if len(selected) < 50:
        print("   IBM file did not yield a full 50-row mix — filling with synthetics.")
        selected.extend(generate_synthetic_records()[: 50 - len(selected)])

    random.shuffle(selected)
    return selected[:50]


def generate_synthetic_records():
    """Fallback: generate 50 synthetic records if IBM file missing."""
    records = []
    records += [
        attach_structuring_history({
            "from_account": f"8ABC{i}",
            "to_account": f"1XYZ{i}",
            "amount": 9500 - i * 50,
            "currency": "USD",
            "fmt": "ACH",
            "from_bank": "0",
            "to_bank": "1",
            "is_laundering": 1,
            "label": "LAUNDERING",
            "pattern": "structuring",
        })
        for i in range(5)
    ]
    records += [
        {
            "from_account": f"2DEF{i}",
            "to_account": f"4GHI{i}",
            "amount": 50000,
            "currency": "USD",
            "fmt": "Wire",
            "from_bank": "3",
            "to_bank": "4",
            "is_laundering": 1,
            "label": "LAUNDERING",
            "pattern": "high_risk_geo",
        }
        for i in range(5)
    ]
    records += [
        {
            "from_account": f"5JKL{i}",
            "to_account": f"7MNO{i}",
            "amount": 500000,
            "currency": "USD",
            "fmt": "Bitcoin",
            "from_bank": "0",
            "to_bank": "8",
            "is_laundering": 1,
            "label": "LAUNDERING",
            "pattern": "high_value",
        }
        for i in range(5)
    ]
    records += [
        {
            "from_account": f"0PQR{i}",
            "to_account": f"1STU{i}",
            "amount": 12000,
            "currency": "USD",
            "fmt": "ACH",
            "from_bank": "0",
            "to_bank": "1",
            "is_laundering": 1,
            "label": "LAUNDERING",
            "pattern": "ach_pattern",
        }
        for i in range(5)
    ]
    records += [
        attach_fan_in_history(
            {
                "from_account": f"6VWX{i}",
                "to_account": "8CONCENTRATOR",
                "amount": 8000,
                "currency": "USD",
                "fmt": "Wire",
                "from_bank": str(i),
                "to_bank": "0",
                "is_laundering": 1,
                "label": "LAUNDERING",
                "pattern": "fan_in",
            },
            [f"6VWX{j}" for j in range(6)],
        )
        for i in range(5)
    ]
    records += [
        {
            "from_account": f"CLEAN{i:04d}",
            "to_account": f"RECV{i:04d}",
            "amount": 500,
            "currency": "USD",
            "fmt": "ACH",
            "from_bank": "0",
            "to_bank": "0",
            "is_laundering": 0,
            "label": "CLEAN",
            "pattern": "clean",
        }
        for i in range(25)
    ]
    random.shuffle(records)
    return records


def run_demo():
    print("\n" + "=" * 60)
    print("   ScoreSentinel — IBM AML Demo Loader")
    print("   Loading 50 curated transactions (25 laundering + 25 clean)")
    print("=" * 60 + "\n")

    if not API_KEY:
        print("ERROR: DEMO_API_KEY is not set. Export it or add it to .env")
        return

    records = load_demo_records()
    tp = fp = fn = tn = 0

    for rec in records:
        crs, alert = score_row(rec)
        is_l = rec.get("is_laundering", 0)

        is_tp = alert and is_l == 1
        is_fp = alert and is_l == 0
        is_fn = (not alert) and is_l == 1
        is_tn = (not alert) and is_l == 0

        if is_tp:
            tp += 1
        if is_fp:
            fp += 1
        if is_fn:
            fn += 1
        if is_tn:
            tn += 1

        crs_str = f"{crs:.0f}" if isinstance(crs, (int, float)) else "N/A"
        icon = "!" if alert else "+"
        status = "ALERT!" if alert else "No alert"
        kind = "ALERT" if alert else "CLEAN"

        print(
            f"  {icon} {kind:<5} | CRS: {crs_str:>3} | {status:<9} | "
            f"Account: {rec['from_account']}"
        )

        time.sleep(DELAY_SECONDS)

    precision = (tp / (tp + fp) * 100) if (tp + fp) else 0
    recall = (tp / (tp + fn) * 100) if (tp + fn) else 0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0

    print(f"\n{'-' * 60}")
    print("  DEMO SUMMARY")
    print(f"  Precision : {precision:.1f}%  |  Recall: {recall:.1f}%  |  F1: {f1:.1f}%")
    print(f"  TP: {tp}  FP: {fp}  FN: {fn}  TN: {tn}")
    print(f"{'-' * 60}\n")

    print("  Opening dashboard...")
    webbrowser.open(DASHBOARD_URL)
    print(f"  Dashboard: {DASHBOARD_URL}\n")


if __name__ == "__main__":
    run_demo()
