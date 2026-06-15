"""
ScoreSentinel Flask API (v1.0)
Part of the ScoreSentinel AML Transaction Risk Scoring Engine
Authored by Atul Krishnan, CAMS | Day 27 of 60
"""

import os
import datetime
import json
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from scoring_engine import ScoreSentinelEngine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Open CORS for production (allows Vercel dashboard to connect)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# MEDIUM FIX 2 — Add rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Rate limit exceeded", 
        "message": "Too many requests, please slow down"
    }), 429

engine = ScoreSentinelEngine()

# Database connection configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
DEMO_API_KEY = os.environ.get('DEMO_API_KEY', 'SCORESENTINEL_DEMO_2027')

# MEDIUM FIX 1 — Protect GET endpoints with read-only API key
READ_API_KEY = os.environ.get('READ_API_KEY', 'SCORESENTINEL_READ_2027')

if not DEMO_API_KEY:
    raise RuntimeError("CRITICAL ERROR: DEMO_API_KEY environment variable is not set.")
if not READ_API_KEY:
    raise RuntimeError("CRITICAL ERROR: READ_API_KEY environment variable is not set.")

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    # Handle sslmode for cloud environments (Supabase/Render)
    if "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor, sslmode='require')
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@app.before_request
def check_auth():
    # Exempt GET /api/health from any auth check
    if request.path == '/api/health' and request.method == 'GET':
        return

    if request.method in ['POST', 'PUT']:
        key = request.headers.get('X-DEMO-API-KEY')
        if key != DEMO_API_KEY:
            return jsonify({"error": "Unauthorized", "message": "Demo API Key required for this action."}), 401
    elif request.method == 'GET':
        key = request.headers.get('X-READ-API-KEY')
        if key != READ_API_KEY:
            return jsonify({"error": "Unauthorized", "message": "Read-only API Key required for this action."}), 401

# MEDIUM FIX 3 — Replace random ID suffix with UUID
def generate_id(prefix):
    """Generates a formatted ID: PREFIX-YYYYMMDD-HHMMSS-{first 8 chars of uuid4}"""
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d-%H%M%S")
    uuid_suffix = str(uuid.uuid4())[:8]
    return f"{prefix}-{date_str}-{uuid_suffix}"

def get_risk_band(crs):
    """Determines the risk band based on the CRS."""
    if crs is None: return "AUTO_ALERT"
    if crs < 20: return "LOW_RISK"
    if crs < 40: return "MEDIUM_LOW"
    if crs < 60: return "MEDIUM_HIGH"
    return "HIGH_RISK"

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "engine": "1.0"})

@app.route('/api/score', methods=['POST'])
@limiter.limit("100 per minute")
def score_transaction():
    """
    POST /api/score
    Receives a transaction, calls the scoring engine, stores result, returns score.
    """
    try:
        data = request.get_json()

        # Validation
        tx_amount = data.get("transaction_amount")
        if tx_amount is None or not isinstance(tx_amount, (int, float)) or tx_amount < 0:
            return jsonify({"error": "Validation failed", "message": "transaction_amount invalid"}), 400

        tx_currency = data.get("transaction_currency")
        if not tx_currency or len(tx_currency) != 3:
            return jsonify({"error": "Validation failed", "message": "transaction_currency invalid"}), 400

        tx_type = data.get("transaction_type")
        if not tx_type or not isinstance(tx_type, str) or tx_type.strip() == "":
            return jsonify({"error": "Validation failed", "message": "transaction_type is missing or empty"}), 400

        sender_country = data.get("sender_country")
        if not sender_country or not isinstance(sender_country, str) or len(sender_country) != 2:
            return jsonify({"error": "Validation failed", "message": "sender_country invalid"}), 400

        receiver_country = data.get("receiver_country")
        if not receiver_country or not isinstance(receiver_country, str) or len(receiver_country) != 2:
            return jsonify({"error": "Validation failed", "message": "receiver_country invalid"}), 400

        customer_id = data.get("customer_id", "UNKNOWN_CUST")
        account_id = data.get("account_id", "DEFAULT_ACC")
        
        customer_data = data.get("customer", {})
        if not customer_data.get("customer_type"):
            customer_data["customer_type"] = "INDIVIDUAL"
            
        history_data = data.get("history", [])
        for item in history_data:
            if "date" not in item:
                item["date"] = datetime.datetime.now().isoformat()
        
        engine_input = {
            "customer": customer_data,
            "transaction": {
                "transaction_type": tx_type,
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
            """, (transaction_id, customer_id, timestamp, tx_amount, tx_currency, tx_type, sender_country, receiver_country, crs, get_risk_band(crs), result.get("rules_fired", []), alert_generated))
            
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
            # MEDIUM FIX 4 — Sanitise error responses
            app.logger.error(f"Database error: {str(e)}")
            return jsonify({"error": "Internal server error", "message": "An unexpected error occurred. Please try again."}), 500
        finally:
            cur.close()
            conn.close()
            
        return jsonify({"transaction_id": transaction_id, "crs": crs, "alert": alert_generated})
    except Exception as e:
        app.logger.error(f"Error in score_transaction: {str(e)}")
        return jsonify({"error": "Internal server error", "message": "An unexpected error occurred. Please try again."}), 500

@app.route('/api/alerts', methods=['GET'])
@limiter.limit("200 per minute")
def get_alerts():
    """
    GET /api/alerts
    Returns all alerts. Supports stage filter.
    """
    try:
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
                    "customer_name": row["customer_name"] or "Unknown",
                    "alert_type": row["alert_type"],
                    "stage": row["stage"],
                    "status": row["status"],
                    "crs": float(row["crs"]) if row["crs"] is not None else "AUTO",
                    "created_at": row["created_at"].isoformat()
                })
            return jsonify({"alerts": alerts, "total": len(alerts)})
        except Exception as e:
            app.logger.error(f"Database error in get_alerts: {str(e)}")
            return jsonify({"error": "Internal server error", "message": "An unexpected error occurred. Please try again."}), 500
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        app.logger.error(f"Error in get_alerts: {str(e)}")
        return jsonify({"error": "Internal server error", "message": "An unexpected error occurred. Please try again."}), 500

@app.route('/api/alerts/<alert_id>', methods=['GET'])
@limiter.limit("200 per minute")
def get_alert_detail(alert_id):
    """
    GET /api/alerts/<alert_id>
    Returns full alert detail including transaction scores and three-point standard.
    """
    try:
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
            app.logger.error(f"Database error in get_alert_detail: {str(e)}")
            return jsonify({"error": "Internal server error", "message": "An unexpected error occurred. Please try again."}), 500
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        app.logger.error(f"Error in get_alert_detail: {str(e)}")
        return jsonify({"error": "Internal server error", "message": "An unexpected error occurred. Please try again."}), 500

@app.route('/api/customers/<customer_id>', methods=['GET'])
@limiter.limit("200 per minute")
def get_customer(customer_id):
    """
    GET /api/customers/<customer_id>
    Returns customer profile and transaction history.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
            cust = cur.fetchone()
            if not cust: return jsonify({"error": "Not found"}), 404
                
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
            app.logger.error(f"Database error in get_customer: {str(e)}")
            return jsonify({"error": "Internal server error", "message": "An unexpected error occurred. Please try again."}), 500
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        app.logger.error(f"Error in get_customer: {str(e)}")
        return jsonify({"error": "Internal server error", "message": "An unexpected error occurred. Please try again."}), 500

@app.route('/api/clusters', methods=['GET'])
@limiter.limit("200 per minute")
def get_clusters():
    """
    GET /api/clusters
    Returns detected mule clusters.
    """
    try:
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
            app.logger.error(f"Database error in get_clusters: {str(e)}")
            return jsonify({"error": "Internal server error", "message": "An unexpected error occurred. Please try again."}), 500
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        app.logger.error(f"Error in get_clusters: {str(e)}")
        return jsonify({"error": "Internal server error", "message": "An unexpected error occurred. Please try again."}), 500

@app.route('/api/clusters/<cluster_id>', methods=['PUT'])
@limiter.limit("60 per minute")
def update_cluster(cluster_id):
    """
    PUT /api/clusters/<cluster_id>
    Updates a mule cluster status.
    """
    try:
        data = request.get_json()
        status = data.get("status")
        reviewer_id = data.get("reviewer_id")
        rationale = data.get("reviewer_rationale")
        
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
                    reviewer_rationale = %s
                WHERE cluster_id = %s
            """, (status, reviewer_id, rationale, cluster_id))
            
            conn.commit()
            return jsonify({"status": "updated", "cluster_id": cluster_id})
        except Exception as e:
            conn.rollback()
            app.logger.error(f"Database error in update_cluster: {str(e)}")
            return jsonify({"error": "Internal server error", "message": "An unexpected error occurred. Please try again."}), 500
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        app.logger.error(f"Error in update_cluster: {str(e)}")
        return jsonify({"error": "Internal server error", "message": "An unexpected error occurred. Please try again."}), 500

@app.route('/api/transactions', methods=['GET'])
@limiter.limit("200 per minute")
def get_transactions():
    """
    GET /api/transactions
    Returns transaction history. Supports ?customer_id filter.
    """
    try:
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
                    "timestamp": row["timestamp_processed"].isoformat()
                })
            return jsonify({"transactions": transactions, "total": len(transactions)})
        except Exception as e:
            app.logger.error(f"Database error in get_transactions: {str(e)}")
            return jsonify({"error": "Internal server error", "message": "An unexpected error occurred. Please try again."}), 500
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        app.logger.error(f"Error in get_transactions: {str(e)}")
        return jsonify({"error": "Internal server error", "message": "An unexpected error occurred. Please try again."}), 500

@app.route('/api/alerts/<alert_id>', methods=['PUT'])
@limiter.limit("60 per minute")
def update_alert(alert_id):
    """
    PUT /api/alerts/<alert_id>
    Updates an alert disposition. Enforces compliance standards.
    """
    try:
        data = request.get_json()
        disposition = data.get("disposition")
        stage = data.get("stage")
        rationale = data.get("reviewer_rationale")
        reviewer_id = data.get("reviewer_id")
        
        # Extract identifiers
        p1_id = data.get("point_1_identifier")
        p1_src = data.get("point_1_source")
        p2_id = data.get("point_2_identifier")
        p2_src = data.get("point_2_source")
        p3_id = data.get("point_3_identifier")
        p3_src = data.get("point_3_source")
        
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT alert_type FROM alerts WHERE alert_id = %s", (alert_id,))
            alert = cur.fetchone()
            if alert is None:
                return jsonify({"error": "Not found", "message": f"Alert {alert_id} not found"}), 404
                
            if disposition in ["FALSE_POSITIVE", "CLEARED"]:
                if alert["alert_type"] == "SCREENING_MATCH":
                    if not all([p1_id, p1_src, p2_id, p2_src, p3_id, p3_src]):
                        return jsonify({"error": "Three-point standard required for screening match dispositions"}), 400
                else:
                    if not reviewer_id or not disposition or not rationale or rationale.strip() == "":
                        return jsonify({"error": "Reviewer rationale mandatory for transaction risk dispositions"}), 400
                
            cur.execute("""
                UPDATE alerts SET status = %s, disposition = %s, reviewer_id = %s, review_timestamp = NOW(), reviewer_rationale = %s, stage = %s,
                point_1_identifier = %s, point_1_source = %s, point_2_identifier = %s, point_2_source = %s, point_3_identifier = %s, point_3_source = %s,
                three_point_met = %s, updated_at = NOW()
                WHERE alert_id = %s
            """, ("RESOLVED" if stage == "RESOLVED" else "PENDING", disposition, reviewer_id, rationale, stage,
                  p1_id, p1_src, p2_id, p2_src, p3_id, p3_src,
                  True if p1_id and p2_id and p3_id else False, alert_id))
            conn.commit()
            return jsonify({"status": "updated", "alert_id": alert_id})
        except Exception as e:
            conn.rollback()
            app.logger.error(f"Database error in update_alert: {str(e)}")
            return jsonify({"error": "Internal server error", "message": "An unexpected error occurred. Please try again."}), 500
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        app.logger.error(f"Error in update_alert: {str(e)}")
        return jsonify({"error": "Internal server error", "message": "An unexpected error occurred. Please try again."}), 500

if __name__ == '__main__':
    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    app.run(debug=False, host=host, port=port)
False, host=host, port=port)
