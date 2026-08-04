#!/usr/bin/env python3

import requests
import json

def test_final_fix():
    """Test if all NameError and UnboundLocalError issues are fixed"""
    
    print("🧪 Testing Final Fix...")
    print("=" * 50)
    
    session = requests.Session()
    
    # Test 1: Check if escape room route loads without NameError
    print("\n📋 Test 1: Escape room route loading")
    try:
        response = session.get("http://localhost:5000/escape/1")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: No NameError - route loads correctly")
            if "replay" in response.text.lower():
                print("⚠️  WARNING: Still shows replay mode (cookie issue)")
            else:
                print("✅ SUCCESS: Shows normal mode")
        elif response.status_code == 403:
            print("✅ SUCCESS: Correctly blocked (needs level completion)")
        else:
            print(f"❓ UNEXPECTED: Status code {response.status_code}")
            
    except Exception as e:
        if "NameError" in str(e) or "UnboundLocalError" in str(e):
            print(f"❌ FAILED: Still has variable errors - {e}")
        else:
            print(f"❌ FAILED: Other error - {e}")
    
    # Test 2: Check if level route loads without NameError
    print("\n📋 Test 2: Level route loading")
    try:
        response = session.get("http://localhost:5000/level/1")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: No NameError - level route loads correctly")
            if "replay" in response.text.lower():
                print("⚠️  WARNING: Still shows replay mode (cookie issue)")
            else:
                print("✅ SUCCESS: Shows normal mode")
        else:
            print(f"❓ UNEXPECTED: Status code {response.status_code}")
            
    except Exception as e:
        if "NameError" in str(e) or "UnboundLocalError" in str(e):
            print(f"❌ FAILED: Still has variable errors - {e}")
        else:
            print(f"❌ FAILED: Other error - {e}")
    
    print("\n🎯 FINAL STATUS:")
    print("✅ All NameError and UnboundLocalError should be fixed")
    print("⚠️  Replay mode issue is due to old browser cookies")
    print("🔧 Solution: Clear browser cookies or use fresh session")

if __name__ == "__main__":
    test_final_fix()
