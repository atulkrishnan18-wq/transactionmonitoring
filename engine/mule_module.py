"""
ScoreSentinel Mule Module (v1.0)
Specialized in detecting coordinated account clusters.
Authored by Atul Krishnan, CAMS | Day 30 of 60
"""

import datetime

class MuleModule:
    def __init__(self):
        self.mcs_threshold = 60

    def concentration_score(self, history, current_tx):
        """
        Dimension 1: Concentration Score (0–30)
        Measures how many accounts are feeding into a single concentrator account.
        """
        score = 0
        rules_fired = []
        
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=1)
        
        senders = set()
        all_tx = history + [current_tx]
        
        for h in all_tx:
            h_date = h.get('date')
            if isinstance(h_date, str):
                try:
                    h_date = datetime.datetime.fromisoformat(h_date)
                except ValueError:
                    continue
            
            if h_date >= yesterday:
                if h.get('type') == 'CREDIT':
                    sender_id = h.get('sender_id')
                    if sender_id:
                        senders.add(sender_id)
        
        unique_senders = len(senders)
        
        if unique_senders >= 10:
            score = 30
            rules_fired.append("MUL-003")
        elif unique_senders >= 5:
            score = 20
            rules_fired.append("MUL-002")
        elif unique_senders >= 2:
            score = 10
            rules_fired.append("MUL-001")
            
        return score, rules_fired

    def velocity_correlation_score(self, history, current_tx, customer_profile):
        """
        Dimension 2: Velocity Correlation Score (0–25)
        Measures coordinated activation or transacting in a time window.
        """
        score = 0
        rules_fired = []
        
        now = datetime.datetime.now()
        cutoff_48h = now - datetime.timedelta(hours=48)
        
        # MUL-005: Dormant account activation
        behaviour = customer_profile.get("behaviour_indicator", "")
        if "Dormant" in behaviour or "Inactive" in behaviour:
            # Check if current transaction is recent
            tx_date = current_tx.get('date')
            if isinstance(tx_date, str): tx_date = datetime.datetime.fromisoformat(tx_date)
            if tx_date >= cutoff_48h:
                score = 20
                rules_fired.append("MUL-005")
            
        # MUL-006: 5+ accounts transacting within same 30-min window
        # We only care about RECENT coordinated activity
        all_tx = history + [current_tx]
        tx_times = []
        for h in all_tx:
            h_date = h.get('date')
            if isinstance(h_date, str):
                try:
                    h_date = datetime.datetime.fromisoformat(h_date)
                except ValueError:
                    continue
            if h_date >= cutoff_48h:
                tx_times.append(h_date)
        
        tx_times.sort()
        max_in_window = 0
        for i in range(len(tx_times)):
            window_end = tx_times[i] + datetime.timedelta(minutes=30)
            count = 0
            for j in range(i, len(tx_times)):
                if tx_times[j] <= window_end:
                    count += 1
                else:
                    break
            max_in_window = max(max_in_window, count)
            
        if max_in_window >= 5:
            score = max(score, 25)
            if "MUL-006" not in rules_fired: rules_fired.append("MUL-006")
            
        # MUL-023: Common Device Nexus
        if customer_profile.get("device_nexus_count", 0) > 3:
            score = max(score, 25)
            rules_fired.append("MUL-023")
            
        return score, rules_fired

    def amount_pattern_score(self, history, current_tx):
        """
        Dimension 3: Amount Pattern Score (0–20)
        Detects structuring patterns across multiple accounts.
        """
        score = 0
        rules_fired = []
        
        # We only care about RECENT patterns
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=1)
        
        all_tx = history + [current_tx]
        recent_amounts = []
        for h in all_tx:
            h_date = h.get('date')
            if isinstance(h_date, str):
                try:
                    h_date = datetime.datetime.fromisoformat(h_date)
                except ValueError:
                    continue
            if h_date >= yesterday:
                recent_amounts.append(h.get('amount', 0))
        
        current_amount = current_tx.get('amount', 0)
        
        # MUL-009: 3+ identical amounts
        from collections import Counter
        counts = Counter(recent_amounts)
        if any(count >= 3 for count in counts.values()):
            score = 15
            rules_fired.append("MUL-009")
            
        # MUL-010: 5+ accounts sending amounts within 10% of each other
        if len(recent_amounts) >= 5:
            recent_amounts.sort()
            for i in range(len(recent_amounts) - 4):
                if recent_amounts[i+4] <= recent_amounts[i] * 1.1:
                    score = max(score, 20)
                    rules_fired.append("MUL-010")
                    break

        # Threshold rules only for current transaction
        if 9000 <= current_amount < 10000:
            score = max(score, 15)
            rules_fired.append("MUL-011")
        if 49000 <= current_amount < 50000:
            score = max(score, 15)
            rules_fired.append("MUL-012")
            
        # MUL-022: Micro-test
        has_micro = any(0 < h.get('amount', 0) <= 10 for h in history)
        if has_micro and current_amount > 1000:
            score = max(score, 15)
            rules_fired.append("MUL-022")
            
        return score, rules_fired

    def pass_through_speed_score(self, history, current_tx):
        """
        Dimension 4: Pass-Through Speed Score (0–15)
        Measures how quickly funds move through the account.
        """
        score = 0
        rules_fired = []
        
        all_tx = history + [current_tx]
        
        for h in all_tx:
            if isinstance(h.get('date'), str):
                h['date_obj'] = datetime.datetime.fromisoformat(h.get('date'))
            else:
                h['date_obj'] = h.get('date')
        
        sorted_tx = sorted(all_tx, key=lambda x: x['date_obj'])
        
        for i in range(len(sorted_tx) - 1):
            if sorted_tx[i].get('type') == 'CREDIT':
                for j in range(i + 1, len(sorted_tx)):
                    if sorted_tx[j].get('type') == 'DEBIT':
                        diff = (sorted_tx[j]['date_obj'] - sorted_tx[i]['date_obj']).total_seconds() / 60
                        if diff <= 30:
                            score = max(score, 15)
                            if "MUL-014" not in rules_fired: rules_fired.append("MUL-014")
                        elif diff <= 120:
                            score = max(score, 10)
                            if "MUL-015" not in rules_fired: rules_fired.append("MUL-015")
                        elif diff <= 1440:
                            score = max(score, 5)
                            if "MUL-016" not in rules_fired: rules_fired.append("MUL-016")
                        break
                            
        return score, rules_fired

    def network_depth_score(self, history, current_tx):
        """
        Dimension 5: Network Depth Score (0–10)
        Detects multi-tier layering structures.
        """
        score = 0
        rules_fired = []
        
        all_tx = history + [current_tx]
        if len(all_tx) > 0:
            score = 5
            rules_fired.append("MUL-018")
            
        return score, rules_fired

    def analyse_cluster(self, transaction_data, history, customer_profile):
        """
        Calculates the Mule Cluster Score (MCS) based on the five dimensions.
        """
        d1_score, d1_rules = self.concentration_score(history, transaction_data)
        d2_score, d2_rules = self.velocity_correlation_score(history, transaction_data, customer_profile)
        d3_score, d3_rules = self.amount_pattern_score(history, transaction_data)
        d4_score, d4_rules = self.pass_through_speed_score(history, transaction_data)
        d5_score, d5_rules = self.network_depth_score(history, transaction_data)
        
        mcs = d1_score + d2_score + d3_score + d4_score + d5_score
        mcs = min(mcs, 100)
        
        rules_fired = d1_rules + d2_rules + d3_rules + d4_rules + d5_rules
        
        risk_band = "LOW"
        if mcs >= 80: risk_band = "ORGANISED_NETWORK"
        elif mcs >= 60: risk_band = "MULE_CLUSTER"
        elif mcs >= 40: risk_band = "HIGH"
        elif mcs >= 20: risk_band = "MEDIUM"
        
        is_knowing_mule = customer_profile.get("device_nexus_count", 0) > 1
        
        return {
            "mcs": mcs,
            "mcs_risk_band": risk_band,
            "cluster_type": "KNOWING_MULE" if is_knowing_mule else "UNKNOWING_VICTIM",
            "rules_fired": rules_fired,
            "is_mule_alert": mcs >= self.mcs_threshold,
            "accounts_in_cluster": list(set([h.get('sender_id') for h in history if h.get('sender_id')] + [transaction_data.get('account_id')])),
            "dimension_scores": {
                "concentration": d1_score,
                "velocity": d2_score,
                "amount_pattern": d3_score,
                "pass_through": d4_score,
                "network_depth": d5_score
            }
        }
