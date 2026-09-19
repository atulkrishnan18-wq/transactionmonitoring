import os
import sys

# Ensure modules can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from feeds.uapa.uapa_screener import screen_uapa
from feeds.ofac.ofac_screener import screen_ofac
from feeds.un.un_screener import screen_un

def screen_all_sanctions(name, entity_type):
    """
    Screens against all sanctions lists in priority order:
    1. UAPA Schedule 4
    2. UAPA Schedule 1
    3. UNSC 1267 (via UAPA module)
    4. UNSC 1988 (via UAPA module)
    5. OFAC SDN
    6. UN Consolidated
    """
    
    lists_checked = [
        "UAPA_SCHEDULE_4", 
        "UAPA_SCHEDULE_1", 
        "UNSC_1267", 
        "UNSC_1988", 
        "OFAC_SDN", 
        "UN_CONSOLIDATED"
    ]
    
    # Check UAPA module which handles Schedule 4, Schedule 1, UNSC 1267, UNSC 1988
    uapa_result = screen_uapa(name, entity_type)
    if uapa_result.get("match_found"):
        uapa_result["lists_checked"] = lists_checked
        return uapa_result
        
    # Check OFAC SDN
    ofac_result = screen_ofac(name, entity_type)
    if ofac_result.get("match_found"):
        ofac_result["lists_checked"] = lists_checked
        return ofac_result
        
    # Check UN Consolidated
    un_result = screen_un(name, entity_type)
    if un_result.get("match_found"):
        un_result["lists_checked"] = lists_checked
        return un_result
        
    return {
        "match_found": False,
        "match_type": "NONE",
        "matched_name": "",
        "matched_alias": "",
        "match_score": 0,
        "list_name": "",
        "regulatory_basis": "",
        "mandatory_actions": [],
        "lists_checked": lists_checked
    }
