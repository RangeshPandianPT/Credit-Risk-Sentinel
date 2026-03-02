
import requests
import time
import json
import os

API_URL = "http://127.0.0.1:8000"
LOG_FILE = "logs/sns_events.jsonl"

def wait_for_api():
    print("Waiting for API to be ready...")
    for _ in range(10):
        try:
            requests.get(f"{API_URL}/docs")
            print("API is ready.")
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    print("API failed to start.")
    return False

def trigger_alert():
    print("Triggering alert via POST /notify...")
    payload = {
        "customerId": 100045, # Alicia W. (High Risk)
        "action": "call",
        "reason": "Test Alert from Verification Script"
    }
    try:
        response = requests.post(f"{API_URL}/notify", json=payload)
        if response.status_code == 200:
            print(f"Triggered successfully: {response.json()}")
            return True
        else:
            print(f"Failed to trigger: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error triggering alert: {e}")
        return False

def verify_log():
    print(f"Verifying log entry in {LOG_FILE}...")
    if not os.path.exists(LOG_FILE):
        print(f"Log file {LOG_FILE} does not exist.")
        return False
        
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            if not lines:
                print("Log file is empty.")
                return False
            
            # Check the last few lines for our payload
            found = False
            for line in reversed(lines):
                entry = json.loads(line)
                msg = json.loads(entry.get("Message", "{}"))
                if msg.get("customer_id") == 100045 and msg.get("reason") == "Test Alert from Verification Script":
                    print("✅ Verification Successful: Found alert in log file.")
                    found = True
                    break
            
            if not found:
                print("❌ Verification Failed: Alert not found in log file.")
                return False
            return True
    except Exception as e:
        print(f"Error reading log file: {e}")
        return False

if __name__ == "__main__":
    if wait_for_api():
        if trigger_alert():
            time.sleep(1) # Wait for file write
            verify_log()
