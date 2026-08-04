#!/usr/bin/env python3

import requests
import time

def test_comprehensive():
    """Test comprehensive coverage of all topics"""
    
    questions = [
        # Greetings
        "hi",
        "hello",
        
        # Learning Modules
        "learning modules",
        "how many learning modules",
        "what do learning modules teach",
        "how do learning modules work",
        "are learning modules required",
        "learning module content",
        "module difficulty",
        "module completion",
        "learning path",
        "module assessment",
        "module topics",
        
        # Game Mechanics
        "how do missions work",
        "how do i earn xp",
        "what are badges",
        "what are escape rooms",
        "how do i unlock missions",
        "how do i level up",
        
        # Cybersecurity Topics
        "what is phishing",
        "social engineering",
        "password safety",
        "browsing safety",
        
        # Platform Info
        "what topics are covered",
        "what is cybermastery"
    ]
    
    print("🎯 Comprehensive Chatbot Test...")
    print("=" * 60)
    
    fast_count = 0
    total_count = len(questions)
    
    for i, question in enumerate(questions, 1):
        print(f"\n📝 {i:2d}. {question}")
        print("-" * 40)
        
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
                    fast_count += 1
                else:
                    print("⚠️  Slow response")
            else:
                print(f"❌ Status: {response.status_code}")
                
        except Exception as e:
            elapsed = time.time() - start
            print(f"⏱️  Time: {elapsed:.2f}s")
            print(f"❌ Error: {e}")
    
    print(f"\n📊 Results: {fast_count}/{total_count} fast responses ({fast_count/total_count*100:.1f}%)")
    
    if fast_count == total_count:
        print("🎉 Perfect! All responses are fast!")
    elif fast_count > total_count * 0.8:
        print("✅ Great performance! Most responses are fast.")
    else:
        print("⚠️  Some responses need optimization.")

if __name__ == "__main__":
    test_comprehensive()
