"""
ScoreSentinel Scoring Engine (v1.0)
Main coordinator for the AML Transaction Risk Scoring Engine.
Authored by Atul Krishnan, CAMS | Day 21 of 60
"""

from engine.customer_module import CustomerModule

class ScoreSentinelEngine:
    def __init__(self):
        self.customer_module = CustomerModule()
        # Other modules will be initialized here as they are built
        # self.structuring_module = StructuringModule()
        # self.geo_module = GeoModule()
        # self.transaction_module = TransactionModule()

    def score_transaction(self, transaction_data):
        """
        Coordinates the scoring across all modules and produces a 
        Composite Risk Score (CRS).
        """
        # Step 1: Score Customer Risk
        customer_result = self.customer_module.get_ccrs(transaction_data.get("customer", {}))
        
        # Step 2: Normalization (placeholder for now)
        # STEP 1 — Normalise each module score to 0–100:
        # Customer Normalised = (Customer Raw / 175) × 100
        customer_normalised = (customer_result["ccrs"] / 175) * 100

        # Placeholder for other modules
        # structuring_normalised = 0
        # geo_normalised = 0
        # txtype_normalised = 0

        # Step 3: Weighted Sum (placeholder for now)
        # CRS = (Customer Normalised × 0.30) + ...
        # For Day 21, we just return the customer results for validation.
        
        return {
            "customer_risk": customer_result,
            "customer_normalised": customer_normalised,
            "overall_crs": customer_normalised * 0.30, # Temporary until other modules added
            "is_auto_alert": customer_result["is_auto_alert"]
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
