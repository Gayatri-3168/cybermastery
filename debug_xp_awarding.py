#!/usr/bin/env python3

import requests
import json

def debug_xp_awarding():
    """Debug XP awarding for first attempts"""
    
    print("🔍 Debugging XP Awarding...")
    print("=" * 50)
    
    session = requests.Session()
    
    # Test level 1 as fresh user (clear cookies first)
    print("\n🧪 Clearing cookies first...")
    try:
        # Clear cookies by visiting clear route
        session.get("http://localhost:5000/debug/clear-cookies")
        print("✅ Cookies cleared")
    except:
        print("❌ Failed to clear cookies")
    
    # Test first attempt on level 1
    print("\n📋 Testing first attempt on level 1...")
    try:
        # Submit correct answer for level 1
        response = session.post("http://localhost:5000/level/1", data={
            'answer': 'correct'  # This should be the correct answer
        })
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Level submitted successfully")
            
            # Check if points were awarded
            if "+10 XP" in response.text:
                print("✅ SUCCESS: +10 XP awarded for first attempt")
            elif "+5 XP" in response.text:
                print("⚠️  WARNING: +5 XP (second attempt logic)")
            elif "+2 XP" in response.text:
                print("⚠️  WARNING: +2 XP (third+ attempt logic)")
            elif "no XP awarded" in response.text:
                print("❌ PROBLEM: No XP awarded (replay logic)")
            else:
                print("❓ UNKNOWN: Check response content")
                print(f"Response preview: {response.text[:200]}...")
                
        else:
            print(f"❌ Failed to submit level: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n💡 Debugging Tips:")
    print("1. Check if 'correct' is the right answer for level 1")
    print("2. Look at server console for debug output")
    print("3. Verify level_completed cookie logic")
    print("4. Check is_replay calculation")

if __name__ == "__main__":
    debug_xp_awarding()
