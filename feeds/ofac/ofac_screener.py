import os
import json
from rapidfuzz import process, fuzz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LATEST_FILE = os.path.join(BASE_DIR, "ofac_latest.json")

_LIST_DATA = {}

def load_data():
    if os.path.exists(LATEST_FILE):
        with open(LATEST_FILE, "r", encoding="utf-8") as f:
            _LIST_DATA.update(json.load(f))

load_data()

def screen_ofac(name, entity_type):
    if not name or not isinstance(name, str):
        return _get_empty_result()
    
    threshold = 85.0
    entries = _LIST_DATA.get("entries", [])
    
    best_match = None
    
    for entry in entries:
        names_to_check = [entry.get("name")] + entry.get("aliases", [])
        valid_names = [n for n in names_to_check if n and isinstance(n, str)]
        if not valid_names:
            continue
            
        res = process.extractOne(name, valid_names, scorer=fuzz.WRatio)
        if res:
            matched_str, score, _ = res
            if score >= threshold:
                if best_match is None or score > best_match["match_score"]:
                    is_alias = matched_str != entry.get("name")
                    best_match = {
                        "match_found": True,
                        "match_type": "OFAC_SDN",
                        "matched_name": entry.get("name"),
                        "matched_alias": matched_str if is_alias else "",
                        "match_score": round(score, 2),
                        "list_name": _LIST_DATA.get("list_name", "OFAC SDN List"),
                        "regulatory_basis": _LIST_DATA.get("regulatory_basis", "US Treasury OFAC"),
                        "mandatory_actions": ["FREEZE_ACCOUNT", "REPORT_FIU_IND", "DO_NOT_TRANSACT", "NOTIFY_COMPLIANCE_OFFICER"]
                    }
                    
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
