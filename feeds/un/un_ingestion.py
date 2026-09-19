import os
import sys
import json
import datetime
import requests
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LATEST_FILE = os.path.join(BASE_DIR, "un_latest.json")
PREVIOUS_FILE = os.path.join(BASE_DIR, "un_previous.json")
LOG_FILE = os.path.join(BASE_DIR, "un_delta_log.txt")

UN_URL = "https://scsanctions.un.org/resources/xml/en/consolidated.xml"

def fetch_and_parse():
    print("Downloading UN Consolidated XML...")
    try:
        response = requests.get(UN_URL, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Error downloading UN list: {e}")
        return None

    print("Parsing UN Consolidated XML...")
    try:
        root = ET.fromstring(response.content)
        
        entries = []
        
        # UN XML has INDIVIDUALS and ENTITIES elements
        for category in ['INDIVIDUALS/INDIVIDUAL', 'ENTITIES/ENTITY']:
            for node in root.findall(category):
                uid = node.findtext('DATAID', default='')
                
                # Combine name parts for individuals
                name_parts = []
                for p in ['FIRST_NAME', 'SECOND_NAME', 'THIRD_NAME', 'FOURTH_NAME']:
                    part = node.findtext(p)
                    if part:
                        name_parts.append(part.strip())
                name = " ".join(name_parts).strip()
                
                # Entity type
                entity_type = "INDIVIDUAL" if "INDIVIDUAL" in category else "ENTITY"
                
                un_ref = node.findtext('REFERENCE_NUMBER', default='')
                date_listed = node.findtext('LISTED_ON', default='')
                committee = node.findtext('UN_LIST_TYPE', default='')
                
                aliases = []
                # Individual aliases
                for aka in node.findall('INDIVIDUAL_ALIAS/ALIAS_NAME'):
                    if aka.text: aliases.append(aka.text.strip())
                # Entity aliases
                for aka in node.findall('ENTITY_ALIAS/ALIAS_NAME'):
                    if aka.text: aliases.append(aka.text.strip())
                    
                remarks = node.findtext('COMMENTS1', default='')

                entries.append({
                    "id": uid,
                    "name": name,
                    "aliases": aliases,
                    "entity_type": entity_type,
                    "program": committee,
                    "designation_date": date_listed,
                    "remarks": remarks
                })

        return {
            "list_name": "UN Consolidated List",
            "regulatory_basis": "UN Security Council",
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d"),
            "source_url": UN_URL,
            "entries": entries
        }
    except Exception as e:
        print(f"Error parsing UN list: {e}")
        return None

def run_ingestion():
    new_data = fetch_and_parse()
    if not new_data:
        return

    # Load previous data
    prev_entries = {}
    if os.path.exists(LATEST_FILE):
        import shutil
        shutil.copy2(LATEST_FILE, PREVIOUS_FILE)
        with open(PREVIOUS_FILE, 'r', encoding='utf-8') as f:
            try:
                prev_data = json.load(f)
                for entry in prev_data.get("entries", []):
                    prev_entries[entry["id"]] = entry
            except json.JSONDecodeError:
                pass

    new_entries = {e["id"]: e for e in new_data["entries"]}

    added = []
    removed = []

    for uid, entry in new_entries.items():
        if uid not in prev_entries:
            added.append(entry)

    for uid, entry in prev_entries.items():
        if uid not in new_entries:
            removed.append(entry)

    # Log delta
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if added or removed:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            for item in added:
                f.write(f"[{now}] ADDED: {item['name']} (ID: {item['id']})\n")
            for item in removed:
                f.write(f"[{now}] REMOVED: {item['name']} (ID: {item['id']})\n")

    # Save latest
    with open(LATEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2)

    print(f"UN update complete \u2014 {len(new_entries)} entries, {len(added)} new, {len(removed)} removed")

if __name__ == "__main__":
    run_ingestion()
