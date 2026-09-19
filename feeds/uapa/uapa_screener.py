import os
import json
from rapidfuzz import process, fuzz

# Paths to the JSON data files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES = {
    "SCHEDULE_4": os.path.join(BASE_DIR, "uapa_schedule4.json"),
    "SCHEDULE_1": os.path.join(BASE_DIR, "uapa_schedule1.json"),
    "UNSC_1267": os.path.join(BASE_DIR, "unsc_1267_isil_alqaida.json"),
    "UNSC_1988": os.path.join(BASE_DIR, "unsc_1988_taliban.json")
}

_LIST_DATA = {}

def load_data():
    """Loads all JSON files on startup."""
    for key, path in FILES.items():
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                _LIST_DATA[key] = json.load(f)
        else:
            _LIST_DATA[key] = {"entries": [], "list_name": "", "regulatory_basis": ""}

# Load data on module import
load_data()

def screen_uapa(name, entity_type):
    """
    Screens a name against UAPA lists using fuzzy matching (85% threshold).
    Priority order: SCHEDULE_4, SCHEDULE_1, UNSC_1267, UNSC_1988
    """
    if not name or not isinstance(name, str):
        return _get_empty_result()
    
    threshold = 85.0
    priorities = ["SCHEDULE_4", "SCHEDULE_1", "UNSC_1267", "UNSC_1988"]
    
    best_match = None
    
    for list_key in priorities:
        list_data = _LIST_DATA.get(list_key, {})
        entries = list_data.get("entries", [])
        
        for entry in entries:
            names_to_check = [entry.get("name")] + entry.get("aliases", [])
            
            # Extract valid names
            valid_names = [n for n in names_to_check if n and isinstance(n, str)]
            if not valid_names:
                continue
                
            # Perform fuzzy matching
            # We use process.extractOne to get the best match for the input name against the valid names
            res = process.extractOne(name, valid_names, scorer=fuzz.WRatio)
            
            if res:
                matched_str, score, _ = res
                if score >= threshold:
                    # Update best match if this is higher or it's the first we found in this list
                    if best_match is None or score > best_match["match_score"]:
                        is_alias = matched_str != entry.get("name")
                        best_match = {
                            "match_found": True,
                            "match_type": list_key,
                            "matched_name": entry.get("name"),
                            "matched_alias": matched_str if is_alias else "",
                            "match_score": round(score, 2),
                            "list_name": list_data.get("list_name", ""),
                            "regulatory_basis": list_data.get("regulatory_basis", ""),
                            "mandatory_actions": ["FREEZE_ACCOUNT", "REPORT_FIU_IND", "ADVISE_MHA"]
                        }
        
        # Since we search in priority order, if we find a match in a higher priority list, we return immediately.
        # Wait, the prompt says "Return the highest confidence match found" but also "Screen against all four lists in this priority order...". 
        # Usually priority means if a match is found in Schedule 4, we don't need to check Schedule 1.
        if best_match:
            return best_match
            
    return _get_empty_result()

def _get_empty_result():
    return {
        "match_found": False,
        "match_type": "NONE",
        "matched_name": "",
        "matched_alias": "",
        "match_score": 0,
        "list_name": "",
        "regulatory_basis": "",
        "mandatory_actions": []
    }
