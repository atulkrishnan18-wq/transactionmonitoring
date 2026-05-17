"""
ScoreSentinel Mule Module (v1.0)
Part of Project MuleCatcher: Specialized in detecting coordinated account clusters.
Authored by Atul Krishnan, CAMS | Day 30 of 60
"""

import datetime

class MuleModule:
    def __init__(self):
        # Weights for Mule Probability Score (MPS)
        self.weights = {
            "rapid_depletion": 35,
            "nexus_velocity": 25,
            "dormant_to_burst": 20,
            "profile_contrast": 15,
            "micro_test": 10
        }
        
        self.mps_threshold = 75

    def get_mps(self, transaction_data, history, customer_profile):
        """
        Calculates the Mule Probability Score (MPS) based on cluster typologies.
        """
        raw_score = 0
        triggered_rules = []
        
        # Rule MUL-001: Rapid Depletion (Drain)
        # Check if recent credits were immediately followed by debits
        credits = sum(h['amount'] for h in history if h.get('type') == 'CREDIT')
        debits = sum(h['amount'] for h in history if h.get('type') == 'DEBIT')
        if credits > 0 and (debits / credits) > 0.95:
            raw_score += self.weights["rapid_depletion"]
            triggered_rules.append("MUL-001")

        # Rule MUL-002: Nexus Velocity (Fan-In)
        unique_senders = len(set(h.get('sender_id') for h in history if h.get('sender_id')))
        if unique_senders >= 5:
            raw_score += self.weights["nexus_velocity"]
            triggered_rules.append("MUL-002")

        # Rule MUL-003: Dormant-to-Burst
        behaviour = customer_profile.get("behaviour_indicator", "")
        if "Dormant" in behaviour or "Inactive" in behaviour:
            if transaction_data.get("amount", 0) > 100000: # ₹1 Lakh threshold
                raw_score += self.weights["dormant_to_burst"]
                triggered_rules.append("MUL-003")

        # Rule MUL-005: Profile Contrast
        low_income_occupations = ["Student", "Unemployed", "Farmer", "Labourer"]
        occupation = customer_profile.get("occupation", "")
        if occupation in low_income_occupations:
            if transaction_data.get("amount", 0) > 50000:
                raw_score += self.weights["profile_contrast"]
                triggered_rules.append("MUL-005")

        # Rule MUL-006: Micro-Test Signal
        has_test = any(h['amount'] <= 10 for h in history)
        if has_test and transaction_data.get("amount", 0) > 10000:
            raw_score += self.weights["micro_test"]
            triggered_rules.append("MUL-006")

        # Normalise MPS to 0-100
        mps = min(raw_score, 100)
        
        return {
            "mps": mps,
            "is_mule_alert": mps >= self.mps_threshold,
            "triggered_rules": triggered_rules,
            "mule_level": "CRITICAL" if mps >= 90 else "HIGH" if mps >= 75 else "MEDIUM" if mps >= 50 else "LOW"
        }
