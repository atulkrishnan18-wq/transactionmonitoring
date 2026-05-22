# QUERIES.md — Common Database Queries

## 1. All high risk alerts today
SELECT transaction_id, customer_id, 
crs, alert_type, timestamp_processed
FROM transactions
WHERE alert_generated = true
AND timestamp_processed >= CURRENT_DATE
ORDER BY crs DESC;

## 2. All transactions for a customer
SELECT * FROM transactions
WHERE customer_id = '[CUSTOMER_ID]'
ORDER BY timestamp_processed DESC;

## 3. All pending sanctions alerts
SELECT a.alert_id, t.customer_id, 
t.crs, a.alert_type, a.stage
FROM alerts a
JOIN transactions t 
ON a.transaction_id = t.transaction_id
WHERE a.alert_type = 'SANCTIONS'
AND a.status = 'PENDING';

## 4. False positive rate this month
SELECT
  COUNT(*) as total_alerts,
  SUM(CASE WHEN disposition = 
    'FALSE_POSITIVE' THEN 1 ELSE 0 END) 
    as false_positives,
  ROUND(SUM(CASE WHEN disposition = 
    'FALSE_POSITIVE' THEN 1 ELSE 0 END) 
    * 100.0 / COUNT(*), 1) as fp_rate
FROM alerts
WHERE created_at >= DATE_TRUNC('month', 
  CURRENT_DATE)
AND status = 'REVIEWED';

## 5. All mule cluster alerts
SELECT cluster_id, cluster_type, mcs,
risk_band, account_ids, str_filed,
detected_at
FROM mule_clusters
WHERE alert_generated = true
ORDER BY mcs DESC;

## 6. Transactions by country last 30 days
SELECT sender_country, 
COUNT(*) as transaction_count,
SUM(CASE WHEN alert_generated = true 
  THEN 1 ELSE 0 END) as alert_count
FROM transactions
WHERE timestamp_processed >= 
  CURRENT_DATE - INTERVAL '30 days'
GROUP BY sender_country
ORDER BY alert_count DESC;
