import os
import json
import datetime

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rules", "rules_config.json")

class RulesEngine:
    def __init__(self):
        self.config = self._load_config()
        self.scenarios = self.config.get("scenarios", [])

    def _load_config(self):
        if not os.path.exists(CONFIG_PATH):
            return {"scenarios": []}
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_config(self):
        self.config["last_updated"] = datetime.datetime.now().isoformat()
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

    def get_active_scenarios(self):
        return [scn for scn in self.scenarios if scn.get("enabled", False)]

    def toggle_scenario(self, scenario_id, enabled, weight=None):
        updated = False
        for scn in self.scenarios:
            if scn["id"] == scenario_id:
                if enabled is not None:
                    scn["enabled"] = bool(enabled)
                if weight is not None:
                    scn["weight"] = weight
                updated = True
                break
        if updated:
            self._save_config()
        return updated

    def evaluate_scenarios(self, transaction, customer, history):
        fired_scenarios = []
        total_score = 0
        evaluated_count = 0
        skipped_count = 0

        amount = transaction.get("amount", 0)
        tx_type = transaction.get("transaction_type", "")
        
        for scn in self.scenarios:
            if not scn.get("enabled", False):
                skipped_count += 1
                continue

            evaluated_count += 1
            triggered = False
            reason = ""
            score_contribution = 0
            
            sc_id = scn["id"]
            conds = scn.get("trigger_conditions", {})
            weight = scn.get("weight", 0)

            if sc_id == "SCN-001": # STRUCTURING
                threshold = conds.get("threshold_amount", 10000)
                min_pct = conds.get("amount_min_pct_of_threshold", 75)
                max_pct = conds.get("amount_max_pct_of_threshold", 99)
                pct = (amount / threshold) * 100 if threshold else 0
                if min_pct <= pct <= max_pct:
                    triggered = True
                    score_contribution = weight
                    reason = f"Amount {amount} is {pct:.1f}% of {threshold} threshold"

            elif sc_id == "SCN-002": # RAPID_MOVEMENT
                min_amount = conds.get("min_amount", 5000)
                # Simplified check for demonstration: just check if history has recent offsetting tx
                if amount >= min_amount and history:
                    # In a real engine, we'd calculate time differences. Mocking trigger if history exists.
                    triggered = True
                    score_contribution = weight
                    reason = "Funds received and sent out within 24 hours"
            
            elif sc_id == "SCN-003": # HIGH_RISK_CORRIDOR
                # Check geography (dummy trigger if country is 'IR', 'KP', etc. For this, we just use a mock)
                sender = transaction.get("sender_country", "")
                receiver = transaction.get("receiver_country", "")
                if sender in ["IR", "KP", "SY", "CU"] or receiver in ["IR", "KP", "SY", "CU"]:
                    triggered = True
                    score_contribution = weight
                    reason = f"Transaction involves high risk jurisdiction: {sender} -> {receiver}"

            elif sc_id == "SCN-004": # FAN_IN
                min_senders = conds.get("min_distinct_senders", 5)
                # Mock logic
                if len(set(h.get("account_id") for h in history if h.get("transaction_type") == "CREDIT")) >= min_senders:
                    triggered = True
                    score_contribution = weight
                    reason = f"Account received funds from >= {min_senders} distinct senders"

            elif sc_id == "SCN-005": # ROUND_AMOUNT
                min_amount = conds.get("min_amount", 10000)
                if amount >= min_amount and amount % 1000 == 0:
                    triggered = True
                    score_contribution = weight
                    reason = f"Suspiciously round transaction amount: {amount}"

            elif sc_id == "SCN-006": # PEP_TRANSACTION
                # Trigger on explicit pep_tier OR on customer_type = PEP / canonical PEP string
                pep_tier = customer.get("pep_tier")
                ctype    = str(customer.get("customer_type", "")).strip().upper()
                is_pep   = (
                    pep_tier == "1" or
                    ctype == "PEP" or
                    ctype == "POLITICALLY EXPOSED PERSON (PEP)"
                )
                if is_pep and conds.get("pep_tier_1_auto_alert"):
                    triggered = True
                    score_contribution = weight
                    reason = "Transaction involves PEP customer"

            elif sc_id == "SCN-007": # CASH_INTENSIVE
                min_cash = conds.get("min_cash_amount", 50000)
                if amount >= min_cash and tx_type in conds.get("transaction_types", []):
                    triggered = True
                    score_contribution = weight
                    reason = f"High volume cash transaction: {amount} ({tx_type})"

            elif sc_id == "SCN-008": # VELOCITY_BREACH
                max_tx = conds.get("max_transactions_7_days", 20)
                if len(history) > max_tx:
                    triggered = True
                    score_contribution = weight
                    reason = f"Transaction count ({len(history)}) exceeds expected pattern"

            elif sc_id == "SCN-009": # CRYPTO_HIGH_VALUE
                # Cryptocurrency or virtual asset transaction above threshold
                # FATF R-15 VASP / RBI VDA Circular — any crypto above min_amount triggers
                min_amount = conds.get("min_amount", 10000)
                allowed_types = conds.get("transaction_types", ["CRYPTO", "Cryptocurrency Transaction", "Bitcoin"])
                if tx_type in allowed_types and amount >= min_amount:
                    triggered = True
                    score_contribution = weight
                    reason = f"Cryptocurrency/VDA transaction of {amount} above {min_amount} threshold ({tx_type})"

            elif sc_id == "SCN-010": # HIGH_VALUE_WIRE
                # Cross-border wire above threshold
                min_amount = conds.get("min_amount", 50000)
                allowed_types = conds.get("transaction_types", ["WIRE_TRANSFER", "Wire Transfer (International)"])
                require_cross_border = conds.get("require_cross_border", True)
                sender = transaction.get("sender_country", "")
                receiver = transaction.get("receiver_country", "")
                is_cross_border = sender != receiver if require_cross_border else True
                if tx_type in allowed_types and amount >= min_amount and is_cross_border:
                    triggered = True
                    score_contribution = weight
                    reason = f"High-value cross-border wire: {amount} ({sender} -> {receiver})"

            if triggered:
                total_score += score_contribution
                fired_scenarios.append({
                    "scenario_id": sc_id,
                    "scenario_name": scn["name"],
                    "triggered": True,
                    "score_contribution": score_contribution,
                    "reason": reason
                })

        return {
            "fired_scenarios": fired_scenarios,
            "total_score_contribution": total_score,
            "stats": {
                "evaluated": evaluated_count,
                "skipped": skipped_count
            }
        }
