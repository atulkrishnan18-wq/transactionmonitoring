"""
ScoreSentinel Structuring / Smurfing Scenario (v2.0)
ID: SCEN-STRUC-01
Part of the ScoreSentinel Enterprise AML Rules Engine
Authored by Atul Krishnan, CAMS
"""

from datetime import timedelta
from typing import Dict, Any, List, Optional
from .base_scenario import BaseScenario

class StructuringScenario(BaseScenario):
    """
    SCEN-STRUC-01: Structuring / Smurfing Pattern Detection.
    Identifies multiple transactions conducted under statutory reporting limits
    ($10,000 CTR limit) within a rolling window to evade regulatory detection.
    """

    def evaluate(
        self,
        current_tx: Dict[str, Any],
        history: Optional[List[Dict[str, Any]]] = None,
        customer_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if not self.enabled:
            return self.build_result(False, "Scenario disabled in configuration.", {}, [])

        lower_bound = float(self.parameters.get("lower_bound", 9000.0))
        upper_bound = float(self.parameters.get("upper_bound", 9999.99))
        lookback_days = int(self.parameters.get("lookback_days", 3))
        min_tx_count = int(self.parameters.get("min_tx_count", 3))
        aggregate_threshold = float(self.parameters.get("aggregate_threshold_check", 25000.0))

        # Normalize and aggregate transactions
        all_tx = (history or []) + [current_tx]
        tx_records = []
        for tx in all_tx:
            dt = self.parse_datetime(tx.get("date"))
            amount = float(tx.get("amount", tx.get("transaction_amount", 0.0)))
            tx_records.append({
                "id": tx.get("id", tx.get("transaction_id", f"tx_{id(tx)}")),
                "date": dt,
                "amount": amount,
                "currency": tx.get("currency", tx.get("transaction_currency", "USD")),
                "sender_country": tx.get("sender_country"),
                "receiver_country": tx.get("receiver_country"),
                "raw_ref": tx
            })

        tx_records.sort(key=lambda x: x["date"])
        current_dt = self.parse_datetime(current_tx.get("date"))
        window_start = current_dt - timedelta(days=lookback_days)

        # Filter to transactions in lookback window up to current transaction
        window_txs = [t for t in tx_records if window_start <= t["date"] <= current_dt]

        # Identify transactions within structuring amount band
        qualifying_txs = [
            t for t in window_txs 
            if lower_bound <= t["amount"] <= upper_bound
        ]

        qualifying_count = len(qualifying_txs)
        qualifying_sum = sum(t["amount"] for t in qualifying_txs)

        metrics = {
            "window_days": lookback_days,
            "window_start": window_start.isoformat(),
            "window_end": current_dt.isoformat(),
            "evaluated_window_transactions": len(window_txs),
            "qualifying_transactions_count": qualifying_count,
            "qualifying_total_amount": round(qualifying_sum, 2),
            "configured_lower_bound": lower_bound,
            "configured_upper_bound": upper_bound,
            "configured_min_count": min_tx_count
        }

        triggered = (qualifying_count >= min_tx_count)

        if triggered:
            # Check for high aggregate total
            severity = "CRITICAL" if qualifying_sum >= aggregate_threshold else self.severity
            breach_summary = (
                f"Detected {qualifying_count} structured transactions totaling "
                f"${qualifying_sum:,.2f} between ${lower_bound:,.2f} and ${upper_bound:,.2f} "
                f"within a {lookback_days}-day rolling window, exceeding minimum threshold count of {min_tx_count}."
            )
            clean_tx_output = [
                {
                    "transaction_id": t["id"],
                    "amount": t["amount"],
                    "currency": t["currency"],
                    "date": t["date"].isoformat()
                }
                for t in qualifying_txs
            ]
            return self.build_result(True, breach_summary, metrics, clean_tx_output, custom_severity=severity)

        return self.build_result(
            False,
            f"Only {qualifying_count} transaction(s) between ${lower_bound:,.2f} and ${upper_bound:,.2f} "
            f"in {lookback_days}-day window (threshold: {min_tx_count}).",
            metrics,
            []
        )
