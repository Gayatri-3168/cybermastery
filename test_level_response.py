#!/usr/bin/env python3

import requests

def test_level_response():
    """Test what's actually being rendered in level response"""
    
    print("🔍 Testing Level Response Content...")
    print("=" * 50)
    
    session = requests.Session()
    
    # Clear cookies first
    try:
        session.get("http://localhost:5000/debug/clear-cookies")
        print("✅ Cookies cleared")
    except:
        print("❌ Failed to clear cookies")
    
    # Test first attempt on level 1
    print("\n📋 Testing first attempt on level 1...")
    try:
        response = session.post("http://localhost:5000/level/1", data={
            'answer': 'correct'  # This should be the correct answer
        })
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Check for XP display
            if "+10 XP" in response.text:
                print("✅ SUCCESS: +10 XP found in response")
            else:
                print("⚠️  WARNING: +10 XP NOT found in response")
                
            # Check for points_awarded value
            if 'points_awarded' in response.text:
                print("✅ SUCCESS: points_awarded variable passed to template")
            else:
                print("⚠️  WARNING: points_awarded variable NOT found")
                
            # Check for next level link
            if "Next Level" in response.text or "next-btn" in response.text:
                print("✅ SUCCESS: Next level option available")
            else:
                print("⚠️  WARNING: Next level option NOT available")
                
            # Show response content
            print(f"\n📄 Response Content Preview:")
            print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
                
        else:
            print(f"❌ Failed: Status code {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_level_response()
