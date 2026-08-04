#!/usr/bin/env python3

import requests
import json

def test_escape_room_access():
    """Test escape room access for employee users"""
    
    print("🔍 Testing Escape Room Access...")
    print("=" * 50)
    
    # Test by simulating a fresh employee user
    session = requests.Session()
    
    # First, let's check what happens when we try to access escape room directly
    print("\n📋 Testing direct escape room access...")
    
    # This would simulate going to escape room without completing levels
    try:
        response = session.get("http://localhost:5000/escape/1")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 403:
            print("✅ CORRECT: Shows 'Complete all 10 levels' message")
        elif response.status_code == 200:
            print("⚠️  ISSUE: Escape room accessible without completing levels")
            # Check if it shows replay mode
            if "replay" in response.text.lower():
                print("❌ PROBLEM: Shows replay mode for first-time access")
        else:
            print(f"❓ UNEXPECTED: Status code {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n🔧 Root Cause Analysis:")
    print("1. is_replay logic: level.level_number < prog.current_level")
    print("2. For new users: prog.current_level = 1, level.level_number = 1")
    print("3. So is_replay = False for first level")
    print("4. Cookie check: level_completed_{level_id} should not exist for new users")
    print("5. Issue might be: prog.current_level not being set correctly for employees")
    
    print("\n💡 Recommendation:")
    print("Check UserMissionProgress.levels_completed for employees")
    print("Verify current_level progression in Progress table")
    print("Ensure escape room cookie logic works for both roles")

if __name__ == "__main__":
    test_escape_room_access()
