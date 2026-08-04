#!/usr/bin/env python3

import requests
import time

def test_more_questions():
    """Test additional common questions"""
    
    questions = [
        "what are escape rooms",
        "how do i unlock missions", 
        "what topics are covered",
        "how do i level up",
        "what is cybermastery",
        "password safety",
        "browsing safety"
    ]
    
    print("🚀 Testing More Questions...")
    print("=" * 50)
    
    for question in questions:
        print(f"\n📝 Question: {question}")
        print("-" * 30)
        
        start = time.time()
        try:
            response = requests.post(
                'http://localhost:5000/chatbot',
                headers={'Content-Type': 'application/json'},
                json={'message': question},
                timeout=5
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                print(f"⏱️  Time: {elapsed:.2f}s")
                print(f"🤖 Response: {data['reply']}")
                
                if elapsed < 3:
                    print("⚡ Fast response!")
                else:
                    print("⚠️  Slow response")
            else:
                print(f"❌ Status: {response.status_code}")
                
        except Exception as e:
            elapsed = time.time() - start
            print(f"⏱️  Time: {elapsed:.2f}s")
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_more_questions()
