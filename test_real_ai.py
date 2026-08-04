#!/usr/bin/env python3

import requests
import json

def test_real_ai():
    """Test if chatbot uses real AI"""
    
    questions = [
        "What is phishing?",
        "How do missions work?",
        "What are learning modules?"
    ]
    
    print("🤖 Testing Real AI Responses...")
    print("=" * 50)
    
    for question in questions:
        print(f"\n📝 Question: {question}")
        print("-" * 30)
        
        try:
            response = requests.post(
                'http://localhost:5000/chatbot',
                headers={'Content-Type': 'application/json'},
                json={'message': question},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data['reply']
                print(f"🤖 Response: {reply}")
                
                # Analyze response quality
                if len(reply) > 100:
                    print("✅ Detailed response")
                else:
                    print("⚠️  Short response")
                    
                # Check for relevant content
                if 'phishing' in question and ('phishing' in reply.lower() or 'scam' in reply.lower()):
                    print("✅ Relevant content detected")
                elif 'mission' in question and ('mission' in reply.lower() or 'level' in reply.lower()):
                    print("✅ Relevant content detected")
                elif 'module' in question and ('module' in reply.lower() or 'learn' in reply.lower()):
                    print("✅ Relevant content detected")
                else:
                    print("⚠️  Generic response")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_real_ai()
