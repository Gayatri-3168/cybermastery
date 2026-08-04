#!/usr/bin/env python3

import google.genai as genai

def test_gemini_direct():
    """Test Gemini API directly"""
    
    print("🤖 Testing Gemini API Directly...")
    print("=" * 50)
    
    try:
        # Initialize client
        GEMINI_API_KEY = 'AIzaSyDm0SBD-4VCXokAm462YCrwka2VJq9JgiE'
        client = genai.Client(api_key=GEMINI_API_KEY)
        print("✅ Client initialized")
        
        # Test simple question
        system_prompt = """You are CyberBot, assistant for CyberMastery cybersecurity learning platform.

Answer questions about:
🎮 Game: 5 learning modules → missions → levels → escape rooms
🏆 XP/Badges: Earn points, Cyber Beginner (2 missions), Cyber Expert (5 missions)
🔒 Topics: Phishing, passwords, browsing, social media, ethics
👥 Roles: Student (K-12) vs Employee (corporate)

Be concise, helpful, use emojis."""
        
        question = "What is phishing?"
        full_prompt = f"{system_prompt}\n\nUser Question: {question}\nAssistant:"
        
        print(f"📝 Question: {question}")
        print("-" * 30)
        
        # Make API call
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=full_prompt
        )
        
        ai_reply = response.text.strip()
        print(f"✅ Gemini Response: {ai_reply}")
        print(f"📏 Response length: {len(ai_reply)} characters")
        
        # Check quality
        if len(ai_reply) > 100 and ('phishing' in ai_reply.lower() or 'scam' in ai_reply.lower()):
            print("🎯 High-quality AI response!")
        else:
            print("⚠️  Basic response")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"❌ Type: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_gemini_direct()
