#!/usr/bin/env python3

import requests
import json

def test_level_access():
    """Test level access to check if UnboundLocalError is fixed"""
    
    print("🎮 Testing Level Access...")
    print("=" * 50)
    
    session = requests.Session()
    
    # Test 1: Try to access level 1 as fresh user
    print("\n📋 Test 1: Fresh access to level 1")
    try:
        response = session.get("http://localhost:5000/level/1")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            if "replay" in response.text.lower():
                print("❌ PROBLEM: Still shows replay mode for level 1")
            else:
                print("✅ SUCCESS: Shows normal level (not replay mode)")
        elif response.status_code == 404:
            print("❓ UNEXPECTED: Level not found")
        else:
            print(f"❓ UNEXPECTED: Status code {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n💡 If still showing replay mode:")
    print("1. Check browser cookies for old level_completed_* cookies")
    print("2. Try accessing in incognito/private window")
    print("3. Check if UnboundLocalError is fixed in play_level function")
    print("4. Verify level_completed cookie is defined before use")

if __name__ == "__main__":
    test_level_access()
