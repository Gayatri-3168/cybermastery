#!/usr/bin/env python3

import requests
import json
import time

def test_speed():
    """Test chatbot response speed"""
    
    questions = [
        "hi",
        "what is phishing", 
        "how do missions work",
        "how do i earn xp",
        "what are badges",
        "what are learning modules",
        "tell me about social engineering"  # This one will use AI
    ]
    
    print("🚀 Testing Chatbot Speed...")
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
                timeout=10
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                print(f"⏱️  Time: {elapsed:.2f}s")
                print(f"🤖 Response: {data['reply']}")
                
                if elapsed < 1:
                    print("⚡ Lightning fast!")
                elif elapsed < 3:
                    print("✅ Good speed")
                else:
                    print("⚠️  Slow response")
            else:
                print(f"❌ Status: {response.status_code}")
                
        except Exception as e:
            elapsed = time.time() - start
            print(f"⏱️  Time: {elapsed:.2f}s")
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_speed()
