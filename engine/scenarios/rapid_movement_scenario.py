"""
ScoreSentinel Rapid Movement of Funds / Pass-Through Scenario (v2.0)
ID: SCEN-VEL-01
Part of the ScoreSentinel Enterprise AML Rules Engine
Authored by Atul Krishnan, CAMS
"""

from datetime import timedelta
from typing import Dict, Any, List, Optional
from .base_scenario import BaseScenario

class RapidMovementScenario(BaseScenario):
    """
    SCEN-VEL-01: Rapid Movement of Funds / Pass-Through Mule Account.
    Detects immediate fund dissipation where incoming credits are routed out 
    as debits in a narrow window, characteristic of mule or layering accounts.
    """

    def evaluate(
        self,
        current_tx: Dict[str, Any],
        history: Optional[List[Dict[str, Any]]] = None,
        customer_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if not self.enabled:
            return self.build_result(False, "Scenario disabled in configuration.", {}, [])

        inflow_window_hours = int(self.parameters.get("inflow_window_hours", 24))
        outflow_ratio_threshold = float(self.parameters.get("outflow_ratio", 0.85))
        min_amount = float(self.parameters.get("min_amount", 10000.0))
        max_retention_hours = int(self.parameters.get("max_retention_hours", 48))

        all_tx = (history or []) + [current_tx]
        tx_records = []
        for tx in all_tx:
            dt = self.parse_datetime(tx.get("date"))
            amount = float(tx.get("amount", tx.get("transaction_amount", 0.0)))
            
            # Determine direction: CREDIT (inflow) vs DEBIT (outflow)
            direction = str(tx.get("type", tx.get("direction", tx.get("transaction_type", "")))).upper()
            if "CREDIT" in direction or "INFLOW" in direction or "DEPOSIT" in direction or "RECEIVE" in direction:
                tx_type = "CREDIT"
            elif "DEBIT" in direction or "OUTFLOW" in direction or "WITHDRAWAL" in direction or "TRANSFER" in direction or "SEND" in direction:
                tx_type = "DEBIT"
            else:
                # Default heuristic based on positive/negative or transaction_type
                tx_type = "DEBIT" if "WIRE" in direction or "PAYMENT" in direction else "CREDIT"

            tx_records.append({
                "id": tx.get("id", tx.get("transaction_id", f"tx_{id(tx)}")),
                "date": dt,
                "amount": abs(amount),
                "type": tx_type,
                "currency": tx.get("currency", tx.get("transaction_currency", "USD")),
                "raw_ref": tx
            })

        tx_records.sort(key=lambda x: x["date"])
        current_dt = self.parse_datetime(current_tx.get("date"))
        window_start = current_dt - timedelta(hours=inflow_window_hours)

        # Aggregate credits and debits within observation window
        window_txs = [t for t in tx_records if window_start <= t["date"] <= current_dt]
        credits = [t for t in window_txs if t["type"] == "CREDIT"]
        debits = [t for t in window_txs if t["type"] == "DEBIT"]

        total_inflows = sum(t["amount"] for t in credits)
        total_outflows = sum(t["amount"] for t in debits)

        # If current_tx itself is a debit, we also check if credits occurred in slightly wider retention window
        if total_inflows < min_amount:
            wider_start = current_dt - timedelta(hours=max_retention_hours)
            wider_credits = [t for t in tx_records if wider_start <= t["date"] <= current_dt and t["type"] == "CREDIT"]
            total_inflows = sum(t["amount"] for t in wider_credits)
            credits = wider_credits

        dissipation_ratio = (total_outflows / total_inflows) if total_inflows > 0 else 0.0

        # Calculate time between earliest inflow and latest outflow
        time_span_minutes = 0.0
        if credits and debits:
            time_span_minutes = abs((debits[-1]["date"] - credits[0]["date"]).total_seconds()) / 60.0

        metrics = {
            "window_hours": inflow_window_hours,
            "total_inflows": round(total_inflows, 2),
            "total_outflows": round(total_outflows, 2),
            "dissipation_ratio": round(dissipation_ratio, 4),
            "time_span_minutes": round(time_span_minutes, 1),
            "credit_count": len(credits),
            "debit_count": len(debits),
            "configured_min_amount": min_amount,
            "configured_outflow_ratio": outflow_ratio_threshold
        }

        triggered = (total_inflows >= min_amount and dissipation_ratio >= outflow_ratio_threshold)

        if triggered:
            breach_summary = (
                f"Pass-through velocity alert: Account received ${total_inflows:,.2f} in inflows "
                f"and dissipated ${total_outflows:,.2f} ({dissipation_ratio:.1%}) within {inflow_window_hours}h "
                f"(configured dissipation threshold: {outflow_ratio_threshold:.1%})."
            )
            triggering_txs = [
                {
                    "transaction_id": t["id"],
                    "amount": t["amount"],
                    "type": t["type"],
                    "date": t["date"].isoformat()
                }
                for t in (credits + debits)
            ]
            return self.build_result(True, breach_summary, metrics, triggering_txs)

        return self.build_result(
            False,
            f"Inflow/outflow ratio ({dissipation_ratio:.1%}) or inflow volume (${total_inflows:,.2f}) "
            f"did not breach parameters (min: ${min_amount:,.2f}, ratio: {outflow_ratio_threshold:.1%}).",
            metrics,
            []
        )
