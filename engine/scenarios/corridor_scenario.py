"""
ScoreSentinel High-Risk Corridor Spike Scenario (v2.0)
ID: SCEN-CORR-01
Part of the ScoreSentinel Enterprise AML Rules Engine
Authored by Atul Krishnan, CAMS
"""

from datetime import timedelta
from typing import Dict, Any, List, Optional
from .base_scenario import BaseScenario
from ..geo_module import GeoModule

class CorridorScenario(BaseScenario):
    """
    SCEN-CORR-01: High-Risk Corridor Spike & Velocity Deviation.
    Detects sudden spikes in transaction volume or velocity directed to or originating
    from FATF Grey/Black list, high CPI corruption, or secrecy jurisdictions compared
    against the customer's historical 30-day baseline.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.geo_module = GeoModule()

    def evaluate(
        self,
        current_tx: Dict[str, Any],
        history: Optional[List[Dict[str, Any]]] = None,
        customer_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if not self.enabled:
            return self.build_result(False, "Scenario disabled in configuration.", {}, [])

        risk_threshold = float(self.parameters.get("corridor_risk_weight_threshold", 40.0))
        velocity_multiplier = float(self.parameters.get("velocity_multiplier", 3.0))
        min_amount = float(self.parameters.get("min_amount", self.parameters.get("min_corridor_amount", 5000.0)))
        greylist_boost = float(self.parameters.get("fatf_greylist_boost", 25.0))

        current_amount = float(current_tx.get("amount", current_tx.get("transaction_amount", 0.0)))
        sender_country = current_tx.get("sender_country", "United Kingdom")
        receiver_country = current_tx.get("receiver_country", "United Kingdom")
        
        # If customer profile specifies country, use as fallback
        if not sender_country and customer_profile:
            sender_country = customer_profile.get("country", "United Kingdom")

        # Evaluate geography using ScoreSentinel's GeoModule
        geo_result = self.geo_module.get_geo_score(sender_country, receiver_country)
        raw_geo_score = geo_result.get("raw_score", 0.0)
        is_auto_alert = geo_result.get("is_auto_alert", False)

        # Calculate historical 30-day baseline from customer history
        current_dt = self.parse_datetime(current_tx.get("date"))
        baseline_start = current_dt - timedelta(days=30)
        
        history_amounts = []
        corridor_history_count = 0
        if history:
            for tx in history:
                tx_dt = self.parse_datetime(tx.get("date"))
                if baseline_start <= tx_dt < current_dt:
                    amt = float(tx.get("amount", tx.get("transaction_amount", 0.0)))
                    history_amounts.append(amt)
                    
                    # Check if previous tx also traversed high risk corridor
                    snd = tx.get("sender_country", sender_country)
                    rcv = tx.get("receiver_country", receiver_country)
                    prev_geo = self.geo_module.get_geo_score(snd, rcv)
                    if prev_geo.get("raw_score", 0.0) >= risk_threshold:
                        corridor_history_count += 1

        baseline_avg_amount = (sum(history_amounts) / len(history_amounts)) if history_amounts else 0.0
        
        # Calculate velocity multiplier
        if baseline_avg_amount > 0:
            observed_multiplier = round(current_amount / baseline_avg_amount, 2)
        else:
            # First transaction or zero baseline: if above min_amount, treat as spike (>= multiplier)
            observed_multiplier = velocity_multiplier if current_amount >= min_amount else 1.0

        metrics = {
            "sender_country": sender_country,
            "receiver_country": receiver_country,
            "corridor_risk_score": raw_geo_score,
            "is_sanctions_auto_alert": is_auto_alert,
            "current_transaction_amount": current_amount,
            "historical_30d_avg_amount": round(baseline_avg_amount, 2),
            "historical_tx_count_30d": len(history_amounts),
            "historical_corridor_tx_count": corridor_history_count,
            "observed_multiplier": observed_multiplier,
            "configured_risk_threshold": risk_threshold,
            "configured_velocity_multiplier": velocity_multiplier,
            "configured_min_amount": min_amount
        }

        # Trigger logic:
        # 1. Direct Sanctions / Blacklist auto-alert
        # 2. Elevated corridor score + Amount >= min_amount + Velocity multiplier breached
        triggered = False
        breach_reasons = []

        if is_auto_alert:
            triggered = True
            breach_reasons.append(f"Direct high-risk / sanctioned jurisdiction detected ({sender_country} -> {receiver_country}).")

        if (raw_geo_score >= risk_threshold and current_amount >= min_amount):
            if observed_multiplier >= velocity_multiplier or corridor_history_count == 0:
                triggered = True
                breach_reasons.append(
                    f"Corridor risk score ({raw_geo_score}) exceeded threshold ({risk_threshold}) "
                    f"with {observed_multiplier}x spike over historical baseline (${baseline_avg_amount:,.2f})."
                )

        if triggered:
            summary = " | ".join(breach_reasons)
            clean_tx = [{
                "transaction_id": current_tx.get("id", current_tx.get("transaction_id", "current_tx")),
                "amount": current_amount,
                "corridor": f"{sender_country} -> {receiver_country}",
                "date": current_dt.isoformat()
            }]
            return self.build_result(True, summary, metrics, clean_tx)

        return self.build_result(
            False,
            f"Corridor risk score ({raw_geo_score}) or volume spike ({observed_multiplier}x) below threshold criteria.",
            metrics,
            []
        )
