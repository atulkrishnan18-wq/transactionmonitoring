import os
import sys
import json
import datetime
import requests
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LATEST_FILE = os.path.join(BASE_DIR, "ofac_latest.json")
PREVIOUS_FILE = os.path.join(BASE_DIR, "ofac_previous.json")
LOG_FILE = os.path.join(BASE_DIR, "ofac_delta_log.txt")

OFAC_URL = "https://www.treasury.gov/ofac/downloads/sdn.xml"
OFAC_NS = {'ns': 'http://tempuri.org/sdnList.xsd'}

def fetch_and_parse():
    print("Downloading OFAC SDN XML...")
    try:
        response = requests.get(OFAC_URL, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Error downloading OFAC list: {e}")
        return None

    print("Parsing OFAC SDN XML...")
    try:
        root = ET.fromstring(response.content)
        
        entries = []
        for sdn in root.findall('ns:sdnEntry', OFAC_NS):
            uid = sdn.findtext('ns:uid', default='', namespaces=OFAC_NS)
            first_name = sdn.findtext('ns:firstName', default='', namespaces=OFAC_NS)
            last_name = sdn.findtext('ns:lastName', default='', namespaces=OFAC_NS)
            
            name = f"{first_name} {last_name}".strip() if first_name else last_name
            
            sdn_type = sdn.findtext('ns:sdnType', default='', namespaces=OFAC_NS)
            program_list = sdn.find('ns:programList', OFAC_NS)
            program = ""
            if program_list is not None:
                program_node = program_list.find('ns:program', OFAC_NS)
                if program_node is not None:
                    program = program_node.text
                    
            aka_list = sdn.find('ns:akaList', OFAC_NS)
            aliases = []
            if aka_list is not None:
                for aka in aka_list.findall('ns:aka', OFAC_NS):
                    aka_first = aka.findtext('ns:firstName', default='', namespaces=OFAC_NS)
                    aka_last = aka.findtext('ns:lastName', default='', namespaces=OFAC_NS)
                    alias_name = f"{aka_first} {aka_last}".strip() if aka_first else aka_last
                    if alias_name:
                        aliases.append(alias_name)
                        
            remarks = sdn.findtext('ns:remarks', default='', namespaces=OFAC_NS)

            entries.append({
                "id": uid,
                "name": name,
                "aliases": aliases,
                "entity_type": sdn_type,
                "program": program,
                "designation_date": "",
                "remarks": remarks
            })

        return {
            "list_name": "OFAC SDN List",
            "regulatory_basis": "US Treasury OFAC",
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d"),
            "source_url": OFAC_URL,
            "entries": entries
        }
    except Exception as e:
        print(f"Error parsing OFAC list: {e}")
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

    print(f"OFAC update complete \u2014 {len(new_entries)} entries, {len(added)} new, {len(removed)} removed")

if __name__ == "__main__":
    run_ingestion()
