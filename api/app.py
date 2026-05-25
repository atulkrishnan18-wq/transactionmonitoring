"""
ScoreSentinel Flask API (v1.0)
Part of the ScoreSentinel AML Transaction Risk Scoring Engine
Authored by Atul Krishnan, CAMS | Day 27 of 60
"""

import os
import random
import datetime
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify
from flask_cors import CORS
from scoring_engine import ScoreSentinelEngine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
engine = ScoreSentinelEngine()

# Database connection configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
DEMO_API_KEY = os.environ.get('DEMO_API_KEY')

if not DEMO_API_KEY:
    raise RuntimeError("CRITICAL ERROR: DEMO_API_KEY environment variable is not set.")

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    # Handle sslmode for cloud environments (Supabase/Render)
    if "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor, sslmode='require')
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@app.before_request
def check_auth():
    if request.method in ['POST', 'PUT']:
        key = request.headers.get('X-DEMO-API-KEY')
        if key != DEMO_API_KEY:
            return jsonify({"error": "Unauthorized", "message": "Demo API Key required."}), 401

def generate_id(prefix):
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d-%H%M%S")
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(4)])
    return f"{prefix}-{date_str}-{random_digits}"

def get_risk_band(crs):
    if crs is None: return "AUTO_ALERT"
    if crs < 20: return "LOW_RISK"
    if crs < 40: return "MEDIUM_LOW"
    if crs < 60: return "MEDIUM_HIGH"
    return "HIGH_RISK"

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "engine": "1.0"})

@app.route('/api/score', methods=['POST'])
def score_transaction():
    data = request.get_json()

    # Validation
    tx_amount = data.get("transaction_amount")
    if tx_amount is None or not isinstance(tx_amount, (int, float)) or tx_amount < 0:
        return jsonify({"error": "Validation failed", "message": "transaction_amount invalid"}), 400

    tx_currency = data.get("transaction_currency")
    if not tx_currency or len(tx_currency) != 3:
        return jsonify({"error": "Validation failed", "message": "transaction_currency invalid"}), 400

    sender_country = data.get("sender_country")
    receiver_country = data.get("receiver_country")
    if not sender_country or len(sender_country) != 2 or not receiver_country or len(receiver_country) != 2:
        return jsonify({"error": "Validation failed", "message": "country codes invalid"}), 400

    customer_id = data.get("customer_id", "UNKNOWN_CUST")
    account_id = data.get("account_id", "DEFAULT_ACC")
    customer_data = data.get("customer", {"customer_type": "INDIVIDUAL"})
    history_data = data.get("history", [])
    
    engine_input = {
        "customer": customer_data,
        "transaction": {
            "transaction_type": data.get("transaction_type", "Wire"),
            "amount": tx_amount,
            "sender_country": sender_country,
            "receiver_country": receiver_country,
            "account_id": account_id,
            "date": datetime.datetime.now()
        },
        "history": history_data
    }
    
    result = engine.score_transaction(engine_input)
    transaction_id = generate_id("TXN")
    timestamp = datetime.datetime.now()
    crs = result.get("crs")
    mcs = result.get("mcs")
    alert_generated = result.get("alert", False)
    mule_alert = result.get("mule_alert", False)
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO customers (customer_id, full_name, customer_type, ccrs, risk_band, country_of_domicile)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (customer_id) DO UPDATE SET last_reviewed = NOW()
        """, (customer_id, customer_data.get("full_name", f"Customer {customer_id}"), customer_data.get("customer_type"), 0, "LOW", sender_country))

        cur.execute("""
            INSERT INTO transactions (transaction_id, customer_id, timestamp_processed, transaction_amount, transaction_currency, 
            transaction_type, sender_country, receiver_country, crs, risk_band, rules_fired, alert_generated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (transaction_id, customer_id, timestamp, tx_amount, tx_currency, data.get("transaction_type"), sender_country, receiver_country, crs, get_risk_band(crs), result.get("rules_fired", []), alert_generated))
        
        if mule_alert:
            cluster_id = generate_id("CLT")
            cur.execute("INSERT INTO mule_clusters (cluster_id, cluster_type, mcs, risk_band, account_ids) VALUES (%s, %s, %s, %s, %s)",
                       (cluster_id, result.get("cluster_type"), mcs, result.get("mcs_risk_band"), [account_id]))

        if alert_generated:
            alert_id = generate_id("ALT")
            atype = "SCREENING_MATCH" if result.get("alert_type") in ["Customer Auto-Alert", "Geography Auto-Alert"] else "TRANSACTION_RISK"
            cur.execute("INSERT INTO alerts (alert_id, transaction_id, customer_id, alert_type, stage, status) VALUES (%s, %s, %s, %s, %s, %s)",
                       (alert_id, transaction_id, customer_id, atype, "PENDING_ASSESSMENT", "PENDING"))
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()
        
    return jsonify({"transaction_id": transaction_id, "crs": crs, "alert": alert_generated})

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT a.*, c.full_name as customer_name, t.crs 
            FROM alerts a
            LEFT JOIN customers c ON a.customer_id = c.customer_id
            LEFT JOIN transactions t ON a.transaction_id = t.transaction_id
            ORDER BY a.created_at DESC
        """)
        rows = cur.fetchall()
        alerts = []
        for row in rows:
            alerts.append({
                "alert_id": row["alert_id"],
                "transaction_id": row["transaction_id"],
                "customer_name": row["customer_name"] or "Unknown",
                "alert_type": row["alert_type"],
                "stage": row["stage"],
                "status": row["status"],
                "crs": float(row["crs"]) if row["crs"] is not None else "AUTO",
                "created_at": row["created_at"].isoformat()
            })
        return jsonify({"alerts": alerts, "total": len(alerts)})
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/alerts/<alert_id>', methods=['GET'])
def get_alert_detail(alert_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM alerts WHERE alert_id = %s", (alert_id,))
        alert = cur.fetchone()
        if not alert: return jsonify({"error": "Not found"}), 404
        cur.execute("SELECT * FROM transactions WHERE transaction_id = %s", (alert["transaction_id"],))
        tx = cur.fetchone()
        cur.execute("SELECT * FROM customers WHERE customer_id = %s", (alert["customer_id"],))
        cust = cur.fetchone()
        return jsonify({
            "alert": {**alert, "customer_name": cust["full_name"] if cust else "Unknown"},
            "transaction": {
                "amount": float(tx["transaction_amount"]) if tx else 0,
                "crs": float(tx["crs"]) if tx and tx["crs"] is not None else None,
                "modules": {"customer": float(tx["customer_normalised"]) if tx else 0, "structuring": float(tx["structuring_normalised"]) if tx else 0, "geo": float(tx["geography_normalised"]) if tx else 0, "transaction": float(tx["transaction_normalised"]) if tx else 0},
                "rules_fired": tx["rules_fired"] if tx else []
            }
        })
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/clusters', methods=['GET'])
def get_clusters():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM mule_clusters ORDER BY detected_at DESC")
        rows = cur.fetchall()
        clusters = []
        for row in rows:
            clusters.append({
                "cluster_id": row["cluster_id"],
                "detected_at": row["detected_at"].isoformat(),
                "mcs": float(row["mcs"]),
                "risk_band": row["risk_band"],
                "account_ids": row["account_ids"],
                "status": row["status"]
            })
        return jsonify({"clusters": clusters, "total": len(clusters)})
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/alerts/<alert_id>', methods=['PUT'])
def update_alert(alert_id):
    data = request.get_json()
    disposition = data.get("disposition")
    stage = data.get("stage")
    rationale = data.get("reviewer_rationale")
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT alert_type FROM alerts WHERE alert_id = %s", (alert_id,))
        alert = cur.fetchone()
        if not alert: return jsonify({"error": "Not found"}), 404
        
        if disposition in ["FALSE_POSITIVE", "CLEARED"]:
            if alert["alert_type"] == "SCREENING_MATCH":
                if not all([data.get("point_1_identifier"), data.get("point_1_source"), data.get("point_2_identifier"), data.get("point_2_source"), data.get("point_3_identifier"), data.get("point_3_source")]):
                    return jsonify({"error": "Three-point standard required for screening match"}), 400
            elif not rationale:
                return jsonify({"error": "Reviewer rationale mandatory for transaction risk"}), 400
            
        cur.execute("""
            UPDATE alerts SET status = %s, disposition = %s, reviewer_id = %s, review_timestamp = NOW(), reviewer_rationale = %s, stage = %s,
            point_1_identifier = %s, point_1_source = %s, point_2_identifier = %s, point_2_source = %s, point_3_identifier = %s, point_3_source = %s,
            three_point_met = %s, updated_at = NOW()
            WHERE alert_id = %s
        """, ("RESOLVED" if stage == "RESOLVED" else "PENDING", disposition, data.get("reviewer_id", "ANALYST_01"), rationale, stage,
              data.get("point_1_identifier"), data.get("point_1_source"), data.get("point_2_identifier"), data.get("point_2_source"), data.get("point_3_identifier"), data.get("point_3_source"),
              True if data.get("point_1_identifier") else False, alert_id))
        conn.commit()
        return jsonify({"status": "updated"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    app.run(debug=False, host=host, port=port)
