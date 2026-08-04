#!/usr/bin/env python3

import requests

def test_attempts_counter():
    """Test if attempts counter decrements correctly"""
    
    print("🔍 Testing Attempts Counter...")
    print("=" * 50)
    
    session = requests.Session()
    
    # Clear cookies first
    try:
        session.get("http://localhost:5000/debug/clear-cookies")
        print("✅ Cookies cleared")
    except:
        print("❌ Failed to clear cookies")
    
    # Test wrong answer on level 1
    print("\n📋 Test 1: First wrong answer")
    try:
        response = session.post("http://localhost:5000/level/1", data={
            'answer': 'A'  # Wrong answer (correct is C)
        })
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            if "Attempts Remaining: <strong>2</strong>" in response.text:
                print("✅ SUCCESS: Attempts Remaining: 2 (after 1 wrong)")
            elif "Attempts Remaining: <strong>3</strong>" in response.text:
                print("❌ PROBLEM: Still shows 3 attempts (not decremented)")
            else:
                print("❓ UNKNOWN: Check attempts display")
                print(f"Response preview: {response.text[:300]}...")
                
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test second wrong answer
    print("\n📋 Test 2: Second wrong answer")
    try:
        response = session.post("http://localhost:5000/level/1", data={
            'answer': 'B'  # Wrong answer again (correct is C)
        })
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            if "Attempts Remaining: <strong>1</strong>" in response.text:
                print("✅ SUCCESS: Attempts Remaining: 1 (after 2 wrong)")
            elif "Attempts Remaining: <strong>2</strong>" in response.text:
                print("❌ PROBLEM: Still shows 2 attempts")
            else:
                print("❓ UNKNOWN: Check attempts display")
                print(f"Response preview: {response.text[:300]}...")
                
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test third wrong answer
    print("\n📋 Test 3: Third wrong answer")
    try:
        response = session.post("http://localhost:5000/level/1", data={
            'answer': 'D'  # Wrong answer again (correct is C)
        })
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            if "No attempts left" in response.text:
                print("✅ SUCCESS: No attempts left (after 3 wrong)")
            elif "Attempts Remaining: <strong>0</strong>" in response.text:
                print("✅ SUCCESS: Attempts Remaining: 0")
            else:
                print("❓ UNKNOWN: Check attempts display")
                print(f"Response preview: {response.text[:300]}...")
                
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_attempts_counter()
