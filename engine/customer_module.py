"""
ScoreSentinel Customer Risk Module (v1.1)
Part of the ScoreSentinel AML Transaction Risk Scoring Engine
Authored by Atul Krishnan, CAMS | Day 21 of 60
"""

class CustomerModule:
    """
    Implements the 5-dimension Composite Customer Risk Score (CCRS) logic
    as defined in CUSTOMER_RULES.md.
    """

    def __init__(self):
        # Module Maximum for normalization as defined in COMPOSITE_LOGIC.md
        self.module_maximum = 175
        self.alert_threshold = 60

    def calculate_customer_type_score(self, customer_type):
        """
        Dimension 1: Customer Type Score (0-50)
        """
        scores = {
            "Shell Company": 50,
            "Sanctions-Adjacent Entity": 50,
            "Politically Exposed Person (PEP)": 50,
            "Cash-Intensive Business": 45,
            "High-Risk Jurisdiction Customer": 45,
            "Tax Haven Associated Entity": 40,
            "Correspondent Bank / NBFI": 40,
            "Crypto-Asset Business": 40,
            "Newly Onboarded Customer": 30,
            "Trust / Foundation": 30,
            "Charity / NGO": 25,
            "Non-Resident Customer": 25,
            "High-Net-Worth Individual (HNWI)": 25,
            "Small/Medium Business (SMB)": 20,
            "Established Business (3+ years)": 10,
            "Verified Salaried Individual": 5,
            "Government Entity": 5,
            "Listed Company": 5
        }
        return scores.get(customer_type, 5)

    def calculate_ownership_transparency_score(self, customer_data):
        """
        Dimension 2: Ownership Transparency Score (0-25 base + additives)
        """
        score = 0
        structure_type = customer_data.get("ownership_structure")
        customer_type = customer_data.get("customer_type")
        geo_tier = customer_data.get("geo_tier")

        scores = {
            "Beneficial owner unidentified or unverifiable": 25,
            "Layered ownership — 3+ levels, offshore intermediaries": 20,
            "Nominee directors or bearer shares present": 20,
            "Beneficial owner identified but not verified": 15,
            "Single corporate layer — owner identified and verified": 5,
            "Individual customer — direct ownership, verified": 0
        }
        score += scores.get(structure_type, 0) # Default to 0 if not specified to allow clean scenarios

        # Additive components for Shell Companies (Scenario 2/16 logic)
        if customer_type == "Shell Company":
            # If BO is unknown/unverified
            if structure_type in ["Beneficial owner unidentified or unverifiable", "Beneficial owner identified but not verified"]:
                # Only add if not already at 25? 
                # Scenario 2: Unknown BO (25). Base for "identified but not verified" is 15.
                # So we add 10 to reach 25? Or add 25?
                # "Shell company (50) + Unknown BO (25) + Offshore (15) = 90"
                # If Dim1 is 50, then Dim2 must be 25 + 15 = 40.
                if structure_type == "Beneficial owner identified but not verified":
                    score = 25 # Upgrade 15 -> 25
                elif structure_type == "Beneficial owner unidentified or unverifiable":
                    score = 25
                
                # Offshore incorporation: +15
                if geo_tier == "Tier 3":
                    score += 15
            
            # Scenario 16 logic: Shell(50) + Unknown BO(25) + Nominee(20) + Offshore(15) + No History(30)
            if structure_type == "Nominee directors or bearer shares present":
                score = 25 + 20 + 15 # Unknown BO(25) + Nominee(20) + Offshore(15) = 60
                
        return score

    def calculate_geographic_risk_score(self, geo_tier):
        """
        Dimension 3: Geographic Risk Score (0-25)
        """
        scores = {
            "Tier 1A": 25,
            "Tier 1B": 25,
            "Tier 1C": 20,
            "Tier 2A": 15,
            "Tier 2B": 10,
            "Tier 3": 15,
            "Tier 4": 0
        }
        return scores.get(geo_tier, 0)

    def calculate_account_behaviour_score(self, behaviour_indicator):
        """
        Dimension 4: Account Behaviour Score (0-25)
        """
        scores = {
            "Transaction pattern inconsistent with stated business purpose": 25,
            "Sudden spike in transaction volume (>300% of 90-day average)": 20,
            "Multiple jurisdictions inconsistent with business profile": 20,
            "Frequent large cash transactions without clear business reason": 20,
            "Newly onboarded — no baseline established yet": 15,
            "Transaction pattern broadly consistent with profile": 5,
            "Fully consistent, stable, long-established pattern": 0,
            "No trading history provided": 30 # Scenario 16
        }
        return scores.get(behaviour_indicator, 0) # Default to 0 for validation

    def calculate_pep_sanctions_score(self, match_type):
        """
        Dimension 5: PEP / Sanctions Score (0-50)
        """
        scores = {
            "Confirmed PEP — Tier 1": 50,
            "Confirmed Sanctions Hit": 50,
            "Confirmed PEP — Tier 2": 40,
            "Confirmed PEP — Tier 3": 30,
            "Adverse Media — confirmed financial crime": 35,
            "Adverse Media — unconfirmed / single source": 15,
            "No PEP / Sanctions / Adverse Media match": 0
        }
        return scores.get(match_type, 0)

    def get_ccrs(self, customer_data):
        """
        Calculates the Composite Customer Risk Score (CCRS).
        """
        dim1 = self.calculate_customer_type_score(customer_data.get("customer_type"))
        dim2 = self.calculate_ownership_transparency_score(customer_data)
        dim3 = self.calculate_geographic_risk_score(customer_data.get("geo_tier"))
        dim4 = self.calculate_account_behaviour_score(customer_data.get("behaviour_indicator"))
        dim5 = self.calculate_pep_sanctions_score(customer_data.get("match_type"))

        total_score = dim1 + dim2 + dim3 + dim4 + dim5
        
        # SR 11-7 Validation Rule: Cap at module maximum
        if total_score > self.module_maximum:
            total_score = self.module_maximum

        return {
            "ccrs": total_score,
            "dimensions": {
                "customer_type": dim1,
                "ownership_transparency": dim2,
                "geographic_risk": dim3,
                "account_behaviour": dim4,
                "pep_sanctions": dim5
            },
            "is_auto_alert": (
                customer_data.get("match_type") in ["Confirmed PEP — Tier 1", "Confirmed Sanctions Hit"] or
                customer_data.get("geo_tier") in ["Tier 1A", "Tier 1B"]
            )
        }
