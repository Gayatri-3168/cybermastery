#!/usr/bin/env python3

import requests
import json

def test_fresh_employee_access():
    """Test fresh employee access to escape room"""
    
    print("🧪 Testing Fresh Employee Access...")
    print("=" * 50)
    
    session = requests.Session()
    
    # Clear all cookies by creating a new session
    print("\n🗑️ Clearing all cookies...")
    
    # Test 1: Try to access escape room as fresh employee
    print("\n📋 Test 1: Fresh employee access to escape room")
    try:
        response = session.get("http://localhost:5000/escape/1")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 403:
            print("✅ CORRECT: Shows 'Complete all 10 levels' message")
        elif response.status_code == 200:
            if "replay" in response.text.lower():
                print("❌ PROBLEM: Still shows replay mode")
            else:
                print("✅ SUCCESS: Shows normal escape room (not replay mode)")
        else:
            print(f"❓ UNEXPECTED: Status code {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n💡 If still showing replay mode:")
    print("1. Check browser cookies for old level_completed_* cookies")
    print("2. Try accessing in incognito/private window")
    print("3. Check if UserMissionProgress has old data")
    print("4. Verify is_replay logic in escape room route")

if __name__ == "__main__":
    test_fresh_employee_access()
