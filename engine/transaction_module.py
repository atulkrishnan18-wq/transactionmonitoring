"""
ScoreSentinel Transaction Type Module (v1.3)
Part of the ScoreSentinel AML Transaction Risk Scoring Engine
Authored by Atul Krishnan, CAMS | Day 23+ of 60

v1.3 additions:
  - 5 Credit card-specific transaction types (CNP, EMI_CONVERSION, CASH_ADVANCE,
    REWARD_REDEMPTION, BALANCE_TRANSFER)
  - MCC risk tier mapping (Tier 1/2/3) aligned with PCI DSS and RBI CC directions
  - CC-specific rules fired: CC-CNP-HIGH-RISK, CC-CASH-ADVANCE-RISK,
    CC-MCC-TIER1, CC-MCC-TIER2, CC-EMI-STRUCTURING
"""


class TransactionModule:
    """
    Implements transaction type risk scoring rules as defined in TRANSACTION_RULES.md.
    """

    def __init__(self):
        # Module Maximum for normalisation as defined in COMPOSITE_LOGIC.md
        self.module_maximum = 55

        # ── Base scores: original 19 transaction types ─────────────
        self.type_scores = {
            "Cryptocurrency Transaction":          55,
            "Correspondent Banking":               50,
            "Wire Transfer (International)":       45,
            "Real Estate Payment":                 45,
            "Trade Finance / Letter of Credit":    45,
            "Foreign Currency Exchange (FX)":      40,
            "Money Order / Cashier's Cheque":      40,
            "Cash Deposit":                        35,
            "Cash Withdrawal":                     35,
            "ATM Transaction":                     30,
            "Cheque Payment":                      25,
            "Securities Trade (Stocks / Bonds)":   25,
            "Internal Account Transfer":           20,
            "Mobile / Peer-to-Peer Transfer":      20,
            "Credit Card Transaction":             15,
            "Online Payment / E-commerce":         15,
            "Domestic Salary Credit":              15,
            "Wire Transfer (Domestic)":            15,
            "Loan Repayment":                      10,
            "Insurance Premium Payment":           10,

            # ── IBM field aliases (Payment_Format values) ────────────
            "WIRE_TRANSFER":   35,   # Wire (domestic/international blend)
            "ACH":             20,
            "CHEQUE":          25,
            "CARD_PAYMENT":    15,
            "CRYPTO":          55,
            "REINVESTMENT":    20,
            "OTHER":           15,

            # ── Credit Card Specific Types (v1.3) ────────────────────
            # REG: RBI Master Direction on Credit Card 2022
            #      RBI Circular on CNP fraud prevention
            "CNP":                 45,   # Card Not Present — highest CC risk
            "CASH_ADVANCE":        55,   # Capped at module max
            "EMI_CONVERSION":      25,
            "REWARD_REDEMPTION":   30,
            "BALANCE_TRANSFER":    35,
        }

        # ── MCC Risk Tiers (PCI DSS / RBI CC Directions) ────────────
        # Tier 1 HIGH RISK: +20 pts
        self.mcc_tier1 = {
            "6011",  # ATM cash disbursements
            "6051",  # Quasi-cash merchants
            "7995",  # Gambling transactions
            "9222",  # Fines and penalties
            "4829",  # Wire transfer money orders
        }
        # Tier 2 MEDIUM RISK: +10 pts
        self.mcc_tier2 = {
            "5411",  # Grocery stores
            "5912",  # Drug stores/pharmacies
            "5999",  # Miscellaneous retail
            "7011",  # Hotels and lodging
            "4111",  # Local/suburban commuter transport
        }
        # Tier 3 LOW RISK: +0 pts (explicit allowlist for documentation)
        self.mcc_tier3 = {
            "5812",  # Eating places/restaurants
            "7372",  # Computer programming services
            "8011",  # Doctors and physicians
            "5945",  # Hobby, toy and game shops
        }

    # ────────────────────────────────────────────────────────────────
    # Internal helpers
    # ────────────────────────────────────────────────────────────────

    def _get_mcc_score(self, mcc):
        """Returns (additional_score, tier_label) for a given MCC code."""
        if not mcc:
            return 0, None
        mcc = str(mcc).strip()
        if mcc in self.mcc_tier1:
            return 20, "TIER1"
        if mcc in self.mcc_tier2:
            return 10, "TIER2"
        if mcc in self.mcc_tier3:
            return 0, "TIER3"
        return 0, None   # Unknown MCC — no additional score

    # ────────────────────────────────────────────────────────────────
    # Escalation rule checks
    # ────────────────────────────────────────────────────────────────

    def check_escalation_rules(self, tx_data):
        """
        Checks for specific escalation rules.
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

    def _check_credit_card_rules(self, tx_data, rules_fired):
        """
        Evaluate credit card-specific rules and append rule IDs to rules_fired.
        Returns additional score from CC rules.
        """
        tx_type = tx_data.get("transaction_type")
        amount  = tx_data.get("amount", tx_data.get("transaction_amount", 0))
        additional = 0

        # CC-CNP-HIGH-RISK: CNP + international merchant or high amount
        if tx_type == "CNP":
            sender  = tx_data.get("sender_country", "")
            receiver = tx_data.get("receiver_country", "")
            is_intl = sender != receiver
            is_high = float(amount) > 10000
            if is_intl or is_high:
                rules_fired.append("CC-CNP-HIGH-RISK")
                additional += 10

        # CC-CASH-ADVANCE-RISK: any cash advance
        if tx_type == "CASH_ADVANCE":
            rules_fired.append("CC-CASH-ADVANCE-RISK")
            additional += 5

        # CC-EMI-STRUCTURING: multiple EMI conversions same day
        # Note: full detection requires history; here we use a flag from tx_data
        if tx_type == "EMI_CONVERSION" and tx_data.get("multiple_emi_same_day"):
            rules_fired.append("CC-EMI-STRUCTURING")
            additional += 15

        return additional

    # ────────────────────────────────────────────────────────────────
    # Main entry point
    # ────────────────────────────────────────────────────────────────

    def get_module_result(self, tx_data):
        """
        Main entry point for the Transaction Type module.
        Accepts optional 'mcc' field in tx_data for MCC-tier scoring.
        """
        tx_type    = tx_data.get("transaction_type")
        mcc        = tx_data.get("mcc")
        rules_fired = []

        # Base score from type taxonomy
        base_score = self.type_scores.get(tx_type, 15)

        # MCC tier score addition
        mcc_addition, mcc_tier = self._get_mcc_score(mcc)
        if mcc_tier == "TIER1":
            rules_fired.append("CC-MCC-TIER1")
        elif mcc_tier == "TIER2":
            rules_fired.append("CC-MCC-TIER2")

        # Credit card rule additions
        cc_additional = self._check_credit_card_rules(tx_data, rules_fired)

        # Sum and cap
        raw_score = base_score + mcc_addition + cc_additional
        if raw_score > self.module_maximum:
            raw_score = self.module_maximum

        # Standard escalation checks
        is_alert, alert_reason = self.check_escalation_rules(tx_data)

        normalised_score = raw_score / self.module_maximum

        return {
            "raw_score":        raw_score,
            "normalised_score": normalised_score,
            "is_auto_alert":    is_alert,
            "alert_reason":     alert_reason,
            "rules_fired":      rules_fired,
            "mcc":              mcc,
            "mcc_tier":         mcc_tier,
        }


# ── Standalone test ─────────────────────────────────────────────────
if __name__ == "__main__":
    engine = TransactionModule()

    # Test 1: Crypto
    print("Crypto:", engine.get_module_result({"transaction_type": "Cryptocurrency Transaction"}))

    # Test 2: CNP + international + MCC 6011
    cnp_data = {
        "transaction_type": "CNP",
        "amount": 15000,
        "sender_country": "IN",
        "receiver_country": "US",
        "mcc": "6011"
    }
    result = engine.get_module_result(cnp_data)
    print(f"\nCNP + MCC 6011: raw={result['raw_score']}  rules={result['rules_fired']}")

    # Test 3: Cash Advance
    result = engine.get_module_result({"transaction_type": "CASH_ADVANCE"})
    print(f"\nCash Advance: raw={result['raw_score']}  rules={result['rules_fired']}")

    # Test 4: EMI structuring
    result = engine.get_module_result({
        "transaction_type": "EMI_CONVERSION",
        "multiple_emi_same_day": True
    })
    print(f"\nEMI Structuring: raw={result['raw_score']}  rules={result['rules_fired']}")

    # Test 5: Insurance escalation
    ins_data = {
        "transaction_type": "Insurance Premium Payment",
        "is_early_surrender": True,
        "refund_to_third_party": True,
    }
    print(f"\nInsurance ML: {engine.get_module_result(ins_data)}")
