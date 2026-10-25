"""
ScoreSentinel — IBM AML Dataset Ingestion Script
Converts IBM HI-Small_Trans.csv into ScoreSentinel API calls
and prints full precision / recall / F1 scoring summary.

Authored by Atul Krishnan, CAMS | Day 28+ of 60
"""

import os
import csv
import time
import requests

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    pass

# ============================================================
# CONFIG — edit these before running
# ============================================================
IBM_FILE_PATH = "C:/Users/Roots and Arrow/AML_Data/HI-Small_Trans.csv"
API_BASE_URL = os.environ.get("API_BASE_URL", "https://scoresentinel-api.onrender.com")
API_KEY = os.environ.get("DEMO_API_KEY")
BATCH_SIZE = 100
MAX_RECORDS = 1000
INCLUDE_LAUNDERING_ONLY = False
LAUNDERING_SAMPLE_RATE = 0.5
DELAY_BETWEEN_CALLS = 0.0
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "ibm_ingestion_results.csv")
# ============================================================

PAYMENT_FORMAT_MAP = {
    "Cheque": "CHEQUE",
    "ACH": "ACH",
    "Wire": "WIRE_TRANSFER",
    "Credit Card": "CARD_PAYMENT",
    "Bitcoin": "CRYPTO",
    "Reinvestment": "REINVESTMENT",
}

BANK_COUNTRY_MAP = {
    "0": "US", "1": "GB", "2": "DE", "3": "CN",
    "4": "AE", "5": "SG", "6": "IN", "7": "HK", "8": "JP",
}


def map_payment_format(fmt):
    return PAYMENT_FORMAT_MAP.get(fmt, "OTHER")


def map_bank_to_country(bank_code):
    if not bank_code:
        return "US"
    return BANK_COUNTRY_MAP.get(str(bank_code)[0], "US")


def map_customer_type(account):
    return "CORPORATE" if str(account).startswith("8") else "INDIVIDUAL"


def ibm_customer_id(from_account):
    """Prefix required so DELETE /api/demo/reset can wipe demo rows."""
    account = str(from_account)
    return account if account.startswith("IBM-") else f"IBM-{account}"


SCORE_URL = f"{API_BASE_URL.rstrip('/')}/api/score"
HEADERS = {
    "Content-Type": "application/json",
    "X-DEMO-API-KEY": API_KEY or "",
}


def score_transaction(row):
    """Build payload from IBM row and call POST /api/score."""
    try:
        from_account = row.get("from_account", "UNKNOWN")
        amount = float(row.get("amount_paid", 0) or 0)
        currency = row.get("payment_currency", "USD") or "USD"
        fmt = row.get("payment_format", "")
        from_bank = row.get("from_bank", "")
        to_bank = row.get("to_bank", "")
        customer_id = ibm_customer_id(from_account)

        payload = {
            "customer_id": customer_id,
            "account_id": from_account,
            "transaction_amount": amount,
            "transaction_currency": currency[:3],
            "transaction_type": map_payment_format(fmt),
            "sender_country": map_bank_to_country(from_bank),
            "receiver_country": map_bank_to_country(to_bank),
            "customer": {
                "customer_id": customer_id,
                "customer_type": map_customer_type(from_account),
                "full_name": f"IBM-{from_account}",
            },
        }

        resp = requests.post(SCORE_URL, json=payload, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        print(f"    WARN API {resp.status_code}: {resp.text[:120]}")
        return None
    except Exception as e:
        print(f"    ERROR scoring row: {e}")
        return None


def read_ibm_csv_rows(filepath):
    """
    Safely reads IBM HI-Small_Trans.csv where header has duplicate 'Account' names:
    Index 0: Timestamp
    Index 1: From Bank
    Index 2: From Account
    Index 3: To Bank
    Index 4: To Account
    Index 5: Amount Received
    Index 6: Receiving Currency
    Index 7: Amount Paid
    Index 8: Payment Currency
    Index 9: Payment Format
    Index 10: Is Laundering
    """
    rows = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for idx, r in enumerate(reader, 1):
            if not r or len(r) < 11:
                continue
            rows.append({
                "row_number": idx,
                "timestamp": r[0],
                "from_bank": r[1],
                "from_account": r[2],
                "to_bank": r[3],
                "to_account": r[4],
                "amount_received": r[5],
                "receiving_currency": r[6],
                "amount_paid": r[7],
                "payment_currency": r[8],
                "payment_format": r[9],
                "is_laundering": int(r[10]) if r[10].isdigit() else 0
            })
    return rows


def run_ingestion():
    print(f"\n{'=' * 60}")
    print("  ScoreSentinel — IBM AML Ingestion")
    print(f"  File  : {IBM_FILE_PATH}")
    print(f"  Target: {API_BASE_URL}")
    print(f"{'=' * 60}\n")

    if not API_KEY:
        print("ERROR: DEMO_API_KEY is not set. Export it or add it to .env")
        return

    if not os.path.exists(IBM_FILE_PATH):
        print(f"ERROR: IBM data file not found at:\n  {IBM_FILE_PATH}")
        print("Please download HI-Small_Trans.csv and place it at that path.")
        return

    results = []
    tp = fp = fn = tn = 0
    alerts_generated = 0
    actual_laundering = 0
    processed = 0

    all_rows = read_ibm_csv_rows(IBM_FILE_PATH)
    laundering_rows = [r for r in all_rows if r["is_laundering"] == 1]
    clean_rows = [r for r in all_rows if r["is_laundering"] == 0]

    if INCLUDE_LAUNDERING_ONLY:
        selected = laundering_rows[:MAX_RECORDS]
    else:
        target_l = int(MAX_RECORDS * LAUNDERING_SAMPLE_RATE)
        target_c = MAX_RECORDS - target_l
        selected = laundering_rows[:target_l] + clean_rows[:target_c]
        selected.sort(key=lambda item: item["row_number"])

    for processed, row in enumerate(selected, 1):
        row_num = row["row_number"]
        is_laundering = row["is_laundering"]
        if processed == 1 or (processed - 1) % BATCH_SIZE == 0:
            batch_no = ((processed - 1) // BATCH_SIZE) + 1
            print(f"  -- Batch {batch_no} ({BATCH_SIZE} records) --")

        if is_laundering == 1:
            actual_laundering += 1

        api_response = score_transaction(row)

        crs_score = None
        alert = False
        transaction_id = ""

        if api_response:
            crs_score = api_response.get("overall_crs")
            if crs_score is None:
                crs_score = api_response.get("crs")
            alert = bool(api_response.get("alert", False))
            transaction_id = api_response.get("transaction_id", "")

        if alert:
            alerts_generated += 1

        is_tp = alert and is_laundering == 1
        is_fp = alert and is_laundering == 0
        is_fn = (not alert) and is_laundering == 1
        is_tn = (not alert) and is_laundering == 0

        if is_tp:
            tp += 1
        if is_fp:
            fp += 1
        if is_fn:
            fn += 1
        if is_tn:
            tn += 1

        from_account = row.get("from_account", "?")
        alert_str = "ALERT!" if alert else "No alert"
        crs_str = f"{crs_score:.1f}" if isinstance(crs_score, (int, float)) else "N/A"
        print(f"  [{processed:>4}] {from_account:<14} | CRS: {crs_str:>6} | {alert_str:<10} | Laundering: {is_laundering}")
        if transaction_id:
            print(f"         txn={transaction_id}")

        results.append({
            "row_number": row_num,
            "from_account": row.get("from_account", ""),
            "to_account": row.get("to_account", ""),
            "amount": row.get("amount_paid", ""),
            "currency": row.get("payment_currency", ""),
            "payment_format": row.get("payment_format", ""),
            "sender_country": map_bank_to_country(row.get("from_bank", "")),
            "receiver_country": map_bank_to_country(row.get("to_bank", "")),
            "crs_score": crs_score,
            "alert_generated": alert,
            "is_laundering_actual": is_laundering,
            "true_positive": int(is_tp),
            "false_positive": int(is_fp),
            "false_negative": int(is_fn),
        })

        if DELAY_BETWEEN_CALLS > 0:
            time.sleep(DELAY_BETWEEN_CALLS)

    total = processed
    alert_rate = (alerts_generated / total * 100) if total else 0
    precision = (tp / (tp + fp) * 100) if (tp + fp) else 0
    recall = (tp / (tp + fn) * 100) if (tp + fn) else 0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0

    print(f"\n{'=' * 46}")
    print("  === IBM INGESTION SUMMARY ===")
    print(f"  Total processed:        {total}")
    print(f"  Alerts generated:       {alerts_generated} ({alert_rate:.1f}%)")
    print(f"  Actual laundering:      {actual_laundering}")
    print(f"  True positives:         {tp} (alerts where Is_Laundering=1)")
    print(f"  False positives:        {fp} (alerts where Is_Laundering=0)")
    print(f"  False negatives:        {fn} (no alert where Is_Laundering=1)")
    print(f"  True negatives:         {tn} (no alert where Is_Laundering=0)")
    print(f"  Precision:              {precision:.1f}% (TP / TP+FP)")
    print(f"  Recall:                 {recall:.1f}% (TP / TP+FN)")
    print(f"  F1 Score:               {f1:.1f}%")
    print("  ==============================")
    print(f"{'=' * 46}\n")

    if results:
        fieldnames = [
            "row_number", "from_account", "to_account",
            "amount", "currency", "payment_format",
            "sender_country", "receiver_country",
            "crs_score", "alert_generated",
            "is_laundering_actual", "true_positive",
            "false_positive", "false_negative",
        ]
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"  Results saved to: {OUTPUT_CSV}")


if __name__ == "__main__":
    run_ingestion()
