#!/usr/bin/env python3

import sys
sys.path.append('.')

try:
    from app import app
    print("✅ App imported")
    
    import google.genai
    print("✅ google.genai imported")
    
    with app.app_context():
        from flask import g
        print(f"🔍 gemini_client: {hasattr(g, 'gemini_client')}")
        
        if hasattr(g, 'gemini_client'):
            print("✅ Chatbot should work!")
        else:
            print("❌ Chatbot client not initialized")
            
except Exception as e:
    print(f"❌ Error: {e}")
