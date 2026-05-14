"""
ScoreSentinel Scoring Engine (v1.0)
Main coordinator for the AML Transaction Risk Scoring Engine.
Authored by Atul Krishnan, CAMS | Day 21 of 60
"""

from engine.customer_module import CustomerModule
from engine.structuring_module import StructuringModule
from engine.geo_module import GeoModule
from engine.transaction_module import TransactionModule

class ScoreSentinelEngine:
    def __init__(self):
        self.customer_module = CustomerModule()
        self.structuring_module = StructuringModule()
        self.geo_module = GeoModule()
        self.transaction_module = TransactionModule()

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
        Composite Risk Score (CRS).
        """
        # Step 1: Score individual modules and check for Auto-Alerts
        
        # Module 1: Customer Risk
        customer_result = self.customer_module.get_ccrs(transaction_data.get("customer", {}))
        if customer_result["is_auto_alert"]:
            return {
                "crs": None,
                "overall_crs": None,
                "alert": True,
                "alert_type": "Customer Auto-Alert",
                "trigger": "PEP/Sanctions or High-Risk Jurisdiction match",
                "rules_fired": ["CUST-AUTO-001"]
            }
        customer_normalised = (customer_result["ccrs"] / 175) * 100

        # Module 2: Structuring
        structuring_result = self.structuring_module.get_structuring_score(
            transaction_data.get("transaction", {}), 
            transaction_data.get("history", [])
        )
        if structuring_result["is_independent_trigger"]:
            return {
                "crs": None,
                "overall_crs": None,
                "alert": True,
                "alert_type": "Structuring Independent Trigger",
                "trigger": "Velocity or Structuring threshold breached",
                "rules_fired": structuring_result["triggered_rules"]
            }
        structuring_normalised = structuring_result["normalised_score"] * 100

        # Module 3: Geography
        geo_result = self.geo_module.get_geo_score(
            transaction_data.get("transaction", {}).get("sender_country"),
            transaction_data.get("transaction", {}).get("receiver_country")
        )
        if geo_result["is_auto_alert"]:
            return {
                "crs": None,
                "overall_crs": None,
                "alert": True,
                "alert_type": "Geography Auto-Alert",
                "trigger": "Sanctioned or Prohibited Jurisdiction",
                "rules_fired": ["GEO-AUTO-001"]
            }
        geo_normalised = geo_result["normalised_score"] * 100

        # Module 4: Transaction Type
        txtype_result = self.transaction_module.get_module_result(transaction_data.get("transaction", {}))
        if txtype_result["is_auto_alert"]:
            return {
                "crs": None,
                "overall_crs": None,
                "alert": True,
                "alert_type": "Transaction Type Auto-Alert",
                "trigger": txtype_result.get("alert_reason"),
                "rules_fired": ["TX-AUTO-001"]
            }
        txtype_normalised = txtype_result["normalised_score"] * 100

        # Step 2: Calculate Composite Risk Score (CRS)
        crs = (
            (customer_normalised * self.weights["customer"]) +
            (structuring_normalised * self.weights["structuring"]) +
            (geo_normalised * self.weights["geo"]) +
            (txtype_normalised * self.weights["transaction"])
        )

        # Step 3: Determine final alert status
        is_alert = crs >= self.alert_threshold

        return {
            "crs": round(crs, 2),
            "overall_crs": round(crs, 2),
            "is_alert": is_alert,
            "alert": is_alert,
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
                }
            }
        }

if __name__ == "__main__":
    # Test with Example 1 from CUSTOMER_RULES.md
    engine = ScoreSentinelEngine()
    test_data = {
        "customer": {
            "customer_type": "Verified Salaried Individual",
            "ownership_structure": "Individual customer — direct ownership, verified",
            "geo_tier": "Tier 4",
            "behaviour_indicator": "Fully consistent, stable, long-established pattern",
            "match_type": "No PEP / Sanctions / Adverse Media match"
        }
    }
    result = engine.score_transaction(test_data)
    print(f"Test Example 1 Result: {result}")
