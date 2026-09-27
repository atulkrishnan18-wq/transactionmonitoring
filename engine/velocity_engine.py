import datetime

def calculate_velocity_score(customer_id, current_transaction, db_connection):
    result = {
        "velocity_score": 0,
        "lookback_days": 7,
        "dimensions": {
            "transaction_count": {"value": 0, "score": 0, "threshold_breached": False},
            "total_volume": {"value": 0, "score": 0, "threshold_breached": False},
            "distinct_counterparties": {"value": 0, "score": 0, "threshold_breached": False},
            "structuring_pattern": {"value": 0, "score": 0, "threshold_breached": False}
        },
        "rules_fired": []
    }
    
    if not customer_id or not db_connection:
        return result
        
    try:
        cur = db_connection.cursor()
        
        # We query the last 7 days of transactions for this customer
        # Coalescing receiver_account_id to receiver_country to avoid crashing if schema is old
        query = """
            SELECT transaction_amount, 
                   COALESCE(receiver_account_id, receiver_country) AS counterparty
            FROM transactions 
            WHERE customer_id = %s 
              AND timestamp_processed >= NOW() - INTERVAL '7 days'
        """
        cur.execute(query, (customer_id,))
        rows = cur.fetchall()
        
        if not rows:
            return result
            
        count = len(rows)
        volume = sum(row[0] for row in rows)
        distinct_counterparties = len(set(row[1] for row in rows if row[1]))
        
        structuring_count = 0
        for row in rows:
            amount = row[0]
            # 75-99% of 10000 threshold
            if 7500 <= amount <= 9900:
                structuring_count += 1
                
        # DIMENSION 1 - Transaction count
        count_score = 0
        if count > 20: count_score = 90
        elif count >= 11: count_score = 70
        elif count >= 5: count_score = 40
        
        # DIMENSION 2 - Total volume
        volume_score = 0
        if volume > 100000: volume_score = 90
        elif volume >= 50000: volume_score = 70
        elif volume >= 10000: volume_score = 40
        
        # DIMENSION 3 - Distinct counterparties
        counterparty_score = 0
        if distinct_counterparties > 10: counterparty_score = 90
        elif distinct_counterparties >= 6: counterparty_score = 70
        elif distinct_counterparties >= 3: counterparty_score = 40
        
        # DIMENSION 4 - Structuring pattern
        structuring_score = 0
        if structuring_count > 5: structuring_score = 95
        elif structuring_count >= 4: structuring_score = 85
        elif structuring_count >= 2: structuring_score = 60
        
        # Build dimensions dictionary
        result["dimensions"]["transaction_count"]["value"] = count
        result["dimensions"]["transaction_count"]["score"] = count_score
        
        result["dimensions"]["total_volume"]["value"] = float(volume)
        result["dimensions"]["total_volume"]["score"] = volume_score
        
        result["dimensions"]["distinct_counterparties"]["value"] = distinct_counterparties
        result["dimensions"]["distinct_counterparties"]["score"] = counterparty_score
        
        result["dimensions"]["structuring_pattern"]["value"] = structuring_count
        result["dimensions"]["structuring_pattern"]["score"] = structuring_score
        
        # Rules Fired logic
        if count_score >= 70:
            result["rules_fired"].append("VEL-001-HIGH-FREQUENCY")
            result["dimensions"]["transaction_count"]["threshold_breached"] = True
            
        if volume_score >= 70:
            result["rules_fired"].append("VEL-002-HIGH-VOLUME")
            result["dimensions"]["total_volume"]["threshold_breached"] = True
            
        if counterparty_score >= 70:
            result["rules_fired"].append("VEL-003-MANY-COUNTERPARTIES")
            result["dimensions"]["distinct_counterparties"]["threshold_breached"] = True
            
        if structuring_score >= 60:
            result["rules_fired"].append("VEL-004-STRUCTURING-PATTERN")
            result["dimensions"]["structuring_pattern"]["threshold_breached"] = True
            
        # Overall Velocity Score (average of 4 dimensions, 25% each)
        avg_score = (count_score + volume_score + counterparty_score + structuring_score) / 4.0
        result["velocity_score"] = round(avg_score, 2)
        
    except Exception as e:
        print(f"Velocity engine error: {e}")
        
    return result
