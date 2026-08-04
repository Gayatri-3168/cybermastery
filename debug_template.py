#!/usr/bin/env python3

import requests

def debug_template():
    """Debug the exact template response"""
    
    print("🔍 Debugging Template Response...")
    print("=" * 50)
    
    session = requests.Session()
    
    # Clear cookies
    session.get("http://localhost:5000/debug/clear-cookies")
    
    # Test level 1 with correct answer
    response = session.post("http://localhost:5000/level/1", data={
        'answer': 'correct'
    })
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.text
        
        # Find the feedback section
        if "<!-- ✅ CORRECT ANSWER -->" in content:
            print("✅ Found correct answer section")
            
            # Extract the feedback div
            start = content.find('<div class="feedback success">')
            end = content.find('</div>', start)
            if start != -1 and end != -1:
                feedback_section = content[start:end]
                print(f"📄 Feedback section: {feedback_section}")
                
                # Check for points_awarded in the feedback
                if "points_awarded=10" in feedback_section:
                    print("✅ points_awarded=10 in template")
                elif "points_awarded=0" in feedback_section:
                    print("⚠️  points_awarded=0 in template")
                else:
                    print("❌ points_awarded variable missing")
                    
        # Find the next level section
        if "Next Level" in content:
            print("✅ Next Level link found")
        elif "Next Mission" in content:
            print("✅ Next Mission link found")
        else:
            print("❌ No next level/mission link found")
            
        # Show the complete response around the feedback area
        print("\n📄 Complete response around feedback:")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'feedback' in line.lower() or 'points_awarded' in line.lower():
                print(f"  Line {i+1}: {line.strip()}")
                
    else:
        print(f"❌ Failed: {response.status_code}")

if __name__ == "__main__":
    debug_template()
