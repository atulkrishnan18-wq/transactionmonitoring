"""
ScoreSentinel Geography Module (v1.1)
Part of the ScoreSentinel AML Transaction Risk Scoring Engine
Authored by Atul Krishnan, CAMS | Day 22 of 60
"""

class GeoModule:
    """
    Implements geographic risk and sanctions screening rules as defined in GEO_RULES.md.
    """

    def __init__(self):
        # Module Maximum for normalization as defined in COMPOSITE_LOGIC.md
        self.module_maximum = 100
        
        # Tier 1A: OFAC Sanctioned AND FATF Black Listed (+50 | AUTO-ALERT)
        self.tier_1a = ["Iran", "North Korea", "Myanmar"]
        
        # Tier 1B: OFAC Sanctioned (+40 | AUTO-ALERT)
        self.tier_1b = ["Syria", "Cuba", "Russia", "Belarus", "Venezuela"]
        
        # Tier 1C: FATF Grey List (+25)
        self.tier_1c = [
            "Afghanistan", "Algeria", "Angola", "Bolivia", "Bulgaria", 
            "Cameroon", "Côte d'Ivoire", "DR Congo", "Haiti", "Kenya", 
            "Kuwait", "Laos", "Lebanon", "Monaco", "Namibia", "Nepal", 
            "Papua New Guinea", "South Sudan", "Syria", "Venezuela", 
            "Vietnam", "British Virgin Islands", "Yemen"
        ]
        
        # Tier 2A: High Corruption Risk (CPI 0–29) (+20)
        self.tier_2a = [
            "Somalia", "North Korea", "South Sudan", "Syria", "Venezuela", 
            "Yemen", "Equatorial Guinea", "Libya", "Haiti", "DR Congo", 
            "Afghanistan", "Sudan", "Burundi", "Cambodia", "Eritrea", 
            "Bangladesh", "Bolivia", "Nigeria", "Pakistan", "Kyrgyzstan", 
            "Tajikistan", "Laos", "Lebanon"
        ]
        
        # Tier 2B: Elevated Corruption Risk (CPI 30–49) (+15)
        self.tier_2b = [
            "China", "India", "Indonesia", "Kenya", "Malaysia", "Mexico", 
            "Egypt", "Ecuador", "Uzbekistan", "South Africa", "Tanzania", 
            "Philippines"
        ]
        
        # Tier 3: Offshore / Secrecy Jurisdictions (+15)
        self.tier_3 = [
            "Cayman Islands", "British Virgin Islands", "Panama", 
            "Seychelles", "Vanuatu", "Cyprus", "Switzerland"
        ]

    def calculate_country_score(self, country):
        """
        Calculates the cumulative score for a single country.
        Returns (score, is_auto_alert)
        """
        score = 0
        is_auto_alert = False
        
        if country in self.tier_1a:
            score += 50
            is_auto_alert = True
        
        if country in self.tier_1b:
            score += 40
            is_auto_alert = True
            
        if country in self.tier_1c:
            score += 25
            
        if country in self.tier_2a:
            score += 20
            
        if country in self.tier_2b:
            score += 15
            
        if country in self.tier_3:
            score += 15
            
        return score, is_auto_alert

    def get_geo_score(self, sender_country, receiver_country):
        """
        Calculates the geographic risk score for a transaction.
        Assessed on BOTH sender and receiver countries.
        """
        sender_score, sender_alert = self.calculate_country_score(sender_country)
        receiver_score, receiver_alert = self.calculate_country_score(receiver_country)
        
        total_raw_score = sender_score + receiver_score
        is_auto_alert = sender_alert or receiver_alert
        
        # SR 11-7 Validation Rule: Cap at module maximum before normalisation
        if total_raw_score > self.module_maximum:
            total_raw_score = self.module_maximum
            
        normalised_score = (total_raw_score / self.module_maximum)
        
        return {
            "raw_score": total_raw_score,
            "normalised_score": normalised_score,
            "is_auto_alert": is_auto_alert,
            "sender": {"country": sender_country, "score": sender_score, "is_auto_alert": sender_alert},
            "receiver": {"country": receiver_country, "score": receiver_score, "is_auto_alert": receiver_alert}
        }

if __name__ == "__main__":
    engine = GeoModule()
    
    # Test Example: India to Cayman
    # India (Tier 2B: +15) + Cayman (Tier 3: +15) = 30
    result = engine.get_geo_score("India", "Cayman Islands")
    print(f"India to Cayman: {result['raw_score']} (Expected: 30)")
    
    # Test Example: Lebanon to BVI
    # Lebanon (Tier 1C: +25 + Tier 2A: +20 = 45)
    # BVI (Tier 1C: +25 + Tier 3: +15 = 40)
    # Total = 85
    result2 = engine.get_geo_score("Lebanon", "British Virgin Islands")
    print(f"Lebanon to BVI: {result2['raw_score']} (Expected: 85)")
    
    # Test Example: Any to Iran
    result3 = engine.get_geo_score("United Kingdom", "Iran")
    print(f"UK to Iran: {result3['raw_score']}, Auto-Alert: {result3['is_auto_alert']}")
