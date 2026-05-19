"""
ScoreSentinel Scoring Engine (v1.0)
Main coordinator for the AML Transaction Risk Scoring Engine.
Authored by Atul Krishnan, CAMS | Day 21 of 60
"""

from engine.customer_module import CustomerModule
from engine.structuring_module import StructuringModule
from engine.geo_module import GeoModule
from engine.transaction_module import TransactionModule
from engine.mule_module import MuleModule

class ScoreSentinelEngine:
    def __init__(self):
        self.customer_module = CustomerModule()
        self.structuring_module = StructuringModule()
        self.geo_module = GeoModule()
        self.transaction_module = TransactionModule()
        self.mule_module = MuleModule()

        # Weights as defined in COMPOSITE_LOGIC.md
        self.weights = {
            "customer": 0.30,
            "structuring": 0.25,
            "geo": 0.25,
            "transaction": 0.20
        }
        
        self.alert_threshold = 60

    def score_transaction(self, transaction_data):
        """
        Coordinates the scoring across all modules and produces a 
        Composite Risk Score (CRS) and Mule Cluster Score (MCS).
        """
        # Step 1: customer_module
        customer_result = self.customer_module.get_ccrs(transaction_data.get("customer", {}))
        customer_normalised = (customer_result["ccrs"] / 175) * 100

        # Step 2: structuring_module
        structuring_result = self.structuring_module.get_structuring_score(
            transaction_data.get("transaction", {}), 
            transaction_data.get("history", [])
        )
        structuring_normalised = structuring_result["normalised_score"] * 100

        # Step 3: geo_module
        geo_result = self.geo_module.get_geo_score(
            transaction_data.get("transaction", {}).get("sender_country"),
            transaction_data.get("transaction", {}).get("receiver_country")
        )
        geo_normalised = geo_result["normalised_score"] * 100

        # Step 4: transaction_module
        txtype_result = self.transaction_module.get_module_result(transaction_data.get("transaction", {}))
        txtype_normalised = txtype_result["normalised_score"] * 100
        
        # Step 5: Calculate CRS
        crs = (
            (customer_normalised * self.weights["customer"]) +
            (structuring_normalised * self.weights["structuring"]) +
            (geo_normalised * self.weights["geo"]) +
            (txtype_normalised * self.weights["transaction"])
        )

        # Step 6: mule_module.analyse_cluster()
        # This MUST run even if there is an auto-alert
        mule_result = self.mule_module.analyse_cluster(
            transaction_data.get("transaction", {}),
            transaction_data.get("history", []),
            transaction_data.get("customer", {})
        )

        # Check for Auto-Alerts AFTER mule module run
        # Note: If multiple auto-alerts fire, we should capture them.
        auto_alert = False
        alert_type = None
        trigger = None
        rules_fired = []
        
        if customer_result["is_auto_alert"]:
            auto_alert = True
            alert_type = "Customer Auto-Alert"
            trigger = "PEP/Sanctions or High-Risk Jurisdiction match"
            rules_fired.append("CUST-AUTO-001")
            
        if structuring_result["is_independent_trigger"]:
            auto_alert = True
            alert_type = "Structuring Independent Trigger"
            trigger = "Velocity or Structuring threshold breached"
            rules_fired.extend(structuring_result["triggered_rules"])
            
        if geo_result["is_auto_alert"]:
            auto_alert = True
            alert_type = "Geography Auto-Alert"
            trigger = "Sanctioned or Prohibited Jurisdiction"
            rules_fired.append("GEO-AUTO-001")
            
        if txtype_result["is_auto_alert"]:
            auto_alert = True
            alert_type = "Transaction Type Auto-Alert"
            trigger = txtype_result.get("alert_reason")
            rules_fired.append("TX-AUTO-001")

        # Step 7: Return both CRS and MCS
        is_alert = crs >= self.alert_threshold or mule_result["is_mule_alert"] or auto_alert

        # Aggregate rules fired
        all_rules = rules_fired.copy()
        all_rules.extend(mule_result.get("rules_fired", []))
        
        final_result = {
            "crs": round(crs, 2) if not auto_alert else None,
            "overall_crs": round(crs, 2),
            "mcs": mule_result["mcs"],
            "mcs_risk_band": mule_result["mcs_risk_band"],
            "cluster_type": mule_result["cluster_type"],
            "mule_alert": mule_result["is_mule_alert"],
            "is_alert": is_alert,
            "alert": is_alert,
            "rules_fired": all_rules,
            "module_scores": {
                "customer": {
                    "raw": customer_result["ccrs"],
                    "normalised": round(customer_normalised, 2)
                },
                "structuring": {
                    "raw": structuring_result["raw_score"],
                    "normalised": round(structuring_normalised, 2),
                    "is_trigger": structuring_result["is_independent_trigger"],
                    "triggered_rules": structuring_result["triggered_rules"]
                },
                "geo": {
                    "raw": geo_result["raw_score"],
                    "normalised": round(geo_normalised, 2),
                    "is_auto_alert": geo_result["is_auto_alert"]
                },
                "transaction_type": {
                    "raw": txtype_result["raw_score"],
                    "normalised": round(txtype_normalised, 2),
                    "is_auto_alert": txtype_result["is_auto_alert"]
                },
                "mule": mule_result["dimension_scores"]
            }
        }
        
        if auto_alert:
            final_result["alert_type"] = alert_type
            final_result["trigger"] = trigger
        elif mule_result["is_mule_alert"]:
            final_result["alert_type"] = "Mule Cluster Alert"
            final_result["trigger"] = f"Mule Cluster Score: {mule_result['mcs']}"
            
        return final_result

if __name__ == "__main__":
    engine = ScoreSentinelEngine()
    test_data = {
        "customer": {
            "customer_type": "Verified Salaried Individual",
            "ownership_structure": "Individual customer — direct ownership, verified",
            "geo_tier": "Tier 4",
            "behaviour_indicator": "Fully consistent, stable, long-established pattern",
            "match_type": "No PEP / Sanctions / Adverse Media match"
        },
        "transaction": {"amount": 1000},
        "history": []
    }
    result = engine.score_transaction(test_data)
    print(f"Test Result: {result}")
