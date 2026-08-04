#!/usr/bin/env python3

import requests

def simple_test():
    """Simple test to check template variables"""
    
    print("🔍 Simple Template Test...")
    print("=" * 40)
    
    session = requests.Session()
    
    # Clear cookies
    session.get("http://localhost:5000/debug/clear-cookies")
    
    # Test level 1 with correct answer
    response = session.post("http://localhost:5000/level/1", data={
        'answer': 'correct'
    })
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        # Look for specific template elements
        content = response.text
        
        print("\n🔍 Checking for template elements:")
        
        # Check for points_awarded in template
        if "points_awarded=10" in content:
            print("✅ points_awarded=10 found")
        elif "points_awarded=0" in content:
            print("⚠️  points_awarded=0 found")
        else:
            print("❌ points_awarded NOT found")
            
        # Check for XP display
        if "+10 XP" in content:
            print("✅ '+10 XP' display found")
        else:
            print("❌ '+10 XP' display NOT found")
            
        # Check for next level
        if "Next Level" in content:
            print("✅ Next Level option found")
        elif "Next Mission" in content:
            print("✅ Next Mission option found")
        else:
            print("❌ Next level/mission option NOT found")
            
        # Show specific lines around points_awarded
        print("\n📄 Lines around points_awarded:")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'points_awarded' in line:
                print(f"  Line {i+1}: {line.strip()}")
                
    else:
        print(f"❌ Failed: {response.status_code}")

if __name__ == "__main__":
    simple_test()
