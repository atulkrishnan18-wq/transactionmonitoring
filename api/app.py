"""
ScoreSentinel Flask API (v1.0)
Part of the ScoreSentinel AML Transaction Risk Scoring Engine
Authored by Atul Krishnan, CAMS | Day 27 of 60
"""

import os
import random
import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify
from scoring_engine import ScoreSentinelEngine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
engine = ScoreSentinelEngine()

# Database connection configuration
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def generate_id(prefix):
    """Generates a formatted ID: PREFIX-YYYYMMDD-RANDOM4"""
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(4)])
    return f"{prefix}-{date_str}-{random_digits}"

def get_risk_band(crs):
    """Determines the risk band based on the CRS."""
    if crs is None:
        return "AUTO_ALERT"
    if crs < 20:
        return "LOW_RISK"
    if crs < 40:
        return "MEDIUM_LOW"
    if crs < 60:
        return "MEDIUM_HIGH"
    return "HIGH_RISK"

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "engine": "1.0"})

@app.route('/api/score', methods=['POST'])
def score_transaction():
    """
    POST /api/score
    Receives a transaction, calls the scoring engine, stores result, returns score.
    """
    data = request.get_json()
    
    # Extract data for engine
    customer_id = data.get("customer_id", "UNKNOWN_CUST")
    account_id = data.get("account_id", "DEFAULT_ACC")
    tx_amount = data.get("transaction_amount", 0.0)
    tx_currency = data.get("transaction_currency", "USD")
    tx_type = data.get("transaction_type", "OTHER")
    sender_country = data.get("sender_country", "GB")
    receiver_country = data.get("receiver_country", "GB")
    
    # Robustness: Ensure customer object exists and has a type
    customer_data = data.get("customer", {})
    if not customer_data.get("customer_type"):
        customer_data["customer_type"] = "INDIVIDUAL"
        
    # Robustness: Ensure history items have dates
    history_data = data.get("history", [])
    for item in history_data:
        if "date" not in item:
            item["date"] = datetime.datetime.now().isoformat()
    
    # Engine requires "transaction" and "customer" keys
    engine_input = {
        "customer": customer_data,
        "transaction": {
            "transaction_type": tx_type,
            "amount": tx_amount,
            "sender_country": sender_country,
            "receiver_country": receiver_country,
            "account_id": account_id, # Pass account_id
            "date": datetime.datetime.now() # Add date for structuring module
        },
        "history": history_data # Optional history for velocity rules
    }
    
    # Call scoring engine
    result = engine.score_transaction(engine_input)
    
    # Generate IDs
    transaction_id = generate_id("TXN")
    timestamp = datetime.datetime.now()
    crs = result.get("crs")
    risk_band = get_risk_band(crs)
    alert_generated = result.get("alert", False)
    
    # Database Persistence
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Step 1: Upsert Customer Record
        cur.execute("""
            INSERT INTO customers (
                customer_id, full_name, customer_type, ccrs, risk_band, country_of_domicile
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (customer_id) DO UPDATE SET
                customer_type = EXCLUDED.customer_type,
                ccrs = EXCLUDED.ccrs,
                risk_band = EXCLUDED.risk_band,
                country_of_domicile = EXCLUDED.country_of_domicile,
                last_reviewed = NOW()
        """, (
            customer_id, 
            customer_data.get("full_name", f"Customer {customer_id}"),
            customer_data.get("customer_type"),
            result.get("module_scores", {}).get("customer", {}).get("raw", 0),
            get_risk_band(result.get("module_scores", {}).get("customer", {}).get("raw", 0)),
            sender_country
        ))

        # Step 2: Insert into transactions table
        cur.execute("""
            INSERT INTO transactions (
                transaction_id, customer_id, timestamp_processed, 
                transaction_amount, transaction_currency, transaction_type,
                sender_country, receiver_country, customer_type,
                customer_risk_raw, structuring_raw, geography_raw, transaction_type_raw,
                customer_normalised, structuring_normalised, geography_normalised, transaction_normalised,
                crs, risk_band, rules_fired, alert_generated, alert_type, auto_alert_trigger
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            transaction_id, customer_id, timestamp,
            tx_amount, tx_currency, tx_type,
            sender_country, receiver_country, customer_data.get("customer_type"),
            result.get("module_scores", {}).get("customer", {}).get("raw", 0),
            result.get("module_scores", {}).get("structuring", {}).get("raw", 0),
            result.get("module_scores", {}).get("geo", {}).get("raw", 0),
            result.get("module_scores", {}).get("transaction_type", {}).get("raw", 0),
            result.get("module_scores", {}).get("customer", {}).get("normalised", 0),
            result.get("module_scores", {}).get("structuring", {}).get("normalised", 0),
            result.get("module_scores", {}).get("geo", {}).get("normalised", 0),
            result.get("module_scores", {}).get("transaction_type", {}).get("normalised", 0),
            crs, risk_band, 
            result.get("rules_fired", []),
            alert_generated,
            result.get("alert_type", "AML_RISK" if crs and crs >= 60 else None),
            result.get("trigger")
        ))
        
        # If alert generated, insert into alerts table
        alert_id = None
        if alert_generated:
            alert_id = generate_id("ALT")
            cur.execute("""
                INSERT INTO alerts (
                    alert_id, transaction_id, customer_id, alert_type, stage, status
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                alert_id, transaction_id, customer_id, 
                result.get("alert_type", "AML_RISK"),
                "PENDING_ASSESSMENT", "PENDING"
            ))
            
        conn.commit()
    except Exception as e:
        import traceback
        traceback.print_exc()
        conn.rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()
        
    # Prepare Response
    response = {
        "transaction_id": transaction_id,
        "crs": crs,
        "risk_band": risk_band,
        "alert": alert_generated,
        "alert_id": alert_id,
        "alert_type": result.get("alert_type", "AML_RISK" if crs and crs >= 60 else None),
        "rules_fired": result.get("rules_fired", []),
        "timestamp": timestamp.isoformat()
    }
    
    if "trigger" in result:
        response["trigger"] = result["trigger"]
        
    return jsonify(response)

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """
    GET /api/transactions
    Returns transaction history. Supports ?customer_id filter.
    """
    customer_id = request.args.get('customer_id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        if customer_id:
            cur.execute("SELECT * FROM transactions WHERE customer_id = %s ORDER BY timestamp_processed DESC", (customer_id,))
        else:
            cur.execute("SELECT * FROM transactions ORDER BY timestamp_processed DESC")
            
        rows = cur.fetchall()
        
        transactions = []
        for row in rows:
            transactions.append({
                "transaction_id": row["transaction_id"],
                "customer_id": row["customer_id"],
                "crs": float(row["crs"]) if row["crs"] is not None else None,
                "risk_band": row["risk_band"],
                "alert_generated": row["alert_generated"],
                "alert_type": row["alert_type"],
                "timestamp": row["timestamp_processed"].isoformat()
            })
            
        return jsonify({
            "transactions": transactions,
            "total": len(transactions)
        })
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/alerts/<alert_id>', methods=['PUT'])
def update_alert(alert_id):
    """
    PUT /api/alerts/<alert_id>
    Updates an alert disposition. Enforces the three-point standard.
    """
    data = request.get_json()
    disposition = data.get("disposition")
    stage = data.get("stage")
    reviewer_id = data.get("reviewer_id")
    rationale = data.get("reviewer_rationale")
    
    # Extract identifiers
    p1_id = data.get("point_1_identifier")
    p1_src = data.get("point_1_source")
    p2_id = data.get("point_2_identifier")
    p2_src = data.get("point_2_source")
    p3_id = data.get("point_3_identifier")
    p3_src = data.get("point_3_source")
    
    # VALIDATION RULE: Three-point standard
    if disposition in ["FALSE_POSITIVE", "CLEARED"]:
        if not all([p1_id, p1_src, p2_id, p2_src, p3_id, p3_src]):
            return jsonify({
                "error": "Three-point standard not met",
                "message": "point_1_identifier, point_1_source, point_2_identifier, point_2_source, point_3_identifier, point_3_source are all required for this disposition"
            }), 400
            
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Verify alert exists
        cur.execute("SELECT * FROM alerts WHERE alert_id = %s", (alert_id,))
        if cur.fetchone() is None:
            return jsonify({"error": "Not found", "message": f"Alert {alert_id} not found"}), 404
            
        # Update alert
        cur.execute("""
            UPDATE alerts SET 
                status = %s,
                disposition = %s,
                reviewer_id = %s,
                review_timestamp = NOW(),
                reviewer_rationale = %s,
                stage = %s,
                point_1_identifier = %s,
                point_1_source = %s,
                point_2_identifier = %s,
                point_2_source = %s,
                point_3_identifier = %s,
                point_3_source = %s,
                three_point_met = %s,
                updated_at = NOW()
            WHERE alert_id = %s
        """, (
            "RESOLVED" if stage == "RESOLVED" else "PENDING",
            disposition,
            reviewer_id,
            rationale,
            stage,
            p1_id, p1_src, p2_id, p2_src, p3_id, p3_src,
            True if all([p1_id, p1_src, p2_id, p2_src, p3_id, p3_src]) else False,
            alert_id
        ))
        
        conn.commit()
        return jsonify({"status": "updated", "alert_id": alert_id})
    except Exception as e:
        import traceback
        traceback.print_exc()
        conn.rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    # When running locally, ensure PYTHONPATH includes the root directory 
    # to find scoring_engine and the engine/ module.
    app.run(debug=True, host='0.0.0.0', port=5000)
