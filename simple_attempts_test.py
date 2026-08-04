#!/usr/bin/env python3

import requests

def simple_attempts_test():
    """Simple test to check attempts logic"""
    
    print("🔍 Simple Attempts Test...")
    print("=" * 40)
    
    session = requests.Session()
    
    # Clear cookies
    session.get("http://localhost:5000/debug/clear-cookies")
    
    # First, get the level page to see initial state
    print("\n📋 Getting level 1 page...")
    try:
        response = session.get("http://localhost:5000/level/1")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # Check initial attempts
            if "Attempts Left:" in response.text:
                print("✅ Attempts Left section found")
            else:
                print("❌ Attempts Left section NOT found")
                
            # Check for form
            if "levelForm" in response.text:
                print("✅ Form found")
            else:
                print("❌ Form NOT found")
                
        else:
            print(f"❌ Failed to get level: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Now try to submit a wrong answer
    print("\n📋 Submitting wrong answer...")
    try:
        response = session.post("http://localhost:5000/level/1", data={
            'answer': 'A'  # Wrong answer
        })
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # Check if we got the feedback section
            if "Wrong Answer" in response.text:
                print("✅ Wrong Answer feedback found")
                
                # Check attempts display
                if "Attempts Remaining:" in response.text:
                    print("✅ Attempts Remaining section found")
                    
                    # Extract the attempts number
                    import re
                    attempts_match = re.search(r'Attempts Remaining: <strong>(\d+)</strong>', response.text)
                    if attempts_match:
                        attempts = attempts_match.group(1)
                        print(f"✅ Attempts Remaining: {attempts}")
                        
                        if attempts == "2":
                            print("✅ SUCCESS: Attempts decremented correctly")
                        elif attempts == "3":
                            print("❌ PROBLEM: Attempts NOT decremented")
                        else:
                            print(f"❓ UNEXPECTED: Attempts = {attempts}")
                    else:
                        print("❌ Could not extract attempts number")
                else:
                    print("❌ Attempts Remaining section NOT found")
            else:
                print("❌ Wrong Answer feedback NOT found")
                print("Response preview:")
                print(response.text[:500] + "...")
                
        else:
            print(f"❌ Failed to submit: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    simple_attempts_test()
