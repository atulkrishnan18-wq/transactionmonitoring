"""
ScoreSentinel Transaction Type Module (v1.2)
Part of the ScoreSentinel AML Transaction Risk Scoring Engine
Authored by Atul Krishnan, CAMS | Day 23 of 60
"""

class TransactionModule:
    """
    Implements transaction type risk scoring rules as defined in TRANSACTION_RULES.md.
    """

    def __init__(self):
        # Module Maximum for normalization as defined in COMPOSITE_LOGIC.md
        self.module_maximum = 55
        
        # Base scores for 19 transaction types
        self.type_scores = {
            "Cryptocurrency Transaction": 55,
            "Correspondent Banking": 50,
            "Wire Transfer (International)": 45,
            "Real Estate Payment": 45,
            "Trade Finance / Letter of Credit": 45,
            "Foreign Currency Exchange (FX)": 40,
            "Money Order / Cashier's Cheque": 40,
            "Cash Deposit": 35,
            "Cash Withdrawal": 35,
            "ATM Transaction": 30,
            "Cheque Payment": 25,
            "Securities Trade (Stocks / Bonds)": 25,
            "Internal Account Transfer": 20,
            "Mobile / Peer-to-Peer Transfer": 20,
            "Credit Card Transaction": 15,
            "Online Payment / E-commerce": 15,
            "Domestic Salary Credit": 15,
            "Wire Transfer (Domestic)": 15,
            "Loan Repayment": 10,
            "Insurance Premium Payment": 10
        }

    def get_transaction_type_score(self, transaction_type):
        """
        Returns the base risk score for a transaction type.
        """
        return self.type_scores.get(transaction_type, 15) # Default to 15 (Medium-Low)

    def check_escalation_rules(self, tx_data):
        """
        Checks for specific escalation rules defined in TRANSACTION_RULES.md.
        Returns (is_alert, reason)
        """
        tx_type = tx_data.get("transaction_type")
        
        # Trade Finance Over-Invoicing Indicator
        if tx_type == "Trade Finance / Letter of Credit":
            if tx_data.get("is_over_invoiced"):
                return True, "TBML Over-Invoicing Indicator"
        
        # Insurance Three-Indicator Rule
        if tx_type == "Insurance Premium Payment":
            indicators = 0
            if tx_data.get("is_cash_payment") or tx_data.get("is_high_risk_geo"):
                indicators += 1
            if tx_data.get("is_early_surrender"):
                indicators += 1
            if tx_data.get("refund_to_third_party"):
                indicators += 1
            
            if indicators >= 2:
                return True, "Three-Indicator Insurance ML Escalation"

        # Loan Repayment Third-Party Rule
        if tx_type == "Loan Repayment":
            if tx_data.get("is_unknown_third_party"):
                return True, "Unknown Third-Party Loan Repayment"
        
        return False, None

    def get_module_result(self, tx_data):
        """
        Main entry point for the module.
        """
        base_score = self.get_transaction_type_score(tx_data.get("transaction_type"))
        is_alert, alert_reason = self.check_escalation_rules(tx_data)
        
        # Capping at module maximum
        if base_score > self.module_maximum:
            base_score = self.module_maximum
            
        normalised_score = (base_score / self.module_maximum)
        
        return {
            "raw_score": base_score,
            "normalised_score": normalised_score,
            "is_auto_alert": is_alert,
            "alert_reason": alert_reason
        }

if __name__ == "__main__":
    engine = TransactionModule()
    
    # Test Crypto
    print(f"Crypto Score: {engine.get_module_result({'transaction_type': 'Cryptocurrency Transaction'})}")
    
    # Test Insurance Escalation
    ins_data = {
        "transaction_type": "Insurance Premium Payment",
        "is_early_surrender": True,
        "refund_to_third_party": True
    }
    print(f"Insurance Escalation Test: {engine.get_module_result(ins_data)}")
