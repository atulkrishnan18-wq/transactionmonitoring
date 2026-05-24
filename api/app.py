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
from psycopg2.pool import ThreadedConnectionPool
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

# CRITICAL FIX 1 — Remove hardcoded API key fallback
if not DEMO_API_KEY:
    raise RuntimeError("CRITICAL ERROR: DEMO_API_KEY environment variable is not set. The app cannot start without a secure key.")

# CRITICAL FIX 3 — Connection Pool initialization
# minconn=2, maxconn=10 as per professional requirements
try:
    # Handle sslmode for cloud environments (Supabase/Render)
    pool_kwargs = {"dsn": DATABASE_URL, "cursor_factory": RealDictCursor}
    if "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL:
        pool_kwargs["sslmode"] = 'require'
    
    db_pool = ThreadedConnectionPool(2, 10, **pool_kwargs)
    print("Database connection pool initialized successfully.")
except Exception as e:
    print(f"Error initializing connection pool: {e}")
    raise RuntimeError("Failed to initialize database connection pool.")

def get_db_connection():
    """Returns a connection from the ThreadedConnectionPool."""
    return db_pool.getconn()

@app.before_request
def check_auth():
    """
    SIMPLE AUTH (Demo Wall)
    Protects all POST/PUT endpoints with a static API Key for the demo.
    Allows GET requests for public dashboard viewing.
    """
    if request.method in ['POST', 'PUT']:
        key = request.headers.get('X-DEMO-API-KEY')
        if key != DEMO_API_KEY:
            return jsonify({"error": "Unauthorized", "message": "Demo API Key required for this action."}), 401

def generate_id(prefix):
    """Generates a formatted ID: PREFIX-YYYYMMDD-HHMMSS-RANDOM4"""
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d-%H%M%S")
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

    # CRITICAL FIX 2 — Add input validation on POST /api/score
    tx_amount = data.get("transaction_amount")
    if tx_amount is None or not isinstance(tx_amount, (int, float)) or tx_amount < 0:
        return jsonify({"error": "Validation failed", "message": "transaction_amount is missing, not a number, or negative"}), 400

    tx_currency = data.get("transaction_currency")
    if not tx_currency or not isinstance(tx_currency, str) or len(tx_currency) != 3:
        return jsonify({"error": "Validation failed", "message": "transaction_currency is missing or not a 3-character string"}), 400

    tx_type = data.get("transaction_type")
    if not tx_type or not isinstance(tx_type, str) or tx_type.strip() == "":
        return jsonify({"error": "Validation failed", "message": "transaction_type is missing or empty"}), 400

    sender_country = data.get("sender_country")
    if not sender_country or not isinstance(sender_country, str) or len(sender_country) != 2:
        return jsonify({"error": "Validation failed", "message": "sender_country is missing or not a 2-character string"}), 400

    receiver_country = data.get("receiver_country")
    if not receiver_country or not isinstance(receiver_country, str) or len(receiver_country) != 2:
        return jsonify({"error": "Validation failed", "message": "receiver_country is missing or not a 2-character string"}), 400
    
    # Extract remaining data for engine
    customer_id = data.get("customer_id", "UNKNOWN_CUST")
    account_id = data.get("account_id", "DEFAULT_ACC")
    
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
    mcs = result.get("mcs")
    risk_band = get_risk_band(crs)
    alert_generated = result.get("alert", False)
    mule_alert = result.get("mule_alert", False)
    
    # Database Persistence
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Step 1: Upsert Customer Record
        cur.execute("""
            INSERT INTO customers (
                customer_id, full_name, customer_type, ccrs, risk_band, country_of_domicile, device_nexus_count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (customer_id) DO UPDATE SET
                customer_type = EXCLUDED.customer_type,
                ccrs = EXCLUDED.ccrs,
                risk_band = EXCLUDED.risk_band,
                country_of_domicile = EXCLUDED.country_of_domicile,
                device_nexus_count = EXCLUDED.device_nexus_count,
                last_reviewed = NOW()
        """, (
            customer_id, 
            customer_data.get("full_name", f"Customer {customer_id}"),
            customer_data.get("customer_type"),
            result.get("module_scores", {}).get("customer", {}).get("raw", 0),
            get_risk_band(result.get("module_scores", {}).get("customer", {}).get("raw", 0)),
            sender_country,
            customer_data.get("device_nexus_count", 0)
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
        
        # Step 3: Insert into mule_clusters if MCS >= 60
        cluster_id = None
        if mule_alert:
            cluster_id = generate_id("CLT")
            # CRITICAL FIX 4 — Misplaced import moved to top
            cur.execute("""
                INSERT INTO mule_clusters (
                    cluster_id, cluster_type, mcs, risk_band, 
                    account_ids, concentrator_id, dimension_scores, rules_fired
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                cluster_id,
                result.get("cluster_type"),
                mcs,
                result.get("mcs_risk_band"),
                [account_id], # Simplified: current account is the focus
                account_id,   # Assuming current account is concentrator for now
                json.dumps(result.get("module_scores", {}).get("mule", {})),
                result.get("rules_fired", [])
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
                result.get("alert_type", "Mule Cluster Alert" if mule_alert else "AML_RISK"),
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
        # CRITICAL FIX 3 — Connection Pool putconn instead of close
        db_pool.putconn(conn)
        
    # Prepare Response
    response = {
        "transaction_id": transaction_id,
        "crs": crs,
        "mcs": mcs,
        "risk_band": risk_band,
        "mcs_risk_band": result.get("mcs_risk_band"),
        "alert": alert_generated,
        "mule_alert": mule_alert,
        "alert_id": alert_id,
        "cluster_id": cluster_id,
        "alert_type": result.get("alert_type"),
        "rules_fired": result.get("rules_fired", []),
        "timestamp": timestamp.isoformat()
    }
    
    if "trigger" in result:
        response["trigger"] = result["trigger"]
        
    return jsonify(response)

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """
    GET /api/alerts
    Returns all alerts. Supports stage filter.
    """
    stage = request.args.get('stage')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        query = """
            SELECT a.*, c.full_name as customer_name, t.crs 
            FROM alerts a
            LEFT JOIN customers c ON a.customer_id = c.customer_id
            LEFT JOIN transactions t ON a.transaction_id = t.transaction_id
        """
        
        if stage:
            cur.execute(query + " WHERE a.stage = %s ORDER BY a.created_at DESC", (stage,))
        else:
            cur.execute(query + " ORDER BY a.created_at DESC")
            
        rows = cur.fetchall()
        
        alerts = []
        for row in rows:
            alerts.append({
                "alert_id": row["alert_id"],
                "transaction_id": row["transaction_id"],
                "customer_id": row["customer_id"],
                "customer_name": row["customer_name"] if row["customer_name"] else "Unknown",
                "alert_type": row["alert_type"],
                "stage": row["stage"],
                "status": row["status"],
                "crs": float(row["crs"]) if row["crs"] is not None else "AUTO",
                "created_at": row["created_at"].isoformat()
            })
            
        return jsonify({
            "alerts": alerts,
            "total": len(alerts)
        })
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        cur.close()
        # CRITICAL FIX 3 — Connection Pool putconn instead of close
        db_pool.putconn(conn)

@app.route('/api/alerts/<alert_id>', methods=['GET'])
def get_alert_detail(alert_id):
    """
    GET /api/alerts/<alert_id>
    Returns full alert detail including transaction scores and three-point standard.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT * FROM alerts WHERE alert_id = %s", (alert_id,))
        alert = cur.fetchone()
        
        if not alert:
            return jsonify({"error": "Not found"}), 404
            
        # Get transaction details
        cur.execute("SELECT * FROM transactions WHERE transaction_id = %s", (alert["transaction_id"],))
        tx = cur.fetchone()
        
        # Get customer details
        cur.execute("SELECT * FROM customers WHERE customer_id = %s", (alert["customer_id"],))
        cust = cur.fetchone()
        
        # Get MCS if it's a mule alert
        mcs = None
        if "Mule" in alert["alert_type"]:
            cur.execute("SELECT mcs FROM mule_clusters WHERE %s = ANY(account_ids) LIMIT 1", (tx["account_id"] if tx and "account_id" in tx else "DEFAULT_ACC",))
            cluster = cur.fetchone()
            if cluster:
                mcs = float(cluster["mcs"])
        
        return jsonify({
            "alert": {
                "alert_id": alert["alert_id"],
                "transaction_id": alert["transaction_id"],
                "customer_id": alert["customer_id"],
                "customer_name": cust["full_name"] if cust else "Unknown",
                "alert_type": alert["alert_type"],
                "stage": alert["stage"],
                "status": alert["status"],
                "client_rp": alert["client_rp"],
                "worldcheck_id": alert["worldcheck_id"],
                "internal_summary": alert["internal_summary"],
                "disposition": alert["disposition"],
                "point_1_identifier": alert["point_1_identifier"],
                "point_1_source": alert["point_1_source"],
                "point_2_identifier": alert["point_2_identifier"],
                "point_2_source": alert["point_2_source"],
                "point_3_identifier": alert["point_3_identifier"],
                "point_3_source": alert["point_3_source"],
                "three_point_met": alert["three_point_met"],
                "reviewer_rationale": alert["reviewer_rationale"]
            },
            "transaction": {
                "amount": float(tx["transaction_amount"]) if tx else 0,
                "currency": tx["transaction_currency"] if tx else "USD",
                "type": tx["transaction_type"] if tx else "UNKNOWN",
                "crs": float(tx["crs"]) if tx and tx["crs"] is not None else None,
                "mcs": mcs,
                "modules": {
                    "customer": float(tx["customer_normalised"]) if tx else 0,
                    "structuring": float(tx["structuring_normalised"]) if tx else 0,
                    "geo": float(tx["geography_normalised"]) if tx else 0,
                    "transaction": float(tx["transaction_normalised"]) if tx else 0
                },
                "rules_fired": tx["rules_fired"] if tx else []
            }
        })
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        cur.close()
        # CRITICAL FIX 3 — Connection Pool putconn instead of close
        db_pool.putconn(conn)

@app.route('/api/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """
    GET /api/customers/<customer_id>
    Returns customer profile and transaction history.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
        cust = cur.fetchone()
        
        if not cust:
            return jsonify({"error": "Not found"}), 404
            
        # Get recent transactions
        cur.execute("SELECT * FROM transactions WHERE customer_id = %s ORDER BY timestamp_processed DESC LIMIT 10", (customer_id,))
        txs = cur.fetchall()
        
        transaction_history = []
        for tx in txs:
            transaction_history.append({
                "transaction_id": tx["transaction_id"],
                "date": tx["timestamp_processed"].isoformat(),
                "amount": float(tx["transaction_amount"]),
                "currency": tx["transaction_currency"],
                "type": tx["transaction_type"],
                "status": tx["disposition_status"]
            })
            
        return jsonify({
            "customer": {
                "customer_id": cust["customer_id"],
                "full_name": cust["full_name"],
                "customer_type": cust["customer_type"],
                "ccrs": cust["ccrs"],
                "risk_band": cust["risk_band"],
                "pep_tier": cust["pep_tier"],
                "country_of_domicile": cust["country_of_domicile"],
                "device_nexus_count": cust["device_nexus_count"],
                "last_reviewed": cust["last_reviewed"].isoformat() if cust["last_reviewed"] else None
            },
            "history": transaction_history
        })
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        cur.close()
        # CRITICAL FIX 3 — Connection Pool putconn instead of close
        db_pool.putconn(conn)

@app.route('/api/clusters', methods=['GET'])
def get_clusters():
    """
    GET /api/clusters
    Returns detected mule clusters.
    """
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
                "cluster_type": row["cluster_type"],
                "mcs": float(row["mcs"]),
                "risk_band": row["risk_band"],
                "account_ids": row["account_ids"],
                "status": row["status"],
                "str_filed": row["str_filed"],
                "str_reference": row["str_reference"]
            })
            
        return jsonify({
            "clusters": clusters,
            "total": len(clusters)
        })
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        cur.close()
        # CRITICAL FIX 3 — Connection Pool putconn instead of close
        db_pool.putconn(conn)

@app.route('/api/clusters/<cluster_id>', methods=['PUT'])
def update_cluster(cluster_id):
    """
    PUT /api/clusters/<cluster_id>
    Updates a mule cluster status and STR filing info.
    """
    data = request.get_json()
    status = data.get("status")
    reviewer_id = data.get("reviewer_id")
    rationale = data.get("reviewer_rationale")
    str_filed = data.get("str_filed", False)
    str_reference = data.get("str_reference")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT * FROM mule_clusters WHERE cluster_id = %s", (cluster_id,))
        if cur.fetchone() is None:
            return jsonify({"error": "Not found", "message": f"Cluster {cluster_id} not found"}), 404
            
        cur.execute("""
            UPDATE mule_clusters SET 
                status = %s,
                reviewer_id = %s,
                review_timestamp = NOW(),
                reviewer_rationale = %s,
                str_filed = %s,
                str_reference = %s
            WHERE cluster_id = %s
        """, (status, reviewer_id, rationale, str_filed, str_reference, cluster_id))
        
        conn.commit()
        return jsonify({"status": "updated", "cluster_id": cluster_id})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        cur.close()
        # CRITICAL FIX 3 — Connection Pool putconn instead of close
        db_pool.putconn(conn)

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
        # CRITICAL FIX 3 — Connection Pool putconn instead of close
        db_pool.putconn(conn)

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
    client_rp = data.get("client_rp")
    worldcheck_id = data.get("worldcheck_id")
    internal_summary = data.get("internal_summary")
    
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
                client_rp = %s,
                worldcheck_id = %s,
                internal_summary = %s,
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
            client_rp,
            worldcheck_id,
            internal_summary,
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
        # CRITICAL FIX 3 — Connection Pool putconn instead of close
        db_pool.putconn(conn)

if __name__ == '__main__':
    # When running locally, ensure PYTHONPATH includes the root directory 
    # to find scoring_engine and the engine/ module.
    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    app.run(debug=debug, host=host, port=port)
