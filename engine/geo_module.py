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
        
        # Tier 1A: OFAC Sanctioned AND FATF Black Listed (+100 | AUTO-ALERT)
        self.tier_1a = ["Iran", "North Korea", "Myanmar"]
        
        # Tier 1B: OFAC Sanctioned (+100 | AUTO-ALERT)
        self.tier_1b = ["Syria", "Cuba", "Russia", "Belarus", "Venezuela"]
        
        # Tier 1C: FATF Grey List (+25)
        self.tier_1c = [
            "Afghanistan", "Algeria", "Angola", "Bolivia", "Bulgaria", 
            "Cameroon", "Côte d'Ivoire", "DR Congo", "Haiti", "Kenya", 
            "Kuwait", "Laos", "Lebanon", "Monaco", "Namibia", "Nepal", 
            "Papua New Guinea", "South Sudan", "Vietnam", "Yemen",
            "Nigeria", "Pakistan", "South Africa"
        ]
        
        # Tier 2A: High Corruption Risk (CPI 0–29) (+20)
        self.tier_2a = [
            "Somalia", "South Sudan", "Syria", "Venezuela", 
            "Yemen", "Equatorial Guinea", "Libya", "Haiti", "DR Congo", 
            "Afghanistan", "Sudan", "Burundi", "Cambodia", "Eritrea", 
            "Bangladesh", "Bolivia", "Pakistan", "Kyrgyzstan", 
            "Tajikistan", "Laos", "Lebanon"
        ]
        
        # Tier 2B: Elevated Corruption Risk (CPI 30–49) (+15)
        self.tier_2b = [
            "China", "India", "Indonesia", "Kenya", "Malaysia", "Mexico", 
            "Egypt", "Ecuador", "Uzbekistan", "South Africa", "Tanzania", 
            "Philippines", "Nigeria"
        ]
        
        # Tier 3: Offshore / Secrecy Jurisdictions (+15)
        self.tier_3 = [
            "Cayman Islands", "British Virgin Islands", "Panama", 
            "Seychelles", "Vanuatu", "Cyprus", "Switzerland", "UAE"
        ]

        # Special Secrecy Premium (+10)
        self.tier_secrecy_premium = ["British Virgin Islands"]
        
        # CPI based risk adjustments for specific scenarios
        # Cayman CPI-based risk adjustment (+40)
        self.tier_cpi_adjustment_40 = ["Cayman Islands"]
        # Nigeria/Pakistan CPI Tier 2B adjustment (+15) or CPI 25 score (+20)
        # We use the tier_2a/2b for these.

        # High-Risk Currencies
        self.high_risk_currencies = {
            "RUB": 25,  # Russian Ruble (Sanctions evasion / capital flight risk)
            "SAR": 15,  # Saudi Riyal (Regional corruption / illicit finance corridor)
            "IRR": 50,  # Iranian Rial (Sanctioned jurisdiction)
            "KPW": 50,  # North Korean Won (Sanctioned jurisdiction)
            "SYP": 50,  # Syrian Pound (Sanctioned jurisdiction)
        }

        # ISO-2 aliases — API validates 2-letter codes; IBM ingestion sends ISO-2.
        self.iso_map = {
            "US": "United States", "GB": "United Kingdom", "UK": "United Kingdom",
            "DE": "Germany", "CN": "China", "AE": "UAE", "SG": "Singapore",
            "IN": "India", "HK": "Hong Kong", "JP": "Japan",
            "IR": "Iran", "KP": "North Korea", "MM": "Myanmar",
            "SY": "Syria", "CU": "Cuba", "RU": "Russia", "BY": "Belarus",
            "VE": "Venezuela", "PK": "Pakistan", "NG": "Nigeria",
            "ZA": "South Africa", "AF": "Afghanistan", "YE": "Yemen",
            "KY": "Cayman Islands", "VG": "British Virgin Islands",
            "PA": "Panama", "CY": "Cyprus", "CH": "Switzerland",
        }

    def _resolve_country(self, country):
        if not country or not isinstance(country, str):
            return country
        mapped = self.iso_map.get(country.strip().upper())
        return mapped if mapped else country

    def calculate_country_score(self, country):
        """
        Calculates the cumulative score for a single country.
        Returns (score, is_auto_alert)
        """
        country = self._resolve_country(country)
        score = 0
        is_auto_alert = False
        
        if country in self.tier_1a:
            score += 100 # Iran/NK are 100 in scenarios
            is_auto_alert = True
        elif country in self.tier_1b:
            score += 100 # Russia/Syria are 100 in scenarios
            is_auto_alert = True
        else:
            if country in self.tier_1c:
                score += 25
            
            if country in self.tier_2a:
                score += 20
            
            if country in self.tier_2b:
                score += 15
            
            if country in self.tier_3:
                score += 15
                
            if country in self.tier_secrecy_premium:
                score += 10
                
            if country in self.tier_cpi_adjustment_40:
                score += 40
            
        return score, is_auto_alert

    def get_geo_score(self, sender_country, receiver_country, currency=None):
        """
        Calculates the geographic risk score for a transaction.
        Assessed on BOTH sender and receiver countries, plus currency risk.
        """
        sender_score, sender_alert = self.calculate_country_score(sender_country)
        receiver_score, receiver_alert = self.calculate_country_score(receiver_country)
        
        currency_code = str(currency).strip().upper() if currency else None
        currency_score = self.high_risk_currencies.get(currency_code, 0) if currency_code else 0
        
        total_raw_score = sender_score + receiver_score + currency_score
        is_auto_alert = sender_alert or receiver_alert
        
        # SR 11-7 Validation Rule: Cap at module maximum before normalisation
        if total_raw_score > self.module_maximum:
            total_raw_score = self.module_maximum
            
        normalised_score = (total_raw_score / self.module_maximum)
        
        return {
            "raw_score": total_raw_score,
            "normalised_score": normalised_score,
            "is_auto_alert": is_auto_alert,
            "currency_risk": {"currency": currency, "score": currency_score},
            "sender": {"country": sender_country, "score": sender_score, "is_auto_alert": sender_alert},
            "receiver": {"country": receiver_country, "score": receiver_score, "is_auto_alert": receiver_alert}
        }
if __name__ == "__main__":
    engine = GeoModule()
    
    # Test Scenario 9: Nigeria (1C+2B=40) to BVI (3+Secrecy=25) = 65
    result = engine.get_geo_score("Nigeria", "British Virgin Islands")
    print(f"Nigeria to BVI: {result['raw_score']} (Expected: 65)")
    
    # Test Scenario 2: UK (0) to Cayman (3+CPI=55) = 55
    result2 = engine.get_geo_score("United Kingdom", "Cayman Islands")
    print(f"UK to Cayman: {result2['raw_score']} (Expected: 55)")

    # Test Scenario 13: Pakistan (1C+2A=45) to UK (0) = 45
    result3 = engine.get_geo_score("Pakistan", "United Kingdom")
    print(f"Pakistan to UK: {result3['raw_score']} (Expected: 45)")
