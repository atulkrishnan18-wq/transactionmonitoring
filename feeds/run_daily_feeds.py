import os
import sys
import datetime
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_script(script_path):
    print(f"Running {os.path.basename(script_path)}...")
    try:
        result = subprocess.run([sys.executable, script_path], check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors/Warnings:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to run {os.path.basename(script_path)}")
        print(e.stdout)
        print(e.stderr)
        return False

def count_entries(json_path):
    import json
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return len(data.get("entries", []))
        except:
            pass
    return 0

def main():
    print(f"Starting daily feeds update at {datetime.datetime.now()}")
    
    ofac_script = os.path.join(BASE_DIR, "ofac", "ofac_ingestion.py")
    un_script = os.path.join(BASE_DIR, "un", "un_ingestion.py")
    uapa_script = os.path.join(BASE_DIR, "uapa", "uapa_updater.py")
    
    run_script(ofac_script)
    run_script(un_script)
    run_script(uapa_script)
    
    ofac_count = count_entries(os.path.join(BASE_DIR, "ofac", "ofac_latest.json"))
    un_count = count_entries(os.path.join(BASE_DIR, "un", "un_latest.json"))
    
    print(f"Daily feed update complete \u2014 OFAC: {ofac_count} entries, UN: {un_count} entries, UAPA: manually maintained")

if __name__ == "__main__":
    main()
