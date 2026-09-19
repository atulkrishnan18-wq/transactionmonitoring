import os
import datetime
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEEN_FILE = os.path.join(BASE_DIR, "uapa_circulars_seen.txt")
LOG_FILE = os.path.join(BASE_DIR, "uapa_update_log.txt")
ALERT_FILE = os.path.join(BASE_DIR, "uapa_update_required.txt")

RBI_URL = "https://rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx"

def check_for_updates():
    try:
        response = requests.get(RBI_URL, timeout=10)
        response.raise_for_status()
        content = response.text
    except Exception as e:
        print(f"Failed to fetch RBI circulars: {e}")
        return

    # For simplicity, we split by lines or look for "UAPA" in text blocks.
    # In a real HTML parser (like BeautifulSoup), we'd extract specific links.
    # Here we just look for lines containing "UAPA".
    
    seen_circulars = set()
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            for line in f:
                seen_circulars.add(line.strip())
                
    new_circulars = []
    
    # Very basic parsing: look for lines containing UAPA
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "UAPA" in line:
            # Try to extract a clean string from the line if it's HTML
            clean_text = line.replace("<", " <").replace(">", "> ").strip()
            # Simple deduplication
            if clean_text not in seen_circulars:
                new_circulars.append(clean_text)
                
    if new_circulars:
        print("NEW UAPA CIRCULAR DETECTED — MANUAL LIST UPDATE REQUIRED")
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            for circ in new_circulars:
                f.write(f"[{now}] Found potential UAPA circular: {circ}\n")
                
        with open(ALERT_FILE, "w", encoding="utf-8") as f:
            f.write(f"Date detected: {now}\n")
            f.write("New UAPA circular(s) detected on RBI website:\n")
            for circ in new_circulars:
                f.write(f"- {circ}\n")
                
        with open(SEEN_FILE, "a", encoding="utf-8") as f:
            for circ in new_circulars:
                f.write(f"{circ}\n")
    else:
        print("No new UAPA circulars detected.")

if __name__ == "__main__":
    check_for_updates()
