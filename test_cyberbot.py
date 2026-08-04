#!/usr/bin/env python3

import requests
import json

def test_cyberbot():
    """Test CyberBot with game and cybersecurity questions"""
    
    base_url = "http://localhost:5000"
    
    test_questions = [
        ("How do missions work?", "game mechanics"),
        ("What is phishing?", "cybersecurity topic"),
        ("How do I earn badges?", "game progression"),
        ("What are escape rooms?", "game features"),
        ("How do learning modules work?", "learning system"),
        ("What topics are covered?", "cybersecurity content"),
        ("How does XP work?", "gamification"),
        ("What's the difference between student and employee?", "user roles")
    ]
    
    print("🤖 Testing CyberBot AI Support...")
    print("=" * 60)
    
    for i, (question, category) in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {question}")
        print(f"🏷️  Category: {category}")
        print("-" * 50)
        
        try:
            response = requests.post(
                f"{base_url}/chatbot",
                headers={"Content-Type": "application/json"},
                json={"message": question},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {data['reply']}")
                
                # Analyze response quality
                response_length = len(data['reply'])
                has_game_terms = any(term in data['reply'].lower() for term in ['mission', 'level', 'xp', 'badge', 'game', 'module', 'escape'])
                has_cyber_terms = any(term in data['reply'].lower() for term in ['phishing', 'password', 'security', 'cyber', 'browsing', 'privacy'])
                
                if response_length > 100 and (has_game_terms or has_cyber_terms):
                    print("🎯 High-quality AI response detected")
                elif response_length > 50:
                    print("📊 Medium-quality response")
                else:
                    print("⚠️  Basic fallback response")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network Error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n🎯 Test complete! Visit: {base_url}/chat-support")
    print("🤖 CyberBot is ready for real questions!")

if __name__ == "__main__":
    test_cyberbot()
