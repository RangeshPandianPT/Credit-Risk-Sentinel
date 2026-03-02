
import sys
import os
import json
import shutil
from pathlib import Path

# Add parent directory to path to import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.phase3_risk_api import FileBasedCache, FileBasedSNS

def test_file_based_cache():
    print("Testing FileBasedCache...")
    test_file = "data/test_store.json"
    if os.path.exists(test_file):
        os.remove(test_file)
    
    cache = FileBasedCache(filename=test_file)
    
    # Test built-in defaults
    hr_key = "high_risk_customers"
    data = cache.get(hr_key)
    if data:
        print("✅ Defaults loaded successfully")
    else:
        print("❌ Defaults failed to load")

    # Test set/get
    cache.set("foo", "bar")
    
    cache2 = FileBasedCache(filename=test_file)
    if cache2.get("foo") == "bar":
        print("✅ Persistence working")
    else:
        print("❌ Persistence failed")
        
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)

def test_file_based_sns():
    print("\nTesting FileBasedSNS...")
    log_file = "logs/sns_events.jsonl"
    # Backup existing log
    backup = None
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            backup = f.read()
        os.remove(log_file)
        
    sns = FileBasedSNS()
    sns.publish("arn:aws:sns:region:123:topic", "Hello World", "Test Subject")
    
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            content = f.read()
            if "Hello World" in content:
                print("✅ SNS Log written successfully")
            else:
                print("❌ SNS Log content mismatch")
    else:
        print("❌ SNS Log file not created")

    # Restore
    if backup:
        with open(log_file, 'w') as f:
            f.write(backup)

if __name__ == "__main__":
    try:
        test_file_based_cache()
        test_file_based_sns()
    except ImportError as e:
        print(f"Skipping tests due to missing dependencies: {e}")
    except Exception as e:
        print(f"Test failed: {e}")
